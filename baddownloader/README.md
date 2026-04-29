# BadDownloader — Generic Script-Kiddie Downloader Emulation

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

BadDownloader is an intentionally simple, "script kiddie" style downloader. Unlike [JawDropper](../jawdropper/) (QakBot) and [MuddyCalc](../muddycalc/) (MuddyWater), there is no sophistication here — no evasion, no encoded commands, no DLL proxy execution, no obfuscation.

**The simplicity is the point.** Even basic, commodity threats leave detectable traces in endpoint telemetry. If your detection pipeline can't see BadDownloader, it definitely can't see QakBot.

**What this emulates:**
- Custom downloader binary (cross-compiled C)
- PowerShell `Invoke-WebRequest` download cradle
- Batch file payload with discovery commands
- Scheduled task persistence
- Safe `calc.exe` final payload

**Safety mechanisms:**
- Final payload is `calc.exe` (hardcoded, not configurable)
- C2 server is `192.168.0.148:8888` (private IP, hardcoded)
- No obfuscation — all code is readable with extensive comments

## Attack Chain

```
BadDownloader.exe                                        ← Custom binary
  └── cmd.exe /c powershell.exe Invoke-WebRequest ...    ← Download .bat
        └── powershell.exe                               ← HTTP GET to C2
  └── cmd.exe /c %TEMP%\baddownload.bat                  ← Execute payload
        ├── whoami                                       ← Discovery
        ├── ipconfig /all                                ← Discovery
        ├── systeminfo                                   ← Discovery
        ├── net user                                     ← Discovery
        ├── schtasks /create /tn "BadDownloader" ...     ← Persistence
        └── calc.exe                                     ← Safe payload
```

## MITRE ATT&CK Mapping

| Technique ID | Name | Implementation |
|-------------|------|----------------|
| T1204.002 | User Execution: Malicious File | Operator executes BadDownloader.exe |
| T1059.001 | Command & Scripting: PowerShell | Invoke-WebRequest download cradle |
| T1059.003 | Command & Scripting: Windows Command Shell | cmd.exe execution of .bat payload |
| T1105 | Ingress Tool Transfer | HTTP download of baddownload.bat |
| T1033 | System Owner/User Discovery | whoami |
| T1016 | System Network Config Discovery | ipconfig /all |
| T1082 | System Information Discovery | systeminfo |
| T1087.001 | Account Discovery: Local Account | net user |
| T1053.005 | Scheduled Task/Job | schtasks /create persistence |

See [docs/mitre-mapping.md](docs/mitre-mapping.md) for detailed technique descriptions.

## Quick Start

### Prerequisites

- **Development machine:** macOS or Linux with:
  - `mingw-w64` cross-compiler (`brew install mingw-w64` on macOS)

- **Target machine:** Windows VM (isolated, snapshotted)
  - Network access to your development machine (192.168.0.148)

### Step 1: Build BadDownloader.exe

```bash
cd baddownloader/stage1-downloader
make
```

This produces `BadDownloader.exe` (64-bit Windows PE).

### Step 2: Host the .bat Payload

```bash
# Simple approach:
cd baddownloader/stage2-payload
python3 -m http.server 8888

# Or with request logging and status page:
python3 baddownloader/c2-server/server.py --port 8888
```

This serves `baddownload.bat` from your MacBook at `192.168.0.148:8888`. See [c2-server/README.md](c2-server/README.md) for the enhanced server's options.

### Step 3: Copy BadDownloader.exe to Windows VM

Transfer `stage1-downloader/BadDownloader.exe` to your Windows test VM.

### Step 4: Execute

1. Open your endpoint telemetry tool / EDR console
2. Run `BadDownloader.exe` on the Windows VM
3. Watch the process tree unfold in the console output
4. Observe `calc.exe` launch as the final "payload"
5. Check Esinta Endpoints for the full telemetry chain

### Step 5: Cleanup

On the Windows VM:
```powershell
# Remove the scheduled task
schtasks /delete /tn "BadDownloader" /f

# Delete the downloaded payload
Remove-Item "$env:TEMP\baddownload.bat" -ErrorAction SilentlyContinue
```

Or simply revert to your VM snapshot.

## What to Expect

### Console Output

BadDownloader prints status messages to stdout:
```
============================================================
  Esinta Emulation Framework - BadDownloader
  FOR AUTHORIZED SECURITY TESTING ONLY
============================================================

[*] TEMP directory: C:\Users\test\AppData\Local\Temp
[*] Downloading payload from http://192.168.0.148:8888/baddownload.bat
[*] Running: powershell.exe Invoke-WebRequest ...
[+] Download complete.

[*] Executing payload...
[*] BadDownloader payload executing...
[*] Running discovery commands...
...
[+] BadDownloader emulation complete.
```

### Telemetry Events

Your endpoint tool should capture approximately **10 process events**, including:
- `BadDownloader.exe` — rare binary with unknown hash
- `cmd.exe` → `powershell.exe` — download cradle
- `cmd.exe` running .bat from `%TEMP%`
- Discovery burst: `whoami`, `ipconfig`, `systeminfo`, `net user`
- `schtasks.exe` — persistence creation
- `calc.exe` — safe payload

See [docs/telemetry-expected.md](docs/telemetry-expected.md) for detailed telemetry expectations.

## Safety Mechanisms

### 1. Hardcoded Safe Payload
The .bat file always launches `calc.exe`. The scheduled task also runs `calc.exe`. Neither can be changed without editing source files.

### 2. Local-Only C2
The download URL `http://192.168.0.148:8888/baddownload.bat` uses a hardcoded private RFC1918 IP address. The binary will not reach out to any public infrastructure.

### 3. No Evasion, No Obfuscation
All code is plaintext with extensive comments. The PowerShell command is not encoded. The .bat file is a simple batch script. This is intentional — the emulation tests basic detection, not evasion bypass.

## Directory Structure

```
baddownloader/
├── README.md                 # This file
├── ATTRIBUTION.md            # Technique sources and references
│
├── stage1-downloader/        # Custom downloader binary
│   ├── downloader.c          # C source
│   ├── Makefile              # Cross-compile config
│   └── README.md             # Stage 1 details
│
├── stage2-payload/           # Batch file payload
│   ├── baddownload.bat       # Discovery + persistence + calc.exe
│   └── README.md             # Stage 2 details
│
├── c2-server/                # Custom HTTP server with request logging
│   ├── server.py             # Logs payload fetches, serves status page
│   └── README.md             # C2 server details
│
├── docs/                     # Documentation
│   ├── attack-chain.md       # Full attack chain walkthrough
│   ├── mitre-mapping.md      # MITRE ATT&CK mapping table
│   └── telemetry-expected.md # Expected telemetry signals
│
└── lab-setup/                # Lab environment configuration
    └── firewall-prep.ps1     # VM firewall configuration
```

## References

- [MITRE ATT&CK](https://attack.mitre.org/) — Adversarial Tactics, Techniques, and Common Knowledge
- [MITRE ATT&CK: PowerShell (T1059.001)](https://attack.mitre.org/techniques/T1059/001/)
- [MITRE ATT&CK: Scheduled Task (T1053.005)](https://attack.mitre.org/techniques/T1053/005/)
- [MITRE ATT&CK: Ingress Tool Transfer (T1105)](https://attack.mitre.org/techniques/T1105/)
