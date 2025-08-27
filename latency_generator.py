import random
import time
import requests

# self URL Pushgateway
PUSHGATEWAY_URL = 'http://localhost:9091/metrics/job/fake_latency_test/instance/manual'

# randomly generate
NODES = ['node-a', 'node-b', 'node-c', 'node-d']

# customize data
# format：source, target, latency_fwd, latency_rev
CUSTOM_LATENCY_DATA = None
# example:
# CUSTOM_LATENCY_DATA = [
#     ('ros-pub', 'ros-sub', 0.12, 0.25),
#     ('ros-sub', 'ros-analyzer', 0.33, 0.29)
# ]

INTERVAL_SECONDS = 10


def generate_latency_metrics_from_nodes(node_list):
    lines = []
    for i in range(len(node_list)):
        for j in range(i + 1, len(node_list)):
            src = node_list[i]
            dst = node_list[j]
            latency_fwd = round(random.uniform(0.05, 1.0), 3)
            latency_rev = round(random.uniform(0.05, 1.0), 3)

            lines.append(f'fake_latency_seconds{{source="{src}",target="{dst}",direction="fwd"}} {latency_fwd}')
            lines.append(f'fake_latency_seconds{{source="{dst}",target="{src}",direction="rev"}} {latency_rev}')
    return '\n'.join(lines)


def generate_latency_metrics_from_custom(data):
    lines = []
    for src, dst, latency_fwd, latency_rev in data:
        lines.append(f'fake_latency_seconds{{source="{src}",target="{dst}",direction="fwd"}} {latency_fwd}')
        lines.append(f'fake_latency_seconds{{source="{dst}",target="{src}",direction="rev"}} {latency_rev}')
    return '\n'.join(lines)


def push_to_gateway(payload: str):
    try:
        headers = {'Content-Type': 'text/plain'}
        res = requests.put(PUSHGATEWAY_URL, data=payload.encode('utf-8'), headers=headers)
        print(f'[✓] Pushed {len(payload.splitlines())} metrics\n{payload}\n')
        print(f"[→] Response code: {res.status_code}, text: {res.text}")
    except Exception as e:
        print(f'[!] Error pushing metrics: {e}')


if __name__ == "__main__":
    while True:
        if CUSTOM_LATENCY_DATA:
            payload = generate_latency_metrics_from_custom(CUSTOM_LATENCY_DATA)
        else:
            payload = generate_latency_metrics_from_nodes(NODES)

        push_to_gateway(payload.strip() + '\n')
        time.sleep(INTERVAL_SECONDS)