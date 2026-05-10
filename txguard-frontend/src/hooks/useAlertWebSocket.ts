import { useEffect } from 'react';
import { useAlertStore } from '@/lib/stores/alertStore';

export function useAlertWebSocket(url: string | undefined) {
  const addAlert = useAlertStore((s) => s.addAlert);

  useEffect(() => {
    if (!url) return;

    const ws = new WebSocket(url);

    ws.onmessage = (e) => {
      try {
        const payload = JSON.parse(e.data);
        const alert = {
          id: payload.id ?? payload.alert_id,
          transaction_id: payload.transaction_id,
          risk_tier: payload.risk_tier,
          rule_triggers: payload.rule_triggers ?? [],
          ml_anomaly_score: payload.ml_anomaly_score ?? 0,
          reason_codes: payload.reason_codes ?? [],
          investigation_status: payload.investigation_status ?? 'PENDING',
          created_at: payload.created_at ?? new Date().toISOString(),
        };

        if (alert.id && alert.transaction_id && alert.risk_tier) {
          addAlert(alert);
        }
      } catch (err) {
        console.error('Failed to parse alert from WS', err);
      }
    };

    ws.onclose = () => {
      console.log('WebSocket disconnected.');
    };

    return () => ws.close();
  }, [url, addAlert]);
}
