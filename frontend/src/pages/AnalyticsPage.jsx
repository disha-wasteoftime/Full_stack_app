import { useEffect, useState } from "react";
import { useLog } from "../context/LogContext";
import { getAnalytics } from "../api";
import RevenueChart from "../components/RevenueChart";
import RankingList from "../components/RankingList";

const rupees = (paise) => `₹${(paise / 100).toLocaleString("en-IN")}`;

export default function AnalyticsPage() {
  const { logId, clinicId, status: logStatus, error: logError } = useLog();
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!logId) return;
    getAnalytics(logId)
      .then(setData)
      .catch((err) => setError(err.response?.data?.detail || err.message));
  }, [logId]);

  if (logStatus === "uploading") return <p>Loading billing data...</p>;
  if (logStatus === "error") return <p style={{ color: "#dc2626" }}>Upload failed: {logError}</p>;
  if (error) return <p style={{ color: "#dc2626" }}>Error: {error}</p>;
  if (!data) return <p>Loading analytics...</p>;

  return (
    <div>
      <div style={{ marginBottom: 4, fontSize: 20, fontWeight: 700 }}>Analytics</div>
      <div style={{ marginBottom: 24, fontSize: 13, color: "#64748b" }}>{clinicId}</div>

      <div style={{ marginBottom: 16 }}>
        <RevenueChart revenueByHour={data.revenue_by_hour} peakHour={data.peak_hour} />
      </div>

      <div style={{ display: "flex", gap: 16, flexWrap: "wrap" }}>
        <RankingList
          title="Top Medicines — by Quantity"
          items={data.top_medicines_by_quantity}
          renderValue={(item) => `${item.qty} units`}
        />
        <RankingList
          title="Top Medicines — by Revenue"
          items={data.top_medicines_by_revenue}
          renderValue={(item) => rupees(item.revenue_paise)}
        />
      </div>
    </div>
  );
}