import { NavLink, Outlet } from "react-router-dom";
import { Receipt, BarChart3, Sparkles } from "lucide-react";

const navItems = [
  { to: "/", label: "EOD Reconciliation", icon: Receipt },
  { to: "/analytics", label: "Analytics", icon: BarChart3 },
  { to: "/narrative", label: "AI Narrative Summary", icon: Sparkles },
];

export default function Layout() {
  return (
    <div style={{ display: "flex", minHeight: "100vh", fontFamily: "sans-serif" }}>
      <aside
        style={{
          width: 220,
          borderRight: "1px solid #e2e8f0",
          padding: "24px 12px",
          background: "#f8fafc",
        }}
      >
        <div style={{ fontWeight: 700, fontSize: 18, marginBottom: 24, padding: "0 8px", color: "#1e3a8a" }}>
          SwasthiQ
        </div>
        <nav style={{ display: "flex", flexDirection: "column", gap: 4 }}>
          {navItems.map(({ to, label, icon: Icon }) => (
            <NavLink
              key={to}
              to={to}
              end={to === "/"}
              style={({ isActive }) => ({
                display: "flex",
                alignItems: "center",
                gap: 10,
                padding: "10px 12px",
                borderRadius: 8,
                textDecoration: "none",
                fontSize: 14,
                color: isActive ? "#1e3a8a" : "#475569",
                background: isActive ? "#e0e7ff" : "transparent",
                fontWeight: isActive ? 600 : 400,
              })}
            >
              <Icon size={18} />
              {label}
            </NavLink>
          ))}
        </nav>
      </aside>
      <main style={{ flex: 1, padding: 32, background: "#fff" }}>
        <Outlet />
      </main>
    </div>
  );
}
