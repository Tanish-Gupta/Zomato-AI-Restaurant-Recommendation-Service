# Vercel serverless: GET /api/locations?cuisine=...
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
            self.send_response(500)
            self.wfile.write(json.dumps({"detail": str(e)}).encode())

    def log_message(self, format, *args):
        pass
