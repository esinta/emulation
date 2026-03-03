# MuddyCalc Stage 3 — POWERSTATS Backdoor Emulation

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

This stage emulates **POWERSTATS** ([MITRE S0223](https://attack.mitre.org/software/S0223/)), a PowerShell-based first-stage backdoor used by MuddyWater since at least 2017. Real POWERSTATS collects system information, sends it to C2, and executes commands received from the operator.

## What Real POWERSTATS Does vs. What We Emulate

| Capability | Real POWERSTATS | Our Emulation |
|-----------|----------------|---------------|
| **Obfuscation** | Multiple layers of base64, string replacement, character substitution | None — plaintext PowerShell |
| **Sandbox detection** | WMI queries checking for VM artifacts, MAC address prefixes | Start-Sleep -Seconds 3 |
| **Discovery** | System info, network config, running processes, domain info | Same commands via cmd.exe /c |
| **C2 protocol** | HTTPS to compromised web servers or cloud storage (OneDrive) | Plaintext HTTP POST to local server |
| **C2 loop** | Persistent loop with backoff, polling for commands | Single execution, no loop |
| **Command execution** | Arbitrary PowerShell/cmd from C2 response | Always launches calc.exe |
| **Credential theft** | Mimikatz, LaZagne deployment | Not implemented |
| **Lateral movement** | PsExec, WMI remote execution | Not implemented |

## Files

| File | Purpose |
|------|---------|
| `powerstats.ps1` | Decoded PowerShell payload — this is the human-readable source |

In the full chain, this script is base64-encoded (by `encode_payload.py`) and delivered via PowerShell's `-encodedcommand` parameter through the VBScript.

## Standalone Testing

```powershell
# Run directly (without the full chain)
powershell.exe -ExecutionPolicy Bypass -File powerstats.ps1
```

Make sure the C2 server is running first:
```bash
# On MacBook
python3 c2-server/server.py --port 8888
```

## Expected Process Tree (Standalone)

```
powershell.exe -ep Bypass -File powerstats.ps1
  ├── cmd.exe /c whoami
  ├── cmd.exe /c systeminfo
  ├── cmd.exe /c ipconfig /all
  ├── cmd.exe /c tasklist
  ├── cmd.exe /c net group "Domain Admins" /domain
  ├── cmd.exe /c dir %USERPROFILE%\Documents
  └── calc.exe
```

## Why cmd.exe /c?

Each discovery command uses `cmd.exe /c` instead of native PowerShell cmdlets (like `Get-Process` instead of `tasklist`). This is intentional:

1. **Telemetry visibility** — `cmd.exe` child processes are captured by process-based monitoring
2. **Realistic behavior** — Real POWERSTATS shells out to cmd.exe for discovery
3. **Detection opportunities** — Each `cmd.exe` spawn is a distinct event for EDR to capture

Using native PowerShell cmdlets would execute within the PowerShell process and be invisible to process tree monitoring.

## Cleanup

```powershell
# The script creates no persistent artifacts beyond the Registry key
# (which is written by the VBScript, not this script)

# If calc.exe is still running:
Stop-Process -Name "calc" -ErrorAction SilentlyContinue
```

## MITRE ATT&CK Mapping

| Technique | ID | Implementation |
|-----------|----|---------------|
| Command & Scripting: PowerShell | T1059.001 | Full script runs as PowerShell |
| Time-Based Evasion | T1497.003 | Start-Sleep -Seconds 3 |
| System Owner/User Discovery | T1033 | cmd.exe /c whoami |
| System Information Discovery | T1082 | cmd.exe /c systeminfo |
| System Network Config Discovery | T1016 | cmd.exe /c ipconfig /all |
| Process Discovery | T1057 | cmd.exe /c tasklist |
| Permission Groups Discovery: Domain | T1069.002 | cmd.exe /c net group "Domain Admins" /domain |
| File and Directory Discovery | T1083 | cmd.exe /c dir %USERPROFILE%\Documents |
| Application Layer Protocol: Web | T1071.001 | HTTP POST to 192.168.0.148:8888/beacon |

## Expected Telemetry

| Event | What to Look For |
|-------|------------------|
| Process creation | `powershell.exe` with `-encodedcommand` (full chain) or `-File` (standalone) |
| Command line | Base64-encoded command string (full chain) |
| Process creation | Multiple `cmd.exe` children of `powershell.exe` |
| Command line | Discovery commands: `whoami`, `systeminfo`, `ipconfig /all`, `tasklist`, `net group`, `dir` |
| Network connection | HTTP POST to `192.168.0.148:8888` |
| Process creation | `calc.exe` spawned by `powershell.exe` |
