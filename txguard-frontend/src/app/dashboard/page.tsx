"use client";

import { useAlertWebSocket } from "@/hooks/useAlertWebSocket";
import { useAlertStore } from "@/lib/stores/alertStore";
import RiskBadge from "@/components/shared/RiskBadge";
import Link from "next/link";
import { ArrowRight } from "lucide-react";

export default function DashboardOverview() {
  useAlertWebSocket(process.env.NEXT_PUBLIC_WS_URL ? `${process.env.NEXT_PUBLIC_WS_URL}/alerts/live` : undefined);
  const alerts = useAlertStore((s) => s.alerts);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-display font-bold text-text tracking-wide">Overview</h1>
        <div className="text-sm text-text-dim font-mono">Last updated: {new Date().toLocaleTimeString()}</div>
      </div>

      <div className="grid grid-cols-4 gap-4">
        {[
          { label: "TRANSACTIONS (24H)", value: "14,289" },
          { label: "ALERTS RAISED", value: "34" },
          { label: "AUTO-CLEARED", value: "12,980" },
          { label: "PENDING REVIEW", value: "8" },
        ].map((kpi) => (
          <div key={kpi.label} className="bg-bg-2 border border-border p-5 rounded-lg flex flex-col gap-2">
            <span className="text-xs font-mono text-text-dim">{kpi.label}</span>
            <span className="text-3xl font-display font-bold text-text">{kpi.value}</span>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-3 gap-6">
        <div className="col-span-2 space-y-6">
          <div className="bg-bg-2 border border-border rounded-lg p-5 h-80 flex flex-col">
            <h3 className="text-sm font-mono text-text-dim mb-4">VOLUME & RISK (24H)</h3>
            <div className="flex-1 flex items-center justify-center border border-dashed border-border-2 rounded bg-bg">
              {/* Placeholder for VolumeChart */}
              <span className="text-text-faint font-mono">VolumeChart (Recharts AreaChart)</span>
            </div>
          </div>
          <div className="bg-bg-2 border border-border rounded-lg p-5 h-64 flex flex-col">
            <h3 className="text-sm font-mono text-text-dim mb-4">SCORE DISTRIBUTION</h3>
            <div className="flex-1 flex items-center justify-center border border-dashed border-border-2 rounded bg-bg">
              {/* Placeholder for ScoreDistChart */}
              <span className="text-text-faint font-mono">ScoreDistChart (Recharts BarChart)</span>
            </div>
          </div>
        </div>

        <div className="bg-bg-2 border border-border rounded-lg p-5 flex flex-col">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-mono text-text-dim flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-risk-critical animate-pulse"></span>
              LIVE ALERTS
            </h3>
            <span className="text-xs font-mono bg-bg-3 px-2 py-1 rounded text-text">{alerts.length}</span>
          </div>
          
          <div className="flex-1 overflow-y-auto space-y-3 pr-2">
            {alerts.length === 0 ? (
              <div className="h-full flex items-center justify-center text-sm font-mono text-text-faint">
                Listening for alerts...
              </div>
            ) : (
              alerts.map((alert) => (
                <div key={alert.id} className="bg-bg border border-border rounded p-3 text-sm">
                  <div className="flex justify-between items-start mb-2">
                    <span className="font-mono text-xs text-text-dim">{alert.id.substring(0, 8)}...</span>
                    <RiskBadge tier={alert.risk_tier} />
                  </div>
                  <div className="text-text font-medium mb-1 truncate">Score: {alert.ml_anomaly_score.toFixed(4)}</div>
                  <div className="text-xs text-text-dim truncate">
                    {alert.reason_codes?.[0] || 'Anomaly detected'}
                  </div>
                  <Link href={`/dashboard/alerts/${alert.id}`} className="mt-3 flex items-center gap-1 text-xs font-mono text-cyan hover:text-cyan-dim transition-colors">
                    View Report <ArrowRight className="w-3 h-3" />
                  </Link>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
