"""
Concurrent HTTP connection stress‑tester that also monitors system load.

Features
--------
  • Spawns a thread per virtual user.
  • Each user sends 3 quick probes + a heavy submit in a loop.
  • Stops when latency > MAX_LATENCY or when MAX_ERRORS are hit.
  • Live CPU & RAM usage is printed every second.
"""

import argparse
import random
import time
import threading
from typing import List

import psutil
import requests

# --------------------------------------------------------------------------- #
# DEFAULT SETTINGS – can be overridden via CLI
# --------------------------------------------------------------------------- #
SERVER_URL = "http://127.0.0.1:5000"
RAMP_UP_INTERVAL = 2           # seconds between new users
MAX_LATENCY_SEC = 5.0
MAX_ERRORS = 3
PROBE_COUNT = 3
PROBE_SLEEP_RANGE = (1, 3)
SUBMIT_SLEEP_RANGE = (5, 10)
CODE = "def solve(n): return n"

# --------------------------------------------------------------------------- #
# GLOBAL METRICS (guarded by a lock)
# --------------------------------------------------------------------------- #
lock = threading.Lock()
active_users = 0
running = True
error_count = 0
latency_history: List[float] = []

# --------------------------------------------------------------------------- #
# USER BOT
# --------------------------------------------------------------------------- #
def student_bot(user_id: int) -> None:
    global running, error_count
    session = requests.Session()
    name = f"LoadTester_{user_id}"

    try:
        reg = session.post(f"{SERVER_URL}/register", json={"username": name})
        reg.raise_for_status()
        uid = reg.json()["id"]
    except Exception as exc:
        with lock:
            error_count += 1
        print(f"💀 User {user_id} register failed: {exc}")
        return

    while running:
        # 1. fast probes
        for _ in range(PROBE_COUNT):
            if not running:
                break
            try:
                session.post(
                    f"{SERVER_URL}/probe",
                    json={"user_id": uid, "question_id": 1, "input": str(random.randint(1, 100))},
                    timeout=2,
                )
            except Exception:
                pass
            time.sleep(random.uniform(*PROBE_SLEEP_RANGE))

        # 2. heavy submit
        if not running:
            break
        start = time.time()
        try:
            res = session.post(
                f"{SERVER_URL}/submit",
                json={
                    "user_id": uid,
                    "question_id": 1,
                    "code": CODE,
                    "language": "python",
                },
                timeout=20,
            )
        except requests.RequestException as exc:
            with lock:
                error_count += 1
            print(f"❌ User {user_id} submit exception: {exc}")
            if error_count >= MAX_ERRORS:
                running = False
            continue

        duration = time.time() - start

        if res.status_code == 200:
            with lock:
                latency_history.append(duration)
            if duration > MAX_LATENCY_SEC:
                print(f"⚠️ High latency ({duration:.2f}s) – stopping.")
                running = False
        else:
            with lock:
                error_count += 1
            print(f"❌ User {user_id} submit error {res.status_code}")
            if error_count >= MAX_ERRORS:
                print("⚠️ Too many errors – stopping.")
                running = False

        time.sleep(random.uniform(*SUBMIT_SLEEP_RANGE))

# --------------------------------------------------------------------------- #
# CPU & RAM monitor
# --------------------------------------------------------------------------- #
def monitor_system(interval=1):
    while running:
        cpu = psutil.cpu_percent()
        mem = psutil.virtual_memory().percent
        with lock:
            print(f"[CPU:{cpu:3d}%  MEM:{mem:3d}%  USERS:{active_users:3d} ERR:{error_count:2d}]", end="\r")
        time.sleep(interval)

# --------------------------------------------------------------------------- #
# MAIN CONTROLLER
# --------------------------------------------------------------------------- #
def main() -> None:
    global active_users, running, SERVER_URL, RAMP_UP_INTERVAL, MAX_LATENCY_SEC, MAX_ERRORS

    parser = argparse.ArgumentParser(description="Concurrent HTTP connection tester")
    parser.add_argument("--url", default=SERVER_URL, help="Base URL of the target webapp")
    parser.add_argument("--ramp", type=float, default=RAMP_UP_INTERVAL,
                        help="seconds between new users")
    parser.add_argument("--latency", type=float, default=MAX_LATENCY_SEC,
                        help="max acceptable submit time (s)")
    parser.add_argument("--max-errors", type=int, default=MAX_ERRORS,
                        help="error threshold")
    parser.add_argument("--duration", type=int, default=0,
                        help="Optional total test duration (seconds)")
    args = parser.parse_args()

    # override defaults
    SERVER_URL = args.url
    RAMP_UP_INTERVAL = args.ramp
    MAX_LATENCY_SEC = args.latency
    MAX_ERRORS = args.max_errors

    # start resource monitor
    monitor_thr = threading.Thread(target=monitor_system, daemon=True)
    monitor_thr.start()

    threads: List[threading.Thread] = []
    try:
        while running and error_count < MAX_ERRORS:
            active_users += 1
            t = threading.Thread(target=student_bot, args=(active_users,), daemon=True)
            threads.append(t)
            t.start()
            time.sleep(RAMP_UP_INTERVAL)

            if args.duration and time.time() - start_time >= args.duration:
                break
    except KeyboardInterrupt:
        print("\n🛑 Stopping test (Ctrl+C)")
    finally:
        running = False
        for t in threads:
            t.join(timeout=1)

        print("\n" + "=" * 60)
        print("📊 MACHINE LIMIT FINDER")
        print(f"✅ Max stable users: {active_users-1}")
        if latency_history:
            avg = sum(latency_history) / len(latency_history)
            print(f"⏱️ Avg submit time: {avg:.2f}s")
        print(f"❌ Total errors: {error_count}")
        print("=" * 60)

if __name__ == "__main__":
    start_time = time.time()
    main()