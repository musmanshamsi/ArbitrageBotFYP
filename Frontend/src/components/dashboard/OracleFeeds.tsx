import React from "react";
import { SlidersHorizontal, Activity } from "lucide-react";

interface OracleFeedsProps {
  binancePrice: number;
  bybitPrice: number;
  spread: number;
  opportunity: boolean;
  threshold: number;
  handleThresholdChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
}

const OracleFeeds: React.FC<OracleFeedsProps> = ({
  binancePrice,
  bybitPrice,
  spread,
  opportunity,
  threshold,
  handleThresholdChange,
}) => {
  return (
    <div className="grid grid-cols-4 gap-4 border-b border-white/10 pb-6 mb-6">
      <div className="flex flex-col">
        <p className="text-[10px] text-gray-500 uppercase font-black tracking-widest mb-1.5 opacity-60">Binance Oracle</p>
        <div className="flex items-end gap-2 text-xl font-mono text-white font-black stroke-green-500 drop-shadow-[0_0_10px_rgba(34,197,94,0.1)]">
          ${(binancePrice || 0).toLocaleString()}
        </div>
      </div>
      <div className="flex flex-col">
        <p className="text-[10px] text-gray-500 uppercase font-black tracking-widest mb-1.5 opacity-60">Bybit Oracle</p>
        <div className="flex items-end gap-2 text-xl font-mono text-white font-black drop-shadow-[0_0_10px_rgba(255,255,255,0.05)]">
          ${(bybitPrice || 0).toLocaleString()}
        </div>
      </div>
      <div className="flex flex-col">
        <p className="text-[10px] text-gray-500 uppercase font-black tracking-widest mb-1.5 opacity-60">Live Current Spread</p>
        <div className={`text-xl font-mono font-black flex items-center gap-2 ${opportunity ? 'text-green-500 animate-pulse' : 'text-gray-300'}`}>
          <Activity size={18} className={opportunity ? 'text-green-500' : 'text-gray-600'} />
          {(spread || 0).toFixed(3)}%
        </div>
      </div>
      <div className="bg-[#111116] p-4 rounded-2xl border border-white/10 flex flex-col justify-center shadow-inner group transition-all hover:border-purple-500/30">
        <div className="flex justify-between items-center mb-2.5">
          <p className="text-[10px] text-purple-400 uppercase font-bold flex items-center gap-1.5 tracking-widest opacity-80 decoration-purple-500">
            <SlidersHorizontal size={10} className="group-hover:rotate-180 transition-transform duration-500" /> 
            Execution Threshold
          </p>
          <span className="text-xs font-mono font-black text-white px-2 py-0.5 bg-purple-500/20 rounded-md border border-purple-500/20 drop-shadow-[0_0_8px_rgba(168,85,247,0.2)]">
            {threshold.toFixed(2)}%
          </span>
        </div>
        <input 
          type="range" 
          min="0.01" 
          max="0.50" 
          step="0.01" 
          value={threshold} 
          onChange={handleThresholdChange} 
          className="w-full h-1 bg-gray-800 rounded-lg appearance-none cursor-pointer accent-purple-500 focus:outline-none hover:accent-purple-400 shadow-[0_0_10px_rgba(168,85,247,0.1)] transition-all" 
        />
      </div>
    </div>
  );
};

export default OracleFeeds;
