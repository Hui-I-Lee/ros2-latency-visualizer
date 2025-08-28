# ROS 2 Latency Visualizer

An experimental pipeline to visualize communication latency between distributed ROS 2 nodes using Prometheus and Grafana. Provides both native integration and a custom workaround for enhanced visualization.

## ⚠️ The Challenge: Grafana Node Graph Limitations

During development, we identified three key limitations in the native Grafana Node Graph panel for visualizing communication latency:

1.  **Bidirectional Blindness**: Cannot display separate edges for A→B and B→A communication, collapsing them into a single bidirectional arrow.
2.  **Over-Simplified Layout**: In complex topologies (e.g., A→C, C→D, A→D), it may automatically hide edges, leading to loss of information.
3.  **Missing Edge Metrics**: Lacks the ability to display latency values directly on the graph edges.

## ✨ Our Solution: A Dual-Approach Pipeline

To address these challenges, this project provides a complete data pipeline and **two visualization options**:

### Option 1: Native Grafana Dashboard
-   **Pros**: Tightly integrated with the Prometheus/Grafana stack, quick setup.
-   **Cons**: Inherits the native Node Graph limitations mentioned above.
-   **Use this for**: Simple topologies and quick monitoring.

### Option 2: Custom Cytoscape.js Visualizer (Workaround)
-   **Pros**: **Solves all three Grafana limitations**:
    -   ✅ Clear directional edges (A→B and B→A are separate lines)
    -   ✅ Preserves all connections in complex topologies
    -   ✅ Displays latency values directly on edges
-   **Cons**: Separate web interface outside of Grafana.
-   **Use this for**: Complex node interactions and detailed analysis.

## 📁 Repository Contents  
```text
ros2-latency-visualizer/
├── README.md
├── LICENSE
├── .gitignore
├── dashboards/
│   └── grafana_latency_dashboard.json
├── scripts/
│   └── ros2_latency_injector.py
├── cyto/
    └── index.html
```

## 🚀 Quick Start

### Prerequisites
-   [Prometheus](https://prometheus.io/download/)
-   Pushgateway
-   [Grafana](https://grafana.com/grafana/download)
-   Python 3.x

### Step 1: Configure Prometheus
Add to your `prometheus.yml`:

```yaml
scrape_configs:
  - job_name: 'fake_latency_test'
    honor_labels: true
    static_configs:
      - targets: ['localhost:pushgateway_port']
```

### Step 2: Run Services  
```bash
# Start Prometheus
./prometheus --config.file=prometheus.yml

# Start Grafana
./grafana-server
```

### Step 3: Generate Metrics
```bash
python3 ros2_latency_injector.py
```
The script will push metrics in this format:
```text
fake_latency_seconds{source="node-a",target="node-b",direction="fwd"} 0.267
```

### Step 4: Visualize

#### Option 1: Native Grafana Dashboard
1.  Start Grafana and log in (default: http://localhost:port_for_full_graph)
2.  Navigate to **Dashboards** → **New** → **Import**
3.  Click **Upload JSON file** and select `grafana_latency_dashboard.json`

**⚠️ Fundamental Limitation of Grafana Node Graph**
As noted in the [Challenge](#-the-challenge-grafana-node-graph-limitations), there are three main limitations. Among them, **only the bidirectional edge issue (A→B vs B→A) can be partially worked around**: Grafana will always collapse them into a single double-headed edge.  

**Workaround for Partial Analysis**:
-   The dashboard includes separate queries for forward (`direction="fwd"`) and reverse (`direction="rev"`) latency
-   **Disable one query** (click the eye icon 👁️) to view only one direction at a time
-   **Manually compare** the two views to understand bidirectional communication patterns

> **Major Drawback**: You lose the ability to see both directions and their respective latency values simultaneously in context.

#### Option 2: Enhanced Cytoscape.js Visualizer (Recommended) - *The Real Solution*
1.  **Start the local server** in the `cyto` directory:
    ```bash
    cd cyto/
    python3 -m http.server port_for_full_graph  # Port can be customized
    ```
2.  **Access from Grafana** (seamless integration!):
    -   Click the **"View Full Cytoscape Graph"** link in the dashboard
    -   Opens the enhanced visualizer in a new tab
3.  **Or access directly** via browser: `http://localhost:port_for_full_graph`

> **Why Option 2 is Essential**: It overcome's Grafana's core limitation by providing:
> -   ✅ **True bidirectional visualization**: A→B and B→A displayed as separate, directed edges
> -   ✅ **Simultaneous viewing**: Both directions visible at the same time with their respective latency values
> -   ✅ **Complete topological context**: No information loss due to edge collapsing
> -   ✅ **Interactive exploration**: Full control over the visualization

**Recommendation**: Use Option 1 for quick checks within Grafana, but switch to Option 2 for any serious analysis of bidirectional communication patterns.

## 🔧 Using Your Own Data  
To use real latency data, format your metrics to match this pattern:
```python
import requests

payload = """
fake_latency_seconds{source="perception_node", target="planning_node", direction="fwd"} 0.15
fake_latency_seconds{source="planning_node", target="perception_node", direction="rev"} 0.22
"""

requests.put(
    'http://localhost:9091/metrics/job/ros2_latency/instance/real_deployment',
    data=payload
)
```
Replace the injector script with your own data pipeline that pushes metrics in this format.  

## ⁉️ Troubleshooting

-   **"No Data" in Grafana?**
    -   Check if Prometheus is scraping the Pushgateway correctly.
    -   Verify the job name (`fake_latency_test`) matches in your Prometheus config, Python script, and Grafana dashboard.

-   **Cannot connect to Pushgateway?**
    -   Ensure the Pushgateway service is running on `localhost:pushgateway_port`.
    -   Check your firewall settings if accessing remotely.

-   **Visualizer not loading?**
    -   Make sure you started the HTTP server: `python3 -m http.server port_for_full_graph` in the `cyto` directory.
    -   Check if the port (8083) is already in use by another application.

-   **Metrics not updating?**
    -   Ensure the `ros2_latency_injector.py` script is running and not encountering errors.
    -   Check the Pushgateway logs for any ingestion issues.

## 📄 License  
MIT License. See LICENSE file.  


