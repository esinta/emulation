# BadDownloader — Stage 1: Downloader Binary

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

A minimal C binary that downloads and executes a .bat payload from the MacBook C2 server. This is intentionally unsophisticated — no evasion, no obfuscation.

## How It Works

1. Resolves `%TEMP%` directory via `GetEnvironmentVariableA`
2. Spawns `cmd.exe /c powershell.exe Invoke-WebRequest ...` to download `baddownload.bat`
3. Spawns `cmd.exe /c %TEMP%\baddownload.bat` to execute the payload

## Build

```bash
# Requires mingw-w64 cross-compiler
# macOS: brew install mingw-w64
make
```

Produces `BadDownloader.exe` (64-bit Windows PE).

## MITRE ATT&CK

| Technique | ID | Detail |
|-----------|-----|--------|
| PowerShell | T1059.001 | Invoke-WebRequest download cradle |
| Windows Command Shell | T1059.003 | cmd.exe execution chain |
| Ingress Tool Transfer | T1105 | HTTP download of .bat payload |
