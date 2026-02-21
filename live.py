import asyncio
from typing import List
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException
from app.services.impact_service import calculate_impact

router = APIRouter()

class TickerManager:
    def __init__(self):
        self.connections: List[WebSocket] = []

    async def connect(self, ws: WebSocket):
        await ws.accept()
        self.connections.append(ws)
        await ws.send_json({"type":"connected","viewers":len(self.connections)})

    def disconnect(self, ws: WebSocket):
        if ws in self.connections:
            self.connections.remove(ws)

    async def broadcast(self, data: dict):
        dead = []
        for ws in self.connections:
            try: await ws.send_json(data)
            except: dead.append(ws)
        for ws in dead: self.disconnect(ws)

ticker = TickerManager()

@router.post("/impact")
def get_impact(valuation_result: dict):
    try:
        return calculate_impact(
            ecosystem_type     = valuation_result.get("ecosystem_type",""),
            area_hectares      = valuation_result.get("area_hectares",0),
            annual_value_inr   = valuation_result.get("annual_value_mid",0),
            carbon_tonnes_yr   = valuation_result.get("carbon_annual_tonnes",0),
            biodiversity_index = valuation_result.get("biodiversity_index",0),
            climate_score      = valuation_result.get("climate_resilience_score",0),
            services           = valuation_result.get("services",[]),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.websocket("/ws/ticker")
async def websocket_ticker(ws: WebSocket):
    await ticker.connect(ws)
    try:
        while True:
            data = await ws.receive_text()
            if data == "ping": await ws.send_json({"type":"pong"})
    except WebSocketDisconnect:
        ticker.disconnect(ws)

async def broadcast_valuation(valuation_result: dict):
    def fmt(n):
        if n>=1e7: return f"₹{n/1e7:.1f} Cr"
        if n>=1e5: return f"₹{n/1e5:.1f} L"
        return f"₹{n:,.0f}"
    await ticker.broadcast({
        "type":          "valuation",
        "ecosystem":     valuation_result.get("ecosystem_name",""),
        "ecosystem_type":valuation_result.get("ecosystem_type",""),
        "location":      valuation_result.get("location_name") or valuation_result.get("region","").replace("_"," ").title(),
        "area_ha":       valuation_result.get("area_hectares",0),
        "annual_value":  fmt(valuation_result.get("annual_value_mid",0)),
        "npv_10yr":      fmt(valuation_result.get("npv",0)),
        "carbon_tonnes": valuation_result.get("carbon_annual_tonnes",0),
        "viewers":       len(ticker.connections),
        "timestamp":     __import__("datetime").datetime.utcnow().isoformat(),
    })