# MuddyCalc — MITRE ATT&CK Mapping

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
| T1566.001 | Phishing: Spearphishing Attachment | Initial Access | Delivery | Macro-enabled .xlsm spreadsheet served from local HTTP server | Email gateway scanning (N/A in lab); file download from unusual source |
| T1204.002 | User Execution: Malicious File | Execution | Stage 1 | User opens spreadsheet and enables macros; `Workbook_Open()` fires automatically | Process creation: Office application spawning child process |
| T1059.005 | Command and Scripting Interpreter: Visual Basic | Execution | Stage 1 → 2 | VBA macro drops VBScript to `%TEMP%\update_check.vbs`; executed via `wscript.exe` | File write: `.vbs` in `%TEMP%`; Process: `soffice.bin` → `wscript.exe` |
| T1547.001 | Boot/Logon Autostart Execution: Registry Run Keys | Persistence | Stage 2 | VBScript writes `HKCU\...\Run\UpdateCheck = "calc.exe"` via `wsh.RegWrite` | Registry modification: new value in `CurrentVersion\Run` |
| T1059.001 | Command and Scripting Interpreter: PowerShell | Execution | Stage 2 → 3 | VBScript launches `powershell.exe -encodedcommand <base64>` containing POWERSTATS | Process: `wscript.exe` → `powershell.exe`; Command line: `-encodedcommand` flag |
| T1497.003 | Virtualization/Sandbox Evasion: Time Based | Defense Evasion | Stage 3 | `Start-Sleep -Seconds 3` before discovery (real POWERSTATS uses WMI sandbox queries) | Timing: delay before child process creation; PowerShell: `Start-Sleep` cmdlet |
| T1033 | System Owner/User Discovery | Discovery | Stage 3 | `cmd.exe /c whoami` — identifies current user context | Process: `powershell.exe` → `cmd.exe`; Command line: `whoami` |
| T1082 | System Information Discovery | Discovery | Stage 3 | `cmd.exe /c systeminfo` — collects OS version, architecture, domain, hotfixes | Process: `powershell.exe` → `cmd.exe`; Command line: `systeminfo` |
| T1016 | System Network Configuration Discovery | Discovery | Stage 3 | `cmd.exe /c ipconfig /all` — enumerates network adapters, DNS, DHCP | Process: `powershell.exe` → `cmd.exe`; Command line: `ipconfig /all` |
| T1057 | Process Discovery | Discovery | Stage 3 | `cmd.exe /c tasklist` — lists running processes (used to identify security tools) | Process: `powershell.exe` → `cmd.exe`; Command line: `tasklist` |
| T1069.002 | Permission Groups Discovery: Domain Groups | Discovery | Stage 3 | `cmd.exe /c net group "Domain Admins" /domain` — enumerates domain admin accounts | Process: `powershell.exe` → `cmd.exe`; Command line: `net group` |
| T1083 | File and Directory Discovery | Discovery | Stage 3 | `cmd.exe /c dir %USERPROFILE%\Documents` — enumerates user documents | Process: `powershell.exe` → `cmd.exe`; Command line: `dir` |
| T1071.001 | Application Layer Protocol: Web Protocols | Command and Control | Stage 3 | HTTP POST to `http://192.168.0.148:8888/beacon` with JSON discovery data | Network: HTTP POST; Destination: unusual port (8888); Content: JSON with system info |

## MITRE ATT&CK Navigator Layer

The techniques above map to the following ATT&CK tactics:

```
Initial Access  →  Execution  →  Persistence  →  Defense Evasion  →  Discovery  →  C2
T1566.001         T1204.002     T1547.001       T1497.003           T1033        T1071.001
                  T1059.005                                          T1082
                  T1059.001                                          T1016
                                                                     T1057
                                                                     T1069.002
                                                                     T1083
```

## Threat Group & Malware References

| MITRE ID | Name | Type |
|----------|------|------|
| G0069 | MuddyWater | Threat Group |
| S0223 | POWERSTATS | Malware |

## Techniques NOT Emulated

These techniques are documented for MuddyWater (G0069) but are not included in MuddyCalc:

| Technique ID | Name | Reason Not Included |
|-------------|------|---------------------|
| T1003 | OS Credential Dumping | Actual offensive capability |
| T1021 | Remote Services | Lateral movement — could cause real damage |
| T1053.005 | Scheduled Task | Additional persistence — unnecessary complexity |
| T1055 | Process Injection | Evasion technique |
| T1105 | Ingress Tool Transfer | Would require downloading additional tools |
| T1132.001 | Data Encoding: Standard Encoding | Multiple obfuscation layers — evasion |
| T1140 | Deobfuscate/Decode Files | Part of obfuscation chain we skip |
| T1218.011 | Signed Binary Proxy: Rundll32 | Alternative execution method |
| T1560 | Archive Collected Data | Data staging for exfiltration |
| T1567.002 | Exfiltration Over Web Service | Cloud C2 channels |
