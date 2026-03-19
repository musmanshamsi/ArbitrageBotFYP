import { useState, useEffect, useRef } from "react";
import {
  LayoutDashboard,
  Activity,
  Database,
  MessageSquare,
  Send,
  Bot as BotIcon,
  Zap,
  Globe
} from "lucide-react";
import { Button } from "@/components/ui/button";
import MetricCard from "@/components/MetricCard";
import SpreadChart from "@/components/SpreadChart";
import { useToast } from "@/hooks/use-toast";

const Index = () => {
  const { toast } = useToast();
  const [botRunning, setBotRunning] = useState(false);
  const [chatOpen, setChatOpen] = useState(true);
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState([
    { role: 'ai', text: 'ArbPro System Online. Ready for analysis.' }
  ]);
  const chatEndRef = useRef<HTMLDivElement>(null);

  // Market & System States
  const [binancePrice, setBinancePrice] = useState(0);
  const [bybitPrice, setBybitPrice] = useState(0);
  const [spread, setSpread] = useState(0);
  const [isOp, setIsOp] = useState(false);
  const [latency, setLatency] = useState(0);
  const [risk, setRisk] = useState("LOW");
  const [spreadData, setSpreadData] = useState<any[]>([]);
  const [tradeLog, setTradeLog] = useState<any[]>([]);

  // --- NEW: CHROME TAB TITLE SYNC ---
  useEffect(() => {
    if (binancePrice > 0) {
      document.title = `$${binancePrice.toLocaleString()} | Arb Pro`;
    } else {
      document.title = "Arbitrage Pro";
    }
  }, [binancePrice]);

  const fetchTradeHistory = async () => {
    try {
      const res = await fetch("http://127.0.0.1:8000/get_trades");
      const data = await res.json();
      if (!data.error) setTradeLog(data);
    } catch (e) { console.error("DB Sync Error", e); }
  };

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  useEffect(() => {
    fetchTradeHistory();
    const socket = new WebSocket("ws://127.0.0.1:8000/ws/market");

    socket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        setBinancePrice(data.binance || 0);
        setBybitPrice(data.kraken || 0);
        setSpread(data.spread || 0);
        setIsOp(data.opportunity || false);
        setLatency(data.latency || 0);
        setRisk(data.risk || "LOW");

        setSpreadData((prev) => [...prev.slice(-19), {
          time: new Date().toLocaleTimeString([], { second: "2-digit" }),
          spread: data.spread || 0,
        }]);

        if (data.opportunity && botRunning) {
          const newTrade = {
            id: Date.now(),
            time: new Date().toLocaleTimeString(),
            route: data.direction,
            profit: `$${(10000 * (data.net_profit / 100)).toFixed(2)}`
          };
          setTradeLog((prev) => [newTrade, ...prev].slice(0, 14));
          toast({ title: "TRADE EXECUTED", description: `${data.direction} successful.` });
        }
      } catch (err) { console.error("Data Stream Error", err); }
    };
    return () => socket.close();
  }, [botRunning, toast]);

  const handleSend = async () => {
    if (!input.trim()) return;
    setMessages(prev => [...prev, { role: 'user', text: input }]);
    setInput("");
    try {
      const res = await fetch("http://127.0.0.1:8000/ask_ai", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: input }),
      });
      const data = await res.json();
      setMessages(prev => [...prev, { role: 'ai', text: data.answer }]);
    } catch (e) { setMessages(prev => [...prev, { role: 'ai', text: "AI Core Unreachable." }]); }
  };

  return (
    <div className="flex h-screen w-full bg-[#0a0a0c] text-white overflow-hidden font-sans">
      {/* Sidebar Navigation */}
      <aside className="w-20 border-r border-white/10 bg-[#0f0f12] flex flex-col items-center py-8 gap-8">
        <div className="w-12 h-12 bg-green-500 rounded-2xl flex items-center justify-center font-black text-2xl text-black">Δ</div>
        <div className="flex flex-col gap-6 text-gray-500">
          <LayoutDashboard className="text-green-500 cursor-pointer" />
          <Activity className="hover:text-white cursor-pointer" />
          <Database className="hover:text-white cursor-pointer" />
          <Globe className="hover:text-white cursor-pointer" />
        </div>
      </aside>

      {/* Main Dashboard Panel */}
      <main className="flex-1 p-8 overflow-y-auto border-r border-white/5">
        <header className="flex justify-between items-center mb-8">
          <div>
            <h2 className="text-3xl font-black italic tracking-tighter text-green-500 uppercase">Arb_Pro_v3</h2>
            <div className="flex items-center gap-4 mt-1">
              <div className="flex items-center gap-2 text-[10px] text-gray-500 uppercase tracking-widest">
                <span className="h-1.5 w-1.5 rounded-full bg-green-500 animate-pulse"></span>
                Network_Stable
              </div>
              <div className={`text-[10px] font-bold px-2 py-0.5 rounded border ${latency < 150 ? 'border-green-500/20 text-green-500' : 'border-yellow-500/20 text-yellow-500'}`}>
                {latency}ms Latency
              </div>
              <div className={`text-[10px] font-bold px-2 py-0.5 rounded border ${risk === 'HIGH' ? 'border-red-500/20 text-red-500 animate-pulse' : 'border-blue-500/20 text-blue-500'}`}>
                Risk: {risk}
              </div>
            </div>
          </div>

          <Button
            className={botRunning ? "bg-red-500 hover:bg-red-600 font-bold" : "bg-green-500 text-black hover:bg-green-400 font-bold"}
            onClick={() => setBotRunning(!botRunning)}
          >
            {botRunning ? "TERMINATE_ALGO" : "EXECUTE_ALGO"}
          </Button>
        </header>

        {/* Global Metrics */}
        <div className="grid grid-cols-3 gap-6 mb-8">
          <MetricCard title="Binance (Live)" value={`$${binancePrice.toLocaleString()}`} />
          <MetricCard title="Bybit (Sim)" value={`$${bybitPrice.toLocaleString()}`} />
          <MetricCard title="Net Spread" value={`${spread.toFixed(3)}%`} isHighlighted={isOp} />
        </div>

        {/* Spread Visualizer */}
        <div className="bg-[#0f0f12] p-6 rounded-3xl border border-white/5 mb-8 h-[300px]">
          <SpreadChart data={spreadData} threshold={0.1} />
        </div>

        {/* Exchange Status Bar */}
        <div className="flex items-center gap-4 mb-4 px-2">
          <div className="flex items-center gap-3 bg-white/5 border border-white/10 rounded-full px-4 py-2">
            <span className="text-[9px] font-bold text-gray-500 uppercase tracking-widest">Binance</span>
            <span className="text-[12px] font-mono text-green-400">${binancePrice.toFixed(2)}</span>
          </div>
          <Zap size={14} className="text-gray-700" />
          <div className="flex items-center gap-3 bg-white/5 border border-white/10 rounded-full px-4 py-2">
            <span className="text-[9px] font-bold text-gray-500 uppercase tracking-widest">Bybit</span>
            <span className="text-[12px] font-mono text-purple-400">${bybitPrice.toFixed(2)}</span>
          </div>
          <div className="ml-auto text-[10px] font-medium text-gray-600 uppercase">
            Sync: {new Date().toLocaleTimeString()}
          </div>
        </div>

        {/* Trade History Table */}
        <div className="bg-[#0f0f12] rounded-3xl border border-white/5 overflow-hidden">
          <div className="px-6 py-4 border-b border-white/5 bg-white/[0.02] flex justify-between items-center">
            <div className="flex items-center gap-2">
              <Database size={14} className="text-green-500" />
              <span className="text-[10px] font-bold text-gray-400 uppercase tracking-widest">Real-Time_Executions</span>
            </div>
            <Button
              variant="ghost" size="sm" className="text-[10px] h-7 bg-white/5 border border-white/10 text-gray-400 hover:text-white"
              onClick={() => window.open("http://127.0.0.1:8000/download_trades")}
            >
              DOWNLOAD_REPORT.CSV
            </Button>
          </div>
          <div className="h-64 overflow-y-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="text-[10px] text-gray-600 border-b border-white/5 bg-black/20">
                  <th className="px-6 py-3 font-black tracking-widest">TIMESTAMP</th>
                  <th className="px-6 py-3 font-black tracking-widest">ROUTE_PATH</th>
                  <th className="px-6 py-3 text-right font-black tracking-widest">PROFIT_USD</th>
                </tr>
              </thead>
              <tbody className="text-xs font-mono">
                {tradeLog.map((trade, idx) => (
                  <tr key={idx} className="border-b border-white/5 hover:bg-white/[0.02] transition-colors">
                    <td className="px-6 py-3 text-gray-500">{trade.time}</td>
                    <td className="px-6 py-3 font-bold text-gray-200">{trade.route}</td>
                    <td className="px-6 py-3 text-right text-green-500 font-bold">{trade.profit}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </main>

      {/* AI Sidebar */}
      <aside className={`${chatOpen ? 'w-96' : 'w-16'} transition-all duration-300 border-l border-white/10 bg-[#0f0f12] flex flex-col`}>
        {chatOpen ? (
          <>
            <div className="p-6 border-b border-white/5 flex justify-between items-center">
              <h3 className="font-bold text-sm flex items-center gap-2">
                <BotIcon size={16} className="text-purple-400" /> AI_TERMINAL
              </h3>
              <button onClick={() => setChatOpen(false)} className="text-gray-500 hover:text-white text-xl">×</button>
            </div>
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
              {messages.map((m, i) => (
                <div key={i} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                  <div className={`max-w-[85%] p-3 rounded-2xl text-[11px] leading-relaxed ${m.role === 'user' ? 'bg-green-600 text-white shadow-lg' : 'bg-white/5 border border-white/10 text-gray-300'}`}>
                    {m.text}
                  </div>
                </div>
              ))}
              <div ref={chatEndRef} />
            </div>
            <div className="p-4 border-t border-white/5 flex gap-2">
              <input value={input} onChange={(e) => setInput(e.target.value)} onKeyPress={(e) => e.key === 'Enter' && handleSend()} placeholder="Query market conditions..." className="flex-1 bg-white/5 border border-white/10 rounded-xl px-4 py-2 text-xs focus:outline-none focus:border-green-500 text-white" />
              <button onClick={handleSend} className="p-2 bg-green-500 rounded-xl text-black hover:bg-green-400"><Send size={16} /></button>
            </div>
          </>
        ) : (
          <button onClick={() => setChatOpen(true)} className="h-full w-full flex flex-col items-center py-8 text-gray-500 hover:text-green-500 transition-colors"><MessageSquare size={24} /></button>
        )}
      </aside>
    </div>
  );
};

export default Index;