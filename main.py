from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, Response
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import json
import pandas as pd
from dotenv import load_dotenv
import os

# Import Version 2.0.0 Services
from app.services import valuation_engine, narrative_service, pdf_service, db_service, rag_service
from app.models.schemas import ValuationRequest, ScenarioCompareRequest
from app.models.database import SessionLocal, engine, Base
from live import router as live_router

# Initialize Database
Base.metadata.create_all(bind=engine)

load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Pre-load RAG index on startup
    try:
        from app.services.rag_service import get_store
        store = get_store()
        print(f"✅ RAG index ready: {store.count()} documents")
    except Exception as e:
        print(f"⚠ RAG index failed to load: {e}")
    yield

app = FastAPI(
    title="EcoValue India",
    description="Ecosystem Services Valuation Engine for India.",
    version="2.0.0",
    docs_url="/docs",
    lifespan=lifespan
)

# Enable CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency for DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Mount static files (your CSS, JS files)
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

# Load data
DATA_PATH = "india_ecosystem_coefficients.json"
CSV_PATH = "PrakritiROI_Synthetic_Dataset_2000 (1).csv"

# Load synthetic dataset for parcel lookups
if os.path.exists(CSV_PATH):
    df_parcels = pd.read_csv(CSV_PATH)
else:
    df_parcels = pd.DataFrame()

@app.get("/")
async def root():
    return {"message": "Welcome to EcoValue India API v2.0.0"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "version": "2.0.0"}

# --- API V1 Endpoints ---

@app.get("/api/v1/ecosystems")
def get_ecosystems():
    from app.data.coefficients import ECOSYSTEMS
    return ECOSYSTEMS

@app.post("/api/v1/valuate")
def valuate(request: ValuationRequest, db: Session = Depends(get_db)):
    result = valuation_engine.compute_valuation(request)
    db_service.save_valuation(db, result.dict(), request.dict())
    return result

@app.post("/api/v1/scenarios/compare")
def compare_scenarios(request: ScenarioCompareRequest):
    return valuation_engine.compute_scenario_comparison(request)

@app.post("/api/v1/report/narrative")
def generate_narrative(request: dict):
    # Expects {"valuation_result": {...}, "location_name": "..."}
    return narrative_service.generate_narrative(
        valuation_result=request.get("valuation_result"),
        location_name=request.get("location_name")
    )

@app.post("/api/v1/report/pdf")
def generate_pdf_report(request: dict):
    pdf_bytes, filename = pdf_service.generate_pdf(
        valuation_result=request.get("valuation_result"),
        narrative=request.get("narrative"),
        location_name=request.get("location_name")
    )
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@app.get("/api/v1/history")
def get_history(db: Session = Depends(get_db)):
    return {"valuations": db_service.list_valuations(db)}

@app.get("/api/v1/analytics")
def get_analytics(db: Session = Depends(get_db)):
    return db_service.get_analytics(db)

@app.post("/api/v1/impact")
def get_impact(valuation_result: dict):
    from app.services.impact_service import calculate_impact
    return calculate_impact(
        ecosystem_type=valuation_result.get("ecosystem_type"),
        area_hectares=valuation_result.get("area_hectares"),
        annual_value_inr=valuation_result.get("annual_value_mid"),
        carbon_tonnes_yr=valuation_result.get("carbon_annual_tonnes"),
        biodiversity_index=valuation_result.get("biodiversity_index"),
        climate_score=valuation_result.get("climate_resilience_score"),
        services=valuation_result.get("services")
    )

@app.get("/api/v1/rag/search")
def rag_search(q: str = Query(..., description="Search query for ecosystem data")):
    return {"context": rag_service.retrieve_context(q)}

@app.post("/api/v1/rag/rebuild")
def rag_rebuild():
    store = rag_service.get_store()
    count = rag_service.build_index(store)
    return {"status": "success", "documents_indexed": count}

# Include WebSocket Ticker
app.include_router(live_router, prefix="/api/v1")

@app.get("/api/v1/parcels")
def list_parcels():
    return df_parcels[["Parcel_ID", "State", "Land_Use_Type"]].to_dict(orient="records")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)