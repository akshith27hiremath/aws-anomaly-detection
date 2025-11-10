# Quick Start Guide

## Prerequisites
- Python 3.9+
- Node.js 16+ and npm
- Backend running (see Backend Setup)

## Running the System

### Step 1: Start the Backend

**Terminal 1:**
```bash
cd anomaly-detection-system
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
python run_system.py
```

Backend will be available at: **http://localhost:8000**

### Step 2: Start the Frontend

**Terminal 2:**
```bash
cd anomaly-detection-system/frontend
npm install  # First time only
npm run dev
```

Frontend will be available at: **http://localhost:5173**

### Step 3: Access the Dashboard

Open your browser and go to:
```
http://localhost:5173
```

## What You'll See

### Initial State
- Connection status in header (will show "Connected" when backend is ready)
- Empty anomaly feed (waiting for data collection)
- Agent panel showing 5 detection agents
- Knowledge graph building...

### After Data Collection Starts (60-300 seconds)
- Real-time anomalies appearing in the feed
- Statistics updating
- Knowledge graph populating
- Time series charts with data

## Features Overview

### Dashboard Components
1. **Header**: System title and connection status
2. **Statistics Bar**: Total anomalies, high severity count, active reports
3. **Live Anomaly Feed**: Real-time anomaly stream with details
4. **Knowledge Graph**: Visual representation of anomaly relationships
5. **Time Series Chart**: Data visualization across all sources
6. **Agent Analysis**: Status of 5 specialized detection agents

### No Emojis
All visual indicators use:
- Colored dots (● replaced with styled SVG circles)
- Badge labels with colors
- Professional animations
- Clean, minimal UI

## Data Sources

The system monitors:

### Cryptocurrency (Updates every 60 seconds)
- Bitcoin, Ethereum, Cardano, Solana
- Price, Volume, Market Cap

### Weather (Updates every 5 minutes)
- New York, London, Tokyo, Singapore
- Temperature, Humidity, Pressure, Wind Speed

### GitHub (Updates every 5 minutes)
- TensorFlow, VSCode, React, Kubernetes
- Commits, Issues, PRs, Stars

## API Endpoints

### REST API
```
GET  http://localhost:8000/health          - System health check
GET  http://localhost:8000/analysis         - Latest anomaly analysis
GET  http://localhost:8000/knowledge-graph  - Graph data
GET  http://localhost:8000/data-sources     - Current data from sources
GET  http://localhost:8000/statistics       - System statistics
POST http://localhost:8000/analyze          - Trigger manual analysis
```

### WebSocket
```
ws://localhost:8000/ws  - Real-time anomaly updates
```

## Configuration

### Environment Variables (.env)
```
COINGECKO_API_KEY=          # Empty - uses free tier
OPENWEATHER_API_KEY=        # Empty - uses Open-Meteo (no key needed)
GITHUB_TOKEN=               # Empty - uses free tier

HOST=0.0.0.0
PORT=8000
DEBUG=true
LOG_LEVEL=INFO
```

### Detection Parameters (config.yaml)
All thresholds, algorithms, and weights can be adjusted in:
```
config/detection_config.yaml
```

## Troubleshooting

### Dashboard shows "Disconnected"
1. Check if backend is running
2. Look for "WebSocket connected" in backend logs
3. Try refreshing the page

### No anomalies appearing
1. Wait 60+ seconds for first data collection
2. Check backend logs for errors
3. Verify API keys if using real data sources

### Frontend not loading
1. Verify frontend is running: `npm run dev`
2. Check http://localhost:5173 in browser
3. Look for CORS errors in console

### Backend crashes
1. Check logs for specific error
2. Verify all dependencies installed: `pip install -r requirements.txt`
3. Ensure no port conflicts (8000 must be available)

## Next Steps

### For Development
1. Modify detection algorithms in `backend/detection/`
2. Customize thresholds in `config/detection_config.yaml`
3. Add new data sources in `backend/data_sources/`
4. Enhance UI in `frontend/src/components/`

### For Deployment
1. Build frontend: `npm run build` (creates `dist/` folder)
2. Use production server (Gunicorn for Python, nginx for frontend)
3. Configure environment variables for production
4. Set up monitoring and alerting

### For Testing
1. Run backend tests: `pytest tests/`
2. Run demo scenario: `python demo_scenario.py`
3. Check API endpoints with curl or Postman

## File Structure

```
anomaly-detection-system/
├── backend/                    # Python FastAPI backend
│   ├── agents/                # AI detection agents
│   ├── data_sources/          # API clients (crypto, weather, github)
│   ├── detection/             # Detection algorithms
│   ├── knowledge_graph/       # Graph analysis
│   ├── api/                   # REST API endpoints
│   └── utils/                 # Configuration and helpers
├── frontend/                  # React + TypeScript dashboard
│   ├── src/
│   │   ├── components/       # React components
│   │   ├── App.tsx           # Main app component
│   │   └── App.css           # Styling (enhanced, no emojis)
│   └── package.json
├── config/                    # YAML configuration files
├── tests/                     # Test suite
├── .env                       # Environment variables
└── README.md                  # Full documentation
```

## Performance Expectations

- Dashboard loads: < 2 seconds
- Real-time updates: < 500ms latency
- Data collection: Every 60-300 seconds per source
- Anomaly detection: < 1 second per cycle
- WebSocket messages: 10-100 per minute

## System Resources

Recommended:
- RAM: 4GB minimum, 8GB recommended
- CPU: 2+ cores
- Disk: 1GB for database and logs
- Network: Stable internet for API calls

## Learning Resources

1. **ARCHITECTURE.md** - System design and how it works
2. **MIGRATION_SUMMARY.md** - Recent changes (OpenWeather to Open-Meteo)
3. **FRONTEND_SETUP.md** - Frontend enhancement details
4. **FRONTEND_GUIDE.md** - Dashboard user guide

## Contact

For questions or issues:
1. Check documentation files
2. Review backend logs: See console output
3. Check browser console: F12 -> Console tab

---

**Ready to go!** Your system is fully configured and ready to detect anomalies.

Start with Step 1 above and you'll have real-time anomaly detection running in minutes.
