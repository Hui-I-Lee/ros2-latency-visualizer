#!/usr/bin/env python3
"""
ROS 2 Latency Metrics Generator for Prometheus Pushgateway.

This tool generates synthetic latency metrics between ROS 2 nodes and pushes them
to a Prometheus Pushgateway. It is designed for testing and demonstrating the
ROS 2 Latency Visualizer pipeline without requiring access to a real ROS 2 deployment.

The generated metrics follow the pattern:
fake_latency_seconds{source="node-a",target="node-b",direction="fwd"} 0.123

Usage:
    python ros2_latency_injector.py --gateway http://localhost:9091 --interval 10
"""

import random
import time
import requests
import argparse

# Default Configuration
DEFAULT_PUSHGATEWAY_URL = 'http://localhost:9091/metrics/job/fake_latency_test/instance/manual'
DEFAULT_NODES = ['node-a', 'node-b', 'node-c', 'node-d']
DEFAULT_INTERVAL_SECONDS = 10
CUSTOM_LATENCY_DATA = None

def generate_latency_metrics_from_nodes(node_list):
    """Generate latency metrics between all pairs of nodes."""
    lines = []
    for i in range(len(node_list)):
        for j in range(len(node_list)):
            if i == j:
                continue
            src = node_list[i]
            dst = node_list[j]
            latency = round(random.uniform(0.05, 1.0), 3)
            lines.append(f'fake_latency_seconds{{source="{src}",target="{dst}",direction="fwd"}} {latency}')
    return '\n'.join(lines)

def generate_latency_metrics_from_custom(data):
    """Generate latency metrics from custom data."""
    lines = []
    for src, dst, latency in data:
        lines.append(f'fake_latency_seconds{{source="{src}",target="{dst}",direction="fwd"}} {latency}')
    return '\n'.join(lines)

def push_to_gateway(payload: str, gateway_url: str):
    """Push metrics to Prometheus Pushgateway."""
    try:
        headers = {'Content-Type': 'text/plain'}
        res = requests.put(gateway_url, data=payload.encode('utf-8'), headers=headers, timeout=5)
        if res.status_code == 200:
            print(f'[✓] Successfully pushed {len(payload.splitlines())} metrics')
        else:
            print(f'[!] Pushgateway returned error: {res.status_code} {res.text}')
    except requests.exceptions.ConnectionError:
        print('[!] Could not connect to Pushgateway. Is it running?')
    except requests.exceptions.Timeout:
        print('[!] Request timeout. Pushgateway may be unresponsive.')
    except Exception as e:
        print(f'[!] Unexpected error: {e}')

def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(description='Generate fake ROS 2 latency metrics for Prometheus')
    parser.add_argument('--gateway', default=DEFAULT_PUSHGATEWAY_URL,
                        help='Pushgateway URL (default: %(default)s)')
    parser.add_argument('--interval', type=int, default=DEFAULT_INTERVAL_SECONDS,
                        help='Interval between pushes in seconds (default: %(default)s)')
    parser.add_argument('--once', action='store_true',
                        help='Run only once instead of continuously')
    args = parser.parse_args()

    print(f"Starting metrics generator\n→ Pushgateway: {args.gateway}\n→ Interval: {args.interval}s")

    while True:
        if CUSTOM_LATENCY_DATA:
            payload = generate_latency_metrics_from_custom(CUSTOM_LATENCY_DATA)
        else:
            payload = generate_latency_metrics_from_nodes(DEFAULT_NODES)

        push_to_gateway(payload.strip() + '\n', args.gateway)

        if args.once:
            break

        try:
            time.sleep(args.interval)
        except KeyboardInterrupt:
            print("\n[!] Stopped by user.")
            break

if __name__ == "__main__":
    main()