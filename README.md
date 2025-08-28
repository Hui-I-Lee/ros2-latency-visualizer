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


## 🚀 Quick Start

### Prerequisites
-   [Prometheus](https://prometheus.io/download/)
-   [Prometheus Pushgateway](https://github.com/prometheus/pushgateway)
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

# Start Pushgateway
./pushgateway

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
1.  Start Grafana and log in (default: http://localhost:grafana_port)
2.  Navigate to **Dashboards** → **New** → **Import**
3.  Click **Upload JSON file** and select `grafana-dashboard-pipeline.json`
4.  Select your Prometheus data source and click **Import**

#### Option 2: Enhanced Visualizer (Workaround) - *Recommended for complex topologies*
1.  **Start the local server** in the directory which `index.html` is in:
    ```bash
    cd cyto/
    python3 -m http.server port_for_full_graph  # Port can be customized
    ```
2.  **Access from Grafana** ( seamless integration! ):
    -   The imported dashboard includes a direct link to the visualizer
    -   Simply click the **"View Full Cytoscapr Graph"** link in the dashboard
3.  **Or access directly** via browser: `http://localhost:port_for_full_graph`

> **Why Option 2?** It solves Grafana's limitations: shows bidirectional edges, preserves complex topology, and displays latency values directly on edges.

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


