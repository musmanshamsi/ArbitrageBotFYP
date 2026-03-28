import React, { useState, useEffect } from 'react';

interface CandleChartProps {
  data: any;
}

const CandleChart = ({ data }: CandleChartProps) => {
  const [chartHistory, setChartHistory] = useState<any[]>([]);

  useEffect(() => {
    // 1. Bulletproof data conversion: Handles both Arrays and Single Objects from WebSockets
    const rawArray = Array.isArray(data) ? data : data ? [data] : [];
    if (rawArray.length === 0) return;

    // 2. Safely parse numbers, treating missing values as the current price if necessary
    const newData = rawArray.map(d => {
      const close = Number(d?.close || d?.price || 0);
      return {
        time: Number(d?.time || Date.now()),
        open: Number(d?.open || close),
        high: Number(d?.high || close),
        low: Number(d?.low || close),
        close: close
      };
    }).filter(d => d.close > 0); // Only accept if we have a valid price

    if (newData.length > 0) {
      setChartHistory(prev => {
        const updatedHistory = newData.length > 1 ? newData : [...prev, newData[0]];
        return updatedHistory.slice(-60);
      });
    }
  }, [data]);

  // If we have no history yet, show the loading state
  if (chartHistory.length === 0) {
    return (
      <div className="w-full h-[380px] bg-[#050505] rounded-[2.5rem] border border-white/5 flex flex-col items-center justify-center text-gray-700 font-mono text-[10px]">
        <div className="w-6 h-6 border-2 border-white/5 border-t-green-500 rounded-full animate-spin mb-3"></div>
        WAITING FOR WEBSOCKET DATA...
      </div>
    );
  }

  // --- CHART MATH ---
  const width = 600;
  const height = 280;
  const padding = 20;

  const minPrice = Math.min(...chartHistory.map(d => d.low)) * 0.9995;
  const maxPrice = Math.max(...chartHistory.map(d => d.high)) * 1.0005;
  const priceRange = Math.max(maxPrice - minPrice, 0.0001);

  const getX = (index: number) => padding + (index * (width - 2 * padding) / (Math.max(chartHistory.length - 1, 1)));
  const getY = (price: number) => height - padding - ((price - minPrice) / priceRange * (height - 2 * padding));

  const barWidth = Math.max((width - 2 * padding) / Math.max(chartHistory.length, 1) * 0.6, 2);

  return (
    <div className="w-full h-[380px] bg-[#050505] rounded-[2.5rem] border border-white/5 p-6 flex flex-col shadow-2xl relative overflow-hidden">

      {/* HEADER */}
      <div className="flex justify-between items-center mb-6 px-2 relative z-10">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-green-500/10 rounded-xl">
            <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></div>
          </div>
          <div>
            <h3 className="text-sm font-black text-white uppercase">Market Flow</h3>
            <p className="text-[9px] text-gray-500 font-mono uppercase tracking-widest">Points in Memory: {chartHistory.length}</p>
          </div>
        </div>
        <div className="text-right">
          <p className="text-[9px] text-gray-600 font-bold uppercase">Price</p>
          <p className="text-xs font-mono font-black text-green-400">${chartHistory[chartHistory.length - 1].close.toFixed(2)}</p>
        </div>
      </div>

      {/* DEBUG HUD - This will print exactly what math is being calculated */}
      <div className="absolute top-20 left-6 text-[10px] font-mono text-white/50 z-50 pointer-events-none">
        <p>Min: {minPrice.toFixed(2)}</p>
        <p>Max: {maxPrice.toFixed(2)}</p>
        <p>Range: {priceRange.toFixed(2)}</p>
        <p>Last Y Coord: {getY(chartHistory[chartHistory.length - 1].close).toFixed(2)}px</p>
      </div>

      {/* CHART SVG */}
      <div className="w-full h-[280px] relative z-20 mt-2 border border-dashed border-red-500/20 bg-white/5">
        <svg viewBox={`0 0 600 280`} width="100%" height="100%" preserveAspectRatio="none">
          {chartHistory.map((d, i) => {
            const x = getX(i);
            const yHigh = getY(d.high);
            const yLow = getY(d.low);
            const yOpen = getY(d.open);
            const yClose = getY(d.close);

            const isUp = d.close >= d.open;
            const color = isUp ? '#22c55e' : '#ef4444';

            // Failsafe for missing coordinates
            if (isNaN(x) || isNaN(yHigh) || isNaN(yLow)) return null;

            return (
              <g key={i}>
                {/* Wick */}
                <line x1={x} y1={yHigh} x2={x} y2={yLow} stroke={color} strokeWidth={2} />
                {/* Body */}
                <rect
                  x={x - barWidth / 2}
                  y={Math.min(yOpen, yClose)}
                  width={barWidth}
                  height={Math.max(Math.abs(yOpen - yClose), 2)}
                  fill={color}
                />
                {/* Debug Dot at Close Price */}
                <circle cx={x} cy={yClose} r={2} fill="white" />
              </g>
            );
          })}
        </svg>
      </div>
    </div>
  );
};

export default CandleChart;