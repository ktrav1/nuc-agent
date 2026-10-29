import os
import subprocess
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse


WEBAPPS_DIR = r"C:\intTech\WebApps"

class AgentHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_url = urlparse(self.path)
        path = parsed_url.path
        query = parse_qs(parsed_url.query)

        # Handle launch command
        if path == '/launch':
            filename = query.get('file', [None])[0]
            if filename:
                filepath = os.path.join(WEBAPPS_DIR, filename)
                if os.path.exists(filepath):
                    # Close any open Chrome instances cleanly
                    os.system('taskkill /f /im chrome.exe /fi "WINDOWTITLE eq *Chrome*"')
                    
                    # Launch Chrome maximized in app mode
                    cmd = f'start chrome --app="{filepath}" --start-maximized'
                    subprocess.Popen(cmd, shell=True)
                    
                    self._send_response(200, f'{{"status":"success","message":"Successfully launched {filename}"}}')
                    return
                else:
                    self._send_response(404, f'{{"status":"error","message":"File {filename} not found in {WEBAPPS_DIR}"}}')
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
        # Allow cross-origin access from your iPad dashboard
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json_message.encode('utf-8'))

    # Suppress default console output logging
    def log_message(self, format, *args):
        return

if __name__ == '__main__':
    # Listen on port 5222 across all local network interfaces
    server = HTTPServer(('0.0.0.0', 5222), AgentHandler)
    server.serve_forever()
