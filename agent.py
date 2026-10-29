import os
import subprocess
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse

WEBAPPS_DIR = r"C:\intTech\WebApps"

# Define a secret password token required for all commands
SECRET_TOKEN = "ClinTech123!"

class AgentHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_url = urlparse(self.path)
        path = parsed_url.path
        query = parse_qs(parsed_url.query)

        # 1. Authenticate with the password token
        client_token = query.get('token', [None])[0]
        if client_token != SECRET_TOKEN:
            self._send_response(401, '{"status":"error","message":"Unauthorized: Invalid or missing password token."}')
            return

        # Handle launch command
        if path == '/launch':
            raw_filename = query.get('file', [None])[0]
            if raw_filename:
                # 2. Sanitize filename to block path traversal (e.g. "../../" is stripped)
                filename = os.path.basename(raw_filename)
                
                # 3. Whitelist check: strictly allow only verified game files
                allowed_files = ["shark.html", "tensorFall.html"]
                if filename not in allowed_files:
                    self._send_response(400, '{"status":"error","message":"Blocked: Unauthorized file requested."}')
                    return

                filepath = os.path.join(WEBAPPS_DIR, filename)
                if os.path.exists(filepath):
                    # Safely close Chrome instances
                    os.system('taskkill /f /im chrome.exe /fi "WINDOWTITLE eq *Chrome*"')
                    
                    # Launch Chrome maximized in app mode
                    cmd = f'start chrome --app="{filepath}" --start-maximized'
                    subprocess.Popen(cmd, shell=True)
                    
                    self._send_response(200, f'{{"status":"success","message":"Successfully launched {filename}"}}')
                    return
                else:
                    self._send_response(404, f'{{"status":"error","message":"File {filename} not found in WebApps"}}')
                    return

        # Handle close command
        elif path == '/close':
            os.system('taskkill /f /im chrome.exe')
            self._send_response(200, '{"status":"success","message":"Closed web app successfully."}')
            return

        self._send_response(404, '{"status":"error","message":"Endpoint not found"}')

    def _send_response(self, code, json_message):
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json_message.encode('utf-8'))

    def log_message(self, format, *args):
        return

if __name__ == '__main__':
    server = HTTPServer(('0.0.0.0', 5222), AgentHandler)
    server.serve_forever()
