export default function RankingList({ title, items, renderValue }) {
  return (
    <div style={{ border: "1px solid #e2e8f0", borderRadius: 10, padding: 16, flex: 1 }}>
      <div style={{ fontWeight: 600, fontSize: 14, marginBottom: 12 }}>{title}</div>
      {items.length === 0 ? (
        <div style={{ fontSize: 13, color: "#94a3b8" }}>No medicines sold.</div>
      ) : (
        <ol style={{ margin: 0, padding: 0, listStyle: "none" }}>
          {items.slice(0, 5).map((item, i) => (
            <li
              key={item.drug_name}
              style={{
                display: "flex",
                justifyContent: "space-between",
                padding: "8px 0",
                borderTop: i > 0 ? "1px solid #f1f5f9" : "none",
                fontSize: 13,
              }}
            >
              <span>
                <span style={{ color: "#94a3b8", marginRight: 8 }}>{i + 1}</span>
                <strong>{item.drug_name}</strong>
              </span>
              <span style={{ color: "#475569" }}>{renderValue(item)}</span>
            </li>
          ))}
        </ol>
      )}
    </div>
  );
}
