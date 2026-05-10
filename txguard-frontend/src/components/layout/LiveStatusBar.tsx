"use client";

import LivePulse from "../shared/LivePulse";

export default function LiveStatusBar() {
  return (
    <div className="flex items-center gap-3 bg-bg-3 border border-border rounded-full px-4 py-1.5">
      <LivePulse />
      <span className="text-xs font-mono text-text-dim tracking-wide">
        LATENCY: 142ms
      </span>
      <span className="w-1 h-1 rounded-full bg-border-2 mx-1"></span>
      <span className="text-xs font-mono text-risk-low tracking-wide font-medium">
        SYSTEM OPTIMAL
      </span>
    </div>
  );
}
