"use client";

import { useModelStatus } from "@/lib/api/model";
import { Activity, AlertTriangle } from "lucide-react";

export default function ModelHealthPage() {
  const { data: status, isLoading } = useModelStatus();

  return (
    <div className="space-y-6 flex flex-col h-full">
      <div className="flex items-center justify-between shrink-0">
        <h1 className="text-2xl font-display font-bold text-text tracking-wide flex items-center gap-3">
          <Activity className="w-6 h-6 text-cyan" />
          Model Health
        </h1>
      </div>

      {status?.drift_detected && (
        <div className="bg-amber/10 border border-amber/30 text-amber p-4 rounded-lg flex items-center gap-3 font-mono text-sm">
          <AlertTriangle className="w-5 h-5 shrink-0" />
          Data drift detected. Rolling mean has deviated by &gt;15% from baseline. Retraining recommended.
        </div>
      )}

      <div className="grid grid-cols-2 gap-6">
        <div className="bg-bg-2 border border-border rounded-lg p-5 flex flex-col gap-4">
          <h3 className="text-sm font-mono text-text-dim border-b border-border pb-2">Active Models</h3>
          <div className="space-y-4 font-mono text-sm">
            <div className="flex justify-between items-center p-3 bg-bg border border-border rounded">
              <div>
                <div className="font-bold text-text">Isolation Forest</div>
                <div className="text-xs text-text-dim">v1.2.0 • Anomaly Detection Core</div>
              </div>
              <div className="text-right">
                <div className="text-risk-low">HEALTHY</div>
                <div className="text-xs text-text-faint">F1: 0.94</div>
              </div>
            </div>
            <div className="flex justify-between items-center p-3 bg-bg border border-border rounded">
              <div>
                <div className="font-bold text-text">Local Outlier Factor</div>
                <div className="text-xs text-text-dim">v1.1.0 • Density Anomalies</div>
              </div>
              <div className="text-right">
                <div className="text-risk-low">HEALTHY</div>
                <div className="text-xs text-text-faint">F1: 0.89</div>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-bg-2 border border-border rounded-lg p-5 h-80 flex flex-col">
          <h3 className="text-sm font-mono text-text-dim mb-4">SCORE DRIFT MONITOR (7D)</h3>
          <div className="flex-1 flex items-center justify-center border border-dashed border-border-2 rounded bg-bg">
            <span className="text-text-faint font-mono">DriftChart (Recharts LineChart)</span>
          </div>
        </div>
      </div>
    </div>
  );
}
