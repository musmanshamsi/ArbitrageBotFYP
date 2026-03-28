import React from "react";
import { TrendingUp, Activity } from "lucide-react";

interface PortfolioMetricsProps {
  grandTotal: number;
  totalProfit: number;
  binanceBalance: number;
  bybitBalance: number;
}

const PortfolioMetrics: React.FC<PortfolioMetricsProps> = ({
  grandTotal,
  totalProfit,
  binanceBalance,
  bybitBalance,
}) => {
  return (
    <section className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
      {/* NET EQUITY CARD */}
      <div className="md:col-span-1 bg-gradient-to-br from-[#0a0a0c] via-[#111116] to-[#050505] border border-white/10 p-6 rounded-2xl relative overflow-hidden group shadow-2xl">
        <div className="absolute top-0 right-0 w-32 h-32 bg-green-500/5 blur-[50px] group-hover:bg-green-500/10 transition-colors"></div>
        <p className="text-[10px] text-gray-500 font-bold uppercase tracking-[0.2em] mb-2">Net Account Equity</p>
        <h2 className="text-4xl font-black text-white mb-2 tracking-tight">
          ${grandTotal.toLocaleString(undefined, { minimumFractionDigits: 2 })}
        </h2>
        <div className="inline-flex items-center gap-1.5 px-2 py-1 bg-green-500/10 text-green-400 text-xs font-bold rounded-lg border border-green-500/20 shadow-[0_0_10px_rgba(34,197,94,0.1)]">
          <TrendingUp size={12} /> +${totalProfit.toFixed(2)} Total Profit
        </div>
      </div>

      <VaultCard name="Binance" color="text-yellow-500" bg="bg-yellow-500/10" balance={binanceBalance} icon="binance" />
      <VaultCard name="Bybit" color="text-orange-500" bg="bg-orange-500/10" balance={bybitBalance} icon="bybit" />
    </section>
  );
};

const VaultCard = ({ name, color, bg, balance, icon }: any) => {
  return (
    <div className="bg-[#0a0a0c] border border-white/5 rounded-2xl p-5 relative overflow-hidden flex flex-col justify-between group hover:border-white/10 transition-all duration-300 shadow-lg">
      <div className="absolute top-0 right-0 w-16 h-16 bg-white/[0.02] -mr-8 -mt-8 rounded-full blur-2xl group-hover:bg-white/[0.05]"></div>
      <div className="flex justify-between items-start mb-4 relative z-10">
        <div>
          <h3 className={`${color} font-bold text-sm uppercase tracking-widest`}>{name}</h3>
          <span className="text-[9px] text-gray-500 uppercase font-black">Exchange Vault Status</span>
        </div>
        <div className={`p-2.5 ${bg} rounded-xl shadow-inner`}>
          {icon === 'binance' ? <TrendingUp size={16} className={color} /> : <Activity size={16} className={color} />}
        </div>
      </div>
      <div className="space-y-2 relative z-10">
        <div className="flex justify-between items-center bg-[#050505]/40 px-3 py-2.5 rounded-xl border border-white/5 shadow-inner">
          <span className="text-gray-500 text-[10px] uppercase font-extrabold tracking-tighter">Liquid Capital</span>
          <span className="font-mono text-gray-200 text-sm font-black">
            ${(balance || 0).toLocaleString(undefined, { minimumFractionDigits: 2 })}
          </span>
        </div>
      </div>
    </div>
  );
};

export default PortfolioMetrics;
