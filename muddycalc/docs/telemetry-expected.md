# MuddyCalc — Expected Endpoint Telemetry

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

This document describes what endpoint detection tools SHOULD capture at each stage of the MuddyCalc attack chain. Use this as a checklist when validating your telemetry collection.

## Telemetry Events by Stage

### Stage 1: Macro Execution

| Event Type | What to Look For | MITRE ID | Priority |
|------------|------------------|----------|----------|
| Process creation | `soffice.bin` spawning `wscript.exe` | T1059.005 | HIGH |
| File write | `.vbs` file created in `%TEMP%` directory | T1059.005 | HIGH |
| Command line | `wscript.exe` with path containing `update_check.vbs` | T1059.005 | HIGH |
| File content | VBScript content written to `%TEMP%\update_check.vbs` | T1059.005 | MEDIUM |

**Key detection rule:** Any Office process (`soffice.bin`, `soffice.exe`, `WINWORD.EXE`, `EXCEL.EXE`) spawning a scripting engine (`wscript.exe`, `cscript.exe`, `powershell.exe`, `cmd.exe`) is a high-confidence indicator of macro-based malware.

### Stage 2: VBScript Persistence + PowerShell Launch

| Event Type | What to Look For | MITRE ID | Priority |
|------------|------------------|----------|----------|
| Registry modification | `HKCU\Software\Microsoft\Windows\CurrentVersion\Run\UpdateCheck` created | T1547.001 | HIGH |
| Registry value | Value = `calc.exe` (Type: REG_SZ) | T1547.001 | HIGH |
| Process creation | `wscript.exe` spawning `powershell.exe` | T1059.001 | HIGH |
| Command line | `powershell.exe -WindowStyle Hidden -ExecutionPolicy Bypass -encodedcommand` | T1059.001 | HIGH |
| Command line | Base64-encoded string in PowerShell arguments | T1059.001 | HIGH |

**Key detection rules:**
- `wscript.exe` → `powershell.exe` parent-child relationship
- PowerShell with `-encodedcommand` flag (common in malware delivery)
- PowerShell with `-WindowStyle Hidden` flag (attempt to hide execution)
- New Registry Run key creation (persistence)

### Stage 3: POWERSTATS Discovery

| Event Type | What to Look For | MITRE ID | Priority |
|------------|------------------|----------|----------|
| Process creation | `powershell.exe` spawning `cmd.exe /c whoami` | T1033 | MEDIUM |
| Process creation | `powershell.exe` spawning `cmd.exe /c systeminfo` | T1082 | MEDIUM |
| Process creation | `powershell.exe` spawning `cmd.exe /c ipconfig /all` | T1016 | MEDIUM |
| Process creation | `powershell.exe` spawning `cmd.exe /c tasklist` | T1057 | MEDIUM |
| Process creation | `powershell.exe` spawning `cmd.exe /c net group "Domain Admins" /domain` | T1069.002 | HIGH |
| Process creation | `powershell.exe` spawning `cmd.exe /c dir %USERPROFILE%\Documents` | T1083 | MEDIUM |

**Key detection rules:**
- Multiple `cmd.exe` children spawned by a single `powershell.exe` process in rapid succession (burst pattern)
- Discovery command enumeration: `whoami` + `systeminfo` + `ipconfig` in the same process tree
- `net group "Domain Admins"` query — high-confidence indicator of domain reconnaissance

### Stage 3: C2 Beacon

| Event Type | What to Look For | MITRE ID | Priority |
|------------|------------------|----------|----------|
| Network connection | HTTP POST from `powershell.exe` to `192.168.0.148:8888` | T1071.001 | HIGH |
| Network content | JSON body with hostname, username, PID, discovery results | T1071.001 | MEDIUM |
| DNS resolution | (None — direct IP connection, no DNS) | — | INFO |

**Key detection rules:**
- PowerShell making outbound HTTP connections
- HTTP POST to non-standard port (8888)
- JSON payload containing system information

### Final Payload

| Event Type | What to Look For | MITRE ID | Priority |
|------------|------------------|----------|----------|
| Process creation | `powershell.exe` spawning `calc.exe` | — | LOW |

**Note:** `calc.exe` is the safe payload. In a real attack, this would be a malicious tool (Mimikatz, LaZagne, RAT, etc.).

## Complete Process Tree Telemetry

Your endpoint tool should capture this full process chain:

```
soffice.exe (PID: A)
  └── soffice.bin (PID: B)
        └── wscript.exe %TEMP%\update_check.vbs (PID: C)
              └── powershell.exe -WindowStyle Hidden -ep Bypass -encodedcommand <base64> (PID: D)
                    ├── cmd.exe /c whoami (PID: E1)
                    ├── cmd.exe /c systeminfo (PID: E2)
                    ├── cmd.exe /c ipconfig /all (PID: E3)
                    ├── cmd.exe /c tasklist (PID: E4)
                    ├── cmd.exe /c net group "Domain Admins" /domain (PID: E5)
                    ├── cmd.exe /c dir %USERPROFILE%\Documents (PID: E6)
                    └── calc.exe (PID: F)
```

## Telemetry Validation Checklist

Use this checklist when testing your endpoint detection:

- [ ] Office → scripting engine parent-child relationship captured
- [ ] File write to `%TEMP%` directory captured
- [ ] Registry Run key modification captured
- [ ] PowerShell with `-encodedcommand` captured
- [ ] PowerShell with `-WindowStyle Hidden` captured
- [ ] Each `cmd.exe` discovery command captured with full command line
- [ ] Process tree relationships (parent-child PIDs) correctly linked
- [ ] HTTP POST network connection captured with destination IP/port
- [ ] `calc.exe` process creation captured

## Notes on LibreOffice vs Microsoft Office

| Behavior | Microsoft Office | LibreOffice |
|----------|-----------------|-------------|
| Parent process | `EXCEL.EXE` | `soffice.bin` or `soffice.exe` |
| Macro engine | VBA engine built-in | StarBASIC (VBA compatibility mode) |
| COM objects | Full support | Requires Windows + COM bridge |
| Detection rules | Well-documented | May need custom rules for `soffice.*` |

If your detection rules only look for `EXCEL.EXE` or `WINWORD.EXE` as parent processes, you may need to add `soffice.exe` and `soffice.bin` patterns for LibreOffice coverage.
