#!/usr/bin/env python3
"""
Wi‑Fi stress‑tester using iperf3.

Prerequisites:
  * iperf3 installed on both client (this script) and a server reachable on the LAN.
  * Run a server:   iperf3 -s

Usage:
  python wifi_test.py --server 192.168.1.10 --streams 200
"""

import argparse
import subprocess
import json
from typing import Dict


def run_iperf(server: str, port: int, streams: int, duration: int) -> Dict:
    cmd = ["iperf3", "-c", server, "-p", str(port), "-P", str(streams), "-t", str(duration), "-J"]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=duration+5)
    if result.returncode != 0:
        raise RuntimeError(f"iperf3 failed: {result.stderr}")
    return json.loads(result.stdout)


def main():
    parser = argparse.ArgumentParser(description="Wi‑Fi concurrent connection tester")
    parser.add_argument("--server", required=True, help="IP of the iperf3 server")
    parser.add_argument("--port", type=int, default=5201, help="iperf3 server port")
    parser.add_argument("--streams", type=int, default=50, help="number of concurrent streams")
    parser.add_argument("--duration", type=int, default=10, help="duration of test in seconds")
    parser.add_argument("--max-latency", type=float, default=200, help="latency threshold in ms")
    args = parser.parse_args()

    print(f"🏡 Testing Wi‑Fi to {args.server}:{args.port} with {args.streams} streams for {args.duration}s")
    results = run_iperf(args.server, args.port, args.streams, args.duration)
    summary = results.get("end", {}).get("sum_sent", {})
    latency = results.get("end", {}).get("sum_sent", {}).get("mean_latency_ms", 0.0)

    print("\n--- iperf3 Summary ---")
    print(f"  Total bandwidth: {summary.get('bits_per_second',0)/1e6:.2f} Mbps")
    print(f"  Avg latency: {latency:.1f} ms")

    if latency > args.max_latency:
        print(f"⚠️ Latency exceeded {args.max_latency} ms – Wi‑Fi may be saturated.")
    else:
        print("✅ Wi‑Fi seems healthy for the tested stream count.")

if __name__ == "__main__":
    main()
