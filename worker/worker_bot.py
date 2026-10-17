import os
import time
import json
import urllib.request
import datetime

API_BASE_URL = os.environ.get("API_BASE_URL", "http://dotnet-api:8080")
WORKER_NAME = os.environ.get("WORKER_NAME", "blogger-poster-node-01")
POLL_INTERVAL = int(os.environ.get("POLL_INTERVAL_SECONDS", "30"))

def run_worker():
    print("=" * 60, flush=True)
    print(f"🤖 Bot Worker Started: {WORKER_NAME}", flush=True)
    print(f"🔗 Connected to .NET API: {API_BASE_URL}", flush=True)
    print("=" * 60, flush=True)

    while True:
        try:
            req = urllib.request.Request(f"{API_BASE_URL}/api/stats", method="GET")
            with urllib.request.urlopen(req, timeout=10) as resp:
                stats = json.loads(resp.read().decode("utf-8"))
                now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(
                    f"[{now_str}] Heartbeat OK | Published: {stats.get('published_count')} | "
                    f"Pending Queue: {stats.get('pending_count')} | Active Keywords: {stats.get('active_keywords')}",
                    flush=True
                )
        except Exception as e:
            print(f"[!] Worker polling notice: {e}", flush=True)

        time.sleep(POLL_INTERVAL)

if __name__ == "__main__":
    run_worker()
