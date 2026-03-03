# MuddyCalc Stage 1 — Macro-Enabled Spreadsheet

```
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
```

## Overview

This stage emulates MuddyWater's initial access vector: a spearphishing attachment containing a macro-enabled spreadsheet. When the user opens the document and enables macros, the VBA code drops a VBScript to `%TEMP%` and executes it via `wscript.exe`.

Real MuddyWater uses social engineering lures including government correspondence, invoices, and internal reports. Our lure is a realistic expense report from a fictional company (Meridian Financial Group).

## Files

| File | Purpose |
|------|---------|
| `build_spreadsheet.py` | Generates the .xlsx with formatted expense data |
| `encode_payload.py` | Base64-encodes PowerShell + generates final macro.vba and update_check.vbs |
| `expense_data.json` | Expense report data (easily modifiable) |
| `macro.vba` | VBA macro source (template — run encode_payload.py for final version) |

## Build Prerequisites

```bash
pip install openpyxl
```

## Build Process

```bash
# Step 1: Generate the spreadsheet
python3 build_spreadsheet.py
# → Q4_2025_ExpenseReport_FINAL_FINAL_v3_DO_NOT_DELETE.xlsx

# Step 2: Generate encoded payload + final macro/VBScript
python3 encode_payload.py
# → Prints base64 string
# → Generates macro.vba (with encoded command)
# → Generates ../stage2-persistence/update_check.vbs (with encoded command)

# Step 3: Open .xlsx in LibreOffice Calc
# → Tools → Macros → Organize Dialogs → BASIC
# → Create a new module and paste the contents of macro.vba (generated version)

# Step 4: Save As .xlsm
# → File → Save As → Microsoft Excel 2007-365 (.xlsm)
# → Name: Q4_2025_ExpenseReport_FINAL_FINAL_v3_DO_NOT_DELETE.xlsm

# Step 5: Copy to muddycalc/ root for serving
# → Copy .xlsm to ~/Documents/Emulation/muddycalc/
```

## Macro Behavior

When `Workbook_Open()` fires:

1. Creates `WScript.Shell` and `Scripting.FileSystemObject` COM objects
2. Constructs VBScript content line-by-line (mirrors real MuddyWater dynamic payload construction)
3. Writes VBScript to `%TEMP%\update_check.vbs`
4. Executes: `wscript.exe "%TEMP%\update_check.vbs"`

### Why Line-by-Line Construction?

Real MuddyWater macros build payloads dynamically using string concatenation and decoding, rather than dropping pre-built files. Writing line-by-line with `scriptFile.WriteLine` emulates this behavior pattern.

### LibreOffice Compatibility Notes

- Uses `CreateObject("WScript.Shell")` instead of VBA `Shell()` for compatibility
- Uses `CreateObject("Scripting.FileSystemObject")` for file operations
- Requires macro security set to **Low** in LibreOffice (Tools → Options → Security → Macro Security)
- Parent process will be `soffice.bin` rather than `EXCEL.EXE` (expected)

## MITRE ATT&CK Mapping

| Technique | ID | Implementation |
|-----------|----|---------------|
| Phishing: Spearphishing Attachment | T1566.001 | Macro-enabled .xlsm delivered to target |
| User Execution: Malicious File | T1204.002 | User opens spreadsheet, enables macros |
| Command & Scripting: VBScript | T1059.005 | Macro drops and executes VBScript to %TEMP% |

## Expected Telemetry

| Event | What to Look For |
|-------|------------------|
| File write | `.vbs` file created in `%TEMP%` directory |
| Process creation | `soffice.bin` spawning `wscript.exe` |
| Command line | `wscript.exe` with path to `update_check.vbs` |
