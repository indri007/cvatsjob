"""
Lightweight health-check HTTP server, run in a background thread alongside
Streamlit.
"""

import json
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from logger import get_logger

logger = get_logger("health_server")

class HealthHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

    def do_GET(self):
        if self.path == "/health":
            self._respond(200, {"status": "ok"})
        elif self.path == "/health/deep":
            try:
                import health_check
                result = health_check.run_all_checks()
                code = 200 if result.get("status") == "ok" else 503
                self._respond(code, result)
            except Exception as e:
                self._respond(503, {"status": "error", "message": str(e)})
        else:
            self._respond(404, {"status": "not_found"})

    def _respond(self, code: int, payload: dict):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

_health_server_thread = None
_health_server_lock = threading.Lock()

def start_health_server(port: int = 8081):
    global _health_server_thread
    with _health_server_lock:
        if _health_server_thread is not None and _health_server_thread.is_alive():
            return _health_server_thread

        def _serve():
            try:
                # Inisialisasi tanpa otomatis binding
                server = HTTPServer(("0.0.0.0", port), HealthHandler, bind_and_activate=False)
                server.allow_reuse_address = True  # <-- INI KUNCI PENYELAMATNYA!
                server.server_bind()
                server.server_activate()
                logger.info("Health server started successfully", extra={"port": port})
                server.serve_forever()
            except OSError as e:
                if e.errno == 98:
                    logger.warning("Port 8081 already in use, skipping creation.", extra={"port": port})
                else:
                    raise e

        _health_server_thread = threading.Thread(target=_serve, daemon=True)
        _health_server_thread.start()
        return _health_server_thread
