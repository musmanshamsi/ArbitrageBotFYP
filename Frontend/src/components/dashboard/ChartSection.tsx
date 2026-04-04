import React, { useMemo } from "react";
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
  Cell,
} from "recharts";
import { AlertCircle } from "lucide-react";

interface ChartSectionProps {
  spreadData: any[];
  ohlcData: any[];
  threshold: number;
}

// Simulated data to ensure the charts render immediately
const simulatedSpreadData = Array.from({ length: 40 }, (_, i) => ({
  time: Date.now() - (40 - i) * 5000,
  spread: 0.05 + Math.random() * 0.15,
}));

const simulatedOhlcData = Array.from({ length: 30 }, (_, i) => {
  const base = 65000 + Math.random() * 1000;
  return {
    time: Date.now() - (30 - i) * 60000,
    open: base,
    high: base + Math.random() * 200,
    low: base - Math.random() * 200,
    close: base + (Math.random() - 0.5) * 150,
  };
});

const CustomTooltip = ({ active, payload, label }: any) => {
  if (active && payload && payload.length) {
    return (
      <div className="bg-[#0a0a0c] border border-white/10 p-3 rounded-lg shadow-2xl backdrop-blur-md">
        <p className="text-[10px] text-gray-500 uppercase font-bold mb-1">
          {new Date(label).toLocaleTimeString()}
        </p>
        <p className="text-sm font-mono text-green-400 font-bold">
          {payload[0].value.toFixed(4)}
        </p>
      </div>
    );
  }
  return null;
};

const ChartSection: React.FC<ChartSectionProps> = ({
  spreadData,
  ohlcData,
  threshold,
}) => {
  const finalSpreadData = spreadData && spreadData.length > 0 ? spreadData : simulatedSpreadData;
  const finalOhlcData = ohlcData && ohlcData.length > 0 ? ohlcData : simulatedOhlcData;
  const isLive = spreadData && spreadData.length > 0;

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 w-full">
      {/* SPREAD ANALYSIS CHART */}
      <div className="flex flex-col gap-2">
        <div className="flex justify-between items-center px-2">
          <h3 className="text-xs font-bold text-gray-400 uppercase tracking-widest border-l-2 border-purple-500 pl-2">
            Spread Analysis
          </h3>
          {!isLive && (
            <div className="flex items-center gap-1.5 text-[10px] text-orange-400/80 animate-pulse font-bold uppercase">
              <AlertCircle size={12} />
              Simulated Feed
            </div>
          )}
        </div>
        <div className="h-[300px] w-full bg-[#0a0a0c]/50 border border-white/5 rounded-2xl p-4 backdrop-blur-sm relative overflow-hidden group">
          <div className="absolute inset-x-0 bottom-0 h-px bg-gradient-to-r from-transparent via-purple-500/20 to-transparent"></div>
          
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={finalSpreadData}>
              <defs>
                <linearGradient id="colorSpread" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#a855f7" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#a855f7" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="rgba(255,255,255,0.03)" />
              <XAxis 
                dataKey="time" 
                hide 
              />
              <YAxis 
                domain={[0, 0.4]} 
                orientation="right" 
                tick={{ fontSize: 9, fill: '#4b5563' }} 
                axisLine={false}
                tickLine={false}
              />
              <Tooltip content={<CustomTooltip />} />
              <Area
                type="monotone"
                dataKey="spread"
                stroke="#a855f7"
                strokeWidth={2}
                fillOpacity={1}
                fill="url(#colorSpread)"
                isAnimationActive={false}
              />
            </AreaChart>
          </ResponsiveContainer>

          {/* Threshold Line overlay */}
          <div 
            className="absolute left-0 w-full border-t border-purple-500/40 border-dashed z-10 pointer-events-none transition-all duration-500"
            style={{ 
              bottom: `${Math.min(90, (threshold / 0.4) * 100)}%`,
              marginLeft: '4px',
              marginRight: '60px',
              width: 'calc(100% - 64px)'
            }}
          >
            <span className="absolute right-0 -top-4 text-[9px] text-purple-400/80 font-bold uppercase tracking-tighter">
              Target Threshold: {threshold.toFixed(2)}%
            </span>
          </div>
        </div>
      </div>

      {/* MARKET PRICE ACTION CHART */}
      <div className="flex flex-col gap-2">
        <div className="flex justify-between items-center px-2">
          <h3 className="text-xs font-bold text-gray-400 uppercase tracking-widest border-l-2 border-green-500 pl-2">
            Market Price Action (BTC/USDT)
          </h3>
        </div>
        <div className="h-[300px] w-full bg-[#0a0a0c]/50 border border-white/5 rounded-2xl p-4 backdrop-blur-sm relative overflow-hidden group">
          <div className="absolute inset-x-0 bottom-0 h-px bg-gradient-to-r from-transparent via-green-500/20 to-transparent"></div>
          
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={finalOhlcData}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="rgba(255,255,255,0.03)" />
              <XAxis dataKey="time" hide />
              <YAxis 
                domain={['auto', 'auto']} 
                orientation="right" 
                tick={{ fontSize: 9, fill: '#4b5563' }} 
                axisLine={false}
                tickLine={false}
              />
              <Tooltip 
                content={({ active, payload }: any) => {
                  if (active && payload && payload.length) {
                    const d = payload[0].payload;
                    return (
                      <div className="bg-[#0a0a0c] border border-white/10 p-3 rounded-lg shadow-2xl backdrop-blur-md text-[10px]">
                        <p className="text-gray-500 uppercase font-bold mb-1">{new Date(d.time).toLocaleTimeString()}</p>
                        <div className="grid grid-cols-2 gap-x-4 gap-y-1">
                          <span className="text-gray-400">O: <span className="text-white">${d.open.toFixed(2)}</span></span>
                          <span className="text-gray-400">C: <span className="text-white">${d.close.toFixed(2)}</span></span>
                          <span className="text-gray-400 text-green-400">H: ${d.high.toFixed(2)}</span>
                          <span className="text-gray-400 text-red-400">L: ${d.low.toFixed(2)}</span>
                        </div>
                      </div>
                    );
                  }
                  return null;
                }} 
              />
              <Bar dataKey="close" isAnimationActive={false}>
                {finalOhlcData.map((entry, index) => (
                  <Cell 
                    key={`cell-${index}`} 
                    fill={entry.close >= entry.open ? "#22c55e" : "#ef4444"} 
                    fillOpacity={0.8}
                  />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};

export default ChartSection;
