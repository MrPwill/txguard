interface KpiCardProps {
  label: string;
  value: string;
  subtext: string;
  accent: "cyan" | "amber" | "green" | "rose";
}

const accentClass: Record<KpiCardProps["accent"], string> = {
  cyan: "text-cyan border-cyan/40",
  amber: "text-amber border-amber/40",
  green: "text-risk-low border-risk-low/40",
  rose: "text-risk-critical border-risk-critical/40",
};

export default function KpiCard({ label, value, subtext, accent }: KpiCardProps) {
  return (
    <div className={`bg-bg-2 border rounded-xl p-5 flex flex-col gap-2 ${accentClass[accent]}`}>
      <span className="text-xs font-mono text-text-dim tracking-widest">{label}</span>
      <span className="text-5xl leading-none font-display font-bold">{value}</span>
      <span className="text-sm font-mono text-text-dim">{subtext}</span>
    </div>
  );
}
