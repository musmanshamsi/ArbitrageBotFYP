# ArbPro - AI Arbitrage Bot 🚀
**v7.0 Stable - Asynchronous Background Intelligence Edition**

An enterprise-grade, AI-powered cryptocurrency arbitrage system designed for the **BTC/USDT** pair. Featuring a **Continuous Background Engine**, a **Manual Safety Valve**, and a high-fidelity glassmorphism dashboard.

## 📡 v7.0 Performance Architecture
*   **⛓️ Non-Blocking Async Logic**: I/O-bound tasks (LLM Analysis & CCXT API calls) are offloaded to background threads. The dashboard remains 100% fluid and responsive at all times.
*   **🤖 Continuous Background Engine**: The arbitrage loop runs 24/7 independently of the browser. It detects, analyzes, and executes trades while the WebSocket operates as a stateless telemetry stream.
*   **🛡️ Manual Operator Approval**: For safety, the AI Agent ("Tier 1") analyzes opportunities and then waits for a **Human Operator** to approve the final execution via the Dashboard.
*   **⚠️ Simulation Fallback**: Built-in "Bybit Fallback" mode allows for full system demonstration even if the exchange API is geo-blocked or unreachable.

## 🌟 Key Features
*   **🧠 4-Tier LLM Multi-Agent System (Gemini 2.0 Flash)**:
    *   **Agent**: Real-time opportunity analysis & risk-adjusted decision making.
    *   **Analyst**: Broad market regime identification (Trending, Ranging, Volatile).
    *   **Advisor**: Batch-processed weekly strategy optimization from trade history.
    *   **ChatBot**: Context-aware Senior Quant Analyst for interactive strategy queries.
*   **📊 Next-Gen Dashboard**: Modular React interface with **Recharts** for real-time spread visualizers and market status monitoring.
*   **🗄️ DatabaseCore v7.0**: SQLite WAL-mode engine with full auto-migration support and LLM decision auditing.

## 🏗️ Project Structure
```text
├── main.py             # Single entry point (Unified Startup)
├── api.py              # FastAPI Engine & Background Arbitrage Loop
├── core/
│   ├── database.py     # SQLite Core & Schema Migrations
│   └── risk_engine.py   # Kelly Criterion & Circuit Breakers
├── execution/
│   └── trader.py       # CCXT API Layer (Binance/Bybit)
└── llm/                # Google Gemini v1.0+ SDK Modules
```

## 🚀 Quick Start (Portability Mode)

### 1. Environment Setup
```bash
# Initialize Virtual Environment
python -m venv .venv
.\.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Mac/Linux

# Install "Hardcore" Dependencies
pip install -r requirements.txt
```

### 2. Configure Credentials (.env)
Copy `.env.example` to `.env` and fill in your keys:
```env
GEMINI_API_KEY=your_key
BINANCE_TESTNET_API_KEY=your_key
BINANCE_TESTNET_SECRET=your_secret
BYBIT_TESTNET_API_KEY=your_key
BYBIT_TESTNET_SECRET=your_secret
JWT_SECRET_KEY=your_custom_secret
```

### 3. Launch System
**Unified Backend:** `python main.py`  
**React Dashboard:** `cd Frontend && npm run dev`

---
*Developed for FYP - Final Year Project: Cross-Exchange Arbitrage & AI Logic Core.*
