# EcoValue India — Backend API

FastAPI backend for the India Ecosystem Services Valuation Engine.

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set your GROQ API key (only needed for AI narrative feature)
cp .env.example .env
# Edit .env and add your GROQ_API_KEY (get free key at https://console.groq.com)

# 3. Run the server
python run.py
# → http://localhost:8000
# → Swagger docs: http://localhost:8000/docs
```

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET  | `/`                          | API overview |
| GET  | `/health`                    | Health + Claude AI status |
| GET  | `/api/v1/ecosystems`         | List all ecosystems |
| GET  | `/api/v1/ecosystems/{type}`  | Detail for one ecosystem |
| POST | `/api/v1/valuate`            | **Core valuation** |
| GET  | `/api/v1/scenarios`          | List land use scenarios |
| POST | `/api/v1/scenarios/compare`  | **Compare scenarios** |
| GET  | `/api/v1/carbon-prices`      | Carbon pricing methods |
| POST | `/api/v1/report/narrative`   | AI policy narrative (Groq AI) |
| POST | `/api/v1/report/pdf`         | Generate PDF report (base64) |
| POST | `/api/v1/report/pdf/download`| PDF direct download |

---

## Example Request — Valuate

```bash
curl -X POST http://localhost:8000/api/v1/valuate \
  -H "Content-Type: application/json" \
  -d '{
    "ecosystem_type": "wetlands_inland",
    "area_hectares": 250,
    "region": "indo_gangetic_plain",
    "carbon_pricing": "voluntary_market",
    "discount_rate": 0.08,
    "projection_years": 10,
    "value_type": "midpoint",
    "location_name": "Harike Wetland, Punjab"
  }'
```

## Example Request — Compare Scenarios

```bash
curl -X POST http://localhost:8000/api/v1/scenarios/compare \
  -H "Content-Type: application/json" \
  -d '{
    "ecosystem_type": "wetlands_inland",
    "area_hectares": 250,
    "region": "indo_gangetic_plain",
    "scenarios": ["preserve", "restore", "solar", "development"],
    "projection_years": 10
  }'
```

## Example Request — PDF Report

```bash
curl -X POST http://localhost:8000/api/v1/report/pdf/download \
  -H "Content-Type: application/json" \
  -d '{
    "valuation_result": { ...paste valuate response here... },
    "scenario_results": [ ...paste scenario compare response scenarios array... ],
    "location_name": "Harike Wetland",
    "prepared_for": "Punjab State Forest Department"
  }' \
  --output report.pdf
```

---

## Project Structure

```
ecovalue_backend/
├── run.py                          # Entry point
├── requirements.txt
├── .env.example
└── app/
    ├── main.py                     # FastAPI app + CORS
    ├── data/
    │   └── coefficients.py         # India ecosystem database (TEEB, FSI, TERI)
    ├── models/
    │   └── schemas.py              # Pydantic request/response models
    ├── services/
    │   ├── valuation_engine.py     # Core NPV + services calculation
    │   ├── narrative_service.py    # Claude AI policy narrative
    │   └── pdf_service.py          # ReportLab PDF generation
    └── routers/
        ├── health.py
        ├── valuation.py
        ├── scenarios.py
        └── report.py
```

---

## Data Sources

All coefficients in INR/hectare/year from:
- **Sukhdev et al. (2008)** — TEEB India Study
- **FSI ISFR 2023** — Forest Survey of India
- **TERI** Ecosystem Services Publications
- **MoEFCC** NATCOM to UNFCCC
- **IIFM Verma (2000)** — HP Forest Valuation
- **Hussain & Badola (2010)** — Wetland Services
- **CPCB** Water Quality Reports
- **ATREE** Western Ghats Studies
- **CPR India** Urban Ecosystem Services

---

## Deploy to Railway

```bash
# railway.toml already configured
railway up
```

Or Render: set Start Command to `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
