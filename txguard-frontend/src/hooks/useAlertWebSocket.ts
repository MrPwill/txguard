import { useEffect } from 'react';
import { useAlertStore } from '@/lib/stores/alertStore';

export function useAlertWebSocket(url: string | undefined) {
  const addAlert = useAlertStore((s) => s.addAlert);

  useEffect(() => {
    if (!url) return;
    const ws = new WebSocket(url);

    ws.onmessage = (e) => {
      try {
        const alert = JSON.parse(e.data);
        addAlert(alert);
      } catch (err) {
        console.error("Failed to parse alert from WS", err);
      }
    };

    ws.onclose = () => {
      console.log("WebSocket disconnected.");
      // For demo, not adding full robust backoff reconnect
    };

    return () => ws.close();
  }, [url, addAlert]);
}
