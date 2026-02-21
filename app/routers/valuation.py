from fastapi import APIRouter, HTTPException, Depends, Query, BackgroundTasks
from sqlalchemy.orm import Session
from app.models.schemas import ValuationRequest, ValuationResponse
from app.models.database import get_db
from app.services.valuation_engine import compute_valuation
from app.services.db_service import save_valuation, get_valuation, list_valuations, delete_valuation
from app.data.coefficients import ECOSYSTEMS, REGIONAL_MULTIPLIERS
from app.routers.live import broadcast_valuation

router = APIRouter()


@router.get("/ecosystems")
def list_ecosystems():
    """List all supported ecosystem types with metadata."""
    return {
        "ecosystems": [
            {
                "key":              key,
                "name":             eco["name"],
                "regions":          eco["regions"],
                "climate_score":    eco["climate_resilience_score"],
                "biodiversity_idx": eco["biodiversity_index"],
                "service_count":    len(eco["services"]),
                "services":         list(eco["services"].keys()),
            }
            for key, eco in ECOSYSTEMS.items()
        ],
        "regions": list(REGIONAL_MULTIPLIERS.keys()),
        "total_ecosystems": len(ECOSYSTEMS),
    }


@router.get("/ecosystems/{ecosystem_type}")
def get_ecosystem_detail(ecosystem_type: str):
    """Get full coefficient detail for one ecosystem type."""
    if ecosystem_type not in ECOSYSTEMS:
        raise HTTPException(status_code=404, detail=f"Ecosystem '{ecosystem_type}' not found")
    eco = ECOSYSTEMS[ecosystem_type]
    return {
        "key":     ecosystem_type,
        "details": eco,
        "regions_and_multipliers": REGIONAL_MULTIPLIERS,
    }


@router.post("/valuate", response_model=ValuationResponse)
def valuate(req: ValuationRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """
    Core valuation endpoint.
    Computes annual ecosystem service value + 10-yr NPV.
    Result is automatically saved to the database.
    """
    try:
        result = compute_valuation(req)
        result_dict = result.model_dump()

        # Broadcast to the live ticker automatically
        background_tasks.add_task(broadcast_valuation, result_dict)

        # Save to DB (non-blocking — if it fails, still return result)
        try:
            record = save_valuation(db, result_dict, req.model_dump())
            result_dict["record_id"] = record.id
        except Exception as db_err:
            print(f"⚠ DB save failed (non-critical): {db_err}")
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/valuations/{valuation_id}")
def fetch_valuation(valuation_id: str, db: Session = Depends(get_db)):
    """Retrieve a previously saved valuation by ID."""
    record = get_valuation(db, valuation_id)
    if not record:
        raise HTTPException(status_code=404, detail="Valuation not found")
    return record.full_result


@router.delete("/valuations/{valuation_id}")
def remove_valuation(valuation_id: str, db: Session = Depends(get_db)):
    """Delete a valuation record."""
    deleted = delete_valuation(db, valuation_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Valuation not found")
    return {"deleted": True, "id": valuation_id}


@router.get("/carbon-prices")
def carbon_prices():
    """Return available carbon pricing methods and current INR values."""
    from app.data.coefficients import CARBON_PRICES
    return {
        "prices": CARBON_PRICES,
        "recommended": "voluntary_market",
        "note": "social_cost recommended for policy analysis; voluntary_market for project finance"
    }
