# Vercel serverless: GET /api/locations?cuisine=...
import os
if os.environ.get("VERCEL"):
    os.environ.setdefault("HOME", "/tmp")
    os.environ.setdefault("HF_HOME", "/tmp")
    os.environ.setdefault("HF_DATASETS_CACHE", "/tmp/zomato-hf-cache")
import json
import sys
from pathlib import Path
from urllib.parse import parse_qs, urlparse
_root = Path(__file__).resolve().parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))
from http.server import BaseHTTPRequestHandler


def get_locations_list(cuisine=None):
    from src.phase3_api.routes import get_recommendation_service
    return get_recommendation_service()._repo.get_unique_locations(cuisine=cuisine)


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        qs = parse_qs(parsed.query)
        cuisine = (qs.get("cuisine") or [None])[0]

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        try:
            data = get_locations_list(cuisine=cuisine)
            self.wfile.write(json.dumps(data).encode())
        except Exception as e:
            msg = str(e)
            if "disk space" in msg.lower() or "not enough" in msg.lower() or "errno 28" in msg.lower():
                self.send_response(503)
                self.send_header("Content-Type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(json.dumps({
                    "detail": "Dataset is too large for Vercel's serverless disk. Deploy the API to Railway or Render for full functionality (see README)."
                }).encode())
            else:
                self.send_response(500)
                self.wfile.write(json.dumps({"detail": msg}).encode())

    def log_message(self, format, *args):
        pass
