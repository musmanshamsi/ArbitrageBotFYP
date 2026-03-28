import React, { useState, useEffect } from 'react';

interface SpreadChartProps {
  data: { time: number; spread: number }[];
  threshold: number;
}

const SpreadChart = ({ data, threshold }: SpreadChartProps) => {
  // Memory bank for spread history
  const [spreadHistory, setSpreadHistory] = useState<{ time: number; spread: number }[]>([]);

  useEffect(() => {
    if (!Array.isArray(data) || data.length === 0) return;

    const newData = data.filter(d =>
      d &&
      typeof Number(d.time) === 'number' && !isNaN(Number(d.time)) &&
      typeof Number(d.spread) === 'number' && !isNaN(Number(d.spread))
    ).map(d => ({ time: Number(d.time), spread: Number(d.spread) }));

    if (newData.length > 0) {
      setSpreadHistory(prev => {
        const updatedHistory = newData.length > 1 ? newData : [...prev, newData[0]];
        return updatedHistory.slice(-60); // Keep last 60 ticks
      });
    }
  }, [data]);

  if (spreadHistory.length < 2) {
    return (
      <div className="w-full h-[380px] bg-[#050505] rounded-[2.5rem] border border-white/5 flex items-center justify-center text-gray-700 font-mono text-[10px]">
        BUILDING SPREAD HISTORY...
      </div>
    );
  }

  const width = 600;
  const height = 280;
  const padding = 20;

  const minSpread = 0;
  let localMaxSpread = 0;
  spreadHistory.forEach(d => {
    if (d.spread > localMaxSpread) localMaxSpread = d.spread;
  });

  const safeThreshold = Number.isFinite(Number(threshold)) ? Number(threshold) : 0;
  const maxSpread = Math.max(localMaxSpread, safeThreshold + 0.1) * 1.1;
  const spreadRange = Math.max(maxSpread - minSpread, 0.00001);

  const getX = (index: number) => padding + (index * (width - 2 * padding) / (Math.max(spreadHistory.length - 1, 1)));
  const getY = (spread: number) => height - padding - ((spread - minSpread) / spreadRange * (height - 2 * padding));

  const areaPoints = spreadHistory.map((d, i) => `${getX(i)},${getY(d.spread)}`);
  const areaPath = `M${getX(0)},${height - padding} L${areaPoints.join(' L')} L${getX(spreadHistory.length - 1)},${height - padding} Z`;
  const linePath = `M${areaPoints.join(' L')}`;
  const thresholdY = getY(safeThreshold);

  return (
    <div className="w-full h-[380px] bg-[#050505] rounded-[2.5rem] border border-white/5 p-6 flex flex-col shadow-2xl relative overflow-hidden group hover:border-white/10 transition-colors">
      <div className="absolute top-0 right-0 w-32 h-32 bg-purple-500/5 blur-[80px]"></div>

      <div className="flex justify-between items-center mb-6 px-2 relative z-10">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-purple-500/10 rounded-xl">
            <div className="w-2 h-2 rounded-full bg-purple-500 animate-pulse shadow-[0_0_10px_rgba(168,85,247,0.5)]"></div>
          </div>
          <div>
            <h3 className="text-sm font-black text-white tracking-tight uppercase">Basis Matrix</h3>
            <p className="text-[9px] text-gray-500 font-mono uppercase tracking-widest">Delta Variance (%)</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-[9px] font-mono text-yellow-500 font-bold bg-yellow-500/5 px-2 py-0.5 rounded border border-yellow-500/10 uppercase tracking-widest">{safeThreshold}% LIMIT</span>
        </div>
      </div>

      <div className="w-full h-[280px] relative z-20 mt-2 border border-dashed border-white/5">
        <svg viewBox={`0 0 600 280`} width="100%" height="100%" preserveAspectRatio="none" className="overflow-visible">
          <defs>
            <linearGradient id="spreadGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#a855f7" stopOpacity={0.4} />
              <stop offset="100%" stopColor="#a855f7" stopOpacity={0} />
            </linearGradient>
          </defs>

          <line x1={padding} y1={thresholdY} x2={width - padding} y2={thresholdY} stroke="#eab308" strokeWidth={1} strokeDasharray="4 4" />
          <path d={areaPath} fill="url(#spreadGrad)" className="transition-all duration-300" />
          <path d={linePath} fill="none" stroke="#a855f7" strokeWidth={2.5} strokeLinecap="round" strokeLinejoin="round" />
          <text x={width - padding + 5} y={thresholdY} fill="#eab308" fontSize={8} fontWeight="bold">LIMIT</text>
        </svg>
      </div>
    </div>
  );
};

export default SpreadChart;