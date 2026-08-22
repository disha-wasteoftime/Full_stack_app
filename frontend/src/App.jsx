import { BrowserRouter, Routes, Route } from "react-router-dom";
import { LogProvider } from "./context/LogContext";
import Layout from "./components/Layout";
import ReconciliationPage from "./pages/ReconciliationPage";
import AnalyticsPage from "./pages/AnalyticsPage";
import NarrativePage from "./pages/NarrativePage";

function App() {
  return (
    <LogProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Layout />}>
            <Route index element={<ReconciliationPage />} />
            <Route path="analytics" element={<AnalyticsPage />} />
            <Route path="narrative" element={<NarrativePage />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </LogProvider>
  );
}

export default App;