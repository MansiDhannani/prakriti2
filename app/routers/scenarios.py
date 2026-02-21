from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.models.schemas import ScenarioCompareRequest, ScenarioCompareResponse
from app.models.database import get_db
from app.services.valuation_engine import compute_scenario_comparison
from app.services.db_service import save_scenario
from app.data.coefficients import LAND_USE_ALTERNATIVES

router = APIRouter()


@router.get("/scenarios")
def list_scenarios():
    """List all land use alternative scenarios."""
    return {
        "scenarios": [
            {
                "key":                  key,
                "name":                 alt["name"],
                "description":          alt["description"],
                "revenue_ha_yr":        alt["revenue_ha_yr"],
                "eco_services_retained_pct": alt["eco_services_retained"] * 100,
            }
            for key, alt in LAND_USE_ALTERNATIVES.items()
        ]
    }


@router.post("/scenarios/compare", response_model=ScenarioCompareResponse)
def compare_scenarios(
    req: ScenarioCompareRequest,
    valuation_id: str = None,
    db: Session = Depends(get_db),
):
    """
    Compare multiple land use scenarios for a given parcel.
    Pass valuation_id (from /valuate response) to link the records in the DB.
    """
    try:
        result = compute_scenario_comparison(req)
        result_dict = result.model_dump()
        try:
            save_scenario(db, valuation_id or "standalone", result_dict, req.model_dump())
        except Exception as db_err:
            print(f"⚠ DB save failed (non-critical): {db_err}")
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
