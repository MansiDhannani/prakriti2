"""
WebSocket Live Ticker — Broadcast valuations to all connected clients in real-time.
Multiple judges/analysts watching the same screen = instant visibility.
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import asyncio
import json
from datetime import datetime
from typing import List, Set

router = APIRouter()

# Global connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()
        self.valuation_history: List[dict] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.add(websocket)
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.discard(websocket)
    
    async def broadcast_valuation(self, valuation: dict):
        """Broadcast a new valuation to all connected clients."""
        message = {
            "type": "valuation",
            "data": {
                "location": valuation.get("location_name", "Unknown"),
                "ecosystem": valuation.get("ecosystem_name", ""),
                "area_ha": valuation.get("area_hectares", 0),
                "annual_value": valuation.get("annual_value_mid", 0),
                "npv": valuation.get("npv", 0),
                "carbon_tonnes": valuation.get("carbon_annual_tonnes", 0),
                "timestamp": datetime.utcnow().isoformat(),
            }
        }
        
        # Store in history
        self.valuation_history.append(message["data"])
        if len(self.valuation_history) > 100:  # Keep last 100
            self.valuation_history.pop(0)
        
        # Send to all connected clients
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                pass  # Client disconnected
    
    async def send_session_stats(self, websocket: WebSocket):
        """Send running session statistics."""
        total_area = sum(v.get("area_ha", 0) for v in self.valuation_history)
        total_value = sum(v.get("annual_value", 0) for v in self.valuation_history)
        total_carbon = sum(v.get("carbon_tonnes", 0) for v in self.valuation_history)
        
        stats = {
            "type": "stats",
            "data": {
                "valuations_count": len(self.valuation_history),
                "total_hectares": total_area,
                "total_annual_value": total_value,
                "total_carbon_tonnes": total_carbon,
            }
        }
        await websocket.send_json(stats)


manager = ConnectionManager()


@router.websocket("/ws/ticker")
async def websocket_ticker(websocket: WebSocket):
    """
    WebSocket endpoint for live valuation ticker.
    
    Usage:
    ```javascript
    const ws = new WebSocket('ws://localhost:8000/api/v1/ws/ticker');
    ws.onmessage = (e) => {
        const msg = JSON.parse(e.data);
        if (msg.type === 'valuation') {
            console.log('New valuation:', msg.data);
        }
    };
    ```
    """
    await manager.connect(websocket)
    
    try:
        # Send initial stats
        await manager.send_session_stats(websocket)
        
        # Send history
        for item in manager.valuation_history:
            await websocket.send_json({
                "type": "valuation",
                "data": item
            })
        
        # Keep connection alive
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)


def broadcast_valuation_to_clients(valuation: dict):
    """Call this from valuation endpoint to notify all connected clients."""
    import asyncio
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            asyncio.create_task(manager.broadcast_valuation(valuation))
        else:
            loop.run_until_complete(manager.broadcast_valuation(valuation))
    except:
        pass  # WebSocket not available (e.g., in testing)
