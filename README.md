# ArbPro - AI Arbitrage Bot 🚀
**v7.0 - Production-Ready with Centralized Configuration**

An advanced, AI-powered cryptocurrency arbitrage system designed to detect and exploit price discrepancies between **Binance** and **Bybit** on the **BTC/USDT** pair. Features professional-grade configuration management, dual-layer neural validation, and a modern glassmorphism dashboard with real-time market intelligence.

## ✨ Key Features

- **⚡ Real-Time Oracle Feeds**: Low-latency price fetching from Binance and Bybit via WebSocket connections
- **🧠 Dual-Layer AI Neural Engine**:
  - **GRU Predictor**: Gated Recurrent Unit network for high-accuracy price trend forecasts
  - **LLM Validation**: Integrated Gemini 2.0 Flash / Groq (LLaMA 3.1) for real-time trade signal approval
- **📊 Professional Dashboard**: Modern React 18 interface with Recharts for real-time spread analysis
- **🛡️ Enterprise Security**: JWT authentication, AES-256 API key encryption, multi-environment support
- **⚙️ Centralized Configuration**: Professional config system with testnet/production environment switching
- **🎮 Dynamic Control**: Real-time threshold adjustment and comprehensive state monitoring

## 🚀 Quick Start

### Prerequisites
- **Python 3.10 or 3.11** (required - not 3.14)
- Node.js 16+ (for frontend)
- Git

### 1️⃣ Clone & Setup

```powershell
# Navigate to project directory
cd E:\AI_Arbitrage_Bot

# Install Python dependencies (using Python 3.10)
py -3.10 -m pip install -r requirements.txt
```

### 2️⃣ Configure Environment

```powershell
# Copy environment template
Copy-Item .env.example .env

# Edit .env with your credentials
```

**Configure your `.env` file:**
```env
# Environment: testnet or production
ENVIRONMENT=testnet

# Binance Credentials
BINANCE_TESTNET_API_KEY=your_testnet_key
BINANCE_TESTNET_SECRET=your_testnet_secret
BINANCE_PROD_API_KEY=your_prod_key
BINANCE_PROD_SECRET=your_prod_secret

# Bybit Credentials
BYBIT_TESTNET_API_KEY=your_testnet_key
BYBIT_TESTNET_SECRET=your_testnet_secret
BYBIT_PROD_API_KEY=your_prod_key
BYBIT_PROD_SECRET=your_prod_secret

# AI/LLM Services
GEMINI_API_KEY=your_gemini_key
GROQ_API_KEY=your_groq_key
OPENAI_API_KEY=your_openai_key

# System Settings
LOG_LEVEL=info
PROXY_URL=http://proxy.example.com:8080  # Optional
```

### 3️⃣ Launch Backend

```powershell
# Start the arbitrage bot (run from project root)
py -3.10 main.py
```

Expected output:
```
========================================
🚀 ARBPRO CORE SYSTEM STARTING
========================================
📡 Initializing API Gateway...
🤖 Starting Arbitrage Engine...
✅ System initialized successfully
```

The backend will be available at: `http://127.0.0.1:8000`

### 4️⃣ Launch Frontend (Optional)

```powershell
# In a new terminal
cd Frontend
npm install
npm run dev
```

Access the dashboard at: `http://localhost:5173`

## 📚 Documentation

Comprehensive guides are available for different use cases:

| Document | Purpose |
|----------|---------|
| [QUICK_START.md](QUICK_START.md) | 5-minute setup guide with examples |
| [CONFIG_SETUP_GUIDE.md](CONFIG_SETUP_GUIDE.md) | Detailed configuration walkthrough |
| [TROUBLESHOOTING.md](TROUBLESHOOTING.md) | Common issues and solutions |
| [API_REFERENCE.md](API_REFERENCE.md) | REST API and WebSocket endpoint documentation |
| [VISUAL_GUIDE.md](VISUAL_GUIDE.md) | Feature overview with screenshots |

## 🏗️ Project Architecture

### Backend Structure
```
├── api.py                    # FastAPI application & WebSocket server
├── main.py                   # System entry point
├── config.py                 # Centralized configuration management
├── predictor.py              # GRU price prediction model
├── core/
│   ├── arbitrage_engine.py   # Core arbitrage logic
│   ├── exchange_engine.py    # CCXT exchange wrapper
│   ├── risk_engine.py        # Risk management & validation
│   ├── database.py           # Database operations
│   └── server.py             # Background server process
├── execution/
│   └── trader.py             # Order execution engine
├── llm/
│   ├── ai_agent.py           # AI decision making
│   ├── chatbot.py            # User interaction
│   └── market_analyst.py     # Market sentiment analysis
└── model/
    ├── gru_model.py          # Neural network definition
    ├── train_model.py        # Training pipeline
    └── data/                 # Historical price data (CSVs)
```

### Frontend Structure
```
Frontend/
├── src/
│   ├── App.tsx               # Main application
│   ├── pages/                # Page components (Dashboard, Login, Blog)
│   ├── components/           # Reusable UI components
│   │   ├── dashboard/        # Dashboard-specific components
│   │   └── ui/               # Base UI elements
│   ├── hooks/                # Custom React hooks
│   └── lib/                  # Utilities
└── public/                   # Static assets
```

## 🛠️ Technology Stack

| Layer | Technology |
|-------|------------|
| **Backend** | Python 3.10, FastAPI, Uvicorn, SQLite |
| **Async** | Asyncio, CCXT (async), WebSockets |
| **Security** | JWT (python-jose), bcrypt, AES-256 |
| **AI/ML** | PyTorch, NumPy, Pandas, Scikit-learn |
| **Frontend** | React 18, TypeScript, Vite, Tailwind CSS |
| **UI Components** | Shadcn/UI, Recharts, Lucide Icons |

## 🔧 Advanced Configuration

### Switching Between Testnet & Production

```powershell
# Testnet (default, safe for testing)
$env:ENVIRONMENT = "testnet"
py -3.10 main.py

# Production (real trading)
$env:ENVIRONMENT = "production"
py -3.10 main.py
```

### Using a Proxy

```env
PROXY_URL=http://proxy.example.com:8080
PROXY_USERNAME=user
PROXY_PASSWORD=pass
```

### Custom Arbitrage Thresholds

Edit thresholds in the UI or via API:
```bash
# Minimum spread percentage to trigger trades (default: 0.5%)
ARBITRAGE_THRESHOLD=0.75
```

## 📊 AI Model Training

To train or refine the GRU model:

```powershell
# Train GRU model on historical data
py -3.10 train_gru.py
```

This will:
- Load historical price data from `model/data/`
- Train GRU network on OHLCV data
- Validate against test set
- Save model to `gru_model.pth`

## 🧪 Testing & Verification

Run verification tests:

```powershell
# Verify system configuration
py -3.10 verify_system.py

# Test API connectivity
py -3.10 test_api.py

# Test exchange connections
py -3.10 test_conn.py

# Test AI predictions
py -3.10 test_ai.py
```

## ⚠️ Important Notes

### Python Version
- ✅ **Recommended**: Python 3.10 or 3.11
- ❌ **Not Supported**: Python 3.14 (incompatibilities with certifi, requests packages)

### Virtual Environment
For clean environment setup:
```powershell
# Using existing .venv (uses system Python, may have issues)
.\.venv\Scripts\activate

# Recommended: Use Python 3.10 directly
py -3.10 -m pip install -r requirements.txt
py -3.10 main.py
```

### Common Issues

**Problem**: `ModuleNotFoundError: No module named 'ccxt'`
- **Solution**: `py -3.10 -m pip install ccxt`

**Problem**: Port 8000 already in use
- **Solution**: Change port in `main.py` or kill existing process: `netstat -ano | findstr :8000`

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for more help.

## 📈 System Architecture Overview

```
User Dashboard (React)
        ↓
    API Server (FastAPI)
        ↓
Arbitrage Engine ← → Exchange APIs (Binance/Bybit)
        ↓
    AI/ML Pipeline
    (GRU + LLM)
        ↓
Risk Engine ← → Database (SQLite)
        ↓
Order Execution (CCXT)
```

## 🔒 Security

- **API Keys**: AES-256 encryption at rest
- **Authentication**: JWT tokens with configurable expiry
- **Network**: Optional proxy support for compliance
- **Audit**: All trades logged to SQLite database
- **Isolation**: Testnet/production environments completely separated

## 📞 Support

For issues or questions:
1. Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
2. Review [CONFIG_SETUP_GUIDE.md](CONFIG_SETUP_GUIDE.md)
3. See [API_REFERENCE.md](API_REFERENCE.md) for endpoint details

## 📄 License

This project is provided as-is for educational and research purposes.

---

**Version**: 7.0 | **Last Updated**: April 2026  
*Professional cryptocurrency arbitrage system with AI-powered decision making*

