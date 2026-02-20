# JawDropper Stage 2 — DLL Loader

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

Stage 2 is a Windows DLL that emulates QakBot post-exploitation behavior. When loaded via `regsvr32.exe /s`, it executes a sequence of discovery commands, creates persistence, beacons to the C2 server, and launches a safe payload (calc.exe).

## Files

| File | Description |
|------|-------------|
| `loader.c` | C source code for the DLL |
| `loader.def` | Module definition file (exports) |
| `Makefile` | Cross-compile configuration |
| `build.sh` | Convenience build script |

## Build Prerequisites

You need mingw-w64 to cross-compile for Windows:

**macOS:**
```bash
brew install mingw-w64
```

**Ubuntu/Debian:**
```bash
apt install mingw-w64
```

**Fedora:**
```bash
dnf install mingw64-gcc
```

## Build Instructions

### Using the build script (recommended):

```bash
./build.sh
```

This will:
1. Check for mingw-w64
2. Clean previous build
3. Compile the DLL
4. Copy to `c2-server/payloads/payload.dll`

### Using make directly:

```bash
make clean && make
make install  # Copies to payloads directory
```

## Execution Flow

When loaded via `regsvr32.exe /s jawdropper.dll`:

```
DllRegisterServer() entry
         │
         ▼
┌─────────────────────────────────────────────────────────────────┐
│ Stage 1: Anti-analysis delay                                    │
│                                                                 │
│ Sleep(2000)                                                     │
│ MITRE: T1497.003 — Time-Based Evasion                           │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│ Stage 2: Discovery burst                                        │
│                                                                 │
│ cmd.exe /c whoami              — T1033 System Owner Discovery   │
│ cmd.exe /c ipconfig /all       — T1016 Network Configuration    │
│ cmd.exe /c net view            — T1018 Remote System Discovery  │
│ cmd.exe /c arp -a              — T1016 ARP Cache                │
│ cmd.exe /c nslookup ...        — T1018 DC Discovery             │
│ cmd.exe /c nltest ...          — T1482 Domain Trust Discovery   │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│ Stage 3: Persistence                                            │
│                                                                 │
│ schtasks /create /tn "JawDropper" /tr "calc.exe" ...            │
│ MITRE: T1053.005 — Scheduled Task                               │
│                                                                 │
│ NOTE: Task runs calc.exe (SAFE), not the DLL                    │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│ Stage 4: C2 Beacon                                              │
│                                                                 │
│ HTTP POST to http://192.168.0.148:8888/beacon                   │
│ Body: {"hostname": "...", "pid": ..., "stage": "loader_complete"}
│ MITRE: T1071.001 — Web Protocols                                │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│ Stage 5: Final payload                                          │
│                                                                 │
│ CreateProcess("calc.exe")                                       │
│ SAFE: This is hardcoded and cannot be changed                   │
└─────────────────────────────────────────────────────────────────┘
```

## MITRE ATT&CK Mapping

| Technique ID | Name | Implementation |
|-------------|------|----------------|
| T1218.010 | Signed Binary Proxy: Regsvr32 | DLL loaded via regsvr32 /s |
| T1497.003 | Time-Based Evasion | Sleep(2000) before activity |
| T1033 | System Owner/User Discovery | whoami command |
| T1016 | System Network Config Discovery | ipconfig /all, arp -a |
| T1018 | Remote System Discovery | net view, nslookup |
| T1482 | Domain Trust Discovery | nltest /domain_trusts |
| T1053.005 | Scheduled Task/Job | schtasks /create |
| T1071.001 | Application Layer Protocol: Web | HTTP POST beacon |

## Expected Process Tree

When the full chain executes:

```
wscript.exe dropper.js                          ← Stage 1
  └── powershell.exe -encodedcommand ...        ← Download cradle
        └── regsvr32.exe /s update.dll          ← Stage 2 entry
              ├── cmd.exe /c whoami
              ├── cmd.exe /c ipconfig /all
              ├── cmd.exe /c net view
              ├── cmd.exe /c arp -a
              ├── cmd.exe /c nslookup ...
              ├── cmd.exe /c nltest ...
              ├── cmd.exe /c schtasks ...
              └── calc.exe                      ← SAFE payload
```

## Telemetry Expected

Security tools should capture:

| Event Type | What to Look For |
|------------|------------------|
| Process creation | regsvr32.exe loading DLL from TEMP |
| Process creation | Multiple cmd.exe children of regsvr32 |
| Command line | Discovery commands (whoami, ipconfig, etc.) |
| Process creation | schtasks.exe creating scheduled task |
| Scheduled task | Task named "JawDropper" created |
| Network | HTTP POST to 192.168.0.148:8888/beacon |
| Process creation | calc.exe spawned by regsvr32 |

## Safety Mechanisms

### 1. Hardcoded Safe Payload

The final payload is defined as:
```c
#define PAYLOAD_COMMAND "calc.exe"
```

This cannot be changed via:
- Command-line arguments
- Environment variables
- C2 server responses
- Configuration files

### 2. Hardcoded Private C2

The C2 address is defined as:
```c
#define C2_HOST L"192.168.0.148"
#define C2_PORT 8888
```

This is a private RFC1918 address that only works on local networks.

### 3. Safe Scheduled Task

The persistence mechanism creates a task that runs `calc.exe`, not the DLL:
```
schtasks /create /tn "JawDropper" /tr "calc.exe" /sc daily /st 09:00 /f
```

## What We Don't Implement

| QakBot Behavior | Why Not Implemented |
|-----------------|---------------------|
| Process injection | Could hide malicious activity |
| Encrypted C2 | Obfuscation, not needed for detection testing |
| Module download | Would require real payload delivery |
| Credential theft | Actual offensive capability |
| Email harvesting | Privacy violation |

## Manual Execution

To test the DLL directly (without stage 1):

```powershell
# On Windows VM
regsvr32.exe /s C:\path\to\jawdropper.dll
```

## Cleanup

After testing, remove the scheduled task:

```powershell
schtasks /delete /tn "JawDropper" /f
```

Or revert to your VM snapshot.

## Attribution

This DLL emulates QakBot behavior documented in:
- CISA AA23-242A (August 2023)
- MITRE ATT&CK S0650
- The DFIR Report QakBot case studies
