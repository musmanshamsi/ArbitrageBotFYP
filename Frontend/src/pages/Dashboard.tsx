import React, { useState, useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";
import { useToast } from "@/hooks/use-toast";
import { 
  LayoutDashboard, 
  Activity, 
  Database, 
  BookOpen, 
  Layout 
} from "lucide-react";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip";

// Import Modular Components
import Header from "@/components/dashboard/Header";
import PortfolioMetrics from "@/components/dashboard/PortfolioMetrics";
import OracleFeeds from "@/components/dashboard/OracleFeeds";
import ChartSection from "@/components/dashboard/ChartSection";
import ExecutionLedger from "@/components/dashboard/ExecutionLedger";
import Sidebar from "@/components/dashboard/Sidebar";
import TradeApprovalModal from "@/components/TradeApprovalModal";

const Dashboard = () => {
  const { toast } = useToast();
  const navigate = useNavigate();
  const chatEndRef = useRef<HTMLDivElement>(null);

  // --- STATE MANAGEMENT ---
  const [botRunning, setBotRunning] = useState(false);
  const [chatOpen, setChatOpen] = useState(true);
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState([
    { role: 'ai', text: 'Arbitrage Bot System Online. Monitoring cross-exchange liquidity.' }
  ]);
  
  const [marketData, setMarketData] = useState<any>(null);
  const [spreadData, setSpreadData] = useState<any[]>([]);
  const [ohlcData, setOhlcData] = useState<any[]>([]);
  const [tradeLog, setTradeLog] = useState<any[]>([]);
  const [totalProfit, setTotalProfit] = useState(0.00);
  const [binanceBalance, setBinanceBalance] = useState(0.00);
  const [bybitBalance, setBybitBalance] = useState(0.00);
  const [pendingTrade, setPendingTrade] = useState<any>(null);
  const [approvalModalOpen, setApprovalModalOpen] = useState(false);
  const [threshold, setThreshold] = useState(0.08);

  const handleLogout = () => {
    localStorage.removeItem('token');
    navigate('/login', { replace: true });
  };

  // --- DATA FETCHING & WEBSOCKETS ---
  useEffect(() => {
    const fetchDatabaseHistory = async () => {
      const token = localStorage.getItem('token');
      try {
        const res = await fetch("http://127.0.0.1:8000/api/history", {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        if (!res.ok) return handleLogout();
        const data = await res.json();
        setTradeLog(data.history || []);
        setTotalProfit(data.total_profit || 0);
      } catch (e) {
        console.error("Failed to fetch history:", e);
      }
    };
    fetchDatabaseHistory();
  }, [navigate]);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) return;

    const socket = new WebSocket(`ws://127.0.0.1:8000/ws/market?token=${token}`);

    socket.onmessage = (event) => {
      const data = JSON.parse(event.data);

      if (data.type === "ai_msg") {
        setMessages(prev => [...prev.slice(-49), { role: 'ai', text: data.text }]);
      } else if (data.type === "pending_trade") {
        setPendingTrade(data.trade);
        setApprovalModalOpen(true);
      } else if (data.type === "trade") {
        setTradeLog(prev => [data.trade, ...prev]);
        if (data.raw_profit !== undefined) setTotalProfit(p => p + data.raw_profit);
        toast({ 
          title: "Arbitrage Executed", 
          description: `Captured: ${data.trade.profit}`, 
          className: "bg-green-500 text-black font-bold border-none shadow-[0_0_20px_rgba(34,197,94,0.4)]" 
        });
      } else if (data.type === "market") {
        setMarketData(data);
        if (data.binance_bal !== undefined) setBinanceBalance(data.binance_bal);
        if (data.bybit_bal !== undefined) setBybitBalance(data.bybit_bal);

        // Spread Tracking
        setSpreadData(prev => [...prev.slice(-39), {
          time: Date.now(),
          spread: Number(data.spread) || 0,
        }]);

        // OHLC Tracking
        const currentPrice = Number(data.binance || data.price || 0);
        if (currentPrice > 0) {
          setOhlcData(prev => {
            const now = Date.now();
            const lastCandle = prev[prev.length - 1];
            if (!lastCandle || (now - lastCandle.time > 5000)) {
              return [...prev.slice(-39), {
                time: now, open: currentPrice, high: currentPrice, low: currentPrice, close: currentPrice
              }];
            } else {
              return [...prev.slice(0, -1), {
                ...lastCandle,
                close: currentPrice,
                high: Math.max(lastCandle.high, currentPrice),
                low: Math.min(lastCandle.low, currentPrice)
              }];
            }
          });
        }
      }
    };

    socket.onclose = (event) => { if (event.code === 1008) handleLogout(); };
    socket.onerror = () => { console.error("WebSocket Error"); };
    return () => socket.close();
  }, [toast, navigate]);

  // --- ACTIONS ---
  const handleSend = async () => {
    if (!input.trim()) return;
    const userMsg = input;
    setMessages(prev => [...prev.slice(-49), { role: 'user', text: userMsg }]);
    setInput("");
    
    const token = localStorage.getItem('token');
    try {
      const res = await fetch("http://127.0.0.1:8000/api/chat", {
        method: "POST",
        headers: { 
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}` 
        },
        body: JSON.stringify({ question: userMsg }),
      });
      
      const data = await res.json();
      if (data.status === "success") {
        setMessages(prev => [...prev.slice(-49), { role: 'ai', text: data.response }]);
      } else {
        setMessages(prev => [...prev, { role: 'ai', text: "The analyst is currently tied up with market data. Please try again soon." }]);
      }
    } catch (err) {
      console.error("Chat Error:", err);
      setMessages(prev => [...prev, { role: 'ai', text: "Network divergence detected. AI Core unreachable." }]);
    }
  };

  useEffect(() => chatEndRef.current?.scrollIntoView({ behavior: "smooth" }), [messages]);

  const toggleBot = async () => {
    const token = localStorage.getItem('token');
    const newState = !botRunning;
    try {
      setBotRunning(newState);
      await fetch("http://127.0.0.1:8000/toggle_bot", {
        method: "POST",
        headers: { "Content-Type": "application/json", "Authorization": `Bearer ${token}` },
        body: JSON.stringify({ active: newState }),
      });
    } catch (e) {
      setBotRunning(!newState);
      toast({ title: "System Offline", description: "Could not reach trading engine.", variant: "destructive" });
    }
  };

  const handleThresholdChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const token = localStorage.getItem('token');
    const newVal = parseFloat(e.target.value);
    setThreshold(newVal);
    try {
      await fetch("http://127.0.0.1:8000/api/threshold", {
        method: "POST",
        headers: { "Content-Type": "application/json", "Authorization": `Bearer ${token}` },
        body: JSON.stringify({ threshold: newVal }),
      });
    } catch (err) { console.error(err); }
  };

  const handleTradeApproval = async (approved: boolean) => {
    const token = localStorage.getItem('token');
    setApprovalModalOpen(false);
    setPendingTrade(null);
    try {
      await fetch("http://127.0.0.1:8000/api/trade/approve", {
        method: "POST",
        headers: { "Content-Type": "application/json", "Authorization": `Bearer ${token}` },
        body: JSON.stringify({ decision: approved ? "APPROVE" : "REJECT" }),
      });
    } catch (err) { console.error(err); }
  };

  const grandTotal = binanceBalance + bybitBalance + totalProfit;

  return (
    <div className="flex h-screen w-full bg-[#050505] text-gray-200 overflow-hidden font-sans relative">
      
      {/* BACKGROUND DECORATION */}
      <div className="absolute inset-0 z-0 pointer-events-none overflow-hidden">
        <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-purple-500/5 blur-[120px] rounded-full"></div>
        <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-green-500/5 blur-[120px] rounded-full"></div>
      </div>

      {pendingTrade && (
        <TradeApprovalModal
          isOpen={approvalModalOpen}
          onApprove={() => handleTradeApproval(true)}
          onReject={() => handleTradeApproval(false)}
          {...pendingTrade}
        />
      )}

      {/* LEFT STATIC NAVBAR */}
      <aside className="w-20 border-r border-white/5 bg-[#0a0a0c]/80 backdrop-blur-xl flex flex-col items-center py-8 gap-8 z-20">
        <div className="w-11 h-11 bg-gradient-to-br from-green-400 to-green-700 rounded-2xl flex items-center justify-center font-black text-xl text-black shadow-[0_0_25px_rgba(34,197,94,0.4)] hover:scale-105 transition-transform cursor-pointer">A</div>
        <nav className="flex flex-col gap-8 text-gray-600">
          <Tooltip><TooltipTrigger asChild><button className="p-3 text-green-500 bg-green-500/10 rounded-xl shadow-[inset_0_0_10px_rgba(34,197,94,0.1)]"><LayoutDashboard size={22} /></button></TooltipTrigger><TooltipContent side="right">Market Dashboard</TooltipContent></Tooltip>
          <Tooltip><TooltipTrigger asChild><button className="p-3 hover:text-gray-300 transition-colors"><Activity size={22} /></button></TooltipTrigger><TooltipContent side="right">Execution Feed</TooltipContent></Tooltip>
          <Tooltip><TooltipTrigger asChild><button className="p-3 hover:text-gray-300 transition-colors"><Database size={22} /></button></TooltipTrigger><TooltipContent side="right">Database Status</TooltipContent></Tooltip>
          <Tooltip><TooltipTrigger asChild><button onClick={() => navigate("/blog")} className="p-3 hover:text-green-500 hover:bg-green-500/5 rounded-xl transition-all"><BookOpen size={22} /></button></TooltipTrigger><TooltipContent side="right">Internal Blog</TooltipContent></Tooltip>
        </nav>
      </aside>

      {/* MAIN CENTER DASHBOARD */}
      <main className="flex-1 p-8 overflow-y-auto flex flex-col gap-8 scrollbar-hide z-10">
        <Header 
          botRunning={botRunning} 
          status={marketData?.status || "INITIALIZING..."} 
          latency={marketData?.latency || 0}
          toggleBot={toggleBot}
          handleLogout={handleLogout}
        />

        <div className="flex-shrink-0">
          <PortfolioMetrics 
            grandTotal={grandTotal}
            totalProfit={totalProfit}
            binanceBalance={binanceBalance}
            bybitBalance={bybitBalance}
          />
        </div>

        <div className="bg-[#0a0a0c]/40 border border-white/5 rounded-[2.5rem] p-8 shadow-2xl backdrop-blur-md relative overflow-hidden flex-shrink-0">
          <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-transparent via-purple-500/20 to-transparent"></div>
          
          <OracleFeeds 
            binancePrice={marketData?.binance || 0}
            bybitPrice={marketData?.bybit || 0}
            spread={marketData?.spread || 0}
            opportunity={marketData?.opportunity || false}
            threshold={threshold}
            handleThresholdChange={handleThresholdChange}
          />

          <ChartSection 
            spreadData={spreadData}
            ohlcData={ohlcData}
            threshold={threshold}
          />
        </div>

        <div className="flex-shrink-0 mb-8">
          <ExecutionLedger tradeLog={tradeLog} />
        </div>
      </main>

      {/* RIGHT SIDEBAR (AI LOGIC CORE) */}
      <Sidebar 
        chatOpen={chatOpen}
        setChatOpen={setChatOpen}
        messages={messages}
        input={input}
        setInput={setInput}
        handleSend={handleSend}
        chatEndRef={chatEndRef}
      />
    </div>
  );
};

export default Dashboard;
