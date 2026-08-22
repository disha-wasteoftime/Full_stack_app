import { createContext, useContext, useEffect, useState } from "react";
import { uploadBillingLog } from "../api";
import sampleDay3 from "../data/sample_day3.json";

const LogContext = createContext(null);

export function LogProvider({ children }) {
  const [logId, setLogId] = useState(null);
  const [clinicId, setClinicId] = useState(null);
  const [status, setStatus] = useState("uploading"); // uploading | ready | error
  const [error, setError] = useState(null);

  useEffect(() => {
    uploadBillingLog(sampleDay3)
      .then((res) => {
        setLogId(res.log_id);
        setClinicId(res.clinic_id);
        setStatus("ready");
      })
      .catch((err) => {
        setError(err.response?.data?.detail || err.message);
        setStatus("error");
      });
  }, []);

  return (
    <LogContext.Provider value={{ logId, clinicId, status, error }}>
      {children}
    </LogContext.Provider>
  );
}

export function useLog() {
  return useContext(LogContext);
}