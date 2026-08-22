import { BarChart, Bar, XAxis, YAxis, ResponsiveContainer, Cell, Tooltip } from "recharts";

const formatHour = (h) => {
  if (h === 0) return "12am";
  if (h === 12) return "12pm";
  return h < 12 ? `${h}am` : `${h - 12}pm`;
};

const rupees = (paise) => `₹${(paise / 100).toLocaleString("en-IN")}`;

export default function RevenueChart({ revenueByHour, peakHour }) {
  // Only show a reasonable window (e.g. 8am-8pm) so the chart isn't 24 empty bars.
  const visibleHours = revenueByHour.filter((h) => h.hour >= 8 && h.hour <= 20);

  const chartData = visibleHours.map((h) => ({
    hourLabel: formatHour(h.hour),
    revenue: h.revenue_paise / 100,
    isPeak: peakHour && h.hour === peakHour.hour,
  }));

  return (
    <div style={{ border: "1px solid #e2e8f0", borderRadius: 10, padding: 16 }}>
      <div style={{ fontWeight: 600, fontSize: 14, marginBottom: 4 }}>Revenue by Hour of Day</div>
      {peakHour ? (
        <div style={{ fontSize: 12, color: "#4338ca", marginBottom: 12 }}>
          Peak: {formatHour(peakHour.hour)}–{formatHour(peakHour.hour + 1)} —{" "}
          {rupees(peakHour.revenue_paise)}
        </div>
      ) : (
        <div style={{ fontSize: 12, color: "#94a3b8", marginBottom: 12 }}>No revenue recorded</div>
      )}
      <ResponsiveContainer width="100%" height={220}>
        <BarChart data={chartData}>
          <XAxis dataKey="hourLabel" fontSize={11} tickLine={false} axisLine={false} />
          <YAxis hide />
          <Tooltip formatter={(v) => [`₹${v.toLocaleString("en-IN")}`, "Revenue"]} />
          <Bar dataKey="revenue" radius={[4, 4, 0, 0]}>
            {chartData.map((entry, i) => (
              <Cell key={i} fill={entry.isPeak ? "#4338ca" : "#c7d2fe"} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}