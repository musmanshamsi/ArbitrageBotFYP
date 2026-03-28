# ArbPro - AI Arbitrage Bot 🚀
**v6.0 - Modular Components & Recharts Edition**

An advanced, AI-powered cryptocurrency arbitrage system designed to detect and exploit price discrepancies between **Binance** and **Bybit** on the **BTC/USDT** pair. Featuring a dual-layer neural validation engine and a high-fidelity glassmorphism dashboard.

## 🌟 Key Features

*   **⚡ Real-Time Oracle Feeds**: Low-latency price fetching from Binance and Bybit via WebSocket connections.
*   **🧠 Dual-Layer AI Neural Engine**:
    *   **GRU Predictor**: Gated Recurrent Unit network for high-accuracy price trend forecasts.
    *   **LLM Validation**: Integrated Gemini 2.0 Flash / Groq (LLaMA 3.1) for real-time trade signal approval and sentiment analysis.
*   **📊 High-Fidelity Dashboard**: Modern, interactive React interface utilizing **Recharts** for real-time spread analysis and market data visualization.
*   **🛡️ Secure Architecture**: Multi-tenant support with JWT-based authentication and AES-256 encryption for API key management.
*   **🎮 Dynamic Bot Control**: Real-time threshold adjustment via UI sliders and comprehensive state monitoring.

## 🏗️ Project Architecture

### [A] Backend (Python / FastAPI)
*   `api.py`: Central WebSocket engine and REST API server.
*   `predictor.py`: GRU-based prediction logic (Refactored for stability).
*   `core/`: Modular components for Arbitrage Strategy, Exchange Connectors, and Risk Management.
*   `execution/`: Professional trader logic with asynchronous order execution via **CCXT**.

### [B] Frontend (React / TypeScript)
*   `Frontend/`: Modular React 18 application built with Vite.
*   `Dashboard.tsx`: Main layout engine for component orchestration.
*   `components/dashboard/`: Reusable components including `Header`, `PortfolioMetrics`, `OracleFeeds`, and `ChartSection`.

## 🛠️ Tech Stack

*   **Backend**: Python 3.10+, FastAPI, Asyncio, CCXT, JWT, Pydantic, SQLite 3.
*   **Frontend**: React 18, TypeScript, Vite, Tailwind CSS, Shadcn/UI, Recharts, Lucide.
*   **AI/ML**: TensorFlow (Keras) for GRU, Google Generative AI (Gemini), Groq SDK.
*   **Design**: Modern Glassmorphism aesthetic with high-tech neon accents.

## 🚀 Getting Started

### 1. Environment Setup

```powershell
# Create and activate virtual environment
python -m venv .venv
.\.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Credentials

Create a `.env` file in the root directory:
```env
BINANCE_TESTNET_API_KEY=your_key
BINANCE_TESTNET_SECRET=your_secret
BYBIT_TESTNET_API_KEY=your_key
BYBIT_TESTNET_SECRET=your_secret
GEMINI_API_KEY=your_gemini_key
```

### 3. Launching the System

**Start the Backend:**
```powershell
python api.py
```

**Start the Frontend:**
```powershell
cd Frontend
npm install
npm run dev
```

## 📈 AI Model & Training

To train or refine the GRU model using the provided datasets:
```powershell
python train_gru.py
```

---
*Developed as a Final Year Project for Cross-Exchange Arbitrage Optimization.*

