from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import json
import pandas as pd
from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI(title="PrakritiROI API")
api_key = os.getenv("GROQ_API_KEY")
client = Groq(api_key=api_key) if api_key else None

# Mount static files (your CSS, JS files)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Load data
DATA_PATH = "india_ecosystem_coefficients.json"
CSV_PATH = "PrakritiROI_Synthetic_Dataset_2000 (1).csv"

with open(DATA_PATH, "r") as f:
    ecosystem_data = json.load(f)

# Load synthetic dataset for parcel lookups
df_parcels = pd.read_csv(CSV_PATH)

class ROIRequest(BaseModel):
    ecosystem_type: str
    area_ha: float
    region: str

class AISummaryRequest(BaseModel):
    ecosystem: str
    region: str
    area_ha: float
    npv_10yr: float

@app.get("/")
async def serve_frontend():
    return FileResponse("index.html")

@app.get("/ecosystems")
def get_ecosystems():
    return ecosystem_data["ecosystems"]

@app.get("/regions")
def get_regions():
    return ecosystem_data["regional_multipliers"]

@app.get("/parcels")
def list_parcels():
    return df_parcels[["Parcel_ID", "State", "Land_Use_Type"]].to_dict(orient="records")

@app.get("/parcel/{parcel_id}")
def get_parcel(parcel_id: int):
    result = df_parcels[df_parcels["Parcel_ID"] == parcel_id]
    if result.empty:
        raise HTTPException(status_code=404, detail="Parcel not found")
    return result.iloc[0].to_dict()

@app.post("/calculate_roi")
def calculate_roi(request: ROIRequest):
    eco = ecosystem_data["ecosystems"].get(request.ecosystem_type)
    multiplier = ecosystem_data["regional_multipliers"].get(request.region)
    
    if not eco or not multiplier:
        raise HTTPException(status_code=404, detail="Ecosystem or Region not found")

    results = []
    total_annual_value = 0
    
    for service_name, service_data in eco["services"].items():
        # Handle different key names for midpoint
        mid_val = service_data.get("value_midpoint", service_data.get("mid", 0))
        adjusted_val = mid_val * multiplier
        total_service_val = adjusted_val * request.area_ha
        
        results.append({
            "service": service_name.replace("_", " ").title(),
            "value_per_ha": adjusted_val,
            "total_value": total_service_val
        })
        total_annual_value += total_service_val

    # 10-Year NPV Calculation (8% discount rate as per JSON notes)
    pv_factor = 6.71 
    npv_10yr = total_annual_value * pv_factor

    return {
        "ecosystem": eco["name"],
        "region": request.region.replace("_", " ").title(),
        "area_ha": request.area_ha,
        "total_annual_value": total_annual_value,
        "npv_10yr": npv_10yr,
        "breakdown": results
    }

@app.post("/ai_summary")
def get_ai_summary(request: AISummaryRequest):
    """Generates an ecological investment thesis using Claude."""
    if not client:
        return {"summary": "AI Insights unavailable: Please configure a valid GROQ_API_KEY."}

    prompt = f"As an ESG analyst, provide a 3-sentence investment thesis for a {request.ecosystem} project in {request.region} covering {request.area_ha} hectares with an NPV of ₹{request.npv_10yr:,.0f}."
    
    try:
        completion = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=150,
            temperature=0.7
        )
        return {"summary": completion.choices[0].message.content}
    except Exception as e:
        print(f"❌ Groq API Error: {e}")
        return {"summary": "AI Insights currently unavailable. Please check your API key."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)