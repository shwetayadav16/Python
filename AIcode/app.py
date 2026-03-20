from __future__ import annotations

import json
import mimetypes
import random
from datetime import datetime, timedelta
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent


def generate_dashboard_payload() -> dict:
    now = datetime.now()
    labels = [(now - timedelta(days=offset)).strftime("%d %b") for offset in range(6, -1, -1)]
    revenue = [random.randint(18, 42) * 1000 for _ in labels]
    orders = [random.randint(90, 180) for _ in labels]
    satisfaction = [round(random.uniform(4.1, 4.9), 1) for _ in labels]

    current_revenue = revenue[-1]
    previous_revenue = revenue[-2]
    revenue_delta = round(((current_revenue - previous_revenue) / previous_revenue) * 100, 1)

    return {
        "generatedAt": now.strftime("%d %b %Y, %I:%M:%S %p"),
        "stats": [
            {
                "label": "Revenue",
                "value": f"${current_revenue:,}",
                "delta": f"{revenue_delta:+}%",
                "tone": "up" if revenue_delta >= 0 else "down",
            },
            {
                "label": "Orders",
                "value": f"{orders[-1]}",
                "delta": f"{orders[-1] - orders[-2]:+} today",
                "tone": "up" if orders[-1] >= orders[-2] else "down",
            },
            {
                "label": "Satisfaction",
                "value": f"{satisfaction[-1]:.1f}/5",
                "delta": f"{satisfaction[-1] - satisfaction[-2]:+0.1f} points",
                "tone": "up" if satisfaction[-1] >= satisfaction[-2] else "down",
            },
            {
                "label": "Active Users",
                "value": f"{random.randint(380, 540)}",
                "delta": f"{random.randint(12, 38)} new sessions",
                "tone": "neutral",
            },
        ],
        "chart": {
            "labels": labels,
            "revenue": revenue,
            "orders": orders,
        },
        "activities": [
            {
                "title": "Campaign launch",
                "detail": "Spring promo went live across email and social.",
                "time": "10 min ago",
                "status": "Live",
            },
            {
                "title": "Ops alert resolved",
                "detail": "Checkout latency returned to normal thresholds.",
                "time": "32 min ago",
                "status": "Closed",
            },
            {
                "title": "Support queue",
                "detail": f"{random.randint(8, 16)} high-priority tickets waiting for review.",
                "time": "1 hour ago",
                "status": "Watch",
            },
        ],
        "segments": [
            {"name": "Direct", "value": random.randint(32, 42)},
            {"name": "Referral", "value": random.randint(18, 26)},
            {"name": "Organic", "value": random.randint(20, 28)},
            {"name": "Paid", "value": random.randint(12, 20)},
        ],
    }


class DashboardHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path in {"/", "/index.html"}:
            self.serve_file(BASE_DIR / "templates" / "index.html", "text/html; charset=utf-8")
            return

        if self.path == "/api/dashboard":
            payload = json.dumps(generate_dashboard_payload()).encode("utf-8")
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
            return

        if self.path.startswith("/static/"):
            relative_path = self.path.removeprefix("/static/")
            file_path = BASE_DIR / "static" / relative_path
            self.serve_file(file_path)
            return

        self.send_error(HTTPStatus.NOT_FOUND, "Not Found")

    def serve_file(self, file_path: Path, content_type: str | None = None):
        if not file_path.exists() or not file_path.is_file():
            self.send_error(HTTPStatus.NOT_FOUND, "File not found")
            return

        data = file_path.read_bytes()
        resolved_type = content_type or mimetypes.guess_type(str(file_path))[0] or "application/octet-stream"
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", resolved_type)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


def run_server():
    server = ThreadingHTTPServer(("127.0.0.1", 5000), DashboardHandler)
    print("Dashboard running at http://127.0.0.1:5000")
    print("Open that address in your browser. Press Ctrl+C in the terminal to stop the server.")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
    finally:
        server.server_close()


if __name__ == "__main__":
    run_server()
