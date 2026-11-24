#!/usr/bin/env python3
"""Render index.html to report.pdf with headless Chrome over a temporary server."""
import http.server
import socketserver
import subprocess
import threading
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PORT_HOLDER = []

CANDIDATES = [
    Path("C:/Program Files/Google/Chrome/Application/chrome.exe"),
    Path("C:/Program Files (x86)/Google/Chrome/Application/chrome.exe"),
    Path("C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe"),
    Path("C:/Program Files/Microsoft/Edge/Application/msedge.exe"),
]
CHROME = next((p for p in CANDIDATES if p.exists()), None)
if CHROME is None:
    raise SystemExit("Chrome or Edge not found")


class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


def serve():
    handler = lambda *a, **k: Quiet(*a, directory=str(ROOT), **k)
    with socketserver.TCPServer(("127.0.0.1", 0), handler) as httpd:
        PORT_HOLDER.append(httpd.server_address[1])
        httpd.serve_forever()


threading.Thread(target=serve, daemon=True).start()
for _ in range(100):
    if PORT_HOLDER:
        break
    time.sleep(0.05)
if not PORT_HOLDER:
    raise SystemExit("could not start the local server")
port = PORT_HOLDER[0]

out = ROOT / "report.pdf"
cmd = [
    str(CHROME),
    "--headless=new",
    "--disable-gpu",
    "--no-pdf-header-footer",
    "--virtual-time-budget=8000",
    f"--print-to-pdf={out}",
    f"http://127.0.0.1:{port}/index.html",
]
subprocess.run(cmd, check=True)
print(f"wrote {out} ({out.stat().st_size:,} bytes)")
