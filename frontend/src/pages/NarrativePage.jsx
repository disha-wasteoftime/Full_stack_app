import { useEffect, useState } from "react";
import { useLog } from "../context/LogContext";
import { getNarrative } from "../api";

export default function NarrativePage() {
  const { logId, clinicId, status: logStatus, error: logError } = useLog();
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!logId) return;
    getNarrative(logId)
      .then(setData)
      .catch((err) => setError(err.response?.data?.detail || err.message));
  }, [logId]);

  if (logStatus === "uploading") return <p>Loading billing data...</p>;
  if (logStatus === "error") return <p style={{ color: "#dc2626" }}>Upload failed: {logError}</p>;
  if (error) return <p style={{ color: "#dc2626" }}>Error: {error}</p>;
  if (!data) return <p>Generating narrative...</p>;

  const traced = data.traced_figures || [];

  return (
    <div>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
        <div>
          <div style={{ fontSize: 20, fontWeight: 700 }}>AI Narrative Summary</div>
          <div style={{ fontSize: 13, color: "#64748b" }}>
            Generated from today's reconciliation — {clinicId}
          </div>
        </div>
        <span
          style={{
            fontSize: 11,
            fontWeight: 600,
            color: "#6d28d9",
            background: "#ede9fe",
            padding: "4px 10px",
            borderRadius: 999,
          }}
        >
          AI SUGGESTED
        </span>
      </div>

      <div style={{ display: "flex", gap: 16, marginTop: 20, alignItems: "flex-start" }}>
        <div
          style={{
            flex: 1.4,
            background: "#dcfce7",
            border: "1px solid #bbf7d0",
            borderRadius: 10,
            padding: 16,
          }}
        >
          <div style={{ fontSize: 12, color: "#166534", marginBottom: 10 }}>
            Sent to Clinic Owner — WhatsApp
          </div>
          <div style={{ fontSize: 14, color: "#14532d", whiteSpace: "pre-wrap", lineHeight: 1.6 }}>
            {data.narrative}
          </div>
          <div
            style={{
              marginTop: 12,
              fontSize: 11,
              fontWeight: 700,
              color: data.grounded ? "#166534" : "#b45309",
            }}
          >
            {data.grounded ? "GROUNDED ✓" : "FALLBACK USED"}
          </div>
        </div>

        <div style={{ flex: 1, border: "1px solid #e2e8f0", borderRadius: 10, padding: 16 }}>
          <div style={{ fontWeight: 600, fontSize: 14, marginBottom: 4 }}>Traced Figures</div>
          <div style={{ fontSize: 12, color: "#94a3b8", marginBottom: 12 }}>
            Every number above maps to the deterministic report — this is what gets auto-checked.
          </div>
          {traced.length === 0 ? (
            <div style={{ fontSize: 13, color: "#94a3b8" }}>No figures traced.</div>
          ) : (
            traced.map((fig, i) => (
              <div
                key={i}
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  padding: "6px 0",
                  borderTop: i > 0 ? "1px solid #f1f5f9" : "none",
                  fontSize: 13,
                }}
              >
                <span style={{ fontWeight: 600 }}>{fig.display_value}</span>
                <span style={{ color: "#6d28d9", fontFamily: "monospace", fontSize: 11 }}>
                  {fig.source_field}
                </span>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
