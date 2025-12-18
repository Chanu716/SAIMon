# 📊 Grafana Setup Guide - After First Login

## 🔐 Step 1: First Login

1. Open http://localhost:3000
2. Login with:
   - **Username:** `admin`
   - **Password:** `admin123`
3. You may be prompted to change password (recommended for production!)
    
---

## ✅ Step 2: Verify Prometheus Datasource

Your Prometheus datasource is **already configured**! Let's verify it:

1. Click the **☰ menu** (top left) → **Connections** → **Data sources**
2. You should see **Prometheus** listed as the default datasource
3. Click on **Prometheus** to verify:
   - URL: `http://prometheus:9090`
   - Status should show: **"Data source is working"**

If you see a green checkmark ✅, you're good to go!

---

## 📈 Step 3: Create Your First Dashboard

### Option A: Quick Dashboard (Recommended for Beginners)

1. Click **☰ menu** → **Dashboards** → **New** → **New Dashboard**
2. Click **+ Add visualization**
3. Select **Prometheus** as the datasource
4. In the query builder, try these queries:

#### Query 1: CPU Usage
```promql
100 - (avg by (instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)
```
- Panel title: "CPU Usage %"
- Visualization: **Time series**

#### Query 2: Memory Usage
```promql
100 * (1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes))
```
- Panel title: "Memory Usage %"
- Visualization: **Gauge**

#### Query 3: Disk I/O
```promql
rate(node_disk_read_bytes_total[5m]) + rate(node_disk_written_bytes_total[5m])
```
- Panel title: "Disk I/O"
- Visualization: **Time series**

#### Query 4: Network Traffic
```promql
rate(node_network_receive_bytes_total[5m]) + rate(node_network_transmit_bytes_total[5m])
```
- Panel title: "Network Traffic"
- Visualization: **Time series**

5. Click **Apply** for each panel
6. Click **Save dashboard** (💾 icon top right)
7. Give it a name: "SAIMon System Overview"

---

### Option B: Import Pre-built Dashboard

Grafana has thousands of community dashboards. Here's how to import one:

1. Go to **☰ menu** → **Dashboards** → **New** → **Import**
2. Try these popular Node Exporter dashboards:
   - **Dashboard ID: 1860** - Node Exporter Full
   - **Dashboard ID: 11074** - Node Exporter for Prometheus
   - **Dashboard ID: 405** - Node Exporter Server Metrics

3. Enter the ID and click **Load**
4. Select **Prometheus** as the datasource
5. Click **Import**

**Recommended:** Start with **1860** - it's the most comprehensive!

---

## 🤖 Step 4: Create SAIMon Anomaly Dashboard

Let's create a custom dashboard to visualize anomalies detected by SAIMon:

### Panel 1: Anomaly Count Over Time

1. Create new dashboard
2. Add visualization
3. Switch to **Code** mode (toggle on right)
4. Use this query:

```promql
saimon_anomalies_detected_total
```

- Visualization: **Time series** or **Stat**
- Panel title: "Total Anomalies Detected"

### Panel 2: Anomalies by Severity

```promql
sum by (severity) (saimon_anomalies_detected_total)
```

- Visualization: **Pie chart** or **Bar gauge**
- Panel title: "Anomalies by Severity"

### Panel 3: Model Accuracy

```promql
saimon_model_accuracy
```

- Visualization: **Gauge**
- Panel title: "Model Accuracy"
- Thresholds: 
  - Red: 0-70
  - Yellow: 70-85
  - Green: 85-100

### Panel 4: Detection Latency

```promql
saimon_detection_latency_seconds
```

- Visualization: **Time series**
- Panel title: "Detection Latency"

---

## ⚙️ Step 5: Configure Dashboard Settings

### Time Range
1. Click the **time picker** (top right)
2. Set default to: **Last 6 hours** or **Last 24 hours**
3. Enable **Auto refresh**: 30s or 1m

### Variables (Advanced)
Create a variable to filter by instance:

1. Dashboard settings (⚙️ icon) → **Variables** → **New variable**
2. Name: `instance`
3. Type: **Query**
4. Data source: **Prometheus**
5. Query: `label_values(up, instance)`
6. Click **Apply**

Now you can use `$instance` in your queries:
```promql
rate(node_cpu_seconds_total{instance="$instance"}[5m])
```

---

## 🎨 Step 6: Customize Panels

Click on any panel title → **Edit** to customize:

### Visualization Options
- **Time series**: Lines, bars, points
- **Gauge**: Thresholds, min/max values
- **Stat**: Big numbers, sparklines
- **Table**: Tabular data
- **Pie chart**: Distribution

### Panel Options
- **Title**: Descriptive name
- **Description**: Add context
- **Transparent background**: Clean look
- **Links**: Link to other dashboards

### Thresholds
Set color-coded thresholds:
- Green: Normal (0-70)
- Yellow: Warning (70-85)
- Red: Critical (85-100)

### Overrides
Apply different styles to specific series

---

## 🔔 Step 7: Set Up Alerts (Optional)

1. Edit a panel → **Alert** tab
2. Click **Create alert rule**
3. Set conditions:
   ```
   WHEN avg() OF query(A, 5m, now) IS ABOVE 80
   ```
4. Configure notifications:
   - Email
   - Slack
   - Webhook

---

## 📊 Step 8: Organize Dashboards

### Create Folders
1. **☰ menu** → **Dashboards**
2. Click **New** → **New folder**
3. Create folders like:
   - System Monitoring
   - SAIMon Analytics
   - Application Metrics

### Dashboard Tags
Add tags to dashboards for easy filtering:
- `system`
- `ml`
- `production`
- `alerts`

---

## 🎯 Recommended Dashboard Layout

### Dashboard 1: System Overview
- CPU usage (all cores)
- Memory usage
- Disk I/O
- Network traffic
- System uptime

### Dashboard 2: SAIMon Analytics
- Total anomalies detected
- Anomalies by severity
- Model performance metrics
- Detection latency
- False positive rate

### Dashboard 3: Real-time Monitoring
- Live metric values
- Recent anomalies (last 1 hour)
- Alert status
- Service health

---

## 💡 Pro Tips

### 1. Use Template Variables
Create variables for:
- **Environment**: dev, staging, prod
- **Instance**: Filter by specific servers
- **Time range**: Quick time selection

### 2. Keyboard Shortcuts
- `Ctrl+S` / `Cmd+S`: Save dashboard
- `d + k`: Toggle kiosk mode (full screen)
- `Ctrl+H` / `Cmd+H`: Hide/show controls

### 3. Dashboard Snapshots
Share dashboards with teammates:
1. **Share** → **Snapshot**
2. Set expiration
3. Copy link

### 4. Playlist Mode
Create a playlist to cycle through dashboards:
1. **☰ menu** → **Playlists**
2. Add dashboards
3. Set interval (e.g., 30 seconds)
4. Start playlist

### 5. Explore Mode
Quick ad-hoc queries:
1. **☰ menu** → **Explore**
2. Select **Prometheus**
3. Run queries without creating dashboards

---

## 🔍 Useful Prometheus Queries

### System Metrics

**CPU Usage per Core:**
```promql
100 - (avg by (cpu) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)
```

**Available Memory (GB):**
```promql
node_memory_MemAvailable_bytes / 1024 / 1024 / 1024
```

**Disk Usage %:**
```promql
100 - ((node_filesystem_avail_bytes / node_filesystem_size_bytes) * 100)
```

**Network Received (MB/s):**
```promql
rate(node_network_receive_bytes_total[5m]) / 1024 / 1024
```

**System Load:**
```promql
node_load1
node_load5
node_load15
```

### SAIMon Metrics (Once Available)

**Anomaly Detection Rate:**
```promql
rate(saimon_anomalies_detected_total[5m])
```

**Active Models:**
```promql
saimon_active_models
```

**Training Duration:**
```promql
saimon_training_duration_seconds
```

---

## 🚀 Quick Start Commands

### Open Grafana
```powershell
start http://localhost:3000
```

### Check Grafana Logs
```powershell
docker-compose logs -f grafana
```

### Restart Grafana
```powershell
docker-compose restart grafana
```

### Check Datasource from CLI
```powershell
# From inside container
docker exec saimon-grafana grafana-cli admin reset-admin-password newpassword
```

---

## 📚 Sample Dashboard JSON

Save this as a JSON file and import it:

```json
{
  "dashboard": {
    "title": "SAIMon Quick Start",
    "panels": [
      {
        "title": "CPU Usage",
        "targets": [
          {
            "expr": "100 - (avg(rate(node_cpu_seconds_total{mode=\"idle\"}[5m])) * 100)"
          }
        ],
        "type": "graph"
      },
      {
        "title": "Memory Usage",
        "targets": [
          {
            "expr": "100 * (1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes))"
          }
        ],
        "type": "gauge"
      }
    ]
  }
}
```

---

## 🎓 Learning Resources

### Official Documentation
- Grafana Docs: https://grafana.com/docs/grafana/latest/
- Dashboard Best Practices: https://grafana.com/docs/grafana/latest/best-practices/
- Panel Documentation: https://grafana.com/docs/grafana/latest/panels/

### Community Dashboards
- Browse: https://grafana.com/grafana/dashboards/
- Node Exporter: https://grafana.com/grafana/dashboards/?search=node+exporter
- Prometheus: https://grafana.com/grafana/dashboards/?dataSource=prometheus

### Video Tutorials
- Grafana YouTube: https://www.youtube.com/c/Grafana
- Getting Started: Search "Grafana tutorial for beginners"

---

## ❓ Troubleshooting

### "No data" in panels
1. Check time range (top right) - set to "Last 6 hours"
2. Verify Prometheus datasource is working
3. Check if metrics exist: **Explore** → Run query `up`
4. Verify Prometheus is scraping: http://localhost:9090/targets

### Dashboard not saving
1. Check browser console for errors
2. Verify you have edit permissions
3. Try exporting JSON and re-importing

### Grafana slow/unresponsive
1. Reduce query time range
2. Increase refresh interval
3. Check Docker resource limits
4. Restart Grafana: `docker-compose restart grafana`

---

## 🎯 Your First 10 Minutes Checklist

- [ ] Login to Grafana (admin/admin123)
- [ ] Verify Prometheus datasource works
- [ ] Import dashboard #1860 (Node Exporter Full)
- [ ] Create a custom panel with CPU usage
- [ ] Set time range to "Last 6 hours"
- [ ] Enable auto-refresh (30s)
- [ ] Add panel for memory usage
- [ ] Save your first dashboard
- [ ] Create a folder "SAIMon Dashboards"
- [ ] Explore other metrics in **Explore** mode

---

## 🎊 Next Steps

Once comfortable with basic dashboards:

1. **Create alerts** for critical metrics
2. **Set up notifications** (email/Slack)
3. **Build SAIMon-specific dashboards** for ML metrics
4. **Create playlists** for monitoring displays
5. **Share dashboards** with your team
6. **Export/backup** dashboard JSON files

---

**Happy Dashboarding! 📊**

*For more help, see the official Grafana documentation or run: `docker-compose logs grafana`*
