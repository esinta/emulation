# JawDropper Attack Chain

```
============================================================================
ESINTA EMULATION — AUTHORIZED SECURITY TESTING ONLY

This document describes the full attack chain for educational purposes.
All techniques are documented in CISA AA23-242A and MITRE ATT&CK.
============================================================================
```

## Overview

JawDropper emulates a QakBot infection chain from initial access through post-exploitation. This document provides a detailed walkthrough of each stage, the techniques employed, and what security tools should detect.

## Attack Chain Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       JAWDROPPER ATTACK CHAIN                               │
│                    QakBot BB27/BB28 TTP Emulation                           │
└─────────────────────────────────────────────────────────────────────────────┘

INITIAL ACCESS
══════════════════════════════════════════════════════════════════════════════

    Attacker                                    Victim
       │                                          │
       │  Email with ZIP containing dropper.js   │
       │ ───────────────────────────────────────► │
       │                                          │
       │                                    ┌─────┴─────┐
       │                                    │   User    │
       │                                    │ extracts  │
       │                                    │   ZIP     │
       │                                    └─────┬─────┘
       │                                          │
       │                                          │ Double-clicks dropper.js
       │                                          │
       │                                          ▼
       │                                    ┌───────────┐
       │                                    │ wscript.  │ T1204.002 User Execution
       │                                    │   exe     │ T1059.007 JavaScript
       │                                    └─────┬─────┘
       │                                          │

EXECUTION
══════════════════════════════════════════════════════════════════════════════

       │                                          │
       │                                          │ shell.Run(powershell...)
       │                                          │
       │                                          ▼
       │                                    ┌───────────┐
       │                                    │powershell │ T1059.001 PowerShell
       │                                    │   .exe    │ -encodedcommand
       │                                    └─────┬─────┘
       │                                          │
       │                                          │ Invoke-WebRequest
       │   ◄──────────────────────────────────────│
       │        GET /payloads/payload.dll         │ T1105 Ingress Tool Transfer
       │   ──────────────────────────────────────►│
       │        [DLL payload]                     │
       │                                          │
       │                                          │ Start-Process regsvr32.exe
       │                                          │
       │                                          ▼
       │                                    ┌───────────┐
       │                                    │ regsvr32  │ T1218.010 Signed Binary
       │                                    │   .exe    │ Proxy Execution
       │                                    └─────┬─────┘
       │                                          │

DLL EXECUTION (Stage 2)
══════════════════════════════════════════════════════════════════════════════

       │                                          │
       │                                          │ DllRegisterServer()
       │                                          │
       │                                          ▼
       │                                    ┌───────────┐
       │                                    │  Sleep()  │ T1497.003 Time-Based
       │                                    │  2000ms   │ Evasion
       │                                    └─────┬─────┘
       │                                          │

DISCOVERY
══════════════════════════════════════════════════════════════════════════════

       │                                          │
       │                                          ├──► cmd.exe /c whoami
       │                                          │    T1033 System Owner Discovery
       │                                          │
       │                                          ├──► cmd.exe /c ipconfig /all
       │                                          │    T1016 Network Config Discovery
       │                                          │
       │                                          ├──► cmd.exe /c net view
       │                                          │    T1018 Remote System Discovery
       │                                          │
       │                                          ├──► cmd.exe /c arp -a
       │                                          │    T1016 Network Config Discovery
       │                                          │
       │                                          ├──► cmd.exe /c nslookup ...
       │                                          │    T1018 Remote System Discovery
       │                                          │
       │                                          └──► cmd.exe /c nltest ...
       │                                               T1482 Domain Trust Discovery

PERSISTENCE
══════════════════════════════════════════════════════════════════════════════

       │                                          │
       │                                          │ schtasks /create
       │                                          │ Task: "JawDropper"
       │                                          │ Action: calc.exe (SAFE)
       │                                          │
       │                                          │ T1053.005 Scheduled Task
       │                                          │

COMMAND & CONTROL
══════════════════════════════════════════════════════════════════════════════

       │                                          │
       │   ◄──────────────────────────────────────│
       │        POST /beacon                      │ T1071.001 Web Protocols
       │        {hostname, pid, stage}            │
       │   ──────────────────────────────────────►│
       │        {status: ok}                      │
       │                                          │

PAYLOAD EXECUTION
══════════════════════════════════════════════════════════════════════════════

       │                                          │
       │                                          │ CreateProcess("calc.exe")
       │                                          │
       │                                          ▼
       │                                    ┌───────────┐
       │                                    │ calc.exe  │ SAFE PAYLOAD
       │                                    │ (benign)  │ Emulation complete
       │                                    └───────────┘
```

## Stage-by-Stage Breakdown

### Stage 0: Initial Access (Emulated)

**What happens in real QakBot:**
- Phishing email with ZIP attachment
- ZIP contains malicious .js, .lnk, or Office document
- User extracts and executes the file

**What JawDropper does:**
- Provides `dropper.js` for manual execution
- User manually copies file to test VM and double-clicks
- No actual phishing — this is the "emulated" part

**Detection opportunity:**
- Email gateway scanning for JavaScript in ZIPs
- User awareness training

### Stage 1: JavaScript Execution

**Process:** `wscript.exe dropper.js`

**MITRE Techniques:**
- T1204.002 — User Execution: Malicious File
- T1059.007 — Command & Scripting Interpreter: JavaScript

**What happens:**
1. User double-clicks `dropper.js`
2. Windows associates `.js` with `wscript.exe`
3. WScript Host executes the JavaScript
4. Script uses `WScript.Shell` to spawn PowerShell

**Detection opportunities:**
- Process creation: wscript.exe with .js argument
- Script block logging (if enabled)
- AMSI scanning of JavaScript content

### Stage 2: PowerShell Download Cradle

**Process:** `powershell.exe -WindowStyle Hidden -ep Bypass -encodedcommand <base64>`

**MITRE Techniques:**
- T1059.001 — Command & Scripting Interpreter: PowerShell
- T1105 — Ingress Tool Transfer

**What happens:**
1. PowerShell runs hidden (no visible window)
2. Base64-encoded command is decoded and executed
3. `Invoke-WebRequest` downloads DLL from C2 server
4. DLL saved to `%TEMP%\update.dll`
5. `Start-Process` launches regsvr32.exe

**Detection opportunities:**
- Process creation: powershell.exe with `-encodedcommand`
- PowerShell script block logging
- Network connection to unusual IP/port
- File write to TEMP directory

### Stage 3: Signed Binary Proxy Execution

**Process:** `regsvr32.exe /s C:\Users\...\AppData\Local\Temp\update.dll`

**MITRE Techniques:**
- T1218.010 — Signed Binary Proxy Execution: Regsvr32

**What happens:**
1. regsvr32.exe loads the DLL
2. Windows calls `DllRegisterServer` export
3. All subsequent behavior executes within this function

**Detection opportunities:**
- Process creation: regsvr32.exe loading DLL from TEMP
- Module load events for unknown DLLs
- regsvr32 without typical registration activity

### Stage 4: Anti-Analysis Delay

**MITRE Techniques:**
- T1497.003 — Virtualization/Sandbox Evasion: Time-Based

**What happens:**
1. `Sleep(2000)` — 2 second delay
2. Creates gap in timeline before suspicious activity

**Detection opportunities:**
- Behavioral analysis noting delay before activity
- (Real QakBot has more sophisticated timing checks)

### Stage 5: Discovery Burst

**MITRE Techniques:**
- T1033 — System Owner/User Discovery
- T1016 — System Network Configuration Discovery
- T1018 — Remote System Discovery
- T1482 — Domain Trust Discovery

**Commands executed:**
```
cmd.exe /c whoami
cmd.exe /c ipconfig /all
cmd.exe /c net view
cmd.exe /c arp -a
cmd.exe /c nslookup -querytype=ALL -timeout=12 _ldap._tcp.dc._msdcs.%USERDNSDOMAIN%
cmd.exe /c nltest /domain_trusts /all_trusts
```

**Detection opportunities:**
- Multiple cmd.exe processes spawned rapidly
- Command-line logging of discovery commands
- Process tree: regsvr32 → multiple cmd.exe
- Behavioral rule: discovery command burst

### Stage 6: Persistence

**MITRE Techniques:**
- T1053.005 — Scheduled Task/Job: Scheduled Task

**Command executed:**
```
schtasks /create /tn "JawDropper" /tr "calc.exe" /sc daily /st 09:00 /f
```

**Detection opportunities:**
- Process creation: schtasks.exe with /create
- Scheduled task created event (Event ID 4698)
- Task triggers executable from unusual path

**Safety note:** The task runs `calc.exe`, not the DLL.

### Stage 7: C2 Beacon

**MITRE Techniques:**
- T1071.001 — Application Layer Protocol: Web Protocols

**What happens:**
1. HTTP POST to `http://192.168.0.148:8888/beacon`
2. JSON body: `{"hostname": "...", "pid": ..., "stage": "loader_complete"}`
3. Response: `{"status": "ok", "command": "calc"}`

**Detection opportunities:**
- Network connection to internal IP on unusual port
- HTTP POST with JSON body to /beacon endpoint
- WinHTTP usage from regsvr32.exe

### Stage 8: Payload Execution

**What happens:**
1. `CreateProcess("calc.exe")`
2. Calculator launches visibly
3. Emulation complete

**Detection opportunities:**
- Process creation: calc.exe spawned by regsvr32.exe
- Unusual parent-child relationship

**Safety note:** The payload is ALWAYS `calc.exe`. This is hardcoded.

## Complete Process Tree

```
wscript.exe dropper.js
  └── powershell.exe -WindowStyle Hidden -ep Bypass -encodedcommand <base64>
        └── regsvr32.exe /s C:\Users\<user>\AppData\Local\Temp\update.dll
              ├── cmd.exe /c whoami
              ├── cmd.exe /c ipconfig /all
              ├── cmd.exe /c net view
              ├── cmd.exe /c arp -a
              ├── cmd.exe /c nslookup -querytype=ALL -timeout=12 _ldap._tcp.dc._msdcs.%USERDNSDOMAIN%
              ├── cmd.exe /c nltest /domain_trusts /all_trusts
              ├── cmd.exe /c schtasks /create /tn "JawDropper" /tr "calc.exe" /sc daily /st 09:00 /f
              └── calc.exe
```

## Timeline

Approximate timeline from execution:

| Time | Event |
|------|-------|
| T+0s | User double-clicks dropper.js |
| T+0s | wscript.exe starts |
| T+0.1s | powershell.exe spawns (hidden) |
| T+0.5s | Network connection to C2 |
| T+1-2s | DLL download completes |
| T+2s | regsvr32.exe loads DLL |
| T+4s | Sleep(2000) completes |
| T+4.5s | whoami executes |
| T+5s | ipconfig /all executes |
| T+5.5s | net view executes |
| T+6s | arp -a executes |
| T+6.5s | nslookup executes |
| T+7s | nltest executes |
| T+7.5s | schtasks creates persistence |
| T+8s | Beacon sent to C2 |
| T+8.5s | calc.exe launches |
