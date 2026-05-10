import { cn } from "@/lib/utils/cn";

export default function RiskBadge({ tier }: { tier: string }) {
  const bgColors: Record<string, string> = {
    LOW: "bg-risk-low/10 text-risk-low border-risk-low/20",
    MEDIUM: "bg-risk-medium/10 text-risk-medium border-risk-medium/20",
    HIGH: "bg-risk-high/10 text-risk-high border-risk-high/20",
    CRITICAL: "bg-risk-critical/10 text-risk-critical border-risk-critical/20",
  };
  
  const colorClass = bgColors[tier?.toUpperCase()] || bgColors.LOW;

  return (
    <span className={cn("px-2.5 py-0.5 rounded-full border text-xs font-mono font-medium tracking-wide", colorClass)}>
      {tier || "UNKNOWN"}
    </span>
  );
}
