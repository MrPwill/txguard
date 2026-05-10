"use client";

import LivePulse from "../shared/LivePulse";

export default function LiveStatusBar() {
  return (
    <div className="flex items-center gap-3">
      <div className="flex items-center gap-2 bg-bg-2 border border-border rounded-full px-4 py-2">
        <LivePulse />
        <span className="text-sm font-mono text-text-dim">SYSTEM</span>
        <span className="text-sm font-mono text-risk-low">OPERATIONAL</span>
      </div>

      <div className="bg-bg-2 border border-border rounded-full px-4 py-2 text-sm font-mono">
        <span className="text-text-dim mr-2">LATENCY</span>
        <span className="text-cyan font-semibold">87ms p95</span>
      </div>
    </div>
  );
}
