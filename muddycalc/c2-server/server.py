#!/usr/bin/env python3
"""
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

MuddyCalc C2 Server

A simple HTTP server that:
1. Serves the macro-enabled spreadsheet (.xlsm) for download
2. Logs POWERSTATS beacon check-ins with discovery data
3. Provides a status page showing recent beacons

Usage:
    python3 server.py --port 8888

For simple file delivery, you can also just use:
    cd muddycalc && python3 -m http.server 8888

This custom server adds beacon logging for video recording purposes.
"""

import argparse
import json
import os
import sys
from datetime import datetime
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse

# Store recent beacons for status page
recent_beacons = []
MAX_BEACONS = 100


def timestamp():
    """Return formatted timestamp for logging."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def log(message):
    """Print timestamped log message."""
    print(f"[{timestamp()}] {message}")


class MuddyCalcHandler(SimpleHTTPRequestHandler):
    """
    Custom HTTP handler for MuddyCalc C2 server.

    Endpoints:
        GET  /              - Status page with recent beacons
        GET  /<file>        - Serve files (spreadsheet, etc.)
        POST /beacon        - Receive POWERSTATS beacon check-ins
    """

    def __init__(self, *args, serve_directory=None, **kwargs):
        self.serve_directory = serve_directory
        super().__init__(*args, **kwargs)

    def translate_path(self, path):
        """Override to serve from custom directory."""
        if self.serve_directory:
            parsed = urlparse(path)
            rel_path = parsed.path.lstrip("/")
            return os.path.join(self.serve_directory, rel_path)
        return super().translate_path(path)

    def do_GET(self):
        """Handle GET requests."""
        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/":
            # Status page
            self.send_status_page()
        else:
            # Serve files and log spreadsheet downloads
            filename = os.path.basename(path)
            if filename.endswith((".xlsm", ".xlsx")):
                try:
                    full_path = self.translate_path(path)
                    if os.path.exists(full_path):
                        size_kb = os.path.getsize(full_path) / 1024
                        log(
                            f"SPREADSHEET SERVED → {filename} ({size_kb:.0f} KB)"
                        )
                except Exception:
                    pass
            super().do_GET()

    def do_POST(self):
        """Handle POST requests (POWERSTATS beacon check-ins)."""
        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/beacon":
            self.handle_beacon()
        else:
            self.send_error(404, "Not Found")

    def handle_beacon(self):
        """Process POWERSTATS beacon check-in."""
        try:
            # Read request body
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length)

            # Parse JSON payload
            try:
                data = json.loads(body.decode("utf-8"))
            except json.JSONDecodeError:
                data = {"raw": body.decode("utf-8", errors="replace")}

            # Extract beacon info
            hostname = data.get("hostname", "UNKNOWN")
            username = data.get("username", "N/A")
            pid = data.get("pid", "N/A")
            stage = data.get("stage", "unknown")
            discovery = data.get("discovery", {})

            # Log the beacon (camera-friendly format)
            whoami_result = discovery.get("whoami", "N/A")
            ip_result = discovery.get("ip", "N/A")
            log(f"BEACON from {hostname} (PID: {pid}, User: {username})")
            print(f"    ├── Discovery: whoami → {whoami_result}")
            print(f"    ├── Discovery: ipconfig → {ip_result}")
            print(f"    └── Stage: {stage}")

            # Store for status page
            beacon_record = {
                "timestamp": timestamp(),
                "hostname": hostname,
                "username": username,
                "pid": pid,
                "stage": stage,
                "ip": self.client_address[0],
                "whoami": whoami_result,
                "discovery_ip": ip_result,
            }
            recent_beacons.insert(0, beacon_record)

            # Trim old beacons
            while len(recent_beacons) > MAX_BEACONS:
                recent_beacons.pop()

            # Send response — always safe payload
            response = json.dumps(
                {"status": "ok", "command": "calc"}  # Always safe payload
            )

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", len(response))
            self.end_headers()
            self.wfile.write(response.encode("utf-8"))

        except Exception as e:
            log(f"ERROR processing beacon: {e}")
            self.send_error(500, "Internal Server Error")

    def send_status_page(self):
        """Send HTML status page with recent beacons."""
        html = """<!DOCTYPE html>
<html>
<head>
    <title>MuddyCalc C2 - Status</title>
    <style>
        body {
            font-family: 'Courier New', monospace;
            background: #1a1a2e;
            color: #eee;
            margin: 40px;
        }
        h1 { color: #e94560; }
        .warning {
            background: #e94560;
            color: white;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
        }
        table {
            border-collapse: collapse;
            width: 100%;
            margin-top: 20px;
        }
        th, td {
            border: 1px solid #333;
            padding: 10px;
            text-align: left;
        }
        th { background: #16213e; }
        tr:nth-child(even) { background: #16213e; }
        .beacon-count {
            font-size: 48px;
            color: #e94560;
            margin: 20px 0;
        }
    </style>
    <meta http-equiv="refresh" content="5">
</head>
<body>
    <h1>MuddyCalc C2 Server</h1>

    <div class="warning">
        <strong>ESINTA EMULATION — AUTHORIZED SECURITY TESTING ONLY</strong><br>
        MuddyWater POWERSTATS emulation — local C2 server for defensive testing.
    </div>

    <div class="beacon-count">""" + str(len(recent_beacons)) + """ beacons received</div>

    <h2>Recent POWERSTATS Beacons</h2>
    <table>
        <tr>
            <th>Timestamp</th>
            <th>Hostname</th>
            <th>User</th>
            <th>PID</th>
            <th>Stage</th>
            <th>whoami</th>
            <th>IP</th>
        </tr>
"""
        for beacon in recent_beacons[:20]:  # Show last 20
            html += f"""        <tr>
            <td>{beacon['timestamp']}</td>
            <td>{beacon['hostname']}</td>
            <td>{beacon['username']}</td>
            <td>{beacon['pid']}</td>
            <td>{beacon['stage']}</td>
            <td>{beacon['whoami']}</td>
            <td>{beacon['discovery_ip']}</td>
        </tr>
"""

        html += """    </table>

    <p style="margin-top: 20px; color: #666;">
        Auto-refreshes every 5 seconds.
        Spreadsheet: <code>/Q4_2025_ExpenseReport_FINAL_FINAL_v3_DO_NOT_DELETE.xlsm</code>
    </p>
</body>
</html>"""

        response = html.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.send_header("Content-Length", len(response))
        self.end_headers()
        self.wfile.write(response)

    def log_message(self, format, *args):
        """Override to use our custom logging format."""
        # Suppress default logging for cleaner output
        pass


def main():
    parser = argparse.ArgumentParser(
        description="MuddyCalc C2 Server - Esinta Emulation",
        epilog="For simple file delivery: cd muddycalc && python3 -m http.server 8888",
    )
    parser.add_argument(
        "--port",
        "-p",
        type=int,
        default=8888,
        help="Port to listen on (default: 8888)",
    )
    parser.add_argument(
        "--serve-dir",
        "-d",
        type=str,
        default=None,
        help="Directory to serve files from (default: parent muddycalc/ directory)",
    )
    parser.add_argument(
        "--bind",
        "-b",
        type=str,
        default="0.0.0.0",
        help="Address to bind to (default: 0.0.0.0)",
    )

    args = parser.parse_args()

    # Determine serve directory
    if args.serve_dir:
        serve_dir = os.path.abspath(args.serve_dir)
    else:
        # Default: parent directory (muddycalc/) so spreadsheet is accessible
        serve_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    if not os.path.isdir(serve_dir):
        print(f"Error: Serve directory does not exist: {serve_dir}")
        sys.exit(1)

    # Create handler with serve directory
    def handler(*args_inner, **kwargs):
        return MuddyCalcHandler(
            *args_inner, serve_directory=serve_dir, **kwargs
        )

    # Start server
    server = HTTPServer((args.bind, args.port), handler)

    print("=" * 70)
    print("ESINTA EMULATION — AUTHORIZED SECURITY TESTING ONLY")
    print("=" * 70)
    print()
    print("MuddyCalc C2 Server — MuddyWater POWERSTATS Emulation")
    print()
    print(f"  Listening:      http://{args.bind}:{args.port}")
    print(f"  Serving files:  {serve_dir}")
    print(f"  Status page:    http://localhost:{args.port}/")
    print(
        f"  Spreadsheet:    http://192.168.0.148:{args.port}/"
        "Q4_2025_ExpenseReport_FINAL_FINAL_v3_DO_NOT_DELETE.xlsm"
    )
    print(f"  Beacon URL:     http://192.168.0.148:{args.port}/beacon")
    print()
    print("Waiting for connections... (Ctrl+C to stop)")
    print("-" * 70)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n" + "-" * 70)
        print(f"Shutting down. Total beacons received: {len(recent_beacons)}")
        server.shutdown()


if __name__ == "__main__":
    main()
