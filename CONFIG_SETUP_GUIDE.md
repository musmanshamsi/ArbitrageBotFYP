# 🚀 PROFESSIONAL API SETUP GUIDE - TESTNET & PRODUCTION
## AI Arbitrage Bot Configuration (v7.0)

---

## **PROBLEM ANALYSIS**

### Current Issues:
```
❌ Market Fetch Error: binance GET https://testnet.binancce.vision/api/v3/exchangeInfo
❌ Market Fetch Error: bybit GET https://api-testnet.bybit.com/v5/asset/cooin/query-info
```

**Root Causes:**
1. **URL Typo in Binance**: `testnet.binancce.vision` → should be `testnet.binance.vision`
2. **URL Issue in Bybit**: Endpoint path includes `cooin` → should be `coin`
3. **Hardcoded Testnet Mode**: Cannot easily switch between testnet/production
4. **No Configuration Management**: Environment variables not properly structured
5. **Proxy Issues**: Bybit proxy fallback not robust enough

---

## **STEP 1: CREATE PROFESSIONAL ENVIRONMENT CONFIGURATION**

### 1.1 Create `.env` file (Root Directory)

```env
# ========================================
# EXCHANGE ENVIRONMENT SELECTION
# ========================================
ENVIRONMENT=testnet  # Options: testnet, production

# ========================================
# BINANCE API CREDENTIALS
# ========================================
# TESTNET
BINANCE_TESTNET_API_KEY=your_testnet_api_key
BINANCE_TESTNET_SECRET=your_testnet_secret

# PRODUCTION
BINANCE_PRODUCTION_API_KEY=your_production_api_key
BINANCE_PRODUCTION_SECRET=your_production_secret

# ========================================
# BYBIT API CREDENTIALS
# ========================================
# TESTNET
BYBIT_TESTNET_API_KEY=your_testnet_api_key
BYBIT_TESTNET_SECRET=your_testnet_secret

# PRODUCTION
BYBIT_PRODUCTION_API_KEY=your_production_api_key
BYBIT_PRODUCTION_SECRET=your_production_secret

# ========================================
# PROXY CONFIGURATION (Optional - for ISP blocks)
# ========================================
HTTP_PROXY=
HTTPS_PROXY=

# ========================================
# AI & JWT CONFIGURATION
# ========================================
GEMINI_API_KEY=your_gemini_key
GROQ_API_KEY=your_groq_key
JWT_SECRET_KEY=your_random_secret_key

# ========================================
# ADVANCED OPTIONS
# ========================================
API_REQUEST_TIMEOUT=10  # seconds
API_RATE_LIMIT_ENABLED=true
ENABLE_PROXY_FALLBACK=true
```

### 1.2 Create `config.py` (Config Management)

Location: `e:\AI_Arbitrage_Bot\config.py`

```python
import os
from dotenv import load_dotenv
from enum import Enum

load_dotenv()

class Environment(str, Enum):
    TESTNET = "testnet"
    PRODUCTION = "production"

class ExchangeConfig:
    """Centralized exchange configuration"""
    
    # Current environment
    ENVIRONMENT = os.getenv("ENVIRONMENT", "testnet").lower()
    
    # Validate environment
    if ENVIRONMENT not in [e.value for e in Environment]:
        raise ValueError(f"Invalid ENVIRONMENT: {ENVIRONMENT}. Use 'testnet' or 'production'")
    
    # ============ BINANCE CONFIGURATION ============
    if ENVIRONMENT == "testnet":
        BINANCE_API_URL = "https://testnet.binance.vision"  # ✅ FIXED TYPO
        BINANCE_API_KEY = os.getenv("BINANCE_TESTNET_API_KEY", "")
        BINANCE_SECRET = os.getenv("BINANCE_TESTNET_SECRET", "")
    else:
        BINANCE_API_URL = "https://api.binance.com"
        BINANCE_API_KEY = os.getenv("BINANCE_PRODUCTION_API_KEY", "")
        BINANCE_SECRET = os.getenv("BINANCE_PRODUCTION_SECRET", "")
    
    # ============ BYBIT CONFIGURATION ============
    if ENVIRONMENT == "testnet":
        BYBIT_API_URL = "https://api-testnet.bybit.com"  # ✅ CORRECT TESTNET URL
        BYBIT_API_KEY = os.getenv("BYBIT_TESTNET_API_KEY", "")
        BYBIT_SECRET = os.getenv("BYBIT_TESTNET_SECRET", "")
    else:
        BYBIT_API_URL = "https://api.bybit.com"
        BYBIT_API_KEY = os.getenv("BYBIT_PRODUCTION_API_KEY", "")
        BYBIT_SECRET = os.getenv("BYBIT_PRODUCTION_SECRET", "")
    
    # ============ PROXY CONFIGURATION ============
    HTTP_PROXY = os.getenv("HTTP_PROXY", "")
    HTTPS_PROXY = os.getenv("HTTPS_PROXY", "")
    ENABLE_PROXY_FALLBACK = os.getenv("ENABLE_PROXY_FALLBACK", "true").lower() == "true"
    
    # ============ API SETTINGS ============
    API_REQUEST_TIMEOUT = int(os.getenv("API_REQUEST_TIMEOUT", "10"))
    API_RATE_LIMIT_ENABLED = os.getenv("API_RATE_LIMIT_ENABLED", "true").lower() == "true"
    
    # ============ AI & SECURITY ============
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "")
    
    @classmethod
    def validate(cls):
        """Validate all required credentials are set"""
        errors = []
        
        if not cls.BINANCE_API_KEY:
            errors.append(f"❌ BINANCE_{cls.ENVIRONMENT.upper()}_API_KEY not set in .env")
        if not cls.BINANCE_SECRET:
            errors.append(f"❌ BINANCE_{cls.ENVIRONMENT.upper()}_SECRET not set in .env")
        if not cls.BYBIT_API_KEY:
            errors.append(f"❌ BYBIT_{cls.ENVIRONMENT.upper()}_API_KEY not set in .env")
        if not cls.BYBIT_SECRET:
            errors.append(f"❌ BYBIT_{cls.ENVIRONMENT.upper()}_SECRET not set in .env")
        
        if errors:
            print("\n⚠️ CONFIGURATION ERRORS:")
            for error in errors:
                print(f"  {error}")
            print("\nPlease update your .env file and restart.\n")
            return False
        
        return True
    
    @classmethod
    def print_config(cls):
        """Print current configuration (sanitized)"""
        print(f"\n📋 CURRENT CONFIGURATION")
        print(f"   Environment: {cls.ENVIRONMENT.upper()}")
        print(f"   Binance URL: {cls.BINANCE_API_URL}")
        print(f"   Bybit URL: {cls.BYBIT_API_URL}")
        print(f"   API Timeout: {cls.API_REQUEST_TIMEOUT}s")
        print(f"   Proxy Fallback: {'✅ Enabled' if cls.ENABLE_PROXY_FALLBACK else '❌ Disabled'}\n")

# Initialize and validate on import
if __name__ != "__main__":
    ExchangeConfig.validate()
```

---

## **STEP 2: FIX EXCHANGE ENGINE WITH PROPER URLs**

### 2.1 Update `core/exchange_engine.py`

```python
import ccxt
from config import ExchangeConfig

class ExchangeEngine:
    def __init__(self, exchange_name="binance"):
        """Initialize exchange with proper configuration"""
        
        if exchange_name.lower() == "binance":
            self.exchange = ccxt.binance({
                "apiKey": ExchangeConfig.BINANCE_API_KEY,
                "secret": ExchangeConfig.BINANCE_SECRET,
                "urls": {
                    "api": ExchangeConfig.BINANCE_API_URL  # ✅ Use configured URL
                },
                "enableRateLimit": ExchangeConfig.API_RATE_LIMIT_ENABLED,
                "proxies": {},  # Force empty proxies for Binance
                "options": {
                    "adjustForTimeDifference": True,
                    "recvWindow": 10000
                }
            })
            if ExchangeConfig.ENVIRONMENT == "testnet":
                self.exchange.set_sandbox_mode(True)
                
        elif exchange_name.lower() == "bybit":
            bybit_config = {
                "apiKey": ExchangeConfig.BYBIT_API_KEY,
                "secret": ExchangeConfig.BYBIT_SECRET,
                "urls": {
                    "api": ExchangeConfig.BYBIT_API_URL  # ✅ Use configured URL
                },
                "enableRateLimit": ExchangeConfig.API_RATE_LIMIT_ENABLED,
                "options": {
                    "adjustForTimeDifference": True
                }
            }
            
            # Add proxy if available
            if ExchangeConfig.HTTPS_PROXY or ExchangeConfig.HTTP_PROXY:
                bybit_config["proxies"] = {
                    "http": ExchangeConfig.HTTP_PROXY or ExchangeConfig.HTTPS_PROXY,
                    "https": ExchangeConfig.HTTPS_PROXY or ExchangeConfig.HTTP_PROXY,
                }
            
            self.exchange = ccxt.bybit(bybit_config)
            if ExchangeConfig.ENVIRONMENT == "testnet":
                self.exchange.set_sandbox_mode(True)
        
        self.name = exchange_name

    def load_markets(self):
        """Load trading pairs from exchange"""
        return self.exchange.load_markets()

    def fetch_ticker(self, symbol):
        """Fetch ticker with error handling"""
        try:
            return self.exchange.fetch_ticker(symbol)
        except Exception as e:
            print(f"❌ {self.name.upper()} fetch_ticker error: {e}")
            raise

    def fetch_order_book(self, symbol):
        """Fetch order book with error handling"""
        try:
            return self.exchange.fetch_order_book(symbol)
        except Exception as e:
            print(f"❌ {self.name.upper()} fetch_order_book error: {e}")
            raise

    def create_order(self, symbol, order_type, side, amount, price=None):
        """Create order with error handling"""
        try:
            return self.exchange.create_order(symbol, order_type, side, amount, price)
        except Exception as e:
            print(f"❌ {self.name.upper()} create_order error: {e}")
            raise
```

---

## **STEP 3: UPDATE TRADER WITH PROPER CONFIGURATION**

### 3.1 Update `execution/trader.py`

Key changes at the top of the file:

```python
import os
import ccxt.async_support as ccxt
import aiohttp
import random
from dotenv import load_dotenv
from config import ExchangeConfig  # ✅ ADD THIS

load_dotenv()

class TradeExecutor:
    def __init__(self, testnet=None):
        """
        Initialize TradeExecutor with automatic environment detection
        testnet (bool, optional): If None, uses ENVIRONMENT variable
        """
        # Use config environment if not explicitly specified
        self._testnet = testnet if testnet is not None else (ExchangeConfig.ENVIRONMENT == "testnet")
        
        # Initialize Binance
        self.binance = ccxt.binance({
            'apiKey': ExchangeConfig.BINANCE_API_KEY,
            'secret': ExchangeConfig.BINANCE_SECRET,
            'enableRateLimit': ExchangeConfig.API_RATE_LIMIT_ENABLED,
            'proxies': {},  # Force no proxy for Binance
            'options': {
                'adjustForTimeDifference': True,
                'recvWindow': 10000
            }
        })
        
        # Initialize Bybit with proxy support
        bybit_opts = {
            'apiKey': ExchangeConfig.BYBIT_API_KEY,
            'secret': ExchangeConfig.BYBIT_SECRET,
            'enableRateLimit': ExchangeConfig.API_RATE_LIMIT_ENABLED,
        }
        
        # Add proxy if configured
        if ExchangeConfig.HTTPS_PROXY or ExchangeConfig.HTTP_PROXY:
            bybit_opts['proxies'] = {
                'http': ExchangeConfig.HTTP_PROXY or ExchangeConfig.HTTPS_PROXY,
                'https': ExchangeConfig.HTTPS_PROXY or ExchangeConfig.HTTP_PROXY,
            }
        
        self.bybit = ccxt.bybit(bybit_opts)
        
        # Set sandbox mode based on environment
        if self._testnet:
            self.binance.set_sandbox_mode(True)
            self.bybit.set_sandbox_mode(True)
            print(f"🧪 TESTNET MODE ENABLED")
        else:
            print(f"🔴 PRODUCTION MODE ENABLED - REAL MONEY")
        
        print(f"📍 Exchange URLs:")
        print(f"   Binance: {ExchangeConfig.BINANCE_API_URL}")
        print(f"   Bybit: {ExchangeConfig.BYBIT_API_URL}\n")
```

---

## **STEP 4: UPDATE API SERVER**

### 4.1 Update `api.py` initialization

Replace the TradeExecutor initialization:

```python
# BEFORE:
trader = TradeExecutor(
    binance_api=os.getenv("BINANCE_TESTNET_API_KEY"),
    binance_secret=os.getenv("BINANCE_TESTNET_SECRET"),
    bybit_api=os.getenv("BYBIT_TESTNET_API_KEY"),
    bybit_secret=os.getenv("BYBIT_TESTNET_SECRET"),
    testnet=True
)

# AFTER:
from config import ExchangeConfig
ExchangeConfig.validate()  # Validate credentials on startup
TradeExecutor = __import__('execution.trader', fromlist=['TradeExecutor']).TradeExecutor
trader = TradeExecutor()  # Uses config automatically
ExchangeConfig.print_config()
```

---

## **STEP 5: MIGRATION CHECKLIST**

### Testnet Setup:
```
✅ Step 1: Create .env file with ENVIRONMENT=testnet
✅ Step 2: Add testnet API credentials to .env
✅ Step 3: Create config.py in root directory
✅ Step 4: Update core/exchange_engine.py
✅ Step 5: Update execution/trader.py
✅ Step 6: Update api.py to use config
✅ Step 7: Test connection: python verify_system.py
```

### Production Transition:
```
1. Change ENVIRONMENT to "production" in .env
2. Add production API keys (BINANCE_PRODUCTION_API_KEY, etc)
3. Run verification: python verify_system.py
4. Monitor logs for 30 min before full deployment
5. Set up alerts for unexpected API errors
6. Keep testnet credentials in .env as backup
```

---

## **STEP 6: TESTING & VERIFICATION**

### 6.1 Create improved `verify_system.py`

```python
import os
import asyncio
import torch
import numpy as np
from dotenv import load_dotenv
import ccxt.async_support as ccxt
from config import ExchangeConfig
from predictor import Predictor

load_dotenv()

async def verify_exchanges():
    print("\n" + "="*60)
    print(f"🔍 EXCHANGE CONNECTIVITY CHECK - {ExchangeConfig.ENVIRONMENT.upper()}")
    print("="*60)
    
    # Check Binance
    print(f"\n📡 Testing Binance ({ExchangeConfig.BINANCE_API_URL})...")
    binance = ccxt.binance({
        'apiKey': ExchangeConfig.BINANCE_API_KEY,
        'secret': ExchangeConfig.BINANCE_SECRET,
        'proxies': {}
    })
    binance.set_sandbox_mode(ExchangeConfig.ENVIRONMENT == "testnet")
    
    try:
        ticker = await asyncio.wait_for(binance.fetch_ticker('BTC/USDT'), timeout=5)
        print(f"   ✅ Ticker: ${ticker['last']:.2f}")
        bal = await binance.fetch_balance()
        usdt = bal.get('USDT', {}).get('free', 0)
        print(f"   ✅ Balance: {usdt:.2f} USDT")
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
    finally:
        await binance.close()
    
    # Check Bybit
    print(f"\n📡 Testing Bybit ({ExchangeConfig.BYBIT_API_URL})...")
    bybit_opts = {
        'apiKey': ExchangeConfig.BYBIT_API_KEY,
        'secret': ExchangeConfig.BYBIT_SECRET,
    }
    if ExchangeConfig.HTTPS_PROXY:
        bybit_opts['proxies'] = {'https': ExchangeConfig.HTTPS_PROXY}
    
    bybit = ccxt.bybit(bybit_opts)
    bybit.set_sandbox_mode(ExchangeConfig.ENVIRONMENT == "testnet")
    
    try:
        ticker = await asyncio.wait_for(bybit.fetch_ticker('BTC/USDT'), timeout=5)
        print(f"   ✅ Ticker: ${ticker['last']:.2f}")
        bal = await bybit.fetch_balance()
        usdt = bal.get('USDT', {}).get('free', 0)
        print(f"   ✅ Balance: {usdt:.2f} USDT")
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
    finally:
        await bybit.close()
    
    print("\n" + "="*60)

async def main():
    ExchangeConfig.print_config()
    await verify_exchanges()

if __name__ == "__main__":
    asyncio.run(main())
```

---

## **STEP 7: COMMAND REFERENCE**

### Switch Environments:

**To Testnet:**
```bash
# Update .env
ENVIRONMENT=testnet

# Restart bot
python api.py
```

**To Production:**
```bash
# Update .env
ENVIRONMENT=production

# Verify credentials exist
python verify_system.py

# Restart bot
python api.py
```

### Verify Connection:
```bash
python verify_system.py
```

### Check Current Config:
```python
from config import ExchangeConfig
ExchangeConfig.print_config()
```

---

## **KEY IMPROVEMENTS SUMMARY**

| Issue | Before | After |
|-------|--------|-------|
| **URL Typo** | `testnet.binancce.vision` | `testnet.binance.vision` ✅ |
| **Environment Management** | Hardcoded testnet=True | Config-based, easily switchable |
| **Credentials Handling** | Scattered in multiple files | Centralized in config.py |
| **Production Support** | Not possible | Full production/testnet support |
| **Error Messages** | Generic CCXT errors | Descriptive, scoped errors |
| **Proxy Fallback** | Basic | Robust with config options |

---

## **TROUBLESHOOTING**

| Error | Solution |
|-------|----------|
| `ExchangeNotAvailable: binance GET` | Check BINANCE_TESTNET_API_KEY in .env |
| `Bybit network timeout` | Verify BYBIT_TESTNET_API_KEY has correct permissions |
| `Connection refused` | Check API URLs in config.py match current exchange endpoints |
| `Invalid signature` | Ensure secrets are correctly copied (no extra spaces) |

--- 

**✅ After implementing these steps, your bot will:**
- Work seamlessly on both testnet and production
- Have clear, repeatable API configuration
- Support easy transitions between environments
- Handle errors professionally
- Scale to support multiple exchanges
