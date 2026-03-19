import { Button } from "@/components/ui/button";
import { CheckCircle, XCircle, TrendingUp, ArrowRight } from "lucide-react";

interface TradeApprovalModalProps {
  isOpen: boolean;
  onApprove: () => void;
  onReject: () => void;
  buyExchange: string;
  sellExchange: string;
  buyPrice: number;
  sellPrice: number;
  spread: number;
  predictedProfit: number;
}

const TradeApprovalModal = ({
  isOpen,
  onApprove,
  onReject,
  buyExchange,
  sellExchange,
  buyPrice,
  sellPrice,
  spread,
  predictedProfit,
}: TradeApprovalModalProps) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-background/80 backdrop-blur-sm animate-slide-up">
      <div className="w-full max-w-md rounded-lg border border-success/30 bg-card p-6 shadow-2xl glow-green">
        {/* Header */}
        <div className="flex items-center gap-3 mb-6">
          <div className="flex h-10 w-10 items-center justify-center rounded-full bg-success/20">
            <TrendingUp className="h-5 w-5 text-success" />
          </div>
          <div>
            <h2 className="text-lg font-bold text-foreground">Arbitrage Opportunity Detected</h2>
            <p className="text-sm text-muted-foreground">Human approval required before execution</p>
          </div>
        </div>

        {/* Trade Details */}
        <div className="space-y-3 mb-6">
          <div className="flex items-center justify-between rounded-md bg-secondary/50 p-3">
            <div>
              <p className="text-xs text-muted-foreground">Buy on {buyExchange}</p>
              <p className="text-lg font-bold font-mono text-foreground">${buyPrice.toLocaleString()}</p>
            </div>
            <ArrowRight className="h-5 w-5 text-muted-foreground" />
            <div className="text-right">
              <p className="text-xs text-muted-foreground">Sell on {sellExchange}</p>
              <p className="text-lg font-bold font-mono text-foreground">${sellPrice.toLocaleString()}</p>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div className="rounded-md bg-secondary/50 p-3">
              <p className="text-xs text-muted-foreground">Spread</p>
              <p className="text-lg font-bold font-mono text-success">{spread.toFixed(3)}%</p>
            </div>
            <div className="rounded-md bg-secondary/50 p-3">
              <p className="text-xs text-muted-foreground">Est. Profit</p>
              <p className="text-lg font-bold font-mono text-success">${predictedProfit.toFixed(2)}</p>
            </div>
          </div>
        </div>

        {/* Action Buttons (Fitts's Law: large, isolated targets) */}
        <div className="flex gap-3">
          <Button variant="success" size="lg" className="flex-1 h-12 text-base" onClick={onApprove}>
            <CheckCircle className="mr-2 h-5 w-5" />
            Approve Trade
          </Button>
          <Button variant="outline" size="lg" className="h-12 px-6" onClick={onReject}>
            <XCircle className="mr-2 h-5 w-5" />
            Reject
          </Button>
        </div>
      </div>
    </div>
  );
};

export default TradeApprovalModal;
