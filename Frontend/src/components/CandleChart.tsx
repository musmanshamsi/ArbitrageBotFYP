import React from 'react';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';

interface CandleChartProps {
  data: any[];
}

const CandleChart = ({ data }: CandleChartProps) => {
  // Ultra-Defensive: Ensure data has required numeric keys for the charts to draw
  const validData = Array.isArray(data) ? data.filter(d =>
    typeof d.time === 'number' && typeof d.close === 'number'
  ) : [];

  if (validData.length === 0) {
    return (
      <div className="w-full h-full flex items-center justify-center bg-[#0a0a0c] border border-red-950/20 text-red-900 text-[10px] animate-pulse">
        WAITING FOR PRICE FEED...
      </div>
    );
  }

  return (
    <div className="w-full h-[350px] bg-[#050505] rounded-3xl border border-white/5 p-4 flex flex-col shadow-2xl relative overflow-hidden group">
      <div className="flex justify-between items-center mb-4 px-2 relative z-10">
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse shadow-[0_0_10px_rgba(34,211,238,0.5)]"></div>
          <h3 className="text-[10px] font-black text-white/50 uppercase tracking-widest">Neural Market Flow</h3>
        </div>
        <div className="flex items-center gap-1.5 px-2 py-0.5 bg-cyan-500/5 rounded-full border border-cyan-500/10">
          <span className="text-[9px] font-mono text-cyan-400 font-bold uppercase tracking-wider">{validData.length} PKTS</span>
        </div>
      </div>

      <div className="flex-1 w-full min-h-0 relative z-10">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={validData}>
            <defs>
              <linearGradient id="cyanGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#22d3ee" stopOpacity={0.3} />
                <stop offset="95%" stopColor="#22d3ee" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#ffffff03" vertical={false} />
            <XAxis
              dataKey="time"
              type="number"
              domain={['dataMin', 'dataMax']}
              hide={true}
            />
            <YAxis
              domain={['auto', 'auto']}
              orientation="right"
              tick={{ fill: '#4b5563', fontSize: 10, fontWeight: 700 }}
              axisLine={false}
              tickLine={false}
              width={50}
              tickFormatter={(v) => v.toLocaleString()}
            />
            <Tooltip
              contentStyle={{ backgroundColor: '#0a0a0c', border: '1px solid #ffffff10', borderRadius: '12px', fontSize: '11px', color: '#fff' }}
              itemStyle={{ color: '#fff' }}
              cursor={{ stroke: '#ffffff10', strokeWidth: 1 }}
              labelFormatter={(t) => new Date(t).toLocaleTimeString()}
            />
            <Area
              type="monotone"
              dataKey="close"
              stroke="#22d3ee"
              strokeWidth={2}
              fill="url(#cyanGradient)"
              isAnimationActive={false}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

export default CandleChart;