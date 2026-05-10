"use client";

import { Area, AreaChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

interface DataPoint {
  hour: string;
  total: number;
  flagged: number;
}

export default function VolumeChart({ data }: { data: DataPoint[] }) {
  return (
    <div className="bg-bg-2 border border-border rounded-xl p-5 h-80 flex flex-col">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-2xl font-display font-semibold text-text">TRANSACTION VOLUME - 24H</h3>
        <span className="text-sm font-mono text-text-dim">total vs flagged</span>
      </div>
      <div className="flex-1">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={data} margin={{ top: 8, right: 8, left: 0, bottom: 0 }}>
            <defs>
              <linearGradient id="totalFill" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#22D3EE" stopOpacity={0.4} />
                <stop offset="95%" stopColor="#22D3EE" stopOpacity={0.05} />
              </linearGradient>
              <linearGradient id="flaggedFill" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#F43F5E" stopOpacity={0.3} />
                <stop offset="95%" stopColor="#F43F5E" stopOpacity={0.02} />
              </linearGradient>
            </defs>
            <CartesianGrid stroke="#1A2035" strokeDasharray="3 3" />
            <XAxis dataKey="hour" stroke="#7B8BA8" tick={{ fontSize: 11 }} minTickGap={20} />
            <YAxis stroke="#7B8BA8" tick={{ fontSize: 11 }} allowDecimals={false} />
            <Tooltip
              contentStyle={{ backgroundColor: "#0C0F16", border: "1px solid #1A2035", color: "#DDE4F0" }}
              labelStyle={{ color: "#7B8BA8" }}
            />
            <Area type="monotone" dataKey="total" stroke="#22D3EE" fill="url(#totalFill)" strokeWidth={2.5} />
            <Area type="monotone" dataKey="flagged" stroke="#F43F5E" fill="url(#flaggedFill)" strokeWidth={2} />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
