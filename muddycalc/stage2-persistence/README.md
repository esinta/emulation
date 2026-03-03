# MuddyCalc Stage 2 — VBScript Persistence

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

This stage emulates the VBScript that MuddyWater macros drop to `%TEMP%`. The script establishes persistence via a Registry Run key and launches the POWERSTATS PowerShell backdoor emulation.

## Files

| File | Purpose |
|------|---------|
| `update_check.vbs` | VBScript template (run `encode_payload.py` to generate final version with encoded command) |

## What It Does

```
update_check.vbs executed by wscript.exe
│
├── [1] Registry persistence (T1547.001 — Boot/Logon Autostart: Registry Run Keys)
│       Write: HKCU\Software\Microsoft\Windows\CurrentVersion\Run\UpdateCheck = "calc.exe"
│       NOTE: Value is calc.exe (SAFE), not the backdoor script
│
└── [2] Launch POWERSTATS emulation (T1059.001 — PowerShell)
        wsh.Run "powershell.exe -WindowStyle Hidden -ep Bypass -encodedcommand <base64>"
        Creates: wscript.exe → powershell.exe parent-child relationship
```

## MuddyWater Attribution

Real MuddyWater macros drop multiple files for staging:
- `.dll` files (payload libraries)
- `.reg` files (registry modifications)
- `.inf` files (INF-based execution via `cmstp.exe`)

We simplify to a single `.vbs` file that handles both persistence and PowerShell launch. This achieves the same telemetry signals (file drop to %TEMP%, wscript.exe execution, registry modification) with less complexity.

## Registry Key Details

| Property | Value |
|----------|-------|
| **Key** | `HKCU\Software\Microsoft\Windows\CurrentVersion\Run` |
| **Name** | `UpdateCheck` |
| **Value** | `calc.exe` |
| **Type** | `REG_SZ` |

**SAFETY:** The Run key value is `calc.exe`, not the PowerShell backdoor. If this persistence fires on reboot, it only opens Calculator.

## Manual Testing

To test the VBScript standalone (after running `encode_payload.py` to generate the final version):

```cmd
wscript.exe update_check.vbs
```

Expected behavior:
1. Registry key `HKCU\...\Run\UpdateCheck` created with value `calc.exe`
2. PowerShell process spawned (hidden window)
3. Discovery commands execute
4. C2 beacon sent to 192.168.0.148:8888
5. calc.exe launches

## Cleanup

```powershell
# Remove Registry Run key
Remove-ItemProperty -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Run" -Name "UpdateCheck" -ErrorAction SilentlyContinue

# Remove dropped VBScript
Remove-Item "$env:TEMP\update_check.vbs" -ErrorAction SilentlyContinue
```

## MITRE ATT&CK Mapping

| Technique | ID | Implementation |
|-----------|----|---------------|
| Boot/Logon Autostart: Registry Run Keys | T1547.001 | Writes `HKCU\...\Run\UpdateCheck = "calc.exe"` |
| Command & Scripting: PowerShell | T1059.001 | Launches PowerShell with encoded command |
| Command & Scripting: VBScript | T1059.005 | Script executed via `wscript.exe` |

## Expected Telemetry

| Event | What to Look For |
|-------|------------------|
| Process creation | `wscript.exe` executing `update_check.vbs` |
| Registry modification | `HKCU\...\Run\UpdateCheck` key created |
| Process creation | `wscript.exe` spawning `powershell.exe` |
| Command line | `powershell.exe` with `-encodedcommand` parameter |
