import { useEffect, useState } from "react";
import { useLog } from "../context/LogContext";
import { getReconciliation } from "../api";
import StatCard from "../components/StatCard";

const rupees = (paise) => `₹${(paise / 100).toLocaleString("en-IN")}`;

export default function ReconciliationPage() {
  const { logId, clinicId, status: logStatus, error: logError } = useLog();
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!logId) return;
    getReconciliation(logId)
      .then(setData)
      .catch((err) => setError(err.response?.data?.detail || err.message));
  }, [logId]);

  if (logStatus === "uploading") return <p>Loading billing data...</p>;
  if (logStatus === "error") return <p style={{ color: "#dc2626" }}>Upload failed: {logError}</p>;
  if (error) return <p style={{ color: "#dc2626" }}>Error: {error}</p>;
  if (!data) return <p>Loading reconciliation...</p>;

  return (
    <div>
      <div style={{ marginBottom: 4, fontSize: 20, fontWeight: 700 }}>EOD Reconciliation</div>
      <div style={{ marginBottom: 24, fontSize: 13, color: "#64748b" }}>
        {clinicId} — {data.total_visits} visits
      </div>

      <div style={{ display: "flex", gap: 16, marginBottom: 24, flexWrap: "wrap" }}>
        <StatCard
          label="Total Billed"
          value={rupees(data.total_billed_paise)}
          sublabel={`${data.total_visits} visits`}
        />
        <StatCard
          label="Total Collected"
          value={rupees(data.total_collected_paise)}
          sublabel={`${data.collected_pct_of_billed}% of billed`}
        />
        <StatCard
          label="Outstanding"
          value={rupees(data.total_outstanding_paise)}
          sublabel={`${data.outstanding_visit_count} pending visits`}
          tone={data.total_outstanding_paise > 0 ? "danger" : "default"}
        />
        <StatCard
          label="Refunds"
          value={rupees(data.total_refunds_paise)}
          sublabel={`${data.refund_visit_count} refund(s)`}
        />
      </div>

      <div style={{ border: "1px solid #e2e8f0", borderRadius: 10, padding: 16 }}>
        <div style={{ fontWeight: 600, marginBottom: 12, fontSize: 14 }}>Payment Mode Breakdown</div>
        <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 13 }}>
          <thead>
            <tr style={{ textAlign: "left", color: "#64748b" }}>
              <th style={{ padding: "6px 0" }}>Mode</th>
              <th>Billed</th>
              <th>Collected</th>
              <th>Outstanding</th>
            </tr>
          </thead>
          <tbody>
            {Object.entries(data.by_payment_mode).map(([mode, values]) => (
              <tr key={mode} style={{ borderTop: "1px solid #f1f5f9" }}>
                <td style={{ padding: "8px 0", fontWeight: 600, textTransform: "capitalize" }}>{mode}</td>
                <td>{rupees(values.billed_paise)}</td>
                <td>{rupees(values.collected_paise)}</td>
                <td>{rupees(values.outstanding_paise)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}