# START HERE - Complete System Setup

## Quick Overview
Your Anomaly Detection System is fully configured and ready to run. This document has everything you need to get started.

## What You Have

### Backend (Python)
- Multi-agent anomaly detection system
- Real-time data collection from 3 sources
- REST API + WebSocket for real-time updates
- FastAPI server running on port 8000

### Frontend (React)
- Beautiful, emoji-free dashboard
- Real-time visualization
- Professional dark theme
- No emojis - clean, minimal design

### Data Sources
1. **Cryptocurrency** (CoinGecko - Free)
   - Bitcoin, Ethereum, Cardano, Solana
   - Updates every 60 seconds

2. **Weather** (Open-Meteo - Free, No API Key!)
   - New York, London, Tokyo, Singapore
   - Updates every 5 minutes

3. **GitHub** (Free tier)
   - TensorFlow, VSCode, React, Kubernetes
   - Updates every 5 minutes

## Getting Started (5 Minutes)

### Option A: Run Backend & Frontend Together

**Terminal 1 - Backend:**
```bash
cd aws-hackathon/anomaly-detection-system

# Create virtual environment (first time only)
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies (first time only)
pip install -r requirements.txt

# Run the backend
python run_system.py
```

You should see:
```
============================================================
Starting Anomaly Detection System
============================================================
Host: 0.0.0.0
Port: 8000
Debug Mode: True
============================================================

Access the API at: http://localhost:8000
API Documentation: http://localhost:8000/docs
WebSocket endpoint: ws://localhost:8000/ws
```

**Terminal 2 - Frontend:**
```bash
cd aws-hackathon/anomaly-detection-system/frontend

# Install dependencies (first time only)
npm install

# Start development server
npm run dev
```

You should see:
```
  VITE v5.0.8  ready in xxx ms

  > Local:   http://localhost:5173/
  > press h to show help
```

### Step 3: Open Dashboard
Open your browser to: **http://localhost:5173**

## What You'll See

### Immediately
- Header with "Anomaly Detection System"
- Connection status (animated dot)
- 3 stat cards (will show 0s initially)
- 5 agent panels

### After 60 Seconds
- CoinGecko data appears
- First anomalies may be detected

### After 5 Minutes
- Weather and GitHub data appears
- Knowledge graph starts populating
- Charts fill with data

## Dashboard Features

### Header
- System title
- Connection status (green=connected, red=disconnected)
- Animated pulsing indicator

### Statistics Bar
- Total Anomalies detected
- High Severity count
- Active Reports

### Panels
1. **Live Anomaly Feed** - Real-time anomalies
2. **Knowledge Graph** - Anomaly relationships
3. **Time Series Chart** - Data over time
4. **Agent Analysis** - 5 detection agents

### Colors & Design
- No emojis - pure professional design
- Dark theme with blue accents
- Colored severity indicators
- Smooth animations

## API Documentation

While running, visit: **http://localhost:8000/docs**

This shows all available REST endpoints and lets you test them.

## Configuration

### Environment Variables
All configured in `.env` file:
```
COINGECKO_API_KEY=          (blank - uses free tier)
OPENWEATHER_API_KEY=        (blank - Open-Meteo is free!)
GITHUB_TOKEN=               (blank - uses free tier)
HOST=0.0.0.0
PORT=8000
DEBUG=true
LOG_LEVEL=INFO
```

### Detection Settings
Located in: `config/detection_config.yaml`
- Adjust thresholds
- Enable/disable algorithms
- Configure agent weights
- Set alert severity levels

## Stopping the System

### Ctrl+C
Press Ctrl+C in each terminal to stop the servers gracefully.

## Common Tasks

### Restart the System
1. Press Ctrl+C in both terminals
2. Run the commands again from "Getting Started"

### Check API Health
```bash
curl http://localhost:8000/health
```

### View Logs
Logs appear in the terminal where backend is running.

### Test with Demo Data
```bash
# Terminal 3, with venv activated:
python demo_scenario.py
```
This injects synthetic anomalies for testing.

### Run Tests
```bash
# Terminal 3, with venv activated:
pytest tests/ -v
```

## Troubleshooting

### Dashboard shows "Disconnected"
1. Check backend terminal - look for errors
2. Backend may still be starting
3. Try refreshing the page
4. Check http://localhost:8000/health

### No data appearing
1. Wait 60+ seconds for first collection
2. Check backend logs for API errors
3. Verify internet connection

### Port already in use
Backend uses port 8000, frontend uses 5173.
If ports are busy:
- Edit .env (change PORT=8000)
- Kill other processes using the port

### Module not found errors
Ensure venv is activated:
```bash
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

### npm command not found
Install Node.js from: https://nodejs.org/

## File Structure Quick Reference

```
aws-hackathon/
├── anomaly-detection-system/
│   ├── backend/              # Python FastAPI
│   ├── frontend/             # React dashboard
│   ├── config/               # Settings
│   ├── tests/                # Test suite
│   ├── .env                  # Configuration
│   └── run_system.py         # Start backend
├── QUICK_START.md            # Detailed setup
├── FRONTEND_ENHANCEMENTS.md  # UI improvements
└── START_HERE.md             # This file
```

## Documentation Files

- **QUICK_START.md** - Detailed setup and features
- **FRONTEND_ENHANCEMENTS.md** - UI/design details
- **FRONTEND_GUIDE.md** - Dashboard user guide
- **FRONTEND_SETUP.md** - Development guide
- **MIGRATION_SUMMARY.md** - Recent changes
- **README.md** - Full project documentation
- **ARCHITECTURE.md** - System design

## System Requirements

- Python 3.9+
- Node.js 16+
- 4GB RAM minimum
- Internet connection
- Ports 8000 and 5173 available

## Next Steps

### Immediate
1. Start backend and frontend (see Getting Started)
2. Open dashboard at http://localhost:5173
3. Watch for real-time anomalies

### Learning
1. Read QUICK_START.md for detailed info
2. Check FRONTEND_GUIDE.md to understand dashboard
3. Read ARCHITECTURE.md to understand how detection works

### Customization
1. Edit `config/detection_config.yaml` for thresholds
2. Modify `frontend/src/App.css` for styling
3. Add new data sources in `backend/data_sources/`

### Production Deployment
1. Build frontend: `npm run build` (in frontend/)
2. Use production Python server (Gunicorn)
3. Use production frontend server (nginx)
4. Configure environment variables

## Support

### Check Logs
Backend logs appear in terminal where it's running.

### API Documentation
Visit http://localhost:8000/docs while backend is running.

### Test Endpoints
```bash
# Health check
curl http://localhost:8000/health

# Get latest analysis
curl http://localhost:8000/analysis

# Get data sources
curl http://localhost:8000/data-sources
```

## Success Checklist

- [ ] Backend running (see "Access the API at..." message)
- [ ] Frontend running (see "Local:   http://localhost:5173/" message)
- [ ] Dashboard loading at http://localhost:5173
- [ ] Status shows "Connected"
- [ ] Waiting for first data collection (60+ seconds)
- [ ] Anomalies appearing in feed
- [ ] Charts populating with data

## You're All Set!

Your system is fully configured and ready to detect anomalies in real-time.

**Start with the Getting Started section above and you'll have everything running in 5 minutes.**

Any questions? Check the documentation files or examine the logs in the backend terminal.

---

**Last Updated**: 2025-11-09
**System Version**: 1.0.0
**Status**: Ready to Deploy
