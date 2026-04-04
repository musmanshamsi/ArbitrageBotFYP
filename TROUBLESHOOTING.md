# 🚨 API ERROR TROUBLESHOOTING GUIDE
## AI Arbitrage Bot v7.0

---

## **QUICK DIAGNOSIS FLOWCHART**

```
API Error Occurred?
    ↓
Is it "ExchangeNotAvailable"?
    ├─ YES → Check API URLs (see URL Issues section)
    └─ NO → Continue...
    
Is it timeout?
    ├─ YES → Check internet & increase timeout (see Timeout Issues)
    └─ NO → Continue...
    
Is it "Invalid signature"?
    ├─ YES → Check API keys (see Credential Issues)
    └─ NO → See specific error at bottom
```

---

## **COMMON ISSUES & SOLUTIONS**

### **1. URL-RELATED ERRORS** 🔗

**Error Messages:**
```
❌ ExchangeNotAvailable: binance GET https://testnet.binancce.vision/api/v3/exchangeInfo
❌ NetworkError: bybit GET https://api-testnet.bybit.com/v5/asset/cooin/query-info
```

**Root Cause:** Incorrect URL construction or typos

**Solution:**
```bash
# ✅ CORRECT URLs in .env:

ENVIRONMENT=testnet

# Testnet URLs
BINANCE_TESTNET_API_URL=https://testnet.binance.vision
BYBIT_TESTNET_API_URL=https://api-testnet.bybit.com

# Production URLs
BINANCE_PRODUCTION_API_URL=https://api.binance.com
BYBIT_PRODUCTION_API_URL=https://api.bybit.com
```

**Verification:**
```python
python verify_system.py
```

---

### **2. CREDENTIAL ISSUES** 🔑

**Error Messages:**
```
❌ AuthenticationError: 401 Unauthorized
❌ InvalidNonce: Signature has expired
❌ PermissionDenied: Account does not have permission
```

**Root Cause:** Wrong/expired API keys or no permission enabled

**Solution:**

**For Binance Testnet:**
1. Visit: https://testnet.binance.vision
2. Login with your account
3. API Management → Create API Key
4. Enable:
   - ✅ Spot Trading Access
   - ✅ Read-only (recommended initially)
   - ✅ Margin Trading (if needed)
5. Copy API Key and Secret
6. Add to `.env`:
```env
BINANCE_TESTNET_API_KEY=your_key_here
BINANCE_TESTNET_SECRET=your_secret_here
```

**For Bybit Testnet:**
1. Visit: https://testnet.bybit.com
2. Create account if needed
3. Account → API Settings
4. Create Key
5. Permissions:
   - ✅ Spot Trading
   - ✅ Account Read (for balances)
6. Add to `.env`:
```env
BYBIT_TESTNET_API_KEY=your_key_here
BYBIT_TESTNET_SECRET=your_secret_here
```

**Verify Credentials:**
```bash
python -c "
from config import ExchangeConfig
ExchangeConfig.print_config()
"
```

---

### **3. CONNECTION TIMEOUT ISSUES** ⏱️

**Error Messages:**
```
⚠️  Market Fetch Timeout (3.5s) on Binance
⚠️  Bybit Market Fetch Error: Connection timeout
```

**Root Cause:** Network latency, proxy issues, or ISP blocks

**Solution A: Increase Timeout**
```env
# In .env, increase timeout (default: 10s)
API_REQUEST_TIMEOUT=15
```

**Solution B: Enable Proxy (for Bybit)**
```env
# Try a public proxy
HTTPS_PROXY=http://proxy.example.com:8080
HTTP_PROXY=http://proxy.example.com:8080
ENABLE_PROXY_FALLBACK=true
```

**Solution C: Verify Connection**
```bash
# Test direct connectivity
python test_conn.py

# Test without proxy
python test_no_proxy.py
```

---

### **4. ENVIRONMENT SWITCHING ISSUES** 🔄

**Problem:** Bot still uses testnet after switching to production

**Solution:**
```env
# 1. Update .env
ENVIRONMENT=production

# 2. Update API keys to PRODUCTION
BINANCE_PRODUCTION_API_KEY=your_production_key
BINANCE_PRODUCTION_SECRET=your_production_secret
BYBIT_PRODUCTION_API_KEY=your_production_key
BYBIT_PRODUCTION_SECRET=your_production_secret

# 3. Verify configuration
python verify_system.py

# 4. Restart bot
python api.py
```

---

### **5. PROXY & ISP BLOCK ISSUES** 🔐

**Symptoms:**
```
⚠️  Bybit Market Fetch Error: Connection timeout
⚠️  ISP may be blocking Bybit
```

**Solution:**

**Step 1: Test without proxy**
```bash
python test_no_proxy.py
```

**Step 2: If failed, enable proxy**
```env
# Option A: Use public proxy
HTTPS_PROXY=http://47.56.69.11:3128
ENABLE_PROXY_FALLBACK=true

# Option B: Use VPN (configure system proxy)
# Then leave these empty:
HTTPS_PROXY=
HTTP_PROXY=
```

**Step 3: Test with proxy**
```bash
python verify_system.py
```

---

### **6. RATE LIMIT ISSUES** 🚦

**Error Messages:**
```
❌ RateLimitExceeded: Rate limit exceeded
❌ ExchangeError: Too many requests
```

**Solution:**
```env
# Ensure rate limiting is ENABLED
API_RATE_LIMIT_ENABLED=true

# Increase retry delay
API_RETRY_DELAY=2.0

# Reduce request frequency in code
```

---

### **7. TIME SYNCHRONIZATION ISSUES** 🕐

**Error Messages:**
```
❌ InvalidNonce: nonce is not increasing
❌ Signature has expired
```

**Solution:**

**Windows:**
```powershell
# Sync system time
net start w32time
w32tm /resync
```

**Linux:**
```bash
# Sync system time
sudo ntpdate -s time.nist.gov
sudo systemctl restart ntp
```

**Verification:**
```bash
python -c "from datetime import datetime; print(datetime.utcnow())"
```

---

## **STEP-BY-STEP DEBUGGING WORKFLOW**

### **First Time Setup:**
```bash
# 1. Verify Python & dependencies
python --version
pip list | grep ccxt

# 2. Check .env configuration
python verify_system.py

# 3. Test each exchange individually
python test_key.py  # Test Bybit
python test_ccxt_proxy.py  # Test Binance with proxy
```

### **After Configuration Change:**
```bash
# 1. Reload environment
# (Manually restart Python/terminal)

# 2. Verify new config
python verify_system.py

# 3. Run full system check
python api.py  # Watch console for errors
```

### **Production Transition:**
```bash
# 1. Prepare .env with production keys
ENVIRONMENT=production
BINANCE_PRODUCTION_API_KEY=xxxx
BINANCE_PRODUCTION_SECRET=xxxx
BYBIT_PRODUCTION_API_KEY=xxxx
BYBIT_PRODUCTION_SECRET=xxxx

# 2. Dry run with small amounts (0.001 BTC)
# Run bot in dry-mode

# 3. Monitor for 30 min without trading
# Check:
# - API connectivity
# - Balance updates
# - Price feeds
# - No errors in logs

# 4. Enable trading with risk limits
# Set MAX_RISK_LOSS=2%
# Trade only on visible opportunities

# 5. Monitor next 24 hours
# Check log files
# Verify trades executed correctly
```

---

## **VERIFICATION CHECKLIST**

- [ ] `.env` file exists in root directory
- [ ] `ENVIRONMENT` variable is set correctly
- [ ] All API keys match the selected environment
- [ ] `config.py` is in root directory
- [ ] `verify_system.py` runs without errors
- [ ] Binance ticker fetches successfully
- [ ] Bybit ticker fetches successfully
- [ ] Balances display correctly
- [ ] Calculations verify as expected
- [ ] Model loads without errors

---

## **ERROR REFERENCE TABLE**

| Error | Cause | Fix |
|-------|-------|-----|
| `ExchangeNotAvailable` | Wrong URL or API down | Check URLs in config.py |
| `InvalidNonce` | System time wrong | Sync system clock |
| `AuthenticationError` | Wrong API key | Verify .env keys match exchange |
| `PermissionDenied` | API key has no permissions | Enable permissions on exchange |
| `RateLimitExceeded` | Too many requests | Enable rate limiting, reduce requests |
| `Timeout` | Network latency | Increase timeout, enable proxy |
| `ConnectionRefused` | ISP blocks exchange | Use proxy, try VPN |
| `InvalidSignature` | Secret corrupted/old | Copy-paste secret again from exchange |
| `InsufficientBalance` | No funds in account | Deposit funds to testnet/production |
| `OrderNotFound` | Order already filled/cancelled | Check balance and try again |

---

## **GETTING HELP**

1. **Check logs:**
   ```bash
   tail -f logs.txt
   ```

2. **Run verification:**
   ```bash
   python verify_system.py
   ```

3. **Test individual components:**
   ```bash
   python test_conn.py
   python test_key.py
   python test_ccxt_proxy.py
   ```

4. **Enable debug mode:**
   ```python
   import logging
   logging.basicConfig(level=logging.DEBUG)
   ```

---

**🎯 Key Takeaway:** Most API errors stem from:
1. **Wrong URLs** ← Fix in `config.py`
2. **Invalid credentials** ← Check `.env` file
3. **Network issues** ← Enable proxy, increase timeout
4. **Time sync** ← Sync system clock

Use `python verify_system.py` to diagnose any issue!
