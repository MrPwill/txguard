interface TierData {
  tier: "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";
  count: number;
  percentage: number;
}

const tierColor: Record<TierData["tier"], string> = {
  LOW: "bg-risk-low",
  MEDIUM: "bg-risk-medium",
  HIGH: "bg-risk-high",
  CRITICAL: "bg-risk-critical",
};

export default function TierBreakdown({ data }: { data: TierData[] }) {
  return (
    <div className="bg-bg-2 border border-border rounded-xl p-5 h-64">
      <h3 className="text-sm font-mono text-text-dim mb-4 tracking-widest">TIER BREAKDOWN</h3>
      <div className="space-y-4">
        {data.map((item) => (
          <div key={item.tier}>
            <div className="flex items-center justify-between text-xs font-mono mb-1">
              <span className="text-text">{item.tier}</span>
              <span className="text-text-dim">{item.count} ({item.percentage.toFixed(1)}%)</span>
            </div>
            <div className="h-2 bg-bg border border-border rounded-full overflow-hidden">
              <div className={`h-full ${tierColor[item.tier]}`} style={{ width: `${item.percentage}%` }} />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
