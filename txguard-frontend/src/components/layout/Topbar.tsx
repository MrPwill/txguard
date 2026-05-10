import LiveStatusBar from "./LiveStatusBar";

export default function Topbar() {
  return (
    <header className="h-16 border-b border-border bg-bg-2 flex items-center justify-between px-6 shrink-0">
      <div className="text-sm font-mono text-text-dim">
        Ops Center &gt; Live Stream
      </div>
      <div className="flex items-center gap-4">
        <LiveStatusBar />
        <div className="flex items-center gap-2 border-l border-border pl-4">
          <div className="w-8 h-8 rounded-full bg-bg-3 border border-border flex items-center justify-center text-xs font-bold text-text-dim">
            AN
          </div>
        </div>
      </div>
    </header>
  );
}
