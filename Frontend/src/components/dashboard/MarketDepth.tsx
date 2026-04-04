import React from 'react';
import { Layers } from 'lucide-react';

interface OrderBookPoint {
  price: number;
  volume: number;
}

interface MarketDepthProps {
  orderBook: {
    bids: any[];
    asks: any[];
  } | null;
}

const MarketDepth: React.FC<MarketDepthProps> = ({ orderBook }) => {
  if (!orderBook) return <div className="p-4 text-center text-gray-500">Loading Depth...</div>;

  const renderSide = (data: any[], type: "bids" | "asks") => {
    const maxVolume = Math.max(...data.map(d => d[1] || 0), 1);

    return (
      <div className="flex flex-col gap-1 text-xs w-1/2">
        <div className="flex justify-between font-bold mb-2 text-gray-400 border-b border-gray-800 pb-1">
          <span>Price</span>
          <span>Size</span>
        </div>
        {data.slice(0, 10).map((lvl, index) => {
          const price = typeof lvl[0] === 'number' ? lvl[0].toFixed(2) : String(lvl[0]);
          const vol = lvl[1] || 0;
          const percentage = (vol / maxVolume) * 100;
          
          return (
            <div key={index} className="relative flex justify-between px-1 py-1 group overflow-hidden">
              <div 
                className={`absolute inset-0 opacity-15 origin-left`} 
                style={{
                  width: `${percentage}%`,
                  background: type === "bids" ? '#22c55e' : '#ef4444'
                }}
              />
              <span className={`z-10 font-medium ${type === "bids" ? "text-green-500" : "text-red-500"}`}>
                ${price}
              </span>
              <span className="z-10 text-gray-300 font-mono">
                {vol.toFixed(4)}
              </span>
            </div>
          );
        })}
      </div>
    );
  };

  return (
    <div className="bg-[#0a0a0c]/40 border border-white/5 rounded-3xl p-6 shadow-2xl backdrop-blur-md relative h-[380px]">
      <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-transparent via-blue-500/20 to-transparent"></div>
      
      <div className="flex items-center gap-3 mb-6">
        <div className="p-2 bg-blue-500/10 rounded-lg text-blue-400 shadow-[0_0_10px_rgba(59,130,246,0.3)]">
          <Layers size={20} />
        </div>
        <h2 className="text-xl font-bold tracking-widest text-[#f5f5f5]">MARKET DEPTH</h2>
      </div>

      <div className="flex gap-4">
        {renderSide(orderBook.bids, "bids")}
        {renderSide(orderBook.asks, "asks")}
      </div>
    </div>
  );
};

export default MarketDepth;
