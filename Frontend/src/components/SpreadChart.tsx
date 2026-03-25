import { 
  Line, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer, 
  Area, 
  AreaChart 
} from "recharts";

interface SpreadChartProps {
  data: { time: number; spread: number }[];
  threshold: number;
}

const SpreadChart = ({ data, threshold }: SpreadChartProps) => {
  return (
    <div className="rounded-lg border border-border bg-card p-6 h-[350px] flex flex-col">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-medium text-muted-foreground">Spread Over Time (%)</h3>
        <div className="flex items-center gap-4 text-xs text-muted-foreground">
          <div className="flex items-center gap-1.5">
            <div className="h-2 w-2 rounded-full bg-success" />
            <span>Spread</span>
          </div>
          <div className="flex items-center gap-1.5">
            <div className="h-0.5 w-4 bg-warning" />
            <span>Threshold ({threshold}%)</span>
          </div>
        </div>
      </div>
      
      <div className="flex-1 w-full min-h-0">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={data}>
            <defs>
              <linearGradient id="spreadGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="hsl(142, 71%, 45%)" stopOpacity={0.3} />
                <stop offset="95%" stopColor="hsl(142, 71%, 45%)" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="hsl(217, 19%, 22%)" />
            <XAxis
              dataKey="time"
              type="number"
              domain={['dataMin', 'dataMax']}
              stroke="hsl(215, 20%, 45%)"
              tick={{ fill: "hsl(215, 20%, 55%)", fontSize: 11 }}
              tickFormatter={(unixTime) => new Date(unixTime).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false })}
              axisLine={{ stroke: "hsl(217, 19%, 22%)" }}
            />
            <YAxis
              stroke="hsl(215, 20%, 45%)"
              tick={{ fill: "hsl(215, 20%, 55%)", fontSize: 11 }}
              axisLine={{ stroke: "hsl(217, 19%, 22%)" }}
              domain={[0, "auto"]}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: "hsl(217, 33%, 17%)",
                border: "1px solid hsl(217, 19%, 27%)",
                borderRadius: "8px",
                color: "hsl(210, 40%, 98%)",
                fontSize: "12px",
              }}
              formatter={(value: number) => [`${value.toFixed(4)}%`, "Spread"]}
              labelFormatter={(label) => new Date(label).toLocaleTimeString()}
            />
            {/* Threshold reference line */}
            <Line
              type="monotone"
              dataKey={() => threshold}
              stroke="hsl(38, 92%, 50%)"
              strokeWidth={1}
              strokeDasharray="6 4"
              dot={false}
              name="Threshold"
            />
            <Area
              type="monotone"
              dataKey="spread"
              stroke="hsl(142, 71%, 45%)"
              strokeWidth={2}
              fill="url(#spreadGradient)"
              dot={false}
              activeDot={{ r: 4, fill: "hsl(142, 71%, 45%)" }}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

export default SpreadChart;
