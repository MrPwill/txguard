"use client";

import Link from "next/link";
import { ArrowRight } from "lucide-react";
import RiskBadge from "@/components/shared/RiskBadge";
import { Alert } from "@/lib/types/alert";

export default function LiveAlertFeed({ alerts }: { alerts: Alert[] }) {
  return (
    <div className="bg-bg-2 border border-border rounded-xl p-5 flex flex-col h-[610px]">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-2xl font-display font-semibold text-text">LIVE ALERT FEED</h3>
        <span className="text-xs font-mono text-risk-critical">LIVE</span>
      </div>

      <div className="flex-1 overflow-y-auto space-y-3 pr-2">
        {alerts.length === 0 ? (
          <div className="h-full flex items-center justify-center text-sm font-mono text-text-faint">Listening for alerts...</div>
        ) : (
          alerts.map((alert) => (
            <div key={alert.id} className="bg-bg border border-border rounded p-3">
              <div className="flex items-start justify-between gap-2 mb-2">
                <span className="font-mono text-cyan">TXN-{alert.transaction_id.slice(0, 5).toUpperCase()}</span>
                <RiskBadge tier={alert.risk_tier} />
              </div>
              <div className="text-text text-lg leading-tight mb-2">{alert.reason_codes?.[0] ?? "Anomaly detected"}</div>
              <div className="flex items-center justify-between text-xs font-mono text-text-dim">
                <span>{new Date(alert.created_at).toLocaleTimeString()}</span>
                <Link href={`/dashboard/alerts/${alert.id}`} className="inline-flex items-center gap-1 text-cyan hover:text-cyan-dim">
                  OPEN <ArrowRight className="w-3 h-3" />
                </Link>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
