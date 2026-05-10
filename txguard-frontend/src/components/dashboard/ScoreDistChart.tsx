"use client";

import { Bar, BarChart, CartesianGrid, Cell, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

interface BarPoint {
  tier: "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";
  count: number;
}

const tierColor: Record<BarPoint["tier"], string> = {
  LOW: "#10B981",
  MEDIUM: "#FB923C",
  HIGH: "#F59E0B",
  CRITICAL: "#F43F5E",
};

export default function ScoreDistChart({ data }: { data: BarPoint[] }) {
  return (
    <div className="bg-bg-2 border border-border rounded-xl p-5 h-64 flex flex-col">
      <h3 className="text-sm font-mono text-text-dim mb-4 tracking-widest">RISK SCORE DISTRIBUTION</h3>
      <div className="flex-1">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data}>
            <CartesianGrid stroke="#1A2035" strokeDasharray="3 3" />
            <XAxis dataKey="tier" stroke="#7B8BA8" tick={{ fontSize: 11 }} />
            <YAxis stroke="#7B8BA8" tick={{ fontSize: 11 }} allowDecimals={false} />
            <Tooltip contentStyle={{ backgroundColor: "#0C0F16", border: "1px solid #1A2035" }} />
            <Bar dataKey="count" radius={[6, 6, 0, 0]}>
              {data.map((entry) => (
                <Cell key={entry.tier} fill={tierColor[entry.tier]} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

