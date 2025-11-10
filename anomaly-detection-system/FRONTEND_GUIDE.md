# Dashboard User Guide

## Dashboard Overview

The Anomaly Detection System dashboard provides real-time monitoring and visualization of anomalies detected across multiple data sources.

### Main Sections

#### 1. Header
- **System Title**: Anomaly Detection System
- **Connection Status**:
  - Green indicator with "Connected" - Backend is active
  - Red indicator with "Disconnected" - Backend unreachable

#### 2. Statistics Bar
Three key metrics displayed as cards:
- **Total Anomalies**: Cumulative count of all detected anomalies
- **High Severity**: Critical and high-severity anomalies (red highlighted)
- **Active Reports**: Current anomaly reports being tracked

#### 3. Live Anomaly Feed (Left Panel)
Real-time stream of detected anomalies with:
- **Colored Left Border**: Severity indicator
  - Red: Critical
  - Orange: High
  - Yellow: Medium
  - Green: Low
- **Severity Badge**: Shows anomaly severity level
- **Confidence Score**: How confident the detection is (0-100%)
- **Timestamp**: When the anomaly was detected
- **Description**: Narrative explanation of the anomaly

#### 4. Knowledge Graph (Right Panel)
Visual representation of anomaly relationships:
- **Nodes**: Individual anomalies
- **Edges**: Relationships between anomalies
- **Statistics**: Number of nodes and edges in the graph

#### 5. Time Series Analysis (Full Width)
Chart showing:
- Data point values over time
- Multiple metric lines
- Source-specific visualization

#### 6. Agent Analysis (Full Width)
Five specialized detection agents with:
- **Statistical Agent** (25% weight)
- **Temporal Agent** (25% weight)
- **Correlation Agent** (20% weight)
- **Context Agent** (15% weight)
- **Coordinator Agent** (15% weight)

Each agent shows:
- Status indicator (green dot)
- Weight in final decision
- Active status

## Features

### Real-time Updates
- WebSocket connection maintains live updates
- Automatic reconnection if disconnected
- No page refresh required

### Color Coding
```
Severity Levels:
- Critical (Red #dc2626)
- High (Orange #ea580c)
- Medium (Yellow #ca8a04)
- Low (Green #65a30d)

Status:
- Connected (Green #10b981)
- Disconnected (Red #ef4444)
```

### Interactive Elements
- Hover over cards for depth effect
- Feed items highlight on hover
- Agent cards show enhanced styling on interaction
- Smooth transitions on all interactive elements

## How to Use

### Monitoring Anomalies
1. Check the **Statistics Bar** for quick overview
2. Review **Live Anomaly Feed** for details
3. High severity items appear first

### Understanding Reports
- **Source**: Where the anomaly was detected (crypto, weather, github)
- **Metric**: What measurement triggered the alert
- **Confidence**: Trust level in the detection
- **Narrative**: Human-readable explanation

### Checking System Health
- Look at the **Connection Status** in header
- Pulsing indicator means data is flowing
- Red indicator means reconnection is needed

## Data Sources

### Cryptocurrency
- Bitcoin, Ethereum, Cardano, Solana
- Metrics: Price, Volume, Market Cap
- Updated: Every 60 seconds

### Weather
- Cities: New York, London, Tokyo, Singapore
- Metrics: Temperature, Humidity, Pressure, Wind Speed
- Updated: Every 5 minutes

### GitHub
- Major repositories: TensorFlow, VSCode, React, Kubernetes
- Metrics: Commits, Issues, Pull Requests, Stars
- Updated: Every 5 minutes

## Troubleshooting

### Dashboard Not Loading
- Check if backend is running: `python run_system.py`
- Verify backend is on http://localhost:8000
- Check browser console for errors

### No Data Appearing
- Backend may be starting up (wait 30 seconds)
- WebSocket connection may be establishing
- Check browser network tab for ws://localhost:8000/ws

### Anomalies Not Updating
- Wait for next data collection cycle
- Crypto: 60 second intervals
- Weather: 5 minute intervals
- GitHub: 5 minute intervals

### Disconnected Status
- Backend might have crashed
- Restart: `python run_system.py`
- Dashboard will auto-reconnect

## Keyboard Shortcuts
- None currently - all interaction is mouse/touch based

## Browser Compatibility
- Chrome/Edge (Latest)
- Firefox (Latest)
- Safari (Latest)

## Performance Tips
- Use Chrome for best performance
- Close unused tabs for smoother experience
- Keep backend well-resourced
- 8GB+ RAM recommended for extended monitoring

## Contact & Support
For issues or feature requests, check the documentation in:
- `README.md` - Project overview
- `ARCHITECTURE.md` - System design
- `MIGRATION_SUMMARY.md` - Recent changes

---

**Last Updated**: 2025-11-09
**Dashboard Version**: 1.0.0
