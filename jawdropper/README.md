# JawDropper — QakBot TTP Emulation

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

JawDropper is a safe reconstruction of the QakBot (Qakbot/Pinkslipbot) attack chain documented in [CISA Advisory AA23-242A](https://www.cisa.gov/news-events/cybersecurity-advisories/aa23-242a). It replicates the exact process tree and TTP chain observed in real QakBot BB27/BB28 campaigns (May 2023), but with safety mechanisms that make it suitable for defensive testing.

**What this emulates:**
- QakBot delivery via JavaScript dropper
- PowerShell download cradle with base64 encoding
- DLL execution via regsvr32.exe (signed binary proxy)
- Post-execution discovery commands
- Scheduled task persistence
- C2 beacon pattern

**Safety mechanisms:**
- Final payload is `calc.exe` (hardcoded, not configurable)
- C2 server is `192.168.0.148:8888` (private IP, hardcoded)
- No obfuscation — all code is readable with extensive comments

## Attack Chain Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           JawDropper Attack Chain                           │
│                      (QakBot BB27/BB28 TTP Emulation)                       │
└─────────────────────────────────────────────────────────────────────────────┘

  [User]                    [Windows Target]                    [MacBook C2]
    │                             │                             192.168.0.148
    │                             │                                  │
    │  1. Double-click            │                                  │
    │     dropper.js              │                                  │
    │ ─────────────────────────►  │                                  │
    │                             │                                  │
    │                    ┌────────┴────────┐                         │
    │                    │   wscript.exe   │ T1059.007               │
    │                    │   dropper.js    │ JavaScript Execution    │
    │                    └────────┬────────┘                         │
    │                             │                                  │
    │                             │ Spawns PowerShell                │
    │                             ▼                                  │
    │                    ┌─────────────────┐                         │
    │                    │  powershell.exe │ T1059.001               │
    │                    │ -encodedcommand │ PowerShell Execution    │
    │                    └────────┬────────┘                         │
    │                             │                                  │
    │                             │ 2. Download DLL                  │
    │                             │ ────────────────────────────────►│
    │                             │    GET /payloads/payload.dll     │
    │                             │ ◄────────────────────────────────│
    │                             │         payload.dll              │
    │                             │                                  │
    │                             │ T1105 Ingress Tool Transfer      │
    │                             │                                  │
    │                             │ Execute regsvr32                 │
    │                             ▼                                  │
    │                    ┌─────────────────┐                         │
    │                    │  regsvr32.exe   │ T1218.010               │
    │                    │  /s update.dll  │ Signed Binary Proxy     │
    │                    └────────┬────────┘                         │
    │                             │                                  │
    │                             │ DllRegisterServer()              │
    │                             ▼                                  │
    │                    ┌─────────────────┐                         │
    │                    │   Sleep(2000)   │ T1497.003               │
    │                    │  Anti-sandbox   │ Time-Based Evasion      │
    │                    └────────┬────────┘                         │
    │                             │                                  │
    │                             │ Discovery burst                  │
    │                             ▼                                  │
    │                    ┌─────────────────┐                         │
    │                    │ cmd.exe /c ...  │ T1033, T1016, T1018     │
    │                    │ • whoami        │ T1482                   │
    │                    │ • ipconfig /all │ Discovery Commands      │
    │                    │ • net view      │                         │
    │                    │ • arp -a        │                         │
    │                    │ • nslookup      │                         │
    │                    │ • nltest        │                         │
    │                    └────────┬────────┘                         │
    │                             │                                  │
    │                             │ Create persistence               │
    │                             ▼                                  │
    │                    ┌─────────────────┐                         │
    │                    │   schtasks      │ T1053.005               │
    │                    │   /create ...   │ Scheduled Task          │
    │                    └────────┬────────┘                         │
    │                             │                                  │
    │                             │ 3. Beacon to C2                  │
    │                             │ ────────────────────────────────►│
    │                             │    POST /beacon                  │
    │                             │    {hostname, pid, stage}        │
    │                             │ ◄────────────────────────────────│
    │                             │    {status: ok}                  │
    │                             │                                  │
    │                             │ T1071.001 Web Protocols          │
    │                             │                                  │
    │                             │ Launch "payload"                 │
    │                             ▼                                  │
    │                    ┌─────────────────┐                         │
    │                    │   calc.exe      │ SAFE PAYLOAD            │
    │                    │   (benign)      │ Emulation complete      │
    │                    └─────────────────┘                         │
    │                                                                │
```

## Expected Process Tree

When executed, endpoint telemetry tools should observe:

```
wscript.exe dropper.js                          ← Stage 1: JS execution
  └── powershell.exe -WindowStyle Hidden -ep Bypass -encodedcommand <base64>
        └── regsvr32.exe /s C:\Users\...\AppData\Local\Temp\update.dll
              ├── cmd.exe /c whoami             ← Discovery
              ├── cmd.exe /c ipconfig /all      ← Discovery
              ├── cmd.exe /c net view           ← Discovery
              ├── cmd.exe /c arp -a             ← Discovery
              ├── cmd.exe /c nslookup ...       ← Discovery
              ├── cmd.exe /c nltest ...         ← Discovery
              ├── cmd.exe /c schtasks ...       ← Persistence
              └── calc.exe                      ← "Payload" (safe)
```

## MITRE ATT&CK Mapping

| Technique ID | Name | Implementation |
|-------------|------|----------------|
| T1204.002 | User Execution: Malicious File | User double-clicks dropper.js |
| T1059.007 | Command & Scripting: JavaScript | wscript.exe executes dropper.js |
| T1059.001 | Command & Scripting: PowerShell | Base64-encoded download cradle |
| T1105 | Ingress Tool Transfer | PowerShell downloads DLL from C2 |
| T1218.010 | Signed Binary Proxy: Regsvr32 | regsvr32.exe /s loads DLL |
| T1497.003 | Time-Based Evasion | Sleep(2000) before activity |
| T1033 | System Owner/User Discovery | whoami |
| T1016 | System Network Config Discovery | ipconfig /all, arp -a |
| T1018 | Remote System Discovery | net view, nslookup LDAP SRV |
| T1482 | Domain Trust Discovery | nltest /domain_trusts |
| T1053.005 | Scheduled Task/Job | schtasks /create |
| T1071.001 | Application Layer Protocol: Web | HTTP POST beacon to C2 |

See [docs/mitre-mapping.md](docs/mitre-mapping.md) for detailed technique descriptions.

## Quick Start

### Prerequisites

- **Development machine:** macOS or Linux with:
  - `mingw-w64` cross-compiler (`brew install mingw-w64` on macOS)
  - Python 3.x

- **Target machine:** Windows VM (isolated, snapshotted)
  - Network access to your development machine (192.168.0.148)

### Step 1: Build the Stage 2 DLL

```bash
cd jawdropper/stage2-loader
./build.sh
```

This compiles `loader.c` and copies the output to `c2-server/payloads/payload.dll`.

### Step 2: Start the C2 Server

**Option A: Simple (just serves files)**
```bash
cd jawdropper
python3 -m http.server 8888
```

**Option B: Enhanced (logs beacons)**
```bash
python3 jawdropper/c2-server/server.py --port 8888
```

### Step 3: Copy dropper.js to Windows VM

Transfer `stage1-dropper/dropper.js` to your Windows test VM.

### Step 4: Execute

1. Open your endpoint telemetry tool / EDR console
2. Double-click `dropper.js` on the Windows VM
3. Watch the process tree unfold
4. Observe `calc.exe` launch as the final "payload"
5. Check C2 server logs for beacon activity

### Step 5: Cleanup

On the Windows VM:
```powershell
# Remove the scheduled task
schtasks /delete /tn "JawDropper" /f

# Delete the downloaded DLL
Remove-Item $env:TEMP\update.dll -ErrorAction SilentlyContinue
```

Or simply revert to your VM snapshot.

## Directory Structure

```
jawdropper/
├── README.md                 # This file
├── ATTRIBUTION.md            # Maps components to public sources
│
├── c2-server/                # Local C2 infrastructure
│   ├── server.py             # Python C2 server with beacon logging
│   ├── payloads/             # Staged DLLs go here
│   │   └── .gitkeep
│   └── README.md             # C2 setup instructions
│
├── stage1-dropper/           # Initial access
│   ├── dropper.js            # JScript dropper
│   ├── encoded_command.ps1   # PowerShell source (reference)
│   └── README.md             # Stage 1 details
│
├── stage2-loader/            # Payload DLL
│   ├── loader.c              # C source
│   ├── loader.def            # Module definition
│   ├── Makefile              # Cross-compile config
│   ├── build.sh              # Build convenience script
│   └── README.md             # Stage 2 details
│
├── docs/                     # Documentation
│   ├── attack-chain.md       # Full attack chain walkthrough
│   ├── mitre-mapping.md      # MITRE ATT&CK mapping table
│   └── telemetry-expected.md # Expected telemetry signals
│
└── lab-setup/                # Lab environment configuration
    ├── firewall-prep.ps1     # VM network config
    ├── disable-defender.ps1  # Disable AV for testing
    └── README.md             # Lab setup guide
```

## References

- [CISA AA23-242A: QakBot Infrastructure](https://www.cisa.gov/news-events/cybersecurity-advisories/aa23-242a)
- [MITRE ATT&CK: QakBot](https://attack.mitre.org/software/S0650/)
- [pr0xylife QakBot IOC Repository](https://github.com/pr0xylife/Qakbot)
- [The DFIR Report: QakBot Case Studies](https://thedfirreport.com/)
