import LiveStatusBar from "./LiveStatusBar";

export default function Topbar() {
  return (
    <header className="h-[72px] border-b border-border bg-bg flex items-center justify-between px-8 shrink-0">
      <div>
        <div className="text-4xl font-display font-bold tracking-wide text-text">Operations Overview</div>
        <div className="text-sm font-mono text-text-dim mt-1">txguard-ai · live monitoring</div>
      </div>
      <LiveStatusBar />
    </header>
  );
}
