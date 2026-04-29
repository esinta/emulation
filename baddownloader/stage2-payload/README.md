# BadDownloader — Stage 2: Batch Payload

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

A simple batch file that runs discovery commands, creates persistence via scheduled task, and launches `calc.exe` as the safe payload.

## Commands Executed

| Command | Purpose | MITRE ID |
|---------|---------|----------|
| `whoami` | Identify current user | T1033 |
| `ipconfig /all` | Network configuration | T1016 |
| `systeminfo` | System information | T1082 |
| `net user` | Local account enumeration | T1087.001 |
| `schtasks /create ...` | Scheduled task persistence | T1053.005 |
| `calc.exe` | Safe payload (benign) | — |

## Deployment

This file is hosted on the MacBook C2 server at `192.168.0.148:8888` and downloaded by the Stage 1 binary via PowerShell `Invoke-WebRequest`.

```bash
# Host from the baddownloader directory:
cd ~/Documents/Emulation/baddownloader/stage2-payload
python3 -m http.server 8888
```
