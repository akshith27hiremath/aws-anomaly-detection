# HIVEMIND - Multi-Agent Anomaly Detection System

**Intelligent Real-Time Anomaly Detection with AI-Powered Insights**

HIVEMIND is a sophisticated, production-ready anomaly detection system that leverages multiple AI agents working in parallel to detect, analyze, and explain anomalies across diverse data sources including cryptocurrency markets, weather patterns, GitHub activity, and derivatives markets.

---

## 🎯 Key Features

### Multi-Agent Detection Architecture
- **5 Specialized AI Agents** working in parallel:
  - **Statistical Agent**: Z-Score, IQR, Modified Z-Score, Grubbs' Test
  - **Temporal Agent**: Moving averages, exponential smoothing, seasonal decomposition
  - **Correlation Agent**: Cross-source analysis, relationship mapping
  - **Context Agent**: Domain-specific rules and metadata analysis
  - **OI Agent**: Open Interest derivatives analysis (funding rates, long/short ratios, divergences)

### LLM-Powered Narratives
- **Anthropic Claude 3 Sonnet** for intelligent, context-aware anomaly explanations
- **OpenAI GPT-4** fallback for high availability
- **Template-based fallback** when no LLM provider is available
- Generates actionable insights instead of raw technical data

### Real-Time Data Sources
- **Cryptocurrency**: Bitcoin, Ethereum, Cardano, Solana (via CoinGecko API)
- **Derivatives**: Binance Futures OI, funding rates, long/short ratios
- **Weather**: Multi-city weather data (via Open-Meteo API)
- **GitHub**: Repository activity, commits, issues, pull requests

### Advanced Explainability
- **Knowledge Graph**: Tracks anomaly relationships and temporal correlations
- **Counterfactual Generation**: "What if" scenarios to explain anomalies
- **Consensus Scoring**: Weighted confidence from multiple agent detections
- **Visual Process Explanation**: Interactive dashboard showing detection pipeline

### Modern Tech Stack
- **Backend**: Python FastAPI, async/await, WebSockets for real-time updates
- **Frontend**: React + TypeScript + Vite with Framer Motion animations
- **Database**: SQLite with async support (aiosqlite)
- **Visualization**: Custom React components with color-coded knowledge graphs

---

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Node.js 16+
- npm or yarn

### Installation

**Backend Setup:**
```bash
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your API keys
```

**Frontend Setup:**
```bash
cd frontend
npm install
```

### Running the System

**Terminal 1 - Backend:**
```bash
python run_system.py
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

**Access:** `http://localhost:5174`

---

## 📊 Dashboard Components

1. **Latest Analysis Panel** - LLM-generated narratives explaining anomalies
2. **System Architecture Explainer** - Interactive visualization of detection pipeline
3. **Knowledge Graph** - Color-coded anomaly relationships
4. **OI Derivatives Panel** - Real-time futures market metrics
5. **Data Sources Monitor** - Status of all collection endpoints
6. **Statistics Panel** - Historical data and trends

---

## 🧠 LLM Integration

### Dual-Provider Architecture
1. **Primary**: Anthropic Claude 3 Sonnet
2. **Fallback**: OpenAI GPT-4
3. **Final Fallback**: Template-based

The system automatically fails over between providers for maximum reliability.

---

## ⚙️ Configuration

### API Keys (`.env` file)

```bash
# Cryptocurrency (required)
COINGECKO_API_KEY=your_key_here

# LLM Primary (recommended)
ANTHROPIC_API_KEY=your_key_here

# LLM Fallback (optional)
OPENAI_API_KEY=your_key_here

# GitHub (optional - for higher rate limits)
GITHUB_TOKEN=your_token_here
```

### Detection Thresholds
```bash
ZSCORE_THRESHOLD=3.0
IQR_MULTIPLIER=1.5
CONFIDENCE_THRESHOLD=0.7
MIN_SAMPLES_FOR_DETECTION=10
COLLECTION_INTERVAL_SECONDS=60
```

---

## 📁 Project Structure

```
anomaly-detection-system/
├── backend/
│   ├── agents/                 # AI detection agents
│   ├── data_sources/          # Data collection clients  
│   ├── detection/             # Detection algorithms
│   ├── explainability/        # LLM & narrative generation
│   └── knowledge_graph/       # Graph management
├── frontend/
│   ├── src/
│   │   ├── components/        # React components
│   │   └── services/          # API integration
│   └── package.json
├── config/
│   └── detection_config.yaml
├── .env
├── requirements.txt
└── README.md
```

---

## 🔍 Detection Methods

- **Statistical**: Z-Score, IQR, Modified Z-Score, Grubbs' Test
- **Temporal**: Moving average, exponential smoothing, seasonal decomposition
- **Correlation**: Pearson correlation, cross-source analysis
- **Context**: Domain rules, metadata analysis, historical comparison
- **OI Derivatives**: Price-OI divergence, funding rates, long/short ratios

---

## 📈 Performance

- Detection Latency: < 100ms per data point
- Agent Parallelization: All 5 agents run simultaneously
- WebSocket Updates: Real-time with <1s delay
- Dashboard Rendering: 60 FPS animations

---

## 🛠️ Development

```bash
# Backend with auto-reload
python run_system.py

# Frontend with hot reload
cd frontend && npm run dev

# Build for production
cd frontend && npm run build
```

---

## 📝 Current Capabilities

### ✅ Fully Implemented
- Multi-agent anomaly detection (5 agents)
- Real-time data collection from 4 sources
- LLM narrative generation (Claude + OpenAI fallback)
- Knowledge graph with relationship tracking
- Interactive dashboard with live updates
- OI derivatives analysis
- WebSocket real-time communication
- Color-coded visual indicators
- System architecture explainer

### 🚧 Future Enhancements
- Machine learning model training
- Historical anomaly replay
- Alert notifications
- Custom dashboard layouts
- Export/reporting features
- Cloud deployment

---

## 🐛 Troubleshooting

### Backend Won't Start
```bash
pip install -r requirements.txt
# Check port 8000 is available
```

### Frontend Won't Start
```bash
cd frontend
rm -rf node_modules
npm install
```

### LLM Not Working
- Verify API keys in `.env`
- Check logs for fallback messages
- System will use templates if LLMs unavailable

---

## 📄 License

MIT License

---

**Built with ❤️ for intelligent anomaly detection**
