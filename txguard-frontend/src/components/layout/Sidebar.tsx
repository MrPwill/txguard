"use client";

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { LayoutDashboard, ShieldAlert, Activity, FileText } from 'lucide-react';
import { cn } from '@/lib/utils/cn';

const navItems = [
  { name: 'Overview', href: '/dashboard', icon: LayoutDashboard },
  { name: 'Transactions', href: '/dashboard/transactions', icon: FileText },
  { name: 'Alert Queue', href: '/dashboard/alerts', icon: ShieldAlert },
  { name: 'Model Health', href: '/dashboard/model', icon: Activity },
];

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="w-64 border-r border-border bg-bg-2 flex flex-col shrink-0">
      <div className="h-16 flex items-center px-6 border-b border-border">
        <div className="font-display font-bold text-xl tracking-wide flex items-center gap-2 text-text">
          <div className="w-4 h-4 bg-cyan rounded-sm"></div>
          TxGuard AI
        </div>
      </div>
      <nav className="flex-1 px-4 py-6 space-y-2">
        {navItems.map((item) => {
          const isActive = pathname === item.href || (pathname.startsWith(item.href) && item.href !== '/dashboard');
          return (
            <Link
              key={item.name}
              href={item.href}
              className={cn(
                "flex items-center gap-3 px-3 py-2 rounded-md transition-colors text-sm font-medium",
                isActive 
                  ? "bg-bg-3 text-cyan" 
                  : "text-text-dim hover:text-text hover:bg-bg-3"
              )}
            >
              <item.icon className="w-4 h-4" />
              {item.name}
            </Link>
          );
        })}
      </nav>
      <div className="p-4 border-t border-border">
        <div className="text-xs text-text-faint font-mono">
          SYSTEM_OP_MODE: ACTIVE
        </div>
      </div>
    </aside>
  );
}
