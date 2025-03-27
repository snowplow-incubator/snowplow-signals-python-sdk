from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import os
from urllib.parse import urlparse, parse_qs
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Disable default HTTP server logging
logging.getLogger("http.server").setLevel(logging.WARNING)


# Load the JSON data from external file
def load_signals_config():

    filename = "static_signals_config_offline.json"
    config_path = os.path.join(os.path.dirname(__file__), filename)

    try:
        with open(config_path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        logger.warning(f"Could not find {config_path}")
        return []
    except json.JSONDecodeError:
        logger.warning(f"Invalid JSON in {config_path}")
        return []


# Load configuration at startup
OFFLINE_SIGNALS_CONFIG = load_signals_config()


class RequestHandler(BaseHTTPRequestHandler):
    # Suppress default logging
    def log_message(self, format, *args):
        pass

    def do_POST(self):
        if self.path != "/api/v1/push":
            self.send_response(404)
            self.end_headers()
            return

        content_length = int(self.headers["Content-Length"])
        post_data = self.rfile.read(content_length)
        data = post_data.decode("utf-8")

        # parse the data to json
        data = json.loads(data)
        # Log the data in a controlled way
        logger.info(f"Received POST data: {json.dumps(data)}")

        self.send_response(200)
        self.end_headers()

    def do_GET(self):
        if not self.path.startswith("/api/v1/registry/views"):
            self.send_response(404)
            self.end_headers()
            return

        # Parse query parameters
        parsed_url = urlparse(self.path)
        query_params = parse_qs(parsed_url.query)

        # Log request info for debugging
        logger.info(f"Received GET request: {self.path}")
        logger.info(f"Query parameters: {query_params}")
        
        # Check for source_type=offline parameter
        if "source_type" in query_params and query_params["source_type"][0] == "offline":
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(OFFLINE_SIGNALS_CONFIG).encode("utf-8"))
            logger.info("Returned offline signals config")
        else:
            logger.warning(f"Invalid or missing source_type parameter: {query_params.get('source_type')}")
            self.send_response(404)
            self.end_headers()


# Default server configuration
DEFAULT_PORT = 8087
SERVER_ADDRESS = ""


def run(server_class=HTTPServer, handler_class=RequestHandler, port=DEFAULT_PORT):
    server_address = (SERVER_ADDRESS, port)
    httpd = server_class(server_address, handler_class)
    logger.info(f"Starting server on port {port}")
    httpd.serve_forever()


if __name__ == "__main__":
    run()
