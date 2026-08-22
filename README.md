# SwasthiQ EOD Billing & Analytics Agent

A full-stack app that ingests a clinic's daily billing log and produces:
1. A deterministic end-of-day reconciliation report
2. Basic analytics (revenue by hour, top medicines by quantity/revenue)
3. An LLM-generated, grounded narrative summary of the above

**Live app:** https://full-stack-app-d24v.vercel.app/
**Live API:** https://full-stack-app-talg.onrender.com (Swagger docs at `/docs`)

> Note: the backend is hosted on Render's free tier, which sleeps after 15
> minutes of inactivity. The first request after a period of inactivity may
> take 30-50 seconds to respond while the server wakes up.

---

## Tech Stack

- **Backend:** Python, FastAPI, Pydantic (validation), pytest
- **Frontend:** React (Vite), React Router, Recharts
- **LLM:** Groq API (`openai/gpt-oss-120b`), OpenAI-compatible endpoint
- **Storage:** In-memory (per assignment constraints — no managed DB required)
- **Deployment:** Backend on Render, frontend on Vercel

---

## Project Structure

```
/backend
  /app
    main.py           - FastAPI app + route definitions
    models.py          - Pydantic schema + validation rules
    reconciliation.py  - Deterministic reconciliation engine (no LLM)
    analytics.py        - Deterministic analytics engine (no LLM)
    narrative.py         - LLM narrative layer + grounding verification
    storage.py            - In-memory log storage
  /tests                  - pytest suite (12 tests)
  /data                    - Sample clinic-day JSON files used in tests
  requirements.txt
/frontend
  /src
    /components          - Reusable UI: Layout, StatCard, RevenueChart, RankingList
    /pages                 - ReconciliationPage, AnalyticsPage, NarrativePage
    /context               - LogContext (shares uploaded log_id across pages)
    api.js                  - API client wrapping all backend calls
README.md
```

---

## API Contracts

### `POST /billing-log/upload`
Ingests and validates a full day's billing log for one clinic.

**Request body:**
```json
{
  "records": [
    {
      "clinic_id": "CLN-KNP-014",
      "visit_id": "V-20260727-001",
      "timestamp": "2026-07-27T09:10:00Z",
      "doctor_id": "DOC-014-01",
      "line_items": [{"drug_name": "PARACETAMOL", "qty": 3, "unit_price_paise": 2000}],
      "payment_mode": "cash",
      "amount_paid_paise": 6000,
      "discount_paise": 0,
      "is_refund": false
    }
  ]
}
```

**Success (201):**
```json
{ "log_id": "uuid-string", "visit_count": 1, "clinic_id": "CLN-KNP-014" }
```

**Validation failure (422):** returns a specific field-level error (Pydantic),
e.g. a row missing `payment_mode` or a refund with a non-negative amount —
never a generic 500.

### `GET /reconciliation?log_id=<id>`
Returns total billed, collected, outstanding, and refunds — overall and
split by payment mode. Pure function of the stored log; never calls an LLM.

### `GET /analytics?log_id=<id>`
Returns revenue by hour-of-day (0-23, zero-filled), the peak hour, and two
independent rankings: top medicines by quantity and by revenue.

### `GET /narrative?log_id=<id>`
Returns an LLM-generated WhatsApp-style summary of the combined
reconciliation + analytics report, plus a `traced_figures` array mapping
every number in the narrative to its source field in the report.

```json
{
  "narrative": "Good day! Today there were 19 visits...",
  "traced_figures": [
    {"display_value": "₹3,230", "source_field": "total_billed_paise"}
  ],
  "grounded": true,
  "source": "llm"
}
```

If the LLM is unavailable, its response is malformed, or any number in its
narrative fails grounding verification, the endpoint transparently falls
back to a deterministic template (`"source": "fallback_template"`) instead
of crashing or returning an empty/incorrect result.

### `GET /billing-logs`
Lists all uploaded logs (id, clinic, date, visit count) — used to populate
a log picker in the frontend.

---

## Design Decisions & Data Consistency

**Deterministic layer is the single source of truth.** `reconciliation.py`
and `analytics.py` never call an LLM and never take LLM output as input —
they are pure functions of the validated billing log. The narrative layer
consumes their output but cannot influence it. This ordering (deterministic
first, narrative second, always) is what guarantees consistency: the same
log always produces the same reconciliation and analytics numbers, and the
narrative can only be checked against those numbers, never the reverse.

**Validation happens once, at the boundary.** All billing log data is
validated by Pydantic models (`models.py`) at the moment it's uploaded. A
row missing a required field, an amount/refund-sign mismatch, or a mixed
multi-clinic file is rejected in full, with a specific error identifying
the offending row and field. Nothing downstream (reconciliation, analytics,
narrative) has to re-validate or guess about malformed input, since only
valid `BillingLog` objects ever reach those layers.

**Money is stored as integer paise throughout** — never floats — to avoid
floating-point rounding errors compounding across hundreds of transactions.
Conversion to rupees for display only happens at the presentation edge (API
response formatting and the React frontend).

**LLM grounding is enforced programmatically, not just by prompting.** The
narrative layer asks the LLM to return structured JSON with a
`traced_figures` list. Separately, the code independently extracts every
numeric token from the generated narrative text via regex and checks it
against every numeric value actually present in the deterministic report
(including both paise and rupee-converted forms). If any number in the
narrative doesn't match something in the report, the LLM's output is
discarded entirely and a safe, deterministic fallback template is returned
instead. The response always includes a `"grounded"` and `"source"` field
so it's clear which path produced the result.

**Malformed/unavailable LLM responses degrade gracefully.** Missing API
key, network failure, non-JSON response, missing expected fields, or a
failed grounding check — all of these are caught and routed to the same
fallback path. The `/narrative` endpoint never returns a 500 or a blank
result due to an LLM issue.

---

## Known Data-Quality Notes (Sample Dataset)

- One sample day (`sample_day3.json`) contains a drug name typo,
  `"PARACETMOL"` vs `"PARACETAMOL"`. This is treated as a distinct drug
  name rather than auto-corrected — silently merging it could mask a real
  data-entry error a clinic owner would want to know about.
- Refund visits are excluded from analytics (revenue-by-hour and medicine
  rankings), since they represent money returned, not medicines sold that
  day.

---

## Running Locally

### Backend
```bash
cd backend
python3 -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\Activate.ps1
pip install -r requirements.txt
# Create backend/.env with: GROQ_API_KEY=your-key-here
uvicorn app.main:app --reload
```
Visit `http://127.0.0.1:8000/docs` for interactive API testing.

### Frontend
```bash
cd frontend
npm install
# Create frontend/.env with: VITE_API_BASE_URL=http://127.0.0.1:8000
npm run dev
```
Visit `http://localhost:5173`.

### Tests
```bash
cd backend
pytest tests/ -v
```
12 tests covering: happy-path reconciliation/analytics, an all-refunds edge
case, an empty (zero-visit) day, a malformed-row rejection, API-level
upload/fetch flows, and both the LLM and fallback paths of the narrative
layer (using `monkeypatch` to deterministically test the fallback
regardless of whether a real API key is configured in the environment).

---

## Deployment

- **Backend:** Render (free tier), `GROQ_API_KEY` set as an environment
  variable in the Render dashboard.
- **Frontend:** Vercel, `VITE_API_BASE_URL` set as an environment variable
  pointing to the live Render backend URL.
- CORS on the backend is restricted to the deployed Vercel origin plus
  local dev origins.