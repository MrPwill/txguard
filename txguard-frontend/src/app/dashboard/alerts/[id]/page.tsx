"use client";

import { use } from "react";
import { useInvestigation } from "@/lib/api/alerts";
import RiskBadge from "@/components/shared/RiskBadge";
import Link from "next/link";
import { ArrowLeft, BookOpen, UserCheck, Shield, BrainCircuit } from "lucide-react";

export default function InvestigationReportPage({ params }: { params: Promise<{ id: string }> }) {
  const resolvedParams = use(params);
  const alertId = resolvedParams.id;
  const { data: report, isLoading } = useInvestigation(alertId);

  if (isLoading) return <div className="text-text-faint font-mono p-6">Loading investigation report...</div>;
  if (!report) return <div className="text-text-faint font-mono p-6">Report not found.</div>;

  const isQueued = report.investigation_status === 'PENDING';
  const isInProgress = report.investigation_status === 'IN_PROGRESS';
  const isFailed = report.investigation_status === 'FAILED';
  const metadata = report.agent_run_metadata || {};

  return (
    <div className="space-y-6 max-w-5xl mx-auto pb-12">
      <Link href="/dashboard/alerts" className="inline-flex items-center gap-2 text-sm font-mono text-text-dim hover:text-text transition-colors">
        <ArrowLeft className="w-4 h-4" /> Back to Queue
      </Link>

      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-display font-bold text-text tracking-wide">Investigation Report</h1>
        <div className="flex items-center gap-3">
          <span className="text-sm font-mono text-text-dim">Alert ID: {alertId}</span>
          <RiskBadge tier={report.risk_tier || 'UNKNOWN'} />
        </div>
      </div>

      {isQueued ? (
        <div className="bg-amber/10 border border-amber/30 text-amber p-6 rounded-lg flex flex-col items-center justify-center gap-3">
          <div className="font-mono text-sm">Investigation queued. Waiting for worker pickup.</div>
          <div className="font-mono text-xs opacity-80">Polling status every 3 seconds.</div>
        </div>
      ) : isInProgress ? (
        <div className="bg-cyan/10 border border-cyan/30 text-cyan p-6 rounded-lg flex flex-col items-center justify-center gap-4">
          <div className="w-8 h-8 border-4 border-cyan border-t-transparent rounded-full animate-spin"></div>
          <div className="font-mono text-sm">Autonomous investigation in progress... Polling agents.</div>
        </div>
      ) : isFailed ? (
        <div className="bg-risk-critical/10 border border-risk-critical/30 text-risk-critical p-6 rounded-lg">
          <div className="font-mono text-sm">Investigation failed. Check audit trail and retry dispatch.</div>
        </div>
      ) : (
        <>
          {/* Recommendation Banner */}
          <div className={`p-6 rounded-lg border flex items-center justify-between ${
            report.recommended_action === 'CLEAR' ? 'bg-risk-low/10 border-risk-low/30 text-risk-low' :
            report.recommended_action === 'ESCALATE_TO_SAR' ? 'bg-risk-critical/10 border-risk-critical/30 text-risk-critical' :
            report.recommended_action === 'BLOCK_AND_HOLD' ? 'bg-risk-high/10 border-risk-high/30 text-risk-high' :
            'bg-border-2 border-border text-text'
          }`}>
            <div className="space-y-1">
              <div className="text-xs font-mono uppercase tracking-widest opacity-80">Final Recommendation</div>
              <div className="text-2xl font-bold">{report.recommended_action?.replace(/_/g, ' ')}</div>
            </div>
            <div className="text-right">
              <div className="text-xs font-mono uppercase tracking-widest opacity-80">Confidence</div>
              <div className="text-2xl font-bold font-mono">{(report.confidence_score * 100).toFixed(1)}%</div>
            </div>
          </div>

          <div className="bg-bg-2 border border-border rounded-lg p-6 space-y-4">
            <h3 className="text-sm font-mono text-text-dim uppercase border-b border-border pb-2">Executive Summary</h3>
            <p className="text-text leading-relaxed text-sm">
              {report.executive_summary || report.behavioral_analysis || "No executive summary available."}
            </p>
          </div>

          <div className="space-y-4">
            <h3 className="text-sm font-mono text-text-dim uppercase border-b border-border pb-2">Agent Chain Trace</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              
              <div className="bg-bg-2 border border-border rounded-lg p-5 flex gap-4">
                <div className="bg-bg-3 p-3 rounded-full shrink-0 h-fit"><UserCheck className="w-5 h-5 text-text-dim" /></div>
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <div className="text-sm font-bold text-text">Transaction Analyst</div>
                    <div className="text-xs font-mono text-risk-low">COMPLETE</div>
                  </div>
                  <p className="text-xs text-text-dim leading-relaxed">
                    Built behavioral profile. Velocity context, geographic anomalies, and amount z-scores evaluated.
                  </p>
                </div>
              </div>

              <div className="bg-bg-2 border border-border rounded-lg p-5 flex gap-4">
                <div className="bg-bg-3 p-3 rounded-full shrink-0 h-fit"><BrainCircuit className="w-5 h-5 text-text-dim" /></div>
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <div className="text-sm font-bold text-text">Fraud Investigator</div>
                    <div className="text-xs font-mono text-risk-low">COMPLETE</div>
                  </div>
                  <p className="text-xs text-text-dim leading-relaxed">
                    Matched behavioral data against typologies. Checked merchant watchlist and counterparty risk.
                  </p>
                </div>
              </div>

              <div className="bg-bg-2 border border-border rounded-lg p-5 flex gap-4">
                <div className="bg-bg-3 p-3 rounded-full shrink-0 h-fit"><Shield className="w-5 h-5 text-text-dim" /></div>
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <div className="text-sm font-bold text-text">Compliance Specialist</div>
                    <div className="text-xs font-mono text-risk-low">COMPLETE</div>
                  </div>
                  <p className="text-xs text-text-dim leading-relaxed">
                    Assessed AML/KYC obligations. Cross-referenced OFAC sanctions and CTR thresholds.
                  </p>
                </div>
              </div>

              <div className="bg-bg-2 border border-border rounded-lg p-5 flex gap-4">
                <div className="bg-bg-3 p-3 rounded-full shrink-0 h-fit"><BookOpen className="w-5 h-5 text-text-dim" /></div>
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <div className="text-sm font-bold text-text">Risk Decision Officer</div>
                    <div className="text-xs font-mono text-risk-low">COMPLETE</div>
                  </div>
                  <p className="text-xs text-text-dim leading-relaxed">
                    Synthesized findings into final report and recommended action. 
                  </p>
                  <div className="text-xs font-mono text-text-faint mt-2 p-2 bg-bg rounded border border-border-2">
                    Output: {metadata.crew_output?.substring(0, 100)}...
                  </div>
                </div>
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
