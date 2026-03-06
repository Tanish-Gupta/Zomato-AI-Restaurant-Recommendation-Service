# Vercel serverless: GET /api/health
import os
if os.environ.get("VERCEL"):
    os.environ.setdefault("HOME", "/tmp")
    os.environ.setdefault("HF_HOME", "/tmp")
    os.environ.setdefault("HF_DATASETS_CACHE", "/tmp/zomato-hf-cache")
import json
from http.server import BaseHTTPRequestHandler


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps({"status": "ok", "service": "restaurant-recommendation"}).encode())

    def log_message(self, format, *args):
        pass
