"use client";

import { use } from "react";
import { useTransactionDetail, useExplain, useTransactionAudit } from "@/lib/api/transactions";
import RiskBadge from "@/components/shared/RiskBadge";
import ScoreRing from "@/components/shared/ScoreRing";
import Link from "next/link";
import { ArrowLeft, ExternalLink, Scale } from "lucide-react";

export default function TransactionDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const resolvedParams = use(params);
  const txnId = resolvedParams.id;
  const { data: txn, isLoading: txnLoading } = useTransactionDetail(txnId);
  const { data: explain, isLoading: explainLoading } = useExplain(txnId);
  const { data: audit, isLoading: auditLoading } = useTransactionAudit(txnId);

  if (txnLoading) return <div className="text-text-faint font-mono p-6">Loading transaction data...</div>;
  if (!txn) return <div className="text-text-faint font-mono p-6">Transaction not found.</div>;

  return (
    <div className="space-y-6 max-w-6xl mx-auto pb-12">
      <Link href="/dashboard/transactions" className="inline-flex items-center gap-2 text-sm font-mono text-text-dim hover:text-text transition-colors">
        <ArrowLeft className="w-4 h-4" /> Back to Monitor
      </Link>

      {/* Header */}
      <div className="bg-bg-2 border border-border rounded-xl p-6 flex items-start justify-between">
        <div className="space-y-4">
          <div className="flex items-center gap-3">
            <h1 className="text-2xl font-mono font-bold text-text">{txn.id}</h1>
            <RiskBadge tier={txn.risk_tier} />
          </div>
          
          <div className="grid grid-cols-3 gap-x-12 gap-y-4 text-sm font-mono">
            <div>
              <div className="text-text-faint">Amount</div>
              <div className="text-xl text-text font-bold">${txn.amount.toLocaleString()}</div>
            </div>
            <div>
              <div className="text-text-faint">Account</div>
              <div className="text-text">{txn.account_id}</div>
            </div>
            <div>
              <div className="text-text-faint">Merchant</div>
              <div className="text-text">{txn.merchant_name || 'N/A'}</div>
            </div>
            <div>
              <div className="text-text-faint">Time</div>
              <div className="text-text">{new Date(txn.timestamp).toLocaleString()}</div>
            </div>
            <div>
              <div className="text-text-faint">Location</div>
              <div className="text-text">{txn.location_city}, {txn.location_country}</div>
            </div>
            <div>
              <div className="text-text-faint">Channel</div>
              <div className="text-text">{txn.channel}</div>
            </div>
          </div>
        </div>

        <div className="flex flex-col items-center gap-3">
          <ScoreRing score={txn.risk_score || 0} size={96} />
          <div className="text-xs font-mono text-text-dim uppercase tracking-wider">Risk Score</div>
          {txn.risk_tier === 'CRITICAL' || txn.risk_tier === 'HIGH' ? (
            <Link 
              href={`/dashboard/alerts/${audit?.find((a: any) => a.action_type === 'ALERT_CREATED')?.payload?.alert_id || ''}`}
              className="mt-2 flex items-center gap-2 px-4 py-2 bg-bg border border-cyan text-cyan rounded-md text-xs font-mono hover:bg-cyan/10 transition-colors"
            >
              View Investigation <ExternalLink className="w-3 h-3" />
            </Link>
          ) : null}
        </div>
      </div>

      <div className="grid grid-cols-2 gap-6">
        {/* Rules breakdown */}
        <div className="bg-bg-2 border border-border rounded-lg p-5 flex flex-col gap-4">
          <h3 className="text-sm font-mono text-text-dim border-b border-border pb-2 flex items-center gap-2">
            <Scale className="w-4 h-4" /> REASON CODES & TRIGGERS
          </h3>
          <ul className="space-y-3 font-mono text-sm">
            {txn.reason_codes?.map((reason: string, i: number) => (
              <li key={i} className="bg-bg border border-border p-3 rounded text-text flex items-start gap-2">
                <span className="text-risk-high mt-0.5">•</span> {reason}
              </li>
            ))}
            {!txn.reason_codes?.length && <li className="text-text-faint">No specific rules triggered.</li>}
          </ul>
        </div>

        {/* Explainability Chart */}
        <div className="bg-bg-2 border border-border rounded-lg p-5 flex flex-col gap-4">
          <h3 className="text-sm font-mono text-text-dim border-b border-border pb-2">SHAP FEATURE ATTRIBUTION</h3>
          {explainLoading ? (
            <div className="flex-1 flex items-center justify-center text-text-faint font-mono text-sm">Calculating SHAP values...</div>
          ) : (
            <div className="flex-1 overflow-y-auto space-y-2 pr-2">
              {explain?.feature_attributions
                ?.sort((a: any, b: any) => Math.abs(b.shap_value) - Math.abs(a.shap_value))
                .slice(0, 10)
                .map((f: any) => {
                  const isPositive = f.shap_value > 0;
                  const absValue = Math.abs(f.shap_value);
                  const width = Math.min(absValue * 200, 100); 
                  
                  return (
                    <div key={f.feature} className="grid grid-cols-[1fr_2fr] gap-4 items-center text-xs font-mono">
                      <div className="truncate text-text-dim" title={f.feature}>{f.feature}</div>
                      <div className="flex items-center gap-2">
                        <div className="w-full h-2 bg-bg rounded-full overflow-hidden flex relative">
                          <div className="w-1/2 flex justify-end">
                            {!isPositive && <div className="h-full bg-risk-low" style={{ width: `${width}%` }} />}
                          </div>
                          <div className="w-1/2 flex justify-start">
                            {isPositive && <div className="h-full bg-risk-critical" style={{ width: `${width}%` }} />}
                          </div>
                        </div>
                        <span className={`w-10 text-right ${isPositive ? 'text-risk-critical' : 'text-risk-low'}`}>
                          {isPositive ? '+' : ''}{f.shap_value.toFixed(2)}
                        </span>
                      </div>
                    </div>
                  );
                })}
            </div>
          )}
        </div>
      </div>

      {/* Audit Timeline */}
      <div className="bg-bg-2 border border-border rounded-lg p-5 flex flex-col gap-4">
        <h3 className="text-sm font-mono text-text-dim border-b border-border pb-2">SYSTEM AUDIT TRAIL</h3>
        <div className="space-y-4 font-mono text-xs pl-2 border-l border-border-2 ml-2">
          {auditLoading ? (
            <div className="text-text-faint">Loading audit log...</div>
          ) : (
            audit?.map((log: any) => (
              <div key={log.id} className="relative pl-6">
                <span className="absolute -left-1.5 top-1 w-3 h-3 rounded-full bg-bg-3 border border-border-2"></span>
                <div className="text-text-dim mb-1">{new Date(log.timestamp).toLocaleString()} • {log.actor}</div>
                <div className="text-text font-medium">{log.action_type.replace(/_/g, ' ')}</div>
                <pre className="mt-2 p-2 bg-bg border border-border rounded text-text-faint overflow-x-auto">
                  {JSON.stringify(log.payload, null, 2)}
                </pre>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
