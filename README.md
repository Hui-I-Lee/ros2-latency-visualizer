# ROS 2 Latency Visualizer

An experimental pipeline to visualize communication latency between distributed ROS 2 nodes using Prometheus and Grafana. Provides both native integration and a custom workaround for enhanced visualization.


## 🎯 Key Features

- 🧠 Simple Python script for generating fake or real latency data
- 📤 Uses Prometheus Pushgateway to send metrics to a specific target/port
- 📊 Grafana dashboard with built-in Node Graph and clickable Cytoscape link
- 🔁 Fully compatible with any system exposing Prometheus metrics — not limited to ROS 2
- 🌐 No need to modify or recompile ROS 2 source code — just follow the metric format
- 🪆 Self-contained and lab-independent — reproducible on any VM, container, or cloud instance


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
-   [Pushgateway](https://prometheus.io/docs/practices/pushing/)
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

👀 Why Two Visualization Options?  
You can visualize the latency data in two different ways:

#### Option 1: Grafana Node Graph (Built-In)  
Use this for quick monitoring and basic setups.
```text
1.  Start Grafana and log in (default: http://localhost:port_for_full_graph)
2.  Navigate to **Dashboards** → **New** → **Import**
3.  Click **Upload JSON file** and select `grafana_latency_dashboard.json`
```
⚠️ Grafana Node Graph Limitations:

 ❌ No Parallel Single Arrow: A → B and B → A exist simultaneously, representation will be A ↔ B  
 ❌ Automatic edge pruning: Complex graphs may omit connections without warning.  
 ❌ No edge labels: Latency values cannot be shown directly on edges.
  
**Workaround for Partial Analysis**:
-   The dashboard includes separate queries for forward (`direction="fwd"`) and reverse (`direction="rev"`) latency
-   **Disable one query** (click the eye icon 👁️) to view only one direction at a time
-   **Manually compare** the two views to understand bidirectional communication patterns

  
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

> 💡 Why Cytoscape?
> - A→B and B→A shown separately  
> - Latency values shown on edges  
> - All topology preserved, even in complex graphs  
> - Fully interactive view  

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


