import { useState, useEffect, useRef } from "react";
import { LayoutDashboard, Activity, Database, MessageSquare, Send, Bot as BotIcon, TrendingUp, Power, AlertCircle, ChevronRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import SpreadChart from "@/components/SpreadChart";
import { useToast } from "@/hooks/use-toast";

const Index = () => {
  const { toast } = useToast();
  const [botRunning, setBotRunning] = useState(false);
  const [chatOpen, setChatOpen] = useState(true);
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState([{ role: 'ai', text: 'ArbPro System Online. Monitoring cross-exchange liquidity.' }]);
  const chatEndRef = useRef<HTMLDivElement>(null);

  const [marketData, setMarketData] = useState<any>(null);
  const [spreadData, setSpreadData] = useState<any[]>([]);
  const [tradeLog, setTradeLog] = useState<any[]>([]);
  const [totalProfit, setTotalProfit] = useState(0.00);

  // Keep track of balances based on your backend's actual keys
  const [binanceBalance, setBinanceBalance] = useState(0.00);
  const [bybitBalance, setBybitBalance] = useState(0.00);

  // Fetch Database History
  useEffect(() => {
    const fetchDatabaseHistory = async () => {
      try {
        const res = await fetch("http://127.0.0.1:8000/api/history");
        const data = await res.json();
        setTradeLog(data.history);
        setTotalProfit(data.total_profit);
      } catch (e) {
        console.error("Database sync failed.", e);
      }
    };
    fetchDatabaseHistory();
  }, []);

  // WebSocket Connection
  useEffect(() => {
    const socket = new WebSocket("ws://127.0.0.1:8000/ws/market");
    socket.onmessage = (event) => {
      const data = JSON.parse(event.data);

      if (data.type === "ai_msg") {
        setMessages(prev => [...prev, { role: 'ai', text: data.text }]);
      } else if (data.type === "trade") {
        setTradeLog(prev => [data.trade, ...prev]);
        if (data.raw_profit !== undefined) setTotalProfit(p => p + data.raw_profit);
        toast({ title: "Arbitrage Executed", description: `Captured: ${data.trade.profit}`, className: "bg-green-500 text-black font-bold border-none" });
      } else if (data.type === "market") {
        setMarketData(data);

        // FIX: Extracting your exact backend balance keys
        if (data.binance_bal !== undefined) setBinanceBalance(data.binance_bal);
        if (data.bybit_bal !== undefined) setBybitBalance(data.bybit_bal);

        setSpreadData(prev => [...prev.slice(-19), {
          time: new Date().toLocaleTimeString([], { second: "2-digit" }),
          spread: data.spread || 0,
        }]);
      }
    };
    return () => socket.close();
  }, [toast]);

  // Auto-scroll chat
  useEffect(() => chatEndRef.current?.scrollIntoView({ behavior: "smooth" }), [messages]);

  const toggleBot = async () => {
    const newState = !botRunning;
    try {
      setBotRunning(newState);
      await fetch("http://127.0.0.1:8000/toggle_bot", {
        method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ active: newState }),
      });
    } catch (e) {
      setBotRunning(!newState);
      toast({ title: "System Offline", description: "Could not reach trading engine.", variant: "destructive" });
    }
  };

  const handleSend = () => {
    if (!input.trim()) return;
    setMessages(prev => [...prev, { role: 'user', text: input }]);
    setInput("");
  };

  if (!marketData) {
    return (
      <div className="h-screen bg-[#050505] flex flex-col items-center justify-center text-green-500 font-mono">
        <div className="w-16 h-16 border-4 border-green-500/20 border-t-green-500 rounded-full animate-spin mb-4"></div>
        <p className="tracking-[0.2em] animate-pulse">ESTABLISHING SECURE CONNECTION...</p>
      </div>
    );
  }

  // Calculate Grand Total (Balances + Profit)
  const grandTotal = binanceBalance + bybitBalance + totalProfit;

  return (
    <div className="flex h-screen w-full bg-[#050505] text-gray-200 overflow-hidden font-sans selection:bg-green-500/30">

      {/* --- SIDEBAR --- */}
      <aside className="w-20 border-r border-white/5 bg-[#0a0a0c] flex flex-col items-center py-6 gap-8 z-10">
        <div className="w-10 h-10 bg-gradient-to-br from-green-400 to-green-600 rounded-xl flex items-center justify-center font-black text-xl text-black shadow-[0_0_20px_rgba(34,197,94,0.3)]">A</div>
        <nav className="flex flex-col gap-6 text-gray-600">
          <button className="p-3 text-green-500 bg-green-500/10 rounded-xl"><LayoutDashboard size={20} /></button>
          <button className="p-3 hover:text-gray-300 transition-colors"><Activity size={20} /></button>
          <button className="p-3 hover:text-gray-300 transition-colors"><Database size={20} /></button>
        </nav>
      </aside>

      {/* --- MAIN DASHBOARD --- */}
      <main className="flex-1 p-8 overflow-y-auto flex flex-col gap-8">

        {/* HEADER AREA */}
        <header className="flex justify-between items-start">
          <div>
            <div className="flex items-center gap-3 mb-1">
              <h1 className="text-3xl font-black tracking-tight text-white">ArbPro Core</h1>
              <span className={`px-3 py-1 text-[10px] font-bold uppercase tracking-widest rounded-full border ${botRunning ? 'border-green-500 text-green-500 bg-green-500/10 animate-pulse' : 'border-gray-600 text-gray-500 bg-gray-800/50'}`}>
                {marketData.status?.replace("_", " ") || "IDLE"}
              </span>
            </div>
            <p className="text-sm text-gray-500 flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-green-500"></span>
              Live Testnet Environment • Latency: {marketData.latency || 0}ms
            </p>
          </div>

          <Button
            onClick={toggleBot}
            className={`h-12 px-6 font-bold tracking-wide transition-all duration-300 rounded-xl flex items-center gap-2 ${botRunning ? "bg-red-500/10 text-red-500 border border-red-500/50 hover:bg-red-500/20" : "bg-green-500 text-black hover:bg-green-400 shadow-[0_0_20px_rgba(34,197,94,0.2)]"}`}
          >
            <Power size={18} />
            {botRunning ? "HALT TRADING" : "ENGAGE ALGORITHM"}
          </Button>
        </header>

        {/* SECTION 1: PORTFOLIO */}
        <section className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Total Equity Hero Card */}
          <div className="md:col-span-1 bg-gradient-to-br from-[#111116] to-[#0a0a0c] border border-white/10 p-6 rounded-2xl relative overflow-hidden group">
            <div className="absolute top-0 right-0 w-32 h-32 bg-green-500/10 blur-[50px] group-hover:bg-green-500/20 transition-all duration-500"></div>
            <p className="text-[10px] text-gray-500 font-bold uppercase tracking-[0.2em] mb-2 flex items-center gap-2">
              Net Account Equity <AlertCircle size={12} />
            </p>
            <h2 className="text-4xl font-black text-white mb-2">
              ${grandTotal.toLocaleString(undefined, { minimumFractionDigits: 2 })}
            </h2>
            <div className="inline-flex items-center gap-1.5 px-2 py-1 bg-green-500/10 text-green-400 text-xs font-bold rounded-lg border border-green-500/20">
              <TrendingUp size={12} /> +${totalProfit.toFixed(2)} Profit
            </div>
          </div>

          {/* FIX: Passing the direct state variables to the VaultCards */}
          <VaultCard name="Binance" color="text-yellow-500" bg="bg-yellow-500/10" balance={binanceBalance} />
          <VaultCard name="Bybit" color="text-orange-500" bg="bg-orange-500/10" balance={bybitBalance} />
        </section>

        {/* SECTION 2: MARKET ANALYTICS */}
        <section className="bg-[#0a0a0c] border border-white/5 rounded-2xl p-6 shadow-xl flex flex-col gap-6">
          {/* Mini-metrics above chart */}
          <div className="grid grid-cols-3 gap-4 border-b border-white/5 pb-6">
            <div>
              <p className="text-[10px] text-gray-500 uppercase tracking-widest font-bold mb-1">Binance Oracle</p>
              <p className="text-xl font-mono text-white">${marketData.binance?.toLocaleString() || 0}</p>
            </div>
            <div>
              <p className="text-[10px] text-gray-500 uppercase tracking-widest font-bold mb-1">Bybit Oracle</p>
              <p className="text-xl font-mono text-white">${marketData.kraken?.toLocaleString() || 0}</p>
            </div>
            <div>
              <p className="text-[10px] text-gray-500 uppercase tracking-widest font-bold mb-1">Target Spread</p>
              <p className={`text-xl font-mono font-bold flex items-center gap-2 ${marketData.opportunity ? 'text-green-500' : 'text-gray-300'}`}>
                {(marketData.spread || 0).toFixed(3)}%
                {marketData.opportunity && <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></span>}
              </p>
            </div>
          </div>
          {/* Chart Area */}
          <div className="h-[220px] w-full">
            <SpreadChart data={spreadData} threshold={0.1} />
          </div>
        </section>

        {/* SECTION 3: EXECUTION LOGS */}
        <section className="bg-[#0a0a0c] border border-white/5 rounded-2xl overflow-hidden flex-1 min-h-[250px]">
          <div className="px-6 py-4 border-b border-white/5 bg-[#111116] flex justify-between items-center">
            <h3 className="text-xs font-bold text-gray-400 uppercase tracking-widest">Execution Ledger</h3>
            <span className="text-[10px] text-gray-600">{tradeLog.length} Records</span>
          </div>
          <div className="overflow-y-auto max-h-[300px]">
            <table className="w-full text-left border-collapse">
              <thead className="sticky top-0 bg-[#0a0a0c]/90 backdrop-blur-sm z-10">
                <tr className="text-[10px] text-gray-600 uppercase tracking-wider">
                  <th className="px-6 py-3 font-semibold">Timestamp</th>
                  <th className="px-6 py-3 font-semibold">Route Path</th>
                  <th className="px-6 py-3 text-right font-semibold">Profit (USD)</th>
                </tr>
              </thead>
              <tbody className="text-xs font-mono">
                {tradeLog.length === 0 ? (
                  <tr>
                    <td colSpan={3} className="px-6 py-8 text-center text-gray-600 italic">No trades executed yet. Standing by.</td>
                  </tr>
                ) : (
                  tradeLog.map((t, i) => (
                    <tr key={i} className="border-b border-white/5 hover:bg-white/[0.02] transition-colors group">
                      <td className="px-6 py-3 text-gray-500">{t.time}</td>
                      <td className="px-6 py-3 text-gray-300 flex items-center gap-2">
                        {t.route?.split('➔')[0] || t.route} <ChevronRight size={12} className="text-gray-600" /> {t.route?.split('➔')[1] || ""}
                      </td>
                      <td className="px-6 py-3 text-right text-green-500 font-bold group-hover:text-green-400">{t.profit}</td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </section>

      </main>

      {/* --- AI TERMINAL --- */}
      <aside className={`${chatOpen ? 'w-[350px]' : 'w-16'} transition-all duration-300 ease-in-out border-l border-white/5 bg-[#0a0a0c] flex flex-col z-10`}>
        {chatOpen ? (
          <>
            <div className="p-5 border-b border-white/5 flex justify-between items-center bg-[#111116]">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-purple-500/10 rounded-lg">
                  <BotIcon size={16} className="text-purple-500" />
                </div>
                <div>
                  <h3 className="font-bold text-sm text-gray-200">AI Logic Core</h3>
                  <p className="text-[9px] text-gray-500 uppercase tracking-widest">Model: Arbitrage-V1</p>
                </div>
              </div>
              <button onClick={() => setChatOpen(false)} className="text-gray-500 hover:text-white transition-colors p-1"><ChevronRight size={18} /></button>
            </div>

            <div className="flex-1 overflow-y-auto p-5 space-y-4 scrollbar-hide">
              {messages.map((m, i) => (
                <div key={i} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                  <div className={`max-w-[85%] p-3.5 rounded-2xl text-[12px] leading-relaxed shadow-sm ${m.role === 'user'
                      ? 'bg-gradient-to-br from-green-500 to-green-600 text-black rounded-tr-sm font-medium'
                      : 'bg-[#111116] border border-white/5 text-gray-300 rounded-tl-sm'
                    }`}>
                    {m.text}
                  </div>
                </div>
              ))}
              <div ref={chatEndRef} />
            </div>

            <div className="p-4 border-t border-white/5 bg-[#111116]">
              <div className="flex gap-2 items-center bg-[#050505] border border-white/10 rounded-xl p-1 pr-2 focus-within:border-purple-500/50 transition-colors">
                <input
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleSend()}
                  placeholder="Ask AI Core..."
                  className="flex-1 bg-transparent px-3 py-2 text-xs text-white outline-none placeholder:text-gray-600"
                />
                <button onClick={handleSend} className="p-2 bg-purple-500/20 hover:bg-purple-500/40 text-purple-400 transition-colors rounded-lg">
                  <Send size={14} />
                </button>
              </div>
            </div>
          </>
        ) : (
          <button onClick={() => setChatOpen(true)} className="h-full w-full flex flex-col items-center py-6 text-gray-600 hover:text-purple-400 transition-colors bg-[#111116]">
            <MessageSquare size={20} />
          </button>
        )}
      </aside>
    </div>
  );
};

// FIX: Updated VaultCard to map straight to the single balance variable
const VaultCard = ({ name, color, bg, balance }: any) => {
  return (
    <div className="bg-[#111116] border border-white/5 rounded-2xl p-5 relative overflow-hidden flex flex-col justify-between">
      <div className="flex justify-between items-start mb-4">
        <div>
          <h3 className={`${color} font-bold text-sm uppercase tracking-tighter`}>{name}</h3>
          <span className="text-[9px] text-gray-500 uppercase tracking-widest">Exchange Vault</span>
        </div>
        <div className={`p-2 ${bg} rounded-lg`}>
          <Database size={16} className={color} />
        </div>
      </div>

      <div className="space-y-2">
        <div className="flex justify-between items-center bg-[#0a0a0c] px-3 py-2 rounded-lg border border-white/5">
          <span className="text-gray-500 text-[10px] uppercase font-bold">Total Assets (USD)</span>
          {/* Automatically formats your single balance variable securely */}
          <span className="font-mono text-gray-200 text-sm font-bold">${(balance || 0).toLocaleString(undefined, { minimumFractionDigits: 2 })}</span>
        </div>
        <div className="flex justify-between items-center bg-[#0a0a0c] px-3 py-2 rounded-lg border border-white/5 opacity-50">
          <span className="text-gray-500 text-[10px] uppercase font-bold">BTC Allocation</span>
          <span className="font-mono text-gray-400 text-xs italic">Auto-Managed</span>
        </div>
      </div>
    </div>
  );
};

export default Index;