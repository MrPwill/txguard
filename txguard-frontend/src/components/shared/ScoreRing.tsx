import { cn } from "@/lib/utils/cn";

export default function ScoreRing({ score, size = 64 }: { score: number, size?: number }) {
  const strokeWidth = 4;
  const radius = (size - strokeWidth) / 2;
  const circumference = radius * 2 * Math.PI;
  const offset = circumference - (score / 100) * circumference;
  
  let strokeColor = "stroke-risk-low";
  if (score > 30) strokeColor = "stroke-risk-medium";
  if (score > 60) strokeColor = "stroke-risk-high";
  if (score > 80) strokeColor = "stroke-risk-critical";

  return (
    <div className="relative flex items-center justify-center" style={{ width: size, height: size }}>
      <svg width={size} height={size} className="transform -rotate-90">
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          strokeWidth={strokeWidth}
          className="stroke-border-2 fill-none"
        />
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          strokeWidth={strokeWidth}
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          className={cn("fill-none transition-all duration-1000 ease-out", strokeColor)}
          strokeLinecap="round"
        />
      </svg>
      <div className="absolute flex items-center justify-center font-mono font-bold text-text">
        {Math.round(score)}
      </div>
    </div>
  );
}
