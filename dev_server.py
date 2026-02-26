#!/usr/bin/env python3
"""
VaultID Local Dev Server
Serves static files from public/ and proxies /api/extract to Groq.
Usage: python dev_server.py
"""

import os, json, urllib.request, urllib.error
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path

PORT = 3000
PUBLIC_DIR = Path(__file__).parent / "public"
GROQ_MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"
GROQ_URL   = "https://api.groq.com/openai/v1/chat/completions"

API_KEY = os.environ.get("GROQ_API_KEY", "")

if not API_KEY:
    print()
    print("=" * 54)
    print("   VaultID Dev Server")
    print("=" * 54)
    print()
    print("  Paste your Groq API key (for AI extraction):")
    API_KEY = input("  > ").strip()
    print()


class Handler(SimpleHTTPRequestHandler):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(PUBLIC_DIR), **kwargs)

    def do_POST(self):
        if self.path == "/api/extract":
            self._handle_extract()
        else:
            self.send_error(404, "Not found")

    def _handle_extract(self):
        if not API_KEY:
            self._json_resp(503, {"error": {"message": "No API key."}})
            return

        raw = self.rfile.read(int(self.headers.get("Content-Length", 0)))
        body = json.loads(raw)

        mime   = body.get("mimeType", "image/jpeg")
        data64 = body.get("data64", "")
        prompt = body.get("prompt", "Extract all fields from this identity document as JSON.")

        data_uri = f"data:{mime};base64,{data64}"

        payload = json.dumps({
            "model": GROQ_MODEL,
            "messages": [{"role": "user", "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": data_uri}}
            ]}],
            "temperature": 0,
            "max_completion_tokens": 1024,
            "response_format": {"type": "json_object"}
        }).encode("utf-8")

        req = urllib.request.Request(GROQ_URL, data=payload, method="POST", headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {API_KEY}",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })

        try:
            with urllib.request.urlopen(req, timeout=90) as r:
                resp = json.loads(r.read())

            text = resp["choices"][0]["message"]["content"].strip()
            if "```" in text:
                parts = text.split("```")
                text = parts[1]
                if text.startswith("json"): text = text[4:]
            text = text.strip()

            parsed = json.loads(text)
            self._json_resp(200, {"content": [{"type": "text", "text": json.dumps(parsed)}]})

        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8", errors="replace")
            try: msg = json.loads(err_body)["error"]["message"]
            except: msg = err_body[:400]
            print(f"\n  Groq HTTP {e.code}: {msg}\n")
            self._json_resp(e.code, {"error": {"message": f"Groq API: {msg}"}})

        except json.JSONDecodeError as e:
            self._json_resp(500, {"error": {"message": f"AI returned invalid JSON — {e}"}})

        except Exception as e:
            self._json_resp(500, {"error": {"message": str(e)}})

    def _json_resp(self, code, data):
        b = json.dumps(data).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", len(b))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(b)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
        super().end_headers()


if __name__ == "__main__":
    server = HTTPServer(("localhost", PORT), Handler)
    print(f"\n  [OK] VaultID running -> http://localhost:{PORT}")
    print(f"  Opening browser...")
    print(f"  Press Ctrl+C to stop.\n")

    import webbrowser, threading
    threading.Timer(0.8, lambda: webbrowser.open(f"http://localhost:{PORT}")).start()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n  Stopped.")
