"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Activity, AlertTriangle, ArrowLeftRight, Gauge } from "lucide-react";
import { cn } from "@/lib/utils/cn";

const navItems = [
  { name: "Overview", href: "/dashboard", icon: Gauge },
  { name: "Transactions", href: "/dashboard/transactions", icon: ArrowLeftRight },
  { name: "Alerts", href: "/dashboard/alerts", icon: AlertTriangle },
  { name: "Model Health", href: "/dashboard/model", icon: Activity },
];

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="w-72 border-r border-border bg-[#050814] flex flex-col shrink-0">
      <div className="h-[104px] px-6 border-b border-border flex flex-col justify-center">
        <div className="flex items-center gap-3">
          <div className="w-6 h-6 bg-amber rotate-45 rounded-sm" />
          <div className="text-4xl leading-none font-display font-bold tracking-wide text-text">TxGuard</div>
        </div>
        <div className="mt-2 text-xs font-mono tracking-[0.25em] text-cyan/80">AI · FRAUD INTEL</div>
      </div>

      <div className="px-6 pt-10 pb-4 text-xs font-mono tracking-[0.3em] text-text-faint">MONITORING</div>
      <nav className="px-3 space-y-2">
        {navItems.map((item) => {
          const isActive = pathname === item.href || (pathname.startsWith(item.href) && item.href !== "/dashboard");
          return (
            <Link
              key={item.name}
              href={item.href}
              className={cn(
                "flex items-center gap-3 px-4 py-3 rounded-xl transition-colors text-2xl font-display",
                isActive
                  ? "bg-amber/15 border border-amber/40 text-amber"
                  : "text-text-dim hover:text-text hover:bg-bg-3",
              )}
            >
              <item.icon className="w-5 h-5" />
              {item.name}
            </Link>
          );
        })}
      </nav>

      <div className="mt-auto p-4 border-t border-border">
        <div className="bg-bg-2 border border-border rounded-xl p-4">
          <div className="text-xs font-mono text-text-faint tracking-[0.2em] mb-3">MODEL STATUS</div>
          <div className="space-y-2 text-sm font-mono">
            <div className="flex items-center justify-between"><span className="text-text-dim">iso_forest</span><span className="text-risk-low border border-risk-low/30 px-2 rounded">OK</span></div>
            <div className="flex items-center justify-between"><span className="text-text-dim">lof</span><span className="text-risk-low border border-risk-low/30 px-2 rounded">OK</span></div>
            <div className="flex items-center justify-between"><span className="text-text-dim">rules_engine</span><span className="text-amber border border-amber/30 px-2 rounded">DRIFT</span></div>
          </div>
        </div>
      </div>
    </aside>
  );
}
