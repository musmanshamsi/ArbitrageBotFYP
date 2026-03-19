import { TrendingUp, TrendingDown, Minus } from "lucide-react";

interface MetricCardProps {
  title: string;
  value: string;
  change?: number;
  isHighlighted?: boolean;
  icon?: React.ReactNode;
}

const MetricCard = ({ title, value, change, isHighlighted, icon }: MetricCardProps) => {
  const changeColor = change && change > 0 ? "text-success" : change && change < 0 ? "text-destructive" : "text-muted-foreground";
  const ChangeIcon = change && change > 0 ? TrendingUp : change && change < 0 ? TrendingDown : Minus;

  return (
    <div
      className={`rounded-lg border p-6 transition-all duration-300 ${
        isHighlighted
          ? "border-success/50 bg-success/5 glow-green"
          : "border-border bg-card"
      }`}
    >
      <div className="flex items-center justify-between mb-2">
        <span className="text-sm text-muted-foreground font-medium">{title}</span>
        {icon && <span className="text-muted-foreground">{icon}</span>}
      </div>
      <div className={`text-3xl font-bold font-mono tracking-tight ${isHighlighted ? "text-success" : "text-foreground"}`}>
        {value}
      </div>
      {change !== undefined && (
        <div className={`flex items-center gap-1 mt-2 text-sm ${changeColor}`}>
          <ChangeIcon className="h-3 w-3" />
          <span className="font-mono">{change > 0 ? "+" : ""}{change.toFixed(2)}%</span>
        </div>
      )}
    </div>
  );
};

export default MetricCard;
