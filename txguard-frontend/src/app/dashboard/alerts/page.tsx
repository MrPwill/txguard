"use client";

import { useAlerts } from "@/lib/api/alerts";
import RiskBadge from "@/components/shared/RiskBadge";
import Link from "next/link";
import { ArrowRight, Search, ShieldAlert } from "lucide-react";

export default function AlertsQueuePage() {
  const { data: alerts, isLoading } = useAlerts();

  return (
    <div className="space-y-6 flex flex-col h-full">
      <div className="flex items-center justify-between shrink-0">
        <h1 className="text-2xl font-display font-bold text-text tracking-wide flex items-center gap-3">
          <ShieldAlert className="w-6 h-6 text-amber" />
          Alert Queue
        </h1>
      </div>

      <div className="flex gap-4 items-center shrink-0 border-b border-border pb-4">
        {['ALL', 'PENDING', 'IN_PROGRESS', 'COMPLETE'].map(status => (
          <button 
            key={status}
            className={`px-4 py-2 text-sm font-mono transition-colors border-b-2 ${
              status === 'ALL' 
                ? 'border-cyan text-cyan' 
                : 'border-transparent text-text-dim hover:text-text hover:border-border'
            }`}
          >
            {status.replace('_', ' ')}
          </button>
        ))}
      </div>

      <div className="flex-1 bg-bg-2 border border-border rounded-lg overflow-hidden flex flex-col">
        <div className="overflow-x-auto flex-1">
          <table className="w-full text-left text-sm whitespace-nowrap">
            <thead className="bg-bg-3 sticky top-0 z-10 font-mono text-xs text-text-dim">
              <tr>
                <th className="px-6 py-4 font-medium">Alert ID</th>
                <th className="px-6 py-4 font-medium">Created At</th>
                <th className="px-6 py-4 font-medium">Transaction ID</th>
                <th className="px-6 py-4 font-medium">Risk Tier</th>
                <th className="px-6 py-4 font-medium">Status</th>
                <th className="px-6 py-4 font-medium">Triggers</th>
                <th className="px-6 py-4 font-medium text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border font-mono">
              {isLoading ? (
                <tr>
                  <td colSpan={7} className="px-6 py-8 text-center text-text-faint">Loading alerts...</td>
                </tr>
              ) : alerts?.length === 0 ? (
                <tr>
                  <td colSpan={7} className="px-6 py-8 text-center text-text-faint">No alerts found</td>
                </tr>
              ) : (
                alerts?.map((a: any) => (
                  <tr key={a.id} className="hover:bg-bg-3/50 transition-colors group">
                    <td className="px-6 py-4 text-text font-medium">{a.id.substring(0, 8)}...</td>
                    <td className="px-6 py-4 text-text-dim">
                      {new Date(a.created_at).toLocaleString()}
                    </td>
                    <td className="px-6 py-4">
                      <Link href={`/dashboard/transactions/${a.transaction_id}`} className="text-text hover:text-cyan transition-colors">
                        {a.transaction_id.substring(0, 8)}...
                      </Link>
                    </td>
                    <td className="px-6 py-4">
                      <RiskBadge tier={a.risk_tier} />
                    </td>
                    <td className="px-6 py-4">
                      <span className={`px-2 py-1 rounded text-xs font-bold ${
                        a.investigation_status === 'COMPLETE' ? 'bg-risk-low/20 text-risk-low' :
                        a.investigation_status === 'IN_PROGRESS' ? 'bg-cyan/20 text-cyan animate-pulse' :
                        'bg-border-2 text-text-dim'
                      }`}>
                        {a.investigation_status}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex gap-1">
                        {a.rule_triggers?.slice(0,2).map((t: string) => (
                          <span key={t} className="px-2 py-0.5 bg-bg border border-border rounded text-xs text-text-dim truncate max-w-[150px]">
                            {t}
                          </span>
                        ))}
                        {a.rule_triggers?.length > 2 && <span className="px-1 text-text-faint">+{a.rule_triggers.length - 2}</span>}
                      </div>
                    </td>
                    <td className="px-6 py-4 text-right">
                      <Link 
                        href={`/dashboard/alerts/${a.id}`}
                        className="inline-flex items-center gap-1 text-cyan hover:text-cyan-dim font-medium"
                      >
                        Open Report <ArrowRight className="w-4 h-4" />
                      </Link>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
