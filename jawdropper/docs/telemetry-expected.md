# JawDropper Expected Telemetry

```
============================================================================
ESINTA EMULATION — AUTHORIZED SECURITY TESTING ONLY

This document describes what endpoint telemetry tools SHOULD capture
when JawDropper executes. Use this to validate your detection capabilities.
============================================================================
```

## Overview

This document lists the telemetry signals that security tools should capture at each stage of JawDropper execution. If your EDR/SIEM doesn't capture these events, you have a visibility gap.

## Telemetry by Stage

### Stage 1: JavaScript Dropper

| Event Type | Field | Expected Value |
|------------|-------|----------------|
| Process Create | Parent | explorer.exe (or shell) |
| Process Create | Process | wscript.exe |
| Process Create | CommandLine | `wscript.exe "...\dropper.js"` |
| Process Create | Child | powershell.exe |
| Script Execution | Script | dropper.js content (if AMSI logging) |

**EDR Detection Logic:**
```
process_name = "wscript.exe" AND
command_line CONTAINS ".js" AND
child_process_name = "powershell.exe"
```

### Stage 2: PowerShell Download Cradle

| Event Type | Field | Expected Value |
|------------|-------|----------------|
| Process Create | Parent | wscript.exe |
| Process Create | Process | powershell.exe |
| Process Create | CommandLine | `-WindowStyle Hidden -ep Bypass -encodedcommand` |
| Script Block | Content | `Invoke-WebRequest`, `$env:TEMP`, `regsvr32` |
| Network Connect | Destination | 192.168.0.148:8888 |
| Network Connect | Protocol | HTTP |
| File Create | Path | `C:\Users\...\AppData\Local\Temp\update.dll` |
| File Create | Extension | .dll |

**EDR Detection Logic:**
```
process_name = "powershell.exe" AND
command_line CONTAINS "-encodedcommand" AND
(
  network_destination MATCHES "192\.168\.\d+\.\d+" OR
  file_path CONTAINS "\\Temp\\" AND file_extension = ".dll"
)
```

### Stage 3: Regsvr32 Execution

| Event Type | Field | Expected Value |
|------------|-------|----------------|
| Process Create | Parent | powershell.exe |
| Process Create | Process | regsvr32.exe |
| Process Create | CommandLine | `/s` and path to DLL in TEMP |
| Module Load | Module | update.dll (or payload.dll) |
| Module Load | Path | `%TEMP%\update.dll` |

**EDR Detection Logic:**
```
process_name = "regsvr32.exe" AND
command_line CONTAINS "/s" AND
module_path CONTAINS "\\Temp\\"
```

### Stage 4: Discovery Commands

| Event Type | Field | Expected Value |
|------------|-------|----------------|
| Process Create | Parent | regsvr32.exe |
| Process Create | Process | cmd.exe |
| Process Create | CommandLine | Various discovery commands |

**Commands to detect:**

| Command | CommandLine Pattern |
|---------|---------------------|
| whoami | `cmd.exe /c whoami` |
| ipconfig | `cmd.exe /c ipconfig /all` |
| net view | `cmd.exe /c net view` |
| arp | `cmd.exe /c arp -a` |
| nslookup | `cmd.exe /c nslookup -querytype=ALL` |
| nltest | `cmd.exe /c nltest /domain_trusts` |

**EDR Detection Logic:**
```
parent_process_name = "regsvr32.exe" AND
process_name = "cmd.exe" AND
command_line MATCHES "(whoami|ipconfig|net view|arp|nslookup|nltest)"
```

**Behavioral Rule (Discovery Burst):**
```
COUNT(process_create WHERE
  parent_process_name = "regsvr32.exe" AND
  process_name = "cmd.exe" AND
  time_window = 60s
) >= 3
```

### Stage 5: Persistence (Scheduled Task)

| Event Type | Field | Expected Value |
|------------|-------|----------------|
| Process Create | Parent | regsvr32.exe |
| Process Create | Process | cmd.exe |
| Process Create | CommandLine | `schtasks /create /tn "JawDropper"` |
| Process Create | Process | schtasks.exe |
| Scheduled Task | TaskName | JawDropper |
| Scheduled Task | Action | calc.exe |
| Windows Event | EventID | 4698 (Task created) |

**EDR Detection Logic:**
```
process_name = "schtasks.exe" AND
command_line CONTAINS "/create"
```

**Windows Event Log:**
- Event ID 4698: A scheduled task was created
- Event ID 106: Task registered (Task Scheduler operational log)

### Stage 6: C2 Beacon

| Event Type | Field | Expected Value |
|------------|-------|----------------|
| Network Connect | Source Process | regsvr32.exe |
| Network Connect | Destination | 192.168.0.148:8888 |
| Network Connect | Method | POST |
| Network Connect | Path | /beacon |
| Network Connect | Body | JSON with hostname, pid |

**EDR Detection Logic:**
```
process_name = "regsvr32.exe" AND
network_connection = TRUE AND
network_destination_port = 8888
```

### Stage 7: Payload Execution

| Event Type | Field | Expected Value |
|------------|-------|----------------|
| Process Create | Parent | regsvr32.exe |
| Process Create | Process | calc.exe |

**EDR Detection Logic:**
```
parent_process_name = "regsvr32.exe" AND
process_name = "calc.exe"
```

(Normally benign, but suspicious parent-child relationship)

## Complete Process Tree

Your telemetry should show:

```
wscript.exe dropper.js
  └── powershell.exe -WindowStyle Hidden -ep Bypass -encodedcommand ...
        └── regsvr32.exe /s C:\Users\...\AppData\Local\Temp\update.dll
              ├── cmd.exe /c whoami
              ├── cmd.exe /c ipconfig /all
              ├── cmd.exe /c net view
              ├── cmd.exe /c arp -a
              ├── cmd.exe /c nslookup -querytype=ALL -timeout=12 ...
              ├── cmd.exe /c nltest /domain_trusts /all_trusts
              ├── cmd.exe /c schtasks /create /tn "JawDropper" ...
              └── calc.exe
```

## Event Summary Table

| Stage | Event Count | Key Detection |
|-------|-------------|---------------|
| JS Dropper | 2 processes | wscript.exe → powershell.exe |
| PowerShell | 1 process, 1 network, 1 file | encodedcommand, HTTP GET, DLL write |
| Regsvr32 | 1 process, 1 module | regsvr32 /s from TEMP |
| Discovery | 6 processes | cmd.exe burst from regsvr32 |
| Persistence | 1 process, 1 task | schtasks /create |
| C2 Beacon | 1 network | HTTP POST to /beacon |
| Payload | 1 process | calc.exe from regsvr32 |
| **Total** | **~13 processes, 2 network, 1 file, 1 module, 1 task** | |

## SIEM Correlation Rules

### Rule 1: QakBot-Style Initial Access

```
(process_name = "wscript.exe" AND command_line CONTAINS ".js")
FOLLOWED BY
(process_name = "powershell.exe" AND command_line CONTAINS "-encodedcommand")
WITHIN 30 seconds
```

### Rule 2: Regsvr32 Loading DLL from TEMP

```
process_name = "regsvr32.exe" AND
command_line CONTAINS "/s" AND
command_line MATCHES "\\Temp\\.*\.dll"
```

### Rule 3: Discovery Command Burst

```
COUNT(
  process_name = "cmd.exe" AND
  parent_process_name IN ("regsvr32.exe", "rundll32.exe") AND
  command_line MATCHES "(whoami|ipconfig|net view|arp|nslookup|nltest)"
) >= 3 WITHIN 120 seconds
```

### Rule 4: Suspicious Scheduled Task Creation

```
process_name = "schtasks.exe" AND
command_line CONTAINS "/create" AND
parent_process_name NOT IN ("taskeng.exe", "svchost.exe", "mmc.exe")
```

### Rule 5: HTTP Beacon Pattern

```
process_name = "regsvr32.exe" AND
network_destination_port NOT IN (80, 443) AND
network_method = "POST"
```

## Visibility Gap Checklist

Use this checklist to validate your telemetry coverage:

| Telemetry Type | Required For | ✓ |
|----------------|--------------|---|
| Process creation with command line | All stages | ☐ |
| Parent-child process relationships | Process tree | ☐ |
| PowerShell script block logging | Stage 2 | ☐ |
| Network connections with process | C2 detection | ☐ |
| File creation events | DLL download | ☐ |
| Module/DLL load events | Stage 3 | ☐ |
| Scheduled task events | Persistence | ☐ |
| Windows Security events (4698) | Persistence | ☐ |

## Testing Procedure

1. Start telemetry collection
2. Execute JawDropper
3. Wait 30 seconds for completion
4. Query for each expected event
5. Document any missing telemetry
6. Adjust collection or detection rules

## Sample Queries

### Splunk

```spl
index=windows sourcetype=WinEventLog:Security
| search EventCode IN (4688, 4698)
| where match(CommandLine, "(?i)(wscript|powershell|regsvr32|schtasks)")
| table _time, ComputerName, User, EventCode, Process_Command_Line
```

### Elastic/KQL

```kql
process.name: ("wscript.exe" or "powershell.exe" or "regsvr32.exe" or "cmd.exe")
and process.args: ("dropper.js" or "-encodedcommand" or "/s" or "schtasks")
| sort @timestamp
```

### Microsoft Defender for Endpoint

```kql
DeviceProcessEvents
| where FileName in~ ("wscript.exe", "powershell.exe", "regsvr32.exe", "cmd.exe")
| where ProcessCommandLine has_any ("dropper.js", "-encodedcommand", "/s", "whoami", "ipconfig")
| project Timestamp, DeviceName, FileName, ProcessCommandLine, InitiatingProcessFileName
```
