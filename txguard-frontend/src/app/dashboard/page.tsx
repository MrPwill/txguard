"use client";

import { useMemo } from "react";
import KpiCard from "@/components/dashboard/KpiCard";
import LiveAlertFeed from "@/components/dashboard/LiveAlertFeed";
import ScoreDistChart from "@/components/dashboard/ScoreDistChart";
import TierBreakdown from "@/components/dashboard/TierBreakdown";
import VolumeChart from "@/components/dashboard/VolumeChart";
import { useAlertWebSocket } from "@/hooks/useAlertWebSocket";
import { useDashboardMetrics } from "@/lib/api/dashboard";
import { useAlertStore } from "@/lib/stores/alertStore";

function formatDelta(today: number, yesterday: number): string {
  if (yesterday === 0) return "+0% vs yesterday";
  const pct = ((today - yesterday) / yesterday) * 100;
  const direction = pct >= 0 ? "+" : "";
  return `${direction}${pct.toFixed(1)}% vs yesterday`;
}

export default function DashboardOverview() {
  useAlertWebSocket(
    process.env.NEXT_PUBLIC_WS_URL ? `${process.env.NEXT_PUBLIC_WS_URL}/alerts/live` : undefined,
  );

  const wsAlerts = useAlertStore((s) => s.alerts);
  const { data: metrics, isLoading } = useDashboardMetrics();

  const feedAlerts = useMemo(() => wsAlerts.slice(0, 20), [wsAlerts]);

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 xl:grid-cols-4 gap-4">
        <KpiCard
          label="TRANSACTIONS TODAY"
          value={isLoading || !metrics ? "-" : metrics.transactionsToday.toLocaleString()}
          subtext={isLoading || !metrics ? "loading..." : formatDelta(metrics.transactionsToday, metrics.transactionsYesterday)}
          accent="cyan"
        />
        <KpiCard
          label="ALERTS RAISED"
          value={isLoading || !metrics ? "-" : metrics.alertsRaised.toLocaleString()}
          subtext={isLoading || !metrics ? "loading..." : `${metrics.criticalAlerts} critical, ${metrics.highAlerts} high`}
          accent="amber"
        />
        <KpiCard
          label="AUTO-CLEARED"
          value={isLoading || !metrics ? "-" : metrics.autoCleared.toLocaleString()}
          subtext={isLoading || !metrics ? "loading..." : `${metrics.transactionsToday ? ((metrics.autoCleared / metrics.transactionsToday) * 100).toFixed(1) : "0.0"}% pass rate`}
          accent="green"
        />
        <KpiCard
          label="PENDING REVIEW"
          value={isLoading || !metrics ? "-" : metrics.pendingReview.toLocaleString()}
          subtext={
            isLoading || !metrics
              ? "loading..."
              : `${metrics.pendingDeltaFromLastHour >= 0 ? "+" : ""}${metrics.pendingDeltaFromLastHour} from last hour`
          }
          accent="rose"
        />
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
        <div className="xl:col-span-2 space-y-6">
          <VolumeChart data={metrics?.volume24h ?? []} />
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <ScoreDistChart data={metrics?.scoreDistribution ?? []} />
            <TierBreakdown data={metrics?.tierBreakdown ?? []} />
          </div>
        </div>
        <LiveAlertFeed alerts={feedAlerts} />
      </div>
    </div>
  );
}
