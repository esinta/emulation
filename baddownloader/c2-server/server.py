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

BadDownloader C2 Server

A simple HTTP server that:
1. Serves the baddownload.bat payload from the stage2-payload/ directory
2. Logs payload requests with timestamps
3. Provides a status page showing recent payload requests

Usage:
    python3 server.py --port 8888

For simple payload delivery, you can also just use:
    cd baddownloader/stage2-payload && python3 -m http.server 8888

This custom server adds request logging for video recording purposes.
"""

import argparse
import os
import sys
from datetime import datetime
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse

# Store recent payload requests for the status page
recent_requests = []
MAX_REQUESTS = 100

# The single payload file BadDownloader fetches
PAYLOAD_FILENAME = "baddownload.bat"


def timestamp():
    """Return formatted timestamp for logging."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def log(message):
    """Print timestamped log message."""
    print(f"[{timestamp()}] {message}")


class C2Handler(SimpleHTTPRequestHandler):
    """
    Custom HTTP handler for BadDownloader C2 server.

    Endpoints:
        GET  /                      - Status page with recent requests
        GET  /baddownload.bat       - Serve the .bat payload (logged)
        GET  /<other>               - Serve other files normally
    """

    def __init__(self, *args, serve_directory=None, **kwargs):
        self.serve_directory = serve_directory
        super().__init__(*args, **kwargs)

    def translate_path(self, path):
        """Override to serve from custom directory."""
        if self.serve_directory:
            parsed = urlparse(path)
            rel_path = parsed.path.lstrip('/')
            return os.path.join(self.serve_directory, rel_path)
        return super().translate_path(path)

    def do_GET(self):
        """Handle GET requests."""
        parsed = urlparse(self.path)
        path = parsed.path

        if path == '/':
            self.send_status_page()
            return

        filename = os.path.basename(path)

        if filename == PAYLOAD_FILENAME:
            log(f"PAYLOAD REQUEST → {filename} (from {self.client_address[0]})")

            super().do_GET()

            try:
                full_path = self.translate_path(path)
                if os.path.exists(full_path):
                    size_kb = os.path.getsize(full_path) / 1024
                    log(f"PAYLOAD DELIVERED → {filename} ({size_kb:.1f} KB)")

                    record = {
                        'timestamp': timestamp(),
                        'filename': filename,
                        'size_kb': f"{size_kb:.1f}",
                        'ip': self.client_address[0],
                    }
                    recent_requests.insert(0, record)
                    while len(recent_requests) > MAX_REQUESTS:
                        recent_requests.pop()
            except Exception:
                pass
        else:
            super().do_GET()

    def send_status_page(self):
        """Send HTML status page with recent payload requests."""
        html = """<!DOCTYPE html>
<html>
<head>
    <title>BadDownloader C2 - Status</title>
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
        .request-count {
            font-size: 48px;
            color: #e94560;
            margin: 20px 0;
        }
    </style>
    <meta http-equiv="refresh" content="5">
</head>
<body>
    <h1>BadDownloader C2 Server</h1>

    <div class="warning">
        <strong>ESINTA EMULATION — AUTHORIZED SECURITY TESTING ONLY</strong><br>
        This is a local C2 server for defensive security testing.
    </div>

    <div class="request-count">""" + str(len(recent_requests)) + """ payload requests served</div>

    <h2>Recent Payload Requests</h2>
    <table>
        <tr>
            <th>Timestamp</th>
            <th>Filename</th>
            <th>Size (KB)</th>
            <th>Source IP</th>
        </tr>
"""
        for record in recent_requests[:20]:
            html += f"""        <tr>
            <td>{record['timestamp']}</td>
            <td>{record['filename']}</td>
            <td>{record['size_kb']}</td>
            <td>{record['ip']}</td>
        </tr>
"""

        html += """    </table>

    <p style="margin-top: 20px; color: #666;">
        Auto-refreshes every 5 seconds.
        Payload endpoint: <code>/baddownload.bat</code>
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
        """Suppress default request logging for cleaner output."""
        pass


def main():
    parser = argparse.ArgumentParser(
        description='BadDownloader C2 Server - Esinta Emulation',
        epilog='For simple payload delivery: cd stage2-payload && python3 -m http.server 8888'
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
        help='Directory to serve files from (default: ../stage2-payload/)'
    )
    parser.add_argument(
        '--bind', '-b',
        type=str,
        default='0.0.0.0',
        help='Address to bind to (default: 0.0.0.0)'
    )

    args = parser.parse_args()

    if args.serve_dir:
        serve_dir = os.path.abspath(args.serve_dir)
    else:
        # Default: ../stage2-payload/ relative to this script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        serve_dir = os.path.abspath(os.path.join(script_dir, '..', 'stage2-payload'))

    if not os.path.isdir(serve_dir):
        print(f"Error: Serve directory does not exist: {serve_dir}")
        sys.exit(1)

    payload_path = os.path.join(serve_dir, PAYLOAD_FILENAME)
    if not os.path.exists(payload_path):
        print(f"Warning: Payload file not found at {payload_path}")
        print(f"  Expected: {PAYLOAD_FILENAME}")
        print(f"  The server will start anyway, but BadDownloader.exe will get a 404.")
        print()

    def handler(*args, **kwargs):
        return C2Handler(*args, serve_directory=serve_dir, **kwargs)

    server = HTTPServer((args.bind, args.port), handler)

    print("=" * 70)
    print("ESINTA EMULATION — AUTHORIZED SECURITY TESTING ONLY")
    print("=" * 70)
    print()
    print("BadDownloader C2 Server")
    print()
    print(f"  Listening:      http://{args.bind}:{args.port}")
    print(f"  Serving files:  {serve_dir}")
    print(f"  Status page:    http://localhost:{args.port}/")
    print(f"  Payload URL:    http://192.168.0.148:{args.port}/{PAYLOAD_FILENAME}")
    print()
    print("Waiting for connections... (Ctrl+C to stop)")
    print("-" * 70)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n" + "-" * 70)
        print(f"Shutting down. Total payload requests served: {len(recent_requests)}")
        server.shutdown()


if __name__ == '__main__':
    main()
