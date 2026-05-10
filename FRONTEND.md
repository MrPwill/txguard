# TxGuard AI — Frontend Architecture
## Next.js Dashboard — Design & Technical Spec

> This document covers the frontend layer of TxGuard AI. It is Phase 5 of the build plan (`Plan.md`). All API endpoints consumed here are defined in `PRD.md` §6 API Surface. The Investigation Report page renders output from the agent crew documented in `AGENTS.md`.

---

## Design Direction

**Aesthetic:** Dark industrial war-room — high information density, no wasted space. Every value feels like it came from a real ops center.
**Palette:** Near-black bg (`#07090E`) · Electric amber (`#F59E0B`) for risk/danger · Cold cyan (`#22D3EE`) for data · Green (`#10B981`) for safe · Red (`#F43F5E`) for critical. Mirrors the risk tier color system defined in `PRD.md` FR-06.
**Typography:** Syne (display/headings) + IBM Plex Mono (data values, IDs, metrics).
**Differentiator:** Monospaced transaction IDs, animated score rings, live pulsing status indicators, real chart density — not a generic dashboard template.

---

## Tech Stack

| Layer | Technology | Notes |
|---|---|---|
| Framework | Next.js 14 (App Router) | SSR for initial load, RSC for data fetching |
| Styling | Tailwind CSS + CSS Variables | Custom design tokens (see §Tailwind Design Tokens) |
| Charts | Recharts | Area, Bar, Line charts |
| Real-time | TanStack Query + WebSocket | Polling for investigation status; WS for alert feed |
| Global State | Zustand | Live alert store, selected transaction state |
| Tables | TanStack Table | Virtual scrolling — handles 10k+ transaction rows |
| Animations | Framer Motion | Staggered reveals, score ring transitions |
| HTTP Client | Axios | Typed, baseURL configured from env |
| Auth | NextAuth.js | Credentials provider for demo analyst login |
| Deployment | Docker | Single container with Nginx, deployed via Terraform |

Full backend stack is in `Plan.md` §Full Tech Stack.

---

## Project Structure

```
txguard-frontend/
├── app/
│   ├── layout.tsx                 # Root layout: font imports, theme provider
│   ├── page.tsx                   # Redirect → /dashboard
│   ├── login/
│   │   └── page.tsx               # Analyst login page
│   └── dashboard/
│       ├── layout.tsx             # Sidebar + topbar shell
│       ├── page.tsx               # Overview (FR-21)
│       ├── transactions/
│       │   ├── page.tsx           # Transaction Monitor (FR-21)
│       │   └── [id]/
│       │       └── page.tsx       # Transaction Detail + SHAP (FR-14, FR-15)
│       ├── alerts/
│       │   ├── page.tsx           # Alert Queue (FR-21)
│       │   └── [id]/
│       │       └── page.tsx       # Investigation Report (FR-23)
│       └── model/
│           └── page.tsx           # Model Health + drift (FR-20)
├── components/
│   ├── layout/
│   │   ├── Sidebar.tsx
│   │   ├── Topbar.tsx
│   │   └── LiveStatusBar.tsx      # System status + latency pill
│   ├── dashboard/
│   │   ├── KpiCard.tsx
│   │   ├── VolumeChart.tsx        # 24h total vs flagged (AreaChart)
│   │   ├── ScoreDistChart.tsx     # Score distribution (BarChart, tier colors)
│   │   ├── TierBreakdown.tsx      # Animated progress bars per tier
│   │   └── LiveAlertFeed.tsx      # WS-powered, new alerts slide in from top
│   ├── transactions/
│   │   ├── TransactionTable.tsx   # TanStack Table with virtual scroll
│   │   ├── TransactionFilters.tsx # Tier, channel, date range filter chips
│   │   ├── RiskScoreCell.tsx      # Mini bar + colored score number
│   │   └── RuleFlagTags.tsx       # Compact rule trigger tag chips
│   ├── alerts/
│   │   ├── AlertQueueTable.tsx    # Sortable alert table with status filter tabs
│   │   └── AlertStatusBadge.tsx   # PENDING / INVESTIGATING / COMPLETE / ESCALATED
│   ├── investigation/
│   │   ├── InvestigationHeader.tsx  # Score ring + transaction metadata
│   │   ├── RecommendationBanner.tsx # Color-coded action banner (FR-23)
│   │   ├── AgentChain.tsx           # Agent 1→2→3→4 trace with durations
│   │   ├── ShapChart.tsx            # Horizontal feature attribution bars (FR-14)
│   │   ├── RegulatoryCards.tsx      # Regulation + provision + implication cards
│   │   └── AuditTrail.tsx           # Ordered decision timeline (FR-18)
│   ├── model/
│   │   ├── DriftChart.tsx           # Baseline vs rolling mean LineChart (FR-20)
│   │   ├── FeatureImportance.tsx    # Horizontal bar chart per model
│   │   └── ModelVersionTable.tsx    # Version, precision, recall, status badge
│   └── shared/
│       ├── ScoreRing.tsx            # SVG ring — color maps to PRD FR-06 tiers
│       ├── RiskBadge.tsx            # LOW / MEDIUM / HIGH / CRITICAL chip
│       ├── DataTable.tsx            # Generic table wrapper
│       └── LivePulse.tsx            # Animated green dot for live indicators
├── lib/
│   ├── api/
│   │   ├── client.ts               # Axios instance + base URL from env
│   │   ├── transactions.ts         # useTransactions, useTransactionDetail, useExplain
│   │   ├── alerts.ts               # useAlerts, useInvestigation
│   │   └── model.ts                # useModelStatus
│   ├── stores/
│   │   └── alertStore.ts           # Zustand: live alert list (max 50), WebSocket sync
│   ├── utils/
│   │   ├── riskColor.ts            # score → color mapping (matches PRD FR-06 tiers)
│   │   └── formatters.ts           # Currency, ISO8601 date, duration, tier labels
│   └── types/
│       ├── transaction.ts          # Transaction, ScoringResponse, ExplainResponse
│       ├── alert.ts                # Alert, AlertStatus
│       └── investigation.ts        # InvestigationReport, AgentRunMetadata
├── hooks/
│   ├── useAlertWebSocket.ts        # WS /alerts/live → Zustand store (FR-22)
│   ├── useTransactions.ts
│   └── useInvestigation.ts         # Polls every 3s while IN_PROGRESS (FR-23)
├── public/
│   └── txguard-logo.svg
├── tailwind.config.ts
└── next.config.ts
```

---

## Pages & Views

All views below consume endpoints from `PRD.md` §6 API Surface.

### 1. `/dashboard` — Operations Overview

**Maps to:** PRD FR-21, FR-22
**Purpose:** Real-time ops center home. First thing an analyst sees on login.

**Components:**
- 4 KPI cards (Transactions Today, Alerts Raised, Auto-Cleared, Pending Review) — count-up animation on load
- Volume chart: 24h total vs flagged transactions (AreaChart)
- Live Alert Feed: WebSocket-powered via `WS /alerts/live`, new alerts slide in from top
- Risk Score Distribution: BarChart, each bar colored by its tier (matches FR-06 tier colors)
- Tier Breakdown: animated progress bars (LOW / MEDIUM / HIGH / CRITICAL)

**Data sources:**
```typescript
// Polling every 30s
const { data: metrics } = useQuery({
  queryKey: ['metrics'],
  queryFn: fetchDailyMetrics,
  refetchInterval: 30_000,
});

// WebSocket live feed (FR-22: < 1s delivery)
const { alerts } = useAlertWebSocket(`${process.env.NEXT_PUBLIC_WS_URL}/alerts/live`);
```

---

### 2. `/dashboard/transactions` — Transaction Monitor

**Maps to:** PRD FR-21
**Purpose:** Full searchable, filterable transaction table. Primary analyst triage surface.

**Components:**
- Search bar (by transaction ID, merchant, account ID)
- Filter chips: tier, channel, date range
- TanStack Table with virtual scrolling (handles 10k+ rows without DOM bloat)
- `RiskScoreCell`: mini filled bar + colored score number per PRD FR-06 tier colors
- `RuleFlagTags`: compact chip list of rule triggers that fired (per FR-07 `rule_triggers[]`)
- Click any row → `/dashboard/transactions/[id]`

**Key UX:** Row hover reveals an inline "Investigate →" action. CRITICAL-tier rows carry a 2px red left border to catch the eye instantly.

---

### 3. `/dashboard/transactions/[id]` — Transaction Detail

**Maps to:** PRD FR-14, FR-15, FR-18
**Purpose:** Full breakdown of a single transaction's scoring decision with explainability.

**Sections:**
- Transaction metadata header: amount, merchant, account, channel, timestamp, status chip
- Hybrid score breakdown: rule weights table (Layer 1) + ML anomaly score (Layer 2) side by side
- SHAP attribution chart: horizontal bars per feature, red = risk-increasing, green = risk-reducing (FR-14)
- Reason codes: the 3 human-readable strings from FR-15
- Audit log timeline for this transaction (`GET /transactions/{id}/audit`, FR-18)
- "View Investigation Report" link if an alert exists for this transaction

---

### 4. `/dashboard/alerts` — Alert Queue

**Maps to:** PRD FR-21, FR-22
**Purpose:** Triage view showing all HIGH and CRITICAL alerts (risk score ≥ 61, per FR-10).

**Components:**
- Status filter tabs: ALL / PENDING / INVESTIGATING / COMPLETE / ESCALATED
- `AlertQueueTable` with sortable columns: tier, created time, investigation status, merchant
- `AlertStatusBadge` for each row
- Inline "Open Report →" button → `/dashboard/alerts/[id]`
- Live badge on the tab showing count of PENDING alerts, updated via WebSocket

---

### 5. `/dashboard/alerts/[id]` — Investigation Report

**Maps to:** PRD FR-11, FR-12, FR-23; AGENTS.md agent output schemas
**Purpose:** The flagship page. Full output of the 4-agent CrewAI investigation.

**Layout:**
```
┌─ Score Ring + Transaction Header ──────────────────────────────────┐
├─ RECOMMENDATION BANNER (CLEAR | ESCALATE_TO_SAR | BLOCK | MONITOR)─┤
├─ Executive Summary (Agent 4 synthesis, regulator-facing) ───────────┤
├─ Agent Chain Trace ─────────────────────────────────────────────────┤
│   Agent 1 → Agent 2 → Agent 3 → Agent 4                            │
│   (each: name, finding summary, execution duration from metadata)   │
├─ SHAP Explanation Chart (same component as Transaction Detail) ──────┤
├─ Regulatory Citations (cards: regulation + provision + implication)──┤
├─ Counterparty Risk + Sanctions Status ──────────────────────────────┤
└─ Audit Trail (full ordered decision log via GET /transactions/{id}/audit)┘
```

**Key interaction (FR-23):** While `investigation_status = IN_PROGRESS`, the page polls `GET /transactions/{id}/report` every 3 seconds. The Agent Chain renders each agent as "pending" (dimmed) until its `agent_run_metadata` entry appears. On COMPLETE, the full report renders and polling stops.

---

### 6. `/dashboard/model` — Model Health

**Maps to:** PRD FR-19, FR-20
**Purpose:** MLOps monitoring. Lets a Risk Manager track model behaviour over time.

**Components:**
- Drift Warning banner (amber) — shown when `/model/status` returns `drift_detected: true` (> 15% shift per FR-20)
- `DriftChart`: LineChart, baseline mean vs 7-day rolling mean (FR-20)
- `FeatureImportance`: horizontal bar chart per model (Isolation Forest, LOF)
- `ModelVersionTable`: name, version, precision, recall, last retrained, health status badge

---

## Real-Time Architecture

```typescript
// hooks/useAlertWebSocket.ts
// Implements PRD FR-22: < 1s alert delivery from WS /alerts/live

export function useAlertWebSocket(url: string) {
  const addAlert = useAlertStore((s) => s.addAlert);

  useEffect(() => {
    const ws = new WebSocket(url);

    ws.onmessage = (e) => {
      const alert = JSON.parse(e.data);
      addAlert(alert);                         // Push to Zustand store
      toast.custom(<AlertToast alert={alert} />); // Toast notification
    };

    ws.onclose = () => setTimeout(() => useAlertWebSocket(url), 3_000); // Auto-reconnect

    return () => ws.close();
  }, [url]);
}

// lib/stores/alertStore.ts
const useAlertStore = create<AlertStore>((set) => ({
  alerts: [],
  addAlert: (alert) =>
    set((s) => ({ alerts: [alert, ...s.alerts].slice(0, 50) })), // Cap at 50
  clearAlerts: () => set({ alerts: [] }),
}));
```

---

## API Integration

All endpoints match `PRD.md` §6 API Surface exactly.

```typescript
// lib/api/client.ts
export const apiClient = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL,
  timeout: 10_000,
});

// lib/api/transactions.ts
export const useTransactions = (filters: TransactionFilters) =>
  useQuery({
    queryKey: ['transactions', filters],
    queryFn: () => apiClient.get('/transactions', { params: filters }).then((r) => r.data),
    staleTime: 10_000,
  });

export const useExplain = (txnId: string) =>
  useQuery({
    queryKey: ['explain', txnId],
    queryFn: () => apiClient.get(`/transactions/${txnId}/explain`).then((r) => r.data),
  });

// lib/api/alerts.ts
// Implements PRD FR-23: poll every 3s while IN_PROGRESS
export const useInvestigation = (txnId: string) =>
  useQuery({
    queryKey: ['investigation', txnId],
    queryFn: () => apiClient.get(`/transactions/${txnId}/report`).then((r) => r.data),
    refetchInterval: (data) => (data?.investigation_status === 'IN_PROGRESS' ? 3_000 : false),
  });

// lib/api/model.ts
export const useModelStatus = () =>
  useQuery({
    queryKey: ['model-status'],
    queryFn: () => apiClient.get('/model/status').then((r) => r.data),
    refetchInterval: 60_000, // Refresh every minute
  });
```

---

## Tailwind Design Tokens

Risk tier colors here match `PRD.md` FR-06 exactly, ensuring visual consistency between the backend tier definitions and frontend rendering.

```typescript
// tailwind.config.ts
export default {
  theme: {
    extend: {
      colors: {
        bg: { DEFAULT: '#07090E', 2: '#0C0F16', 3: '#111520' },
        border: { DEFAULT: '#1A2035', 2: '#222840' },
        amber: { DEFAULT: '#F59E0B', dim: '#D97706' },
        cyan: { DEFAULT: '#22D3EE', dim: '#0891B2' },
        risk: {
          low: '#10B981',       // score 0–30
          medium: '#FB923C',    // score 31–60
          high: '#F59E0B',      // score 61–80
          critical: '#F43F5E',  // score 81–100
        },
        text: { DEFAULT: '#DDE4F0', dim: '#7B8BA8', faint: '#3D4E6A' },
      },
      fontFamily: {
        display: ['Syne', 'sans-serif'],
        mono: ['IBM Plex Mono', 'monospace'],
      },
    },
  },
};
```

---

## Environment Variables

```bash
# .env.local
NEXT_PUBLIC_API_URL=http://localhost:8000      # FastAPI backend (txguard-api)
NEXT_PUBLIC_WS_URL=ws://localhost:8000         # WebSocket base (same server)
NEXTAUTH_SECRET=your-secret-here
NEXTAUTH_URL=http://localhost:3000

# Production (Cloud Run / Container Apps)
NEXT_PUBLIC_API_URL=https://your-app-domain.com
NEXT_PUBLIC_WS_URL=wss://your-app-domain.com
```

---

## Setup Commands

```bash
# Scaffold
npx create-next-app@latest txguard-frontend --typescript --tailwind --app
cd txguard-frontend

# Install dependencies
npm install recharts \
  @tanstack/react-query @tanstack/react-table \
  zustand framer-motion axios next-auth

# Development
npm run dev

# Production build
npm run build && npm run export
```

The full stack (backend + frontend) is deployed as a single Docker container managed by Supervisord. See `Plan.md` §Monorepo Structure.

---

## Demo Mode

For portfolio demos and screen recordings, enable "Demo Mode" in the dashboard settings. When active, a mock WebSocket event fires every 15 seconds injecting a new CRITICAL alert into the live feed — ensuring the real-time system is visibly active throughout any review or recording session.
