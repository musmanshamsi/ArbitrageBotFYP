# ⚡ QUICK START GUIDE - 5 MINUTES TO WORKING BOT
## AI Arbitrage Bot v7.0 | Professional Setup

---

## **✅ PRE-FLIGHT CHECKLIST**

Before you begin, ensure you have:
- [ ] Python 3.10+ installed
- [ ] Git bash or PowerShell (Windows)
- [ ] Basic exchange account knowledge
- [ ] Internet connection
- [ ] 15 minutes of free time

---

## **📋 STEP 1: GATHER CREDENTIALS (5 min)**

### **1.1 Binance Testnet Keys**

```bash
1. Open: https://testnet.binance.vision
2. Login with your Binance account (or create free testnet account)
3. Select "Account" → "API Management"
4. Click "Create New Key"
5. Confirm with email if needed
6. Copy these two values:
   - API Key: ▌▌▌▌▌▌▌▌▌▌
   - Secret Key: ▌▌▌▌▌▌▌▌▌▌
```

### **1.2 Bybit Testnet Keys**

```bash
1. Open: https://testnet.bybit.com
2. Create account if needed (2 min)
3. Login
4. Click your profile → "API"
5. Create "API Key"
6. Permissions needed:
   ✅ Spot Trading
   ✅ Account Read
7. Copy these two values:
   - API Key: ▌▌▌▌▌▌▌▌▌▌
   - Secret Key: ▌▌▌▌▌▌▌▌▌▌
```

---

## **⚙️ STEP 2: CONFIGURE YOUR BOT (3 min)**

### **2.1 Create `.env` File**

In your bot's root directory (`e:\AI_Arbitrage_Bot\`), create a new file called `.env`:

```powershell
# Windows PowerShell
cd e:\AI_Arbitrage_Bot
New-Item -Name .env -ItemType File
```

Or use Notepad:
1. Right-click empty space → New → Text Document
2. Name it `rename_to_.env`
3. Rename to `.env` (remove `.txt`)

### **2.2 Add Credentials to `.env`**

Copy this template and fill in your values:

```env
# Environment Mode
ENVIRONMENT=testnet

# Binance Testnet (from Step 1.1)
BINANCE_TESTNET_API_KEY=paste_your_key_here
BINANCE_TESTNET_SECRET=paste_your_secret_here

# Bybit Testnet (from Step 1.2)
BYBIT_TESTNET_API_KEY=paste_your_key_here
BYBIT_TESTNET_SECRET=paste_your_secret_here

# Security - Generate: python -c "import secrets; print(secrets.token_hex(32))"
JWT_SECRET_KEY=your_random_generated_key

# AI (Optional - can be added later)
GEMINI_API_KEY=
GROQ_API_KEY=

# Keep everything else as defaults
API_REQUEST_TIMEOUT=10
API_RATE_LIMIT_ENABLED=true
```

### **2.3 Verify Configuration**

```powershell
cd e:\AI_Arbitrage_Bot
python verify_system.py
```

Expected output:
```
✅ ARBPRO SYSTEM VERIFICATION
   Environment: TESTNET
   Binance: ✅ Configured
   Bybit: ✅ Configured
🔍 EXCHANGE CONNECTIVITY CHECK
   🟡 Binance: ✅ Ticker ✅ Balance ✅ WORKING
   ⚫ Bybit: ✅ Ticker ✅ Balance ✅ WORKING
✅ VERIFICATION COMPLETE
```

---

## **🚀 STEP 3: START THE BOT (2 min)**

### **3.1 Terminal 1: Start Backend API**

```powershell
cd e:\AI_Arbitrage_Bot
python api.py
```

Wait for:
```
✅ LOCAL VAULT ONLINE (Port 8080)
🤖 BACKEND & ARBITRAGE ENGINE RUNNING ON PORT 8000...
📊 WebSocket connected successfully
```

### **3.2 Terminal 2: Start Frontend (Optional)**

```powershell
cd e:\AI_Arbitrage_Bot\Frontend
npm install
npm run dev
```

Access at: `http://localhost:5173`

---

## **🧪 STEP 4: TEST LIVE (Monitor for 10 min)**

### **4.1 Watch Console Output**

Backend API should show:
```
📊 Binance: 65234.50 | Bybit: 65456.78 | Spread: 0.34%
📊 Binance: 65234.60 | Bybit: 65456.90 | Spread: 0.34%
```

### **4.2 Check Logs**

```powershell
# Watch for errors
Get-Content api.log -Tail 10 -Wait
```

### **4.3 Test API Manually**

```powershell
# Get market data
curl http://localhost:8000/api/market-data

# Get balances
curl http://localhost:8000/api/balance
```

---

## **✅ SUCCESSFUL SETUP INDICATORS**

- [ ] No ❌ errors in terminal
- [ ] Prices updating every 2-3 seconds
- [ ] Both exchanges show ✅ WORKING
- [ ] Balances display correctly
- [ ] WebSocket connection successful
- [ ] Can access frontend at localhost:5173

---

## **🔄 SWITCHING TO PRODUCTION (When Ready)**

### **Step 1: Get Production API Keys**

**Binance Production:**
```
https://www.binance.com/en/account/api-management
```

**Bybit Production:**
```
https://www.bybit.com/en/user/api-management
```

### **Step 2: Update `.env`**

```env
ENVIRONMENT=production

# Add PRODUCTION keys (from Step 1)
BINANCE_PRODUCTION_API_KEY=your_production_key
BINANCE_PRODUCTION_SECRET=your_production_secret
BYBIT_PRODUCTION_API_KEY=your_production_key
BYBIT_PRODUCTION_SECRET=your_production_secret
```

### **Step 3: Verify**

```powershell
python verify_system.py
# Should show "Environment: PRODUCTION"
```

### **Step 4: Dry Run First**

Before real trading:
```
1. Set MIN_SPREAD_PERCENT=0.5 (high, to avoid trades)
2. Run for 30 minutes
3. Monitor for errors
4. Check that balances update correctly
```

### **Step 5: Enable Trading Cautiously**

```
1. Set MIN_SPREAD_PERCENT=0.3 (realistic)
2. Set MAX_POSITION_SIZE=100 (small)
3. Monitor next 24 hours
4. Gradually increase position size
```

---

## **🚨 TROUBLESHOOTING QUICK FIXES**

| Problem | Solution |
|---------|----------|
| "Invalid API Key" | Check .env file spelling, verify keys on exchange |
| "Connection timeout" | Increase API_REQUEST_TIMEOUT=15, check internet |
| "Exchange not available" | Check API URLs in config.py |
| "No module named 'ccxt'" | pip install ccxt |
| "Permission denied" | Enable API permissions on exchange account |
| ".env not found" | Create .env in root directory (e:\AI_Arbitrage_Bot\) |

---

## **📊 WHAT HAPPENS NEXT**

Your bot will automatically:

1. **🔄 Fetch Prices** (every 2-3 sec)
   - Connect to Binance and Bybit
   - Get BTC/USDT prices
   - Calculate spread

2. ⚡ **Analyze Opportunities** (every 5 sec)
   - Check if spread > MIN_SPREAD_PERCENT
   - Ask AI if it's a good trade
   - Display recommendation

3. 💰 **Execute Trades** (when condition met)
   - Wait for your approval
   - Buy on lower exchange
   - Sell on higher exchange
   - Record profit

4. 📈 **Show Dashboard** (real-time)
   - Live prices
   - Spread percentage
   - Execution history
   - Total profit

---

## **📚 NEXT STEPS (Optional)**

- [ ] Read [CONFIG_SETUP_GUIDE.md](CONFIG_SETUP_GUIDE.md) for advanced configuration
- [ ] Read [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for common issues
- [ ] Add API keys for Kraken, Coinbase (in .env file)
- [ ] Configure email notifications (NOTIFICATION_EMAIL in .env)
- [ ] Set up daily loss limits (MAX_DAILY_LOSS_PERCENT in .env)

---

## **✨ YOU'RE READY!**

Your bot is now:
- ✅ Configured correctly
- ✅ Connected to exchanges
- ✅ Monitoring prices
- ✅ Ready to trade

**Start with testnet to build confidence, then move to production when comfortable!**

---

**Need help?** See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for detailed solutions.

**Questions?** Check [CONFIG_SETUP_GUIDE.md](CONFIG_SETUP_GUIDE.md) for all configuration options.
