# 🚀 Quick Start Guide

Get the Anomaly Detection System running in under 5 minutes!

## Prerequisites

- Python 3.9+
- Node.js 16+
- pip and npm

## Step 1: Clone and Setup Python Environment

```bash
cd anomaly-detection-system

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Step 2: Configure Environment (Optional)

```bash
# Copy example environment file
cp .env.example .env

# Edit .env to add your API keys (optional for demo)
# The system works without API keys using mock data
nano .env
```

## Step 3: Run the Backend

```bash
# Start the FastAPI server
python run_system.py
```

You should see:
```
🚀 Starting Anomaly Detection System
========================================
Host: 0.0.0.0
Port: 8000
========================================

Access the API at: http://localhost:8000
API Documentation: http://localhost:8000/docs
```

## Step 4: Run the Frontend (Optional)

Open a new terminal:

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Dashboard will be available at: http://localhost:5173

## Step 5: Run Demo Scenarios

In another terminal:

```bash
# Activate virtual environment
source venv/bin/activate

# Run demo
python demo_scenario.py
```

This will run 3 demo scenarios showing:
1. Flash crash in crypto with GitHub correlation
2. Weather anomaly with GitHub activity spike
3. Cascading anomalies across all sources

## Testing the API

### Using curl

```bash
# Health check
curl http://localhost:8000/health

# Get latest analysis
curl http://localhost:8000/analysis

# Get knowledge graph
curl http://localhost:8000/knowledge-graph

# Trigger manual analysis
curl -X POST http://localhost:8000/analyze

# Get system statistics
curl http://localhost:8000/statistics
```

### Using the Interactive API Docs

Visit http://localhost:8000/docs for Swagger UI

## Testing WebSocket Connection

```javascript
const ws = new WebSocket('ws://localhost:8000/ws');

ws.onopen = () => console.log('Connected!');
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Received:', data);
};
```

## Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=backend --cov-report=html

# Run specific test file
pytest tests/test_detectors.py -v
```

## Viewing Logs

The system logs to stdout. To save logs to a file:

```bash
python run_system.py 2>&1 | tee system.log
```

## Common Issues

### Port Already in Use

If port 8000 is already in use, edit `.env`:

```
PORT=8001
```

### Missing API Keys

The system works without API keys using simulated data. To use real data:

1. Get free API keys:
   - CoinGecko: https://www.coingecko.com/en/api
   - OpenWeather: https://openweathermap.org/api
   - GitHub: https://github.com/settings/tokens

2. Add to `.env` file

### Import Errors

Make sure you're in the virtual environment:

```bash
which python  # Should point to venv/bin/python
```

## Next Steps

- Explore the API documentation at `/docs`
- Check the knowledge graph visualization in the dashboard
- Review individual agent analysis in the Agent Panel
- Experiment with different detection thresholds in `config/detection_config.yaml`

## Stopping the System

Press `Ctrl+C` in the terminal running the backend

## Getting Help

- Check `README.md` for full documentation
- View API docs at http://localhost:8000/docs
- Review configuration in `config/detection_config.yaml`
- Check logs for error messages

---

**You're now running a production-ready multi-agent anomaly detection system! 🎉**
