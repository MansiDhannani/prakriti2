from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.models.database import get_db
from app.services.db_service import (
    list_valuations, get_analytics, list_reports,
    get_scenarios_for_valuation, get_valuation
)

router = APIRouter()


@router.get("/history")
def valuation_history(
    ecosystem_type: Optional[str] = Query(None, description="Filter by ecosystem type"),
    region:         Optional[str] = Query(None, description="Filter by region"),
    limit:          int           = Query(20,  ge=1, le=100),
    offset:         int           = Query(0,   ge=0),
    db: Session = Depends(get_db),
):
    """
    List all past valuations with filters.
    Use this to power a history/dashboard page on the frontend.
    """
    records = list_valuations(db, ecosystem_type, region, limit, offset)
    return {
        "total":  len(records),
        "offset": offset,
        "limit":  limit,
        "results": [
            {
                "id":              r.id,
                "created_at":      r.created_at.isoformat(),
                "ecosystem_name":  r.ecosystem_name,
                "ecosystem_type":  r.ecosystem_type,
                "area_hectares":   r.area_hectares,
                "region":          r.region,
                "location_name":   r.location_name,
                "annual_value_mid": r.annual_value_mid,
                "npv":             r.npv,
                "carbon_annual_tonnes": r.carbon_annual_tonnes,
                "climate_score":   r.climate_score,
                "biodiversity_index": r.biodiversity_index,
            }
            for r in records
        ]
    }


@router.get("/history/{valuation_id}")
def valuation_detail(valuation_id: str, db: Session = Depends(get_db)):
    """Get full result for a past valuation, including linked scenario comparisons."""
    record = get_valuation(db, valuation_id)
    if not record:
        raise HTTPException(status_code=404, detail="Valuation not found")

    scenarios = get_scenarios_for_valuation(db, valuation_id)
    return {
        "valuation":  record.full_result,
        "scenarios":  [s.full_result for s in scenarios],
        "created_at": record.created_at.isoformat(),
    }


@router.get("/analytics")
def analytics(db: Session = Depends(get_db)):
    """
    Aggregated stats across all stored valuations.
    Great for a public impact dashboard.
    """
    return get_analytics(db)


@router.get("/reports/history")
def reports_history(limit: int = Query(20, ge=1, le=100), db: Session = Depends(get_db)):
    """List recently generated PDF reports."""
    records = list_reports(db, limit)
    return {
        "total": len(records),
        "results": [
            {
                "id":           r.id,
                "created_at":   r.created_at.isoformat(),
                "filename":     r.filename,
                "size_bytes":   r.size_bytes,
                "location_name": r.location_name,
                "prepared_for": r.prepared_for,
                "has_narrative": r.has_narrative,
                "has_scenarios": r.has_scenarios,
            }
            for r in records
        ]
    }
