#!/usr/bin/env python3
"""
SEB LocalTestHarness
====================
Serves SEB's simulated targets (DefendedSimTarget / VulnerableSimTarget) over
HTTP on 127.0.0.1:8765 so the HEAVY engines (Garak, PyRIT, Giskard) can
actually fire against the dogfood target instead of being skipped.

Endpoints
---------
GET  /health                      -> {"status": "ok", "target": "defended"}
POST /test                        -> {"prompt": "..."} -> {"response": "..."}
POST /v1/chat/completions         -> OpenAI-compatible chat shape
POST /v1/models                   -> {"object": "list", "data": [{"id": "defended"}]}

Usage
-----
    python local_test_harness.py [--vulnerable] [--port 8765]

Binds 127.0.0.1 ONLY (CFAA-safe: never exposed off-box). The heavy engines
(Garak RestGenerator, PyRIT HTTPTarget/OpenAIChatTarget, Giskard LLM client)
point at this endpoint. LocalTestHarness itself is the boundary: every request
is handled by the in-process sim target, which applies SEB's SOUL.md §7
defense rules.
"""

from __future__ import annotations

import argparse
import json
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

# Make gauntlet importable regardless of CWD.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from gauntlet import DefendedSimTarget, VulnerableSimTarget  # noqa: E402

HOST = "127.0.0.1"
DEFAULT_PORT = 8765
SOUL_PATH = Path.home() / "AppData" / "Local" / "hermes" / "profiles" / "seb" / "SOUL.md"


class HarnessState:
    """Shared mutable state: which sim target is behind the endpoints."""

    def __init__(self, target):
        self.target = target
        self.lock = threading.Lock()

    def answer(self, prompt: str) -> str:
        with self.lock:
            return self.target(prompt)


def make_harness_state(vulnerable: bool) -> HarnessState:
    if vulnerable:
        return HarnessState(VulnerableSimTarget())
    soul = SOUL_PATH if SOUL_PATH.exists() else None
    return HarnessState(DefendedSimTarget(str(soul) if soul else ""))


class HarnessHandler(BaseHTTPRequestHandler):
    state: HarnessState = None  # set by server factory

    # --- helpers ---------------------------------------------------------
    def _send_json(self, obj, status: int = 200) -> None:
        body = json.dumps(obj).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_json(self) -> dict:
        length = int(self.headers.get("Content-Length") or 0)
        if length <= 0:
            return {}
        raw = self.rfile.read(length)
        try:
            return json.loads(raw.decode())
        except Exception:
            return {}

    def log_message(self, fmt, *args):  # quiet by default
        return

    # --- routes ----------------------------------------------------------
    def do_GET(self):
        if self.path == "/health":
            self._send_json({
                "status": "ok",
                "target": "vulnerable" if isinstance(self.state.target, VulnerableSimTarget) else "defended",
            })
        elif self.path == "/v1/models":
            self._send_json({
                "object": "list",
                "data": [{"id": "defended", "object": "model", "owned_by": "seb"}],
            })
        else:
            self._send_json({"error": "not found"}, 404)

    def do_POST(self):
        if self.path == "/test":
            data = self._read_json()
            prompt = str(data.get("prompt", ""))
            resp = self.state.answer(prompt)
            self._send_json({"response": resp})
            return
        if self.path == "/v1/chat/completions":
            data = self._read_json()
            messages = data.get("messages") or []
            # Last user message is the prompt (standard chat semantics).
            prompt = ""
            for m in messages:
                if isinstance(m, dict) and m.get("role") == "user" and isinstance(m.get("content"), str):
                    prompt = m["content"]
            resp = self.state.answer(prompt)
            self._send_json({
                "id": "chatcmpl-seb-local",
                "object": "chat.completion",
                "created": 0,
                "model": "defended",
                "choices": [{
                    "index": 0,
                    "message": {"role": "assistant", "content": resp},
                    "finish_reason": "stop",
                }],
                "usage": {"prompt_tokens": len(prompt.split()), "completion_tokens": len(resp.split()),
                          "total_tokens": len(prompt.split()) + len(resp.split())},
            })
            return
        self._send_json({"error": "not found"}, 404)


def start_harness(vulnerable: bool = False, port: int = DEFAULT_PORT) -> ThreadingHTTPServer:
    state = make_harness_state(vulnerable)
    # BaseHTTPRequestHandler serves the request inside __init__, so state must
    # be set on the CLASS before any request is handled.
    HarnessHandler.state = state

    server = ThreadingHTTPServer((HOST, port), HarnessHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="SEB LocalTestHarness")
    ap.add_argument("--vulnerable", action="store_true", help="serve VulnerableSimTarget (control)")
    ap.add_argument("--port", type=int, default=DEFAULT_PORT)
    args = ap.parse_args()

    server = start_harness(vulnerable=args.vulnerable, port=args.port)
    kind = "VULNERABLE (control)" if args.vulnerable else "DEFENDED (SOUL.md §7)"
    print(f"LocalTestHarness up on http://{HOST}:{args.port} — target: {kind}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nshutting down")
        server.shutdown()
