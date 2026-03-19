import { useState, useRef, useEffect } from "react";
import { Send, Bot, User } from "lucide-react";
import { Button } from "@/components/ui/button";

interface Message {
  id: number;
  role: "user" | "assistant";
  content: string;
  timestamp: string;
}

const initialMessages: Message[] = [
  {
    id: 1,
    role: "assistant",
    content: "Hello! I'm your Agentic AI trading assistant. I monitor cross-exchange arbitrage opportunities using a GRU-based prediction model. Ask me anything about the current market conditions or my trading rationale.",
    timestamp: "10:00 AM",
  },
  {
    id: 2,
    role: "user",
    content: "Why did you flag the last trade opportunity?",
    timestamp: "10:01 AM",
  },
  {
    id: 3,
    role: "assistant",
    content: "Great question. Here's my analysis:\n\n**Signal Detection:** The GRU model detected a 0.42% spread between Binance ($67,234) and Bybit ($67,516) at 09:58 UTC.\n\n**Confidence Score:** 87.3% — based on the last 120 data points showing a converging trend pattern.\n\n**Risk Assessment:** Current volatility index is low (VIX-crypto: 22.4), reducing slippage risk. The predicted execution window was ~4.2 seconds.\n\n**Recommendation:** BUY on Binance → SELL on Bybit with an estimated profit of $28.20 after fees (0.1% taker fee on both sides).",
    timestamp: "10:01 AM",
  },
  {
    id: 4,
    role: "user",
    content: "What's the current market sentiment?",
    timestamp: "10:03 AM",
  },
  {
    id: 5,
    role: "assistant",
    content: "**Current Market Sentiment: Cautiously Bullish** 📈\n\n- BTC dominance: 52.3% (↑ 0.4% from yesterday)\n- Fear & Greed Index: 61 (Greed territory)\n- 24h volume across monitored exchanges: $34.2B\n- Funding rates are slightly positive, indicating mild long bias\n\nThe spread opportunities have been averaging 0.18% today, slightly below our 0.30% threshold. I'm monitoring for any volatility spikes that could create actionable opportunities.",
    timestamp: "10:03 AM",
  },
];

const AIAssistant = () => {
  const [messages, setMessages] = useState<Message[]>(initialMessages);
  const [input, setInput] = useState("");
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  const handleSend = () => {
    if (!input.trim()) return;

    const userMsg: Message = {
      id: messages.length + 1,
      role: "user",
      content: input,
      timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
    };

    setMessages((prev) => [...prev, userMsg]);
    setInput("");

    // Simulate AI response
    setTimeout(() => {
      const aiMsg: Message = {
        id: messages.length + 2,
        role: "assistant",
        content: "I'm currently processing your query against the latest market data. Based on the GRU model's most recent forward pass, the predicted spread for the next 5 minutes is **0.24%** — below our action threshold. I'll alert you immediately when conditions change.\n\nIs there anything specific you'd like me to monitor?",
        timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
      };
      setMessages((prev) => [...prev, aiMsg]);
    }, 1200);
  };

  return (
    <div className="flex h-full flex-col">
      {/* Messages Area */}
      <div ref={scrollRef} className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`flex gap-3 animate-slide-up ${msg.role === "user" ? "flex-row-reverse" : ""}`}
          >
            <div
              className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-full ${
                msg.role === "assistant" ? "bg-success/20 text-success" : "bg-accent/20 text-accent"
              }`}
            >
              {msg.role === "assistant" ? <Bot className="h-4 w-4" /> : <User className="h-4 w-4" />}
            </div>
            <div
              className={`max-w-[75%] rounded-lg px-4 py-3 text-sm leading-relaxed ${
                msg.role === "assistant"
                  ? "bg-card border border-border text-foreground"
                  : "bg-accent/20 text-foreground"
              }`}
            >
              {/* Simple markdown-like rendering */}
              {msg.content.split("\n").map((line, i) => (
                <p key={i} className={i > 0 ? "mt-2" : ""}>
                  {line.split(/(\*\*.*?\*\*)/).map((part, j) =>
                    part.startsWith("**") && part.endsWith("**") ? (
                      <strong key={j} className="font-semibold text-foreground">
                        {part.slice(2, -2)}
                      </strong>
                    ) : (
                      <span key={j}>{part}</span>
                    )
                  )}
                </p>
              ))}
              <span className="mt-2 block text-xs text-muted-foreground">{msg.timestamp}</span>
            </div>
          </div>
        ))}
      </div>

      {/* Input Area */}
      <div className="border-t border-border p-4">
        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSend()}
            placeholder="Ask the AI about market conditions, trade rationale..."
            className="flex-1 rounded-lg border border-border bg-secondary/50 px-4 py-3 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring"
          />
          <Button onClick={handleSend} size="lg" className="h-12 px-4">
            <Send className="h-4 w-4" />
          </Button>
        </div>
      </div>
    </div>
  );
};

export default AIAssistant;
