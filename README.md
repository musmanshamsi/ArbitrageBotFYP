# AI Arbitrage Bot 🚀

An advanced cryptocurrency arbitrage bot that leverages deep learning (GRU) and real-time market data to identify and execute profitable arbitrage opportunities across exchanges.

## 🌟 Key Features

- **Real-time Monitoring**: Fetches live prices from **Binance** and **Bybit** using WebSockets.
- **AI-Powered Predictions**: Uses a **GRU (Gated Recurrent Unit)** neural network to predict future price spreads and confirm trade signals.
- **Dashboard UI**: Modern **React (Vite)** frontend for monitoring market data, AI spreads, and trade execution.
- **Automated Execution**: Connects to exchange Testnets via **CCXT** to simulate real-world trading without risk.
- **Adaptive Spread Buffer**: Sophisticated logic to calculate and maintain spread buffers for risk management.

## 🏗️ Project Structure

- `main_api.py`: FastAPI server handling WebSocket connections and core bot logic.
- `model/`: Machine learning training scripts and datasets.
- `frontend/`: The React web application for monitoring and visualization.
- `core/`: Modular engines for arbitrage, exchanges, risk, and server management.
- `execution/`: Trader logic for order placement.
- `llm/`: Integration with AI agents for enhanced decision-making.

## 🛠️ Tech Stack

- **Backend**: FastAPI (Python)
- **Frontend**: React (Vite, CSS Modules)
- **AI/ML**: TensorFlow (Keras), Scikit-learn
- **API**: CCXT (Exchange Connectivity)
- **Storage**: SQLite (for trade history)

## 🚀 Getting Started

### 1. Environment Setup

```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure API Keys

Create a `.env` file in the root directory for your exchange credentials:

```env
BINANCE_TESTNET_API_KEY=your_key
BINANCE_TESTNET_SECRET=your_secret
BYBIT_TESTNET_API_KEY=your_key
BYBIT_TESTNET_SECRET=your_secret
```

### 3. Running the Project

**Start the Backend:**
```powershell
python main_api.py
```

**Start the Frontend:**
```powershell
cd frontend
npm install
npm run dev
```

### 4. Training the AI Model

To retrain the GRU model using the provided datasets:
```powershell
python model/train_model.py
```

---
*Developed for Cross-Exchange Arbitrage Optimization.*
