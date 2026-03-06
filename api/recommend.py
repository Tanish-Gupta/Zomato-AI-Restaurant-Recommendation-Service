# Vercel serverless: POST /api/recommend
import os
if os.environ.get("VERCEL"):
    os.environ.setdefault("HOME", "/tmp")
    os.environ.setdefault("HF_HOME", "/tmp")
    os.environ.setdefault("HF_DATASETS_CACHE", "/tmp/zomato-hf-cache")
import json
import sys
from pathlib import Path
_root = Path(__file__).resolve().parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))
from http.server import BaseHTTPRequestHandler


def read_body(handler_self):
    content_length = int(handler_self.headers.get("Content-Length", 0))
    if content_length == 0:
        return {}
    return json.loads(handler_self.rfile.read(content_length).decode())


def recommend(body):
    from src.phase3_api.recommendation import RecommendationService
    from src.phase3_api.schemas import RecommendationRequest
    svc = RecommendationService()
    svc._repo.initialize()
    req = RecommendationRequest(**body)
    resp = svc.get_recommendations(req)
    return resp.model_dump()


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            body = read_body(self)
            data = recommend(body)
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
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
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"detail": msg}).encode())

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def log_message(self, format, *args):
        pass
