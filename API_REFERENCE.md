# 📡 EXCHANGE API REFERENCE
## AI Arbitrage Bot v7.0 | Official API URLs & Endpoints

---

## **🟡 BINANCE - TESTNET & PRODUCTION**

### **Testnet URLs**
```
REST API Base: https://testnet.binance.vision
WebSocket: wss://stream.testnet.binance.vision:9443

Common Endpoints:
- GET /api/v3/ping                  → Connectivity test
- GET /api/v3/time                  → Server time
- GET /api/v3/exchangeInfo          → Market info
- GET /api/v3/ticker/price          → Current prices
- GET /api/v3/account               → Account balance
- POST /api/v3/order                → Create order
- GET /api/v3/order                 → Get order status
- DELETE /api/v3/order              → Cancel order
```

### **Production URLs**
```
REST API Base: https://api.binance.com
WebSocket: wss://stream.binance.com:9443

Endpoints: (Same as testnet)
```

### **Setup Instructions**
```
1. Visit: https://testnet.binance.vision
2. Create account or login
3. Account → API Management
4. Create API Key
5. Permissions:
   ✅ Spot Trading Read (not needed for reads)
   ✅ Spot Trading (for orders)
   ✅ IP Whitelist (optionally your IP)
6. Copy API Key & Secret
```

### **Important Notes**
- ✅ Supports both margin and spot
- ✅ Highest liquidity
- ✅ Fastest API
- ⚠️  Signature expires after 1 hour (set `recvWindow=10000`)
- ⚠️  System time must be within 1000ms of exchange

---

## **⚫ BYBIT - TESTNET & PRODUCTION**

### **Testnet URLs**
```
REST API Base: https://api-testnet.bybit.com
WebSocket: wss://stream-testnet.bybit.com/v5/public/spot

Common Endpoints (V5 API):
- GET /v5/market/time              → Server time
- GET /v5/market/instruments       → Market info
- GET /v5/market/tickers           → Ticker data
- GET /v5/asset/transfer-info      → Transfer info
- GET /v5/account/wallet/balance   → Account balance
- POST /v5/order/create            → Create order
- GET /v5/order/realtime           → Get order status
- POST /v5/order/cancel            → Cancel order

Note: Bybit recently deprecated /v5/asset/coin/query-info
Use /v5/market/instruments instead!
```

### **Production URLs**
```
REST API Base: https://api.bybit.com
WebSocket: wss://stream.bybit.com/v5/public/spot

Endpoints: (Same as testnet)
```

### **Setup Instructions**
```
1. Visit: https://testnet.bybit.com
2. Create account if needed
3. Account → API Settings
4. Create API Key
5. Permissions:
   ✅ Spot Trading
   ✅ Read (balances)
   ⚠️  IP Whitelist: Your IP (recommended)
6. Copy API Key & Secret
```

### **Important Notes**
- ⚠️  May require proxy if ISP blocks (common in some regions)
- ✅ Good liquidity, second exchange for arbitrage
- ✅ Supports multiple trading pairs
- ⚠️  V5 API recently changed - old V4 code will break
- ⚠️  System time must be within 5000ms of exchange

---

## **🔵 KRAKEN (Future Support)**

### **Testnet URLs**
```
(Kraken does not offer sandbox testnet)
Use production with small amounts for testing
```

### **Production URLs**
```
REST API Base: https://api.kraken.com
WebSocket: wss://ws.kraken.com/
```

### **Setup Instructions**
```
1. Visit: https://www.kraken.com
2. Login/Create account
3. Settings → API
4. Create New Key
5. Permissions:
   ✅ Query Funds
   ✅ Query Open Orders & Trades
   ✅ Query Closed Orders & Trades
   ✅ Create & Modify Orders
   ✅ Cancel/Close Orders
6. Copy API Key & Private Key
```

---

## **🟢 COINBASE (Future Support)**

### **Testnet URLs**
```
REST API Base: https://api-sandbox.exchange.coinbase.com
WebSocket: wss://ws-sandbox.exchange.coinbase.com
```

### **Production URLs**
```
REST API Base: https://api.exchange.coinbase.com
WebSocket: wss://ws-feed.pro.coinbase.com
```

### **Setup Instructions**
```
1. Visit: https://www.coinbase.com/advanced
2. Login/Create account
3. Settings → API
4. Create New API Key
5. Permissions:
   ✅ View Account Details
   ✅ Manage Account Orders
   ✅ Transfer Funds
6. Copy API Key & Passphrase
```

---

## **QUICK COMPARISON TABLE**

| Feature | Binance | Bybit | Kraken | Coinbase |
|---------|---------|-------|--------|----------|
| **Testnet** | ✅ Yes | ✅ Yes | ❌ No | ✅ Yes |
| **Speed** | ⚡ Fastest | 🔹 Fast | 🔹 Medium | 🔹 Medium |
| **Liquidity** | 💰 Highest | 💰 High | 💰 High | 💰 Medium |
| **API Latency** | <50ms | <100ms | <200ms | <200ms |
| **Requires Proxy** | ❌ No | ⚠️  Maybe | ❌ No | ❌ No |
| **Sandbox** | ✅ Full | ✅ Full | ❌ None | ✅ Full |

---

## **CORRECT URL CONFIGURATIONS**

### **✅ CORRECT (Used in config.py)**

```python
# Testnet
BINANCE_TESTNET = "https://testnet.binance.vision"
BYBIT_TESTNET = "https://api-testnet.bybit.com"

# Production  
BINANCE_PRODUCTION = "https://api.binance.com"
BYBIT_PRODUCTION = "https://api.bybit.com"
```

### **❌ INCORRECT (Common Mistakes)**

```python
# Wrong spellings
BINANCE_TESTNET = "https://testnet.binancce.vision"  # ❌ Double 'c'
BINANCE_TESTNET = "https://testnet.binance.vision/"  # ❌ Trailing slash
BYBIT_TESTNET = "https://api-testnet.bybit.com/v5/asset/cooin"  # ❌ Wrong path

# Missing or extra paths
BINANCE = "https://api.binance.com/v3"  # ❌ CCXT adds this automatically
BYBIT = "https://api.bybit.com/v5"      # ❌ CCXT adds this automatically
```

---

## **API RATE LIMITS**

### **Binance**
- **Default**: 1200 requests/min per IP
- **Weighted**: Some endpoints count more
- **Headers**: Check `X-MBX-USED-WEIGHT` response header

### **Bybit**
- **Default**: 100 requests/sec per account
- **Method**: Rate limit by user ID, not IP
- **Bursts**: Allowed up to 200 requests/sec for 10 seconds

### **Kraken**
- **Default**: Tiered based on API tier
- **Method**: Sliding window algorithm
- **Standard**: 15 requests per 15 seconds

---

## **COMMON ENDPOINT MAPPINGS** (via CCXT)

```python
# Price Fetching
exchange.fetch_ticker('BTC/USDT')  # Current price

# Balances
exchange.fetch_balance()            # Account balance

# Order Management
exchange.create_order(symbol, type, side, amount, price)
exchange.fetch_order(order_id, symbol)
exchange.cancel_order(order_id, symbol)
exchange.fetch_closed_orders(symbol)

# Market Data
exchange.fetch_order_book(symbol)   # Bid/Ask data
exchange.fetch_trades(symbol)       # Recent trades
```

---

## **AUTHENTICATION**

### **All Exchanges Use HMAC-SHA256**

```python
import hmac
import hashlib

# Signature generation (simplified)
signature = hmac.new(
    secret.encode(),
    message.encode(),
    hashlib.sha256
).hexdigest()
```

### **Nonce Handling**

| Exchange | Nonce Type | Freshness Requirement |
|----------|------------|-----------------------|
| Binance | Timestamp (ms) | ±1000ms from server |
| Bybit | Timestamp (ms) | ±5000ms from server |
| Kraken | Integer | Strictly increasing |
| Coinbase | ISO 8601 timestamp | ±30s from server |

---

## **WEBHOOK & STREAM ENDPOINTS**

### **For Real-Time Data (WebSocket)**

**Binance Spot:**
```
wss://stream.binance.com:9443/ws/btcusdt@ticker
wss://stream.binance.com:9443/ws/btcusdt@trade
wss://stream.binance.com:9443/ws/btcusdt@depth
```

**Bybit Spot (V5):**
```
wss://stream.bybit.com/v5/public/spot
  Book trades: channel="publicTrade", symbol="BTCUSDT"
  Ticker: channel="tickers", symbol="BTCUSDT"
```

---

## **DEBUGGING: VALIDATE YOUR URLs**

```bash
# Test Binance testnet
curl https://testnet.binance.vision/api/v3/ping

# Test Bybit testnet
curl https://api-testnet.bybit.com/v5/market/time

# Test Kraken production
curl https://api.kraken.com/0/public/Time

# Test Coinbase sandbox
curl https://api-sandbox.exchange.coinbase.com/products
```

---

## **CONFIGURATION IN PROJECT**

### **How to Use Different Exchanges**

```python
from config import ExchangeConfig

# Automatically uses correct URL based on ENVIRONMENT
config = ExchangeConfig.get_exchange_config('binance')
config = ExchangeConfig.get_exchange_config('bybit')
config = ExchangeConfig.get_exchange_config('kraken')
config = ExchangeConfig.get_exchange_config('coinbase')
```

### **To Add New Exchange**

1. Add to `.env`:
```env
NEWEXCHANGE_TESTNET_API_KEY=key
NEWEXCHANGE_TESTNET_SECRET=secret
```

2. Add to `config.py`:
```python
NEWEXCHANGE_API_URL = "https://api.newexchange.com"
```

3. Use in code:
```python
config = ExchangeConfig.get_exchange_config('newexchange')
```

---

## **MIGRATION GUIDE: OLD → NEW URLS**

If you had old configurations:

| Old | New | Reason |
|-----|-----|--------|
| `binance.com` | `api.binance.com` | Production correct URL |
| `testnet.binance.us` | `testnet.binance.vision` | US testnet deprecated |
| `api.bybit.com/v3` | `api.bybit.com/v5` | V3 API deprecated |
| `api-testnet.bybit.com:443` | `https://api-testnet.bybit.com` | Explicit HTTPS |

---

**✅ All URLs are correctly configured in `config.py`**  
**✅ No manual URL editing needed**  
**✅ Environment selection is automatic**

Use `python verify_system.py` to test your configuration!
