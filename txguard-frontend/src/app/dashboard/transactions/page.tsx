"use client";

import { useMemo, useState } from "react";
import { useTransactions } from "@/lib/api/transactions";
import { Transaction } from "@/lib/types/transaction";
import RiskBadge from "@/components/shared/RiskBadge";
import Link from "next/link";
import { ArrowRight, Search, Filter } from "lucide-react";

interface AdvancedFilters {
  channel: string;
  country: string;
  status: string;
  minAmount: string;
  maxAmount: string;
  dateFrom: string;
  dateTo: string;
}

export default function TransactionsPage() {
  const [filters, setFilters] = useState<{ tier?: string, limit: number }>({ limit: 100 });
  const [searchTerm, setSearchTerm] = useState("");
  const [showAdvancedFilters, setShowAdvancedFilters] = useState(false);
  const [advancedFilters, setAdvancedFilters] = useState<AdvancedFilters>({
    channel: "",
    country: "",
    status: "",
    minAmount: "",
    maxAmount: "",
    dateFrom: "",
    dateTo: "",
  });
  const { data: transactions, isLoading } = useTransactions(filters);

  const filteredTransactions = useMemo(() => {
    if (!transactions) return [];
    const q = searchTerm.trim().toLowerCase();
    return transactions.filter((t: Transaction) => {
      const id = t.id?.toLowerCase() ?? "";
      const merchant = t.merchant_name?.toLowerCase() ?? "";
      const account = t.account_id?.toLowerCase() ?? "";
      const matchesSearch = !q || id.includes(q) || merchant.includes(q) || account.includes(q);

      const matchesChannel = !advancedFilters.channel || t.channel === advancedFilters.channel;
      const matchesCountry =
        !advancedFilters.country ||
        (t.location_country ?? "").toLowerCase().includes(advancedFilters.country.toLowerCase());
      const matchesStatus = !advancedFilters.status || t.status === advancedFilters.status;

      const minAmount = advancedFilters.minAmount ? Number(advancedFilters.minAmount) : null;
      const maxAmount = advancedFilters.maxAmount ? Number(advancedFilters.maxAmount) : null;
      const matchesMinAmount = minAmount === null || t.amount >= minAmount;
      const matchesMaxAmount = maxAmount === null || t.amount <= maxAmount;

      const txnDate = new Date(t.timestamp);
      const fromDate = advancedFilters.dateFrom ? new Date(`${advancedFilters.dateFrom}T00:00:00`) : null;
      const toDate = advancedFilters.dateTo ? new Date(`${advancedFilters.dateTo}T23:59:59`) : null;
      const matchesFromDate = !fromDate || txnDate >= fromDate;
      const matchesToDate = !toDate || txnDate <= toDate;

      return (
        matchesSearch &&
        matchesChannel &&
        matchesCountry &&
        matchesStatus &&
        matchesMinAmount &&
        matchesMaxAmount &&
        matchesFromDate &&
        matchesToDate
      );
    });
  }, [transactions, searchTerm, advancedFilters]);

  return (
    <div className="space-y-6 flex flex-col h-full">
      <div className="flex items-center justify-between shrink-0">
        <h1 className="text-2xl font-display font-bold text-text tracking-wide">Transaction Monitor</h1>
      </div>

      <div className="flex gap-4 items-center shrink-0">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-text-faint" />
          <input 
            type="text" 
            placeholder="Search by ID, merchant, account..." 
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full bg-bg-2 border border-border rounded-md pl-10 pr-4 py-2 text-sm font-mono text-text placeholder:text-text-faint focus:outline-none focus:border-cyan"
          />
        </div>
        <div className="flex gap-2">
          {['ALL', 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW'].map(tier => (
            <button 
              key={tier}
              onClick={() => setFilters(prev => ({ ...prev, tier: tier === 'ALL' ? undefined : tier }))}
              className={`px-3 py-1.5 rounded-md border text-xs font-mono transition-colors ${
                (filters.tier === tier || (tier === 'ALL' && !filters.tier))
                  ? 'bg-bg-3 border-border text-text'
                  : 'bg-bg border-transparent text-text-dim hover:text-text'
              }`}
            >
              {tier}
            </button>
          ))}
        </div>
        <div className="ml-auto flex items-center gap-2">
          <button
            onClick={() => setShowAdvancedFilters((prev) => !prev)}
            className="flex items-center gap-2 px-3 py-1.5 rounded-md bg-bg-2 border border-border text-xs font-mono text-text-dim hover:text-text transition-colors"
          >
            <Filter className="w-4 h-4" /> More Filters
          </button>
          <button
            onClick={() => {
              setFilters({ limit: 100 });
              setSearchTerm("");
              setAdvancedFilters({
                channel: "",
                country: "",
                status: "",
                minAmount: "",
                maxAmount: "",
                dateFrom: "",
                dateTo: "",
              });
            }}
            className="px-3 py-1.5 rounded-md bg-bg border border-border text-xs font-mono text-text-dim hover:text-text transition-colors"
          >
            Reset
          </button>
        </div>
      </div>

      {showAdvancedFilters ? (
        <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-3 bg-bg-2 border border-border rounded-lg p-4">
          <select
            value={advancedFilters.channel}
            onChange={(e) => setAdvancedFilters((prev) => ({ ...prev, channel: e.target.value }))}
            className="bg-bg border border-border rounded-md px-3 py-2 text-xs font-mono text-text"
          >
            <option value="">All Channels</option>
            <option value="online">online</option>
            <option value="atm">atm</option>
            <option value="pos">pos</option>
            <option value="transfer">transfer</option>
          </select>

          <input
            type="text"
            placeholder="Country (e.g. US)"
            value={advancedFilters.country}
            onChange={(e) => setAdvancedFilters((prev) => ({ ...prev, country: e.target.value }))}
            className="bg-bg border border-border rounded-md px-3 py-2 text-xs font-mono text-text placeholder:text-text-faint"
          />

          <select
            value={advancedFilters.status}
            onChange={(e) => setAdvancedFilters((prev) => ({ ...prev, status: e.target.value }))}
            className="bg-bg border border-border rounded-md px-3 py-2 text-xs font-mono text-text"
          >
            <option value="">All Statuses</option>
            <option value="PENDING">PENDING</option>
            <option value="SCORED">SCORED</option>
            <option value="FLAGGED">FLAGGED</option>
            <option value="CLEARED">CLEARED</option>
            <option value="BLOCKED">BLOCKED</option>
          </select>

          <input
            type="number"
            min="0"
            placeholder="Min Amount"
            value={advancedFilters.minAmount}
            onChange={(e) => setAdvancedFilters((prev) => ({ ...prev, minAmount: e.target.value }))}
            className="bg-bg border border-border rounded-md px-3 py-2 text-xs font-mono text-text placeholder:text-text-faint"
          />

          <input
            type="number"
            min="0"
            placeholder="Max Amount"
            value={advancedFilters.maxAmount}
            onChange={(e) => setAdvancedFilters((prev) => ({ ...prev, maxAmount: e.target.value }))}
            className="bg-bg border border-border rounded-md px-3 py-2 text-xs font-mono text-text placeholder:text-text-faint"
          />

          <input
            type="date"
            value={advancedFilters.dateFrom}
            onChange={(e) => setAdvancedFilters((prev) => ({ ...prev, dateFrom: e.target.value }))}
            className="bg-bg border border-border rounded-md px-3 py-2 text-xs font-mono text-text"
          />

          <input
            type="date"
            value={advancedFilters.dateTo}
            onChange={(e) => setAdvancedFilters((prev) => ({ ...prev, dateTo: e.target.value }))}
            className="bg-bg border border-border rounded-md px-3 py-2 text-xs font-mono text-text"
          />
        </div>
      ) : null}

      <div className="flex-1 bg-bg-2 border border-border rounded-lg overflow-hidden flex flex-col">
        <div className="overflow-x-auto flex-1">
          <table className="w-full text-left text-sm whitespace-nowrap">
            <thead className="bg-bg-3 sticky top-0 z-10 font-mono text-xs text-text-dim">
              <tr>
                <th className="px-6 py-4 font-medium">Transaction ID</th>
                <th className="px-6 py-4 font-medium">Time</th>
                <th className="px-6 py-4 font-medium">Account / Merchant</th>
                <th className="px-6 py-4 font-medium">Amount</th>
                <th className="px-6 py-4 font-medium">Risk Score</th>
                <th className="px-6 py-4 font-medium">Status</th>
                <th className="px-6 py-4 font-medium text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border font-mono">
              {isLoading ? (
                <tr>
                  <td colSpan={7} className="px-6 py-8 text-center text-text-faint">Loading transactions...</td>
                </tr>
              ) : filteredTransactions.length === 0 ? (
                <tr>
                  <td colSpan={7} className="px-6 py-8 text-center text-text-faint">No transactions found</td>
                </tr>
              ) : (
                filteredTransactions.map((t: Transaction) => (
                  <tr key={t.id} className="hover:bg-bg-3/50 transition-colors group">
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-2">
                        {t.risk_tier === 'CRITICAL' && <div className="w-1 h-4 bg-risk-critical rounded-full" />}
                        <span className="text-text">{t.id.substring(0, 12)}...</span>
                      </div>
                    </td>
                    <td className="px-6 py-4 text-text-dim">
                      {new Date(t.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex flex-col">
                        <span className="text-text">{t.account_id}</span>
                        <span className="text-xs text-text-dim">{t.merchant_name} • {t.location_country}</span>
                      </div>
                    </td>
                    <td className="px-6 py-4 font-medium text-text">
                      {new Intl.NumberFormat('en-US', { style: 'currency', currency: t.currency || 'USD' }).format(t.amount)}
                    </td>
                    <td className="px-6 py-4">
                      {t.risk_score !== undefined && t.risk_score !== null ? (
                        <div className="flex items-center gap-3">
                          <span className="w-8">{t.risk_score.toFixed(1)}</span>
                          <div className="w-16 h-1.5 bg-bg border border-border rounded-full overflow-hidden">
                            <div 
                              className={`h-full ${
                                t.risk_score > 80 ? 'bg-risk-critical' :
                                t.risk_score > 60 ? 'bg-risk-high' :
                                t.risk_score > 30 ? 'bg-risk-medium' : 'bg-risk-low'
                              }`}
                              style={{ width: `${t.risk_score}%` }}
                            />
                          </div>
                        </div>
                      ) : (
                        <span className="text-text-faint">-</span>
                      )}
                    </td>
                    <td className="px-6 py-4">
                      <RiskBadge tier={t.risk_tier || 'UNKNOWN'} />
                    </td>
                    <td className="px-6 py-4 text-right">
                      <Link 
                        href={`/dashboard/transactions/${t.id}`}
                        className="inline-flex items-center gap-1 text-cyan opacity-0 group-hover:opacity-100 transition-opacity hover:text-cyan-dim"
                      >
                        Investigate <ArrowRight className="w-4 h-4" />
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
