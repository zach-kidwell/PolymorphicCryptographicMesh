"""Tiny dependency-free local server for the Q-Mesh classroom demo."""
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
import os

HOST = "127.0.0.1"
PORT = 4173

if __name__ == "__main__":
    os.chdir(Path(__file__).parent)
    print(f"Q-Mesh Lab running at http://{HOST}:{PORT}")
    ThreadingHTTPServer((HOST, PORT), SimpleHTTPRequestHandler).serve_forever()
