export default function StatCard({ label, value, sublabel, tone = "default" }) {
  const toneColors = {
    default: "#0f172a",
    danger: "#dc2626",
    muted: "#64748b",
  };

  return (
    <div
      style={{
        border: "1px solid #e2e8f0",
        borderRadius: 10,
        padding: 16,
        flex: 1,
        minWidth: 160,
      }}
    >
      <div style={{ fontSize: 11, fontWeight: 600, color: "#64748b", letterSpacing: 0.5 }}>
        {label.toUpperCase()}
      </div>
      <div style={{ fontSize: 24, fontWeight: 700, color: toneColors[tone], marginTop: 4 }}>
        {value}
      </div>
      {sublabel && <div style={{ fontSize: 12, color: "#94a3b8", marginTop: 4 }}>{sublabel}</div>}
    </div>
  );
}