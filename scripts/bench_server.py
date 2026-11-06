"""Local server for the RQ3 browser benchmark (bench/index.html): the museum models, the full models and the results.

    /                    bench/index.html and bench.js
    /museum/<path>       the museum folder (museum models in museum/models/)
    /full/<id>.glb       full L3 models from export_full_glb.py (outside the repo)
    /list                exhibit ids, from museum/artifacts.json
    POST /result?name=x  writes experiments/results/rq3/<x>.json

A GLB request with ?mbps=N is sent at N megabits per second, to time downloads at a fixed bandwidth without
hosting the site. Latency is not simulated.

Usage (PowerShell):
    python scripts/bench_server.py          # then open http://localhost:8766/
"""

import argparse
import json
import re
import sys
import time
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

REPO = Path(__file__).resolve().parents[1]
FULL = Path(r"D:\heritage3d-data\full_glb")
RESULTS = REPO / "experiments" / "results" / "rq3"
CHUNK = 64 * 1024


class Handler(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def _file(self, path, mbps):
        if not path.is_file():
            return self.send_error(404)
        data = path.read_bytes()
        self.send_response(200)
        types = {".html": "text/html", ".js": "text/javascript", ".json": "application/json", ".glb": "model/gltf-binary"}
        self.send_header("Content-Type", types.get(path.suffix, "application/octet-stream"))
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        start = time.perf_counter()
        for i in range(0, len(data), CHUNK):
            self.wfile.write(data[i:i + CHUNK])
            if mbps:
                ahead = (i + CHUNK) * 8 / (mbps * 1e6) - (time.perf_counter() - start)
                if ahead > 0:
                    time.sleep(ahead)

    def do_GET(self):
        url = urlparse(self.path)
        mbps = float(parse_qs(url.query).get("mbps", ["0"])[0])
        if url.path in ("/", "/index.html"):
            return self._file(REPO / "bench" / "index.html", 0)
        if url.path == "/bench.js":
            return self._file(REPO / "bench" / "bench.js", 0)
        if url.path == "/list":
            ids = [e["id"] for e in json.loads((REPO / "museum" / "artifacts.json").read_text(encoding="utf-8"))["artifacts"]]
            body = json.dumps([i for i in ids if (FULL / f"{i}.glb").exists()]).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            return self.wfile.write(body)
        m = re.fullmatch(r"/full/([\w.-]+\.glb)", url.path)
        if m:
            return self._file(FULL / m.group(1), mbps)
        m = re.fullmatch(r"/museum/([\w./-]+)", url.path)
        if m and ".." not in m.group(1):
            return self._file(REPO / "museum" / m.group(1), mbps)
        self.send_error(404)

    def do_POST(self):
        url = urlparse(self.path)
        name = parse_qs(url.query).get("name", [""])[0]
        if url.path != "/result" or not re.fullmatch(r"[\w-]+", name):
            return self.send_error(400)
        body = self.rfile.read(int(self.headers["Content-Length"]))
        RESULTS.mkdir(parents=True, exist_ok=True)
        (RESULTS / f"{name}.json").write_text(json.dumps(json.loads(body), indent=1), encoding="utf-8")
        self.send_response(204)
        self.end_headers()


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--port", type=int, default=8766)
    args = p.parse_args(argv)
    print(f"http://localhost:{args.port}/", flush=True)
    ThreadingHTTPServer(("127.0.0.1", args.port), Handler).serve_forever()


if __name__ == "__main__":
    sys.exit(main())
