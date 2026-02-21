import asyncio
from typing import List
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException
from app.services.impact_service import calculate_impact
from datetime import datetime

router = APIRouter()

class TickerManager:
    def __init__(self):
        self.connections: List[WebSocket] = []
        self.history: List[dict] = []
        self.totals = {
            "count": 0,
            "area": 0,
            "value": 0,
            "carbon": 0
        }

    async def connect(self, ws: WebSocket):
        await ws.accept()
        self.connections.append(ws)
        # Send current global stats first
        await ws.send_json({
            "type": "stats",
            "data": self.totals
        })
        # Send history to new client so they see recent valuations immediately
        for item in self.history:
            await ws.send_json(item)
        await ws.send_json({"type":"connected","viewers":len(self.connections)})

    def disconnect(self, ws: WebSocket):
        if ws in self.connections:
            self.connections.remove(ws)

    async def broadcast(self, data: dict):
        # Update global aggregates
        if data.get("type") == "valuation":
            v = data["data"]
            self.totals["count"] += 1
            self.totals["area"]  += v.get("area_hectares", 0)
            self.totals["value"] += v.get("annual_value_mid", 0)
            self.totals["carbon"] += v.get("carbon_annual_tonnes", 0)

        # Store in history (keep last 100)
        self.history.append(data)
        if len(self.history) > 100: self.history.pop(0)
        
        dead = []
        for ws in self.connections:
            try: 
                await ws.send_json(data)
                if data.get("type") == "valuation":
                    await ws.send_json({"type": "stats", "data": self.totals})
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
    await ticker.broadcast({
        "type":          "valuation",
        "data": {
            "ecosystem_name": valuation_result.get("ecosystem_name") or valuation_result.get("ecosystem", "Unknown"),
            "location_name":  valuation_result.get("location_name") or valuation_result.get("region", "").replace("_"," ").title(),
            "area_hectares":  valuation_result.get("area_hectares") or valuation_result.get("area_ha", 0),
            "annual_value_mid": valuation_result.get("annual_value_mid") or valuation_result.get("total_annual_value", 0),
            "carbon_annual_tonnes": valuation_result.get("carbon_annual_tonnes", 0),
            "region":         valuation_result.get("region", ""),
            "timestamp":      datetime.utcnow().isoformat()
        }
    })
