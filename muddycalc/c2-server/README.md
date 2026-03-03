# MuddyCalc C2 Server

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

Local HTTP server that serves the macro-enabled spreadsheet and receives POWERSTATS beacon check-ins. Runs on the developer's MacBook at `192.168.0.148:8888`.

## Quick Start

### Simple (Python built-in server)

Serves files from `muddycalc/` directory — sufficient for spreadsheet delivery:

```bash
cd ~/Documents/Emulation/muddycalc
python3 -m http.server 8888
```

### Enhanced (Custom server with beacon logging)

Adds beacon logging for camera-friendly video recording:

```bash
python3 c2-server/server.py --port 8888
```

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | Status page showing recent beacons |
| GET | `/<file>` | Serve files from muddycalc/ directory |
| POST | `/beacon` | Receive POWERSTATS beacon check-in |

## Beacon Format

The POWERSTATS emulation sends a JSON POST to `/beacon`:

```json
{
    "hostname": "MALWARE-TEST-01",
    "username": "middl",
    "pid": 3284,
    "stage": "powerstats_complete",
    "discovery": {
        "whoami": "MALWARE-TEST-01\\middl",
        "ip": "192.168.0.XXX"
    }
}
```

Response is always:

```json
{"status": "ok", "command": "calc"}
```

## Console Output

The server produces camera-friendly log output:

```
[2026-03-01 14:22:15] SPREADSHEET SERVED → Q4_2025_ExpenseReport_FINAL_FINAL_v3_DO_NOT_DELETE.xlsm (89 KB)
[2026-03-01 14:22:31] BEACON from MALWARE-TEST-01 (PID: 3284, User: middl)
    ├── Discovery: whoami → MALWARE-TEST-01\middl
    ├── Discovery: ipconfig → 192.168.0.XXX
    └── Stage: powerstats_complete
```

## Command-Line Arguments

| Argument | Default | Description |
|----------|---------|-------------|
| `--port`, `-p` | 8888 | Port to listen on |
| `--serve-dir`, `-d` | `muddycalc/` | Directory to serve files from |
| `--bind`, `-b` | 0.0.0.0 | Address to bind to |

## Dependencies

None — uses Python 3 standard library only (`http.server`, `json`).

## MITRE Mapping

| Technique | ID | Role |
|-----------|----|------|
| Application Layer Protocol: Web | T1071.001 | Server receives HTTP POST beacons from POWERSTATS |
