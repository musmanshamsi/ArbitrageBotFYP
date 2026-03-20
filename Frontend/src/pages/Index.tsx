import { useState, useEffect, useRef } from "react";
import { LayoutDashboard, Activity, Database, MessageSquare, Send, Bot as BotIcon, Globe, DollarSign, Wallet, Landmark, TrendingUp } from "lucide-react";
import { Button } from "@/components/ui/button";
import MetricCard from "@/components/MetricCard";
import SpreadChart from "@/components/SpreadChart";
import { useToast } from "@/hooks/use-toast";

const Index = () => {
  const { toast } = useToast();
  const [botRunning, setBotRunning] = useState(false);
  const [chatOpen, setChatOpen] = useState(true);
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState([{ role: 'ai', text: 'ArbPro System Online. Ready for analysis.' }]);
  const chatEndRef = useRef<HTMLDivElement>(null);

  // Market & System States
  const [binancePrice, setBinancePrice] = useState(0);
  const [bybitPrice, setBybitPrice] = useState(0);
  const [spread, setSpread] = useState(0);
  const [isOp, setIsOp] = useState(false);
  const [latency, setLatency] = useState(0);
  const [risk, setRisk] = useState("LOW");
  const [botStatus, setBotStatus] = useState("OFFLINE");
  const [spreadData, setSpreadData] = useState<any[]>([]);

  // Capital & Balance Tracking
  const [binanceBalance, setBinanceBalance] = useState(0.00);
  const [bybitBalance, setBybitBalance] = useState(0.00);

  // --- DATABASE-DRIVEN STATE ---
  const [tradeLog, setTradeLog] = useState<any[]>([]);
  const [totalProfit, setTotalProfit] = useState(0.00);

  // Fetch official history from SQLite Backend on load
  useEffect(() => {
    const fetchDatabaseHistory = async () => {
      try {
        const res = await fetch("http://127.0.0.1:8000/api/history");
        const data = await res.json();
        setTradeLog(data.history);
        setTotalProfit(data.total_profit);
      } catch (e) {
        console.error("Failed to connect to database.", e);
      }
    };
    fetchDatabaseHistory();
  }, []);
  // -----------------------------

  // SECRETE DATABASE WIPER FUNCTION
  const resetData = async () => {
    try {
      await fetch("http://127.0.0.1:8000/api/reset", { method: "POST" });
      setTotalProfit(0);
      setTradeLog([]);
      toast({
        title: "DATABASE WIPED",
        description: "SQLite table dropped. Starting fresh.",
        variant: "destructive"
      });
    } catch (e) {
      toast({ title: "ERROR", description: "Failed to reach database.", variant: "destructive" });
    }
  };

  useEffect(() => {
    document.title = binancePrice > 0 ? `$${binancePrice.toLocaleString()} | Arb Pro` : "Arbitrage Pro";
  }, [binancePrice]);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const toggleBot = async () => {
    const newState = !botRunning;
    try {
      setBotRunning(newState);
      await fetch("http://127.0.0.1:8000/toggle_bot", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ active: newState }),
      });
      toast({
        title: newState ? "ALGO_ACTIVATED" : "ALGO_TERMINATED",
        description: newState ? "Monitoring spreads..." : "System standing down.",
        variant: newState ? "default" : "destructive",
      });
    } catch (e) {
      setBotRunning(!newState);
      toast({ title: "CONNECTION_ERROR", description: "Backend unreachable.", variant: "destructive" });
    }
  };

  useEffect(() => {
    const socket = new WebSocket("ws://127.0.0.1:8000/ws/market");

    socket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);

        if (data.type === "ai_msg") {
          setMessages(prev => [...prev, { role: 'ai', text: data.text }]);
          return;
        }

        if (data.type === "trade") {
          setTradeLog(prev => [data.trade, ...prev].slice(0, 50));

          if (data.raw_profit !== undefined) {
            setTotalProfit(prev => prev + data.raw_profit);
          }

          toast({
            title: "TRADE EXECUTED",
            description: `Locked in profit: ${data.trade.profit}`,
            variant: "default",
            className: "bg-green-600 text-white border-none"
          });
          return;
        }

        if (data.type === "market") {
          setBinancePrice(data.binance || 0);
          setBybitPrice(data.kraken || 0);
          setSpread(data.spread || 0);
          setIsOp(data.opportunity || false);
          setLatency(data.latency || 0);
          setRisk(data.risk || "LOW");
          setBotStatus(data.status || "IDLE");

          if (data.binance_bal !== undefined) setBinanceBalance(data.binance_bal);
          if (data.bybit_bal !== undefined) setBybitBalance(data.bybit_bal);

          setSpreadData((prev) => [...prev.slice(-19), {
            time: new Date().toLocaleTimeString([], { second: "2-digit" }),
            spread: data.spread || 0,
          }]);
        }
      } catch (err) {
        console.error("Data Stream Error", err);
      }
    };

    return () => socket.close();
  }, [toast]);

  const handleSend = async () => {
    if (!input.trim()) return;
    const userMsg = { role: 'user', text: input };
    setMessages(prev => [...prev, userMsg]);
    setInput("");
    try {
      const res = await fetch("http://127.0.0.1:8000/ask_ai", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: input }),
      });
      const data = await res.json();
      setMessages(prev => [...prev, { role: 'ai', text: data.answer }]);
    } catch (e) {
      setMessages(prev => [...prev, { role: 'ai', text: "AI Core Unreachable." }]);
    }
  };

  return (
    <div className="flex h-screen w-full bg-[#0a0a0c] text-white overflow-hidden font-sans">
      <aside className="w-20 border-r border-white/10 bg-[#0f0f12] flex flex-col items-center py-8 gap-8 z-10">
        <div
          onClick={resetData}
          title="Click to wipe SQLite database"
          className="w-12 h-12 bg-green-500 rounded-2xl flex items-center justify-center font-black text-2xl text-black shadow-[0_0_15px_rgba(34,197,94,0.3)] cursor-pointer hover:bg-green-400 hover:scale-105 transition-all"
        >
          Δ
        </div>
        <div className="flex flex-col gap-6 text-gray-500">
          <LayoutDashboard className="text-green-500 cursor-pointer" />
          <Activity className="hover:text-white cursor-pointer transition-colors" />
          <Database className="hover:text-white cursor-pointer transition-colors" />
          <Globe className="hover:text-white cursor-pointer transition-colors" />
        </div>
      </aside>

      <main className="flex-1 p-8 overflow-y-auto border-r border-white/5 flex flex-col">
        <header className="flex justify-between items-center mb-6">
          <div>
            <h2 className="text-3xl font-black italic tracking-tighter text-green-500 uppercase flex items-center gap-3">
              Arb_Pro_v3
              <span className="text-sm font-bold bg-green-500/10 text-green-400 px-3 py-1 rounded-full border border-green-500/20 not-italic flex items-center gap-1">
                <TrendingUp size={14} /> {totalProfit.toFixed(2)} NET PROFIT
              </span>
            </h2>
            <div className="flex items-center gap-4 mt-2">
              <div className="flex items-center gap-2 text-[10px] text-gray-500 uppercase tracking-widest">
                <span className="h-1.5 w-1.5 rounded-full bg-green-500 animate-pulse"></span> Network_Stable
              </div>
              <div className={`text-[10px] font-bold px-2 py-0.5 rounded border ${botStatus === 'EXECUTING_TRADE' ? 'border-red-500 text-red-500 animate-pulse bg-red-500/10' :
                  botStatus === 'CONSULTING_AI' ? 'border-purple-500 text-purple-400 animate-pulse bg-purple-500/10' :
                    botStatus === 'SCANNING_MARKET' ? 'border-green-500 text-green-500 bg-green-500/10' :
                      'border-gray-500 text-gray-500 bg-white/5'
                }`}>
                STATUS: {botStatus}
              </div>
              <div className={`text-[10px] font-bold px-2 py-0.5 rounded border ${risk === 'HIGH' ? 'border-red-500/50 text-red-400' : 'border-green-500/20 text-green-500'}`}>
                RISK: {risk}
              </div>
            </div>
          </div>
          <Button
            className={`transition-all duration-300 shadow-lg ${botRunning ? "bg-red-500 hover:bg-red-600 font-bold shadow-red-500/20" : "bg-green-500 text-black hover:bg-green-400 font-bold shadow-green-500/20"}`}
            onClick={toggleBot}
          >
            {botRunning ? "TERMINATE_ALGO" : "EXECUTE_ALGO"}
          </Button>
        </header>

        <div className="grid grid-cols-3 gap-6 mb-6">
          <div className="bg-[#15151a] border border-white/5 rounded-2xl p-5 flex items-center justify-between">
            <div>
              <p className="text-[10px] text-gray-500 font-bold uppercase tracking-widest mb-1">Binance Capital (USD)</p>
              <h3 className="text-2xl font-black text-white flex items-center gap-1">
                <DollarSign size={20} className="text-gray-500" /> {binanceBalance.toFixed(2)}
              </h3>
            </div>
            <div className="p-3 bg-blue-500/10 rounded-xl"><Wallet className="text-blue-500" size={24} /></div>
          </div>

          <div className="bg-[#15151a] border border-white/5 rounded-2xl p-5 flex items-center justify-between">
            <div>
              <p className="text-[10px] text-gray-500 font-bold uppercase tracking-widest mb-1">Bybit Capital (USD)</p>
              <h3 className="text-2xl font-black text-white flex items-center gap-1">
                <DollarSign size={20} className="text-gray-500" /> {bybitBalance.toFixed(2)}
              </h3>
            </div>
            <div className="p-3 bg-orange-500/10 rounded-xl"><Wallet className="text-orange-500" size={24} /></div>
          </div>

          <div className="bg-[#15151a] border border-green-500/20 rounded-2xl p-5 flex items-center justify-between shadow-[0_0_15px_rgba(34,197,94,0.05)]">
            <div>
              <p className="text-[10px] text-green-500/70 font-bold uppercase tracking-widest mb-1">Total Est. Portfolio</p>
              <h3 className="text-2xl font-black text-green-400 flex items-center gap-1">
                <DollarSign size={20} className="text-green-500/50" />
                {(binanceBalance + bybitBalance + totalProfit).toFixed(2)}
              </h3>
            </div>
            <div className="p-3 bg-green-500/10 rounded-xl"><Landmark className="text-green-500" size={24} /></div>
          </div>
        </div>

        <div className="grid grid-cols-3 gap-6 mb-8">
          <MetricCard title="Binance (Live Price)" value={`$${binancePrice.toLocaleString()}`} />
          <MetricCard title="Bybit (Sim Price)" value={`$${bybitPrice.toLocaleString()}`} />
          <MetricCard title="Net Spread Threshold" value={`${spread.toFixed(3)}%`} isHighlighted={isOp} />
        </div>

        <div className="bg-[#0f0f12] p-6 rounded-3xl border border-white/5 mb-8 h-[300px] flex-shrink-0">
          <SpreadChart data={spreadData} threshold={0.1} />
        </div>

        <div className="bg-[#0f0f12] rounded-3xl border border-white/5 overflow-hidden flex-1 min-h-[200px]">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="text-[10px] text-gray-600 border-b border-white/5 bg-black/20">
                <th className="px-6 py-4 font-black">TIMESTAMP</th>
                <th className="px-6 py-4 font-black">ROUTE_PATH</th>
                <th className="px-6 py-4 text-right font-black">PROFIT_USD</th>
              </tr>
            </thead>
            <tbody className="text-xs font-mono">
              {tradeLog.length === 0 ? (
                <tr>
                  <td colSpan={3} className="px-6 py-8 text-center text-gray-600 italic">
                    Standing by. Awaiting arbitrage opportunities...
                  </td>
                </tr>
              ) : (
                tradeLog.map((trade, idx) => (
                  <tr key={idx} className="border-b border-white/5 hover:bg-white/[0.02] transition-colors">
                    <td className="px-6 py-4 text-gray-500">{trade.time}</td>
                    <td className="px-6 py-4 font-bold text-gray-200">{trade.route}</td>
                    <td className="px-6 py-4 text-right text-green-500 font-bold">{trade.profit}</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </main>

      <aside className={`${chatOpen ? 'w-96' : 'w-16'} transition-all duration-300 border-l border-white/10 bg-[#0f0f12] flex flex-col z-10`}>
        {chatOpen ? (
          <>
            <div className="p-6 border-b border-white/5 flex justify-between items-center bg-[#0f0f12]">
              <h3 className="font-bold text-sm flex items-center gap-2 text-white">
                <BotIcon size={18} className="text-purple-400" /> AI_TERMINAL
              </h3>
              <button onClick={() => setChatOpen(false)} className="text-gray-500 hover:text-white transition-colors text-xl font-light">×</button>
            </div>

            <div className="flex-1 overflow-y-auto p-4 space-y-4 scrollbar-thin scrollbar-thumb-gray-800">
              {messages.map((m, i) => (
                <div key={i} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                  <div className={`max-w-[85%] p-3.5 rounded-2xl text-[12px] leading-relaxed shadow-sm ${m.role === 'user'
                      ? 'bg-green-600 text-white rounded-br-sm'
                      : 'bg-white/5 border border-white/10 text-gray-300 rounded-bl-sm'
                    }`}>
                    {m.text}
                  </div>
                </div>
              ))}
              <div ref={chatEndRef} className="h-1" />
            </div>

            <div className="p-4 border-t border-white/5 bg-[#0f0f12] flex gap-2 items-center">
              <input
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSend()}
                placeholder="Query market parameters..."
                className="flex-1 bg-[#15151a] border border-white/10 rounded-xl px-4 py-3 text-xs text-white focus:outline-none focus:border-green-500/50 transition-colors"
              />
              <button
                onClick={handleSend}
                className="p-3 bg-green-500 hover:bg-green-400 transition-colors rounded-xl text-black shadow-[0_0_10px_rgba(34,197,94,0.2)]"
              >
                <Send size={16} />
              </button>
            </div>
          </>
        ) : (
          <button onClick={() => setChatOpen(true)} className="h-full w-full flex flex-col items-center py-8 text-gray-500 hover:text-purple-400 transition-colors">
            <MessageSquare size={24} />
          </button>
        )}
      </aside>
    </div>
  );
};

export default Index;