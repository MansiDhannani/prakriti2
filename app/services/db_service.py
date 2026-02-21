"""
CRUD helpers — all DB reads/writes go through here.
Keeps routers thin and logic testable.
"""
from datetime import datetime
from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.database import ValuationRecord, ScenarioRecord, ReportRecord


# ── Valuation ─────────────────────────────────────────────────────────────────

def save_valuation(db: Session, result: dict, request_params: dict) -> ValuationRecord:
    record = ValuationRecord(
        ecosystem_type    = request_params.get("ecosystem_type"),
        ecosystem_name    = result.get("ecosystem_name"),
        area_hectares     = request_params.get("area_hectares"),
        region            = request_params.get("region"),
        location_name     = request_params.get("location_name"),
        carbon_pricing    = request_params.get("carbon_pricing", "voluntary_market"),
        discount_rate     = request_params.get("discount_rate", 0.08),
        projection_years  = request_params.get("projection_years", 10),
        value_type        = request_params.get("value_type", "midpoint"),

        annual_value_mid  = result.get("annual_value_mid"),
        annual_value_min  = result.get("annual_value_min"),
        annual_value_max  = result.get("annual_value_max"),
        npv               = result.get("npv"),
        carbon_annual_tonnes = result.get("carbon_annual_tonnes"),
        carbon_annual_value  = result.get("carbon_annual_value_inr"),
        climate_score     = result.get("climate_resilience_score"),
        biodiversity_index= result.get("biodiversity_index"),

        full_result       = result,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def get_valuation(db: Session, valuation_id: str) -> Optional[ValuationRecord]:
    return db.query(ValuationRecord).filter(ValuationRecord.id == valuation_id).first()


def list_valuations(
    db: Session,
    ecosystem_type: Optional[str] = None,
    region: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
) -> List[ValuationRecord]:
    q = db.query(ValuationRecord)
    if ecosystem_type:
        q = q.filter(ValuationRecord.ecosystem_type == ecosystem_type)
    if region:
        q = q.filter(ValuationRecord.region == region)
    return q.order_by(ValuationRecord.created_at.desc()).offset(offset).limit(limit).all()


def delete_valuation(db: Session, valuation_id: str) -> bool:
    record = get_valuation(db, valuation_id)
    if not record:
        return False
    db.delete(record)
    db.commit()
    return True


# ── Scenarios ─────────────────────────────────────────────────────────────────

def save_scenario(
    db: Session,
    valuation_id: str,
    result: dict,
    request_params: dict,
) -> ScenarioRecord:
    record = ScenarioRecord(
        valuation_id        = valuation_id,
        scenarios_requested = request_params.get("scenarios"),
        projection_years    = request_params.get("projection_years", 10),
        discount_rate       = request_params.get("discount_rate", 0.08),
        baseline_eco_npv    = result.get("baseline_eco_npv"),
        recommended         = result.get("recommended"),
        full_result         = result,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def get_scenarios_for_valuation(db: Session, valuation_id: str) -> List[ScenarioRecord]:
    return (
        db.query(ScenarioRecord)
        .filter(ScenarioRecord.valuation_id == valuation_id)
        .order_by(ScenarioRecord.created_at.desc())
        .all()
    )


# ── Reports ───────────────────────────────────────────────────────────────────

def save_report(
    db: Session,
    filename: str,
    size_bytes: int,
    valuation_id: Optional[str] = None,
    location_name: Optional[str] = None,
    prepared_for: Optional[str] = None,
    has_narrative: bool = False,
    has_scenarios: bool = False,
) -> ReportRecord:
    record = ReportRecord(
        valuation_id  = valuation_id,
        filename      = filename,
        size_bytes    = size_bytes,
        location_name = location_name,
        prepared_for  = prepared_for,
        has_narrative = has_narrative,
        has_scenarios = has_scenarios,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def list_reports(db: Session, limit: int = 20) -> List[ReportRecord]:
    return (
        db.query(ReportRecord)
        .order_by(ReportRecord.created_at.desc())
        .limit(limit)
        .all()
    )


# ── Analytics ─────────────────────────────────────────────────────────────────

def get_analytics(db: Session) -> dict:
    """Quick summary stats for a /analytics endpoint."""
    from sqlalchemy import func

    total_valuations = db.query(func.count(ValuationRecord.id)).scalar()
    total_area_ha    = db.query(func.sum(ValuationRecord.area_hectares)).scalar() or 0
    total_npv        = db.query(func.sum(ValuationRecord.npv)).scalar() or 0
    total_carbon     = db.query(func.sum(ValuationRecord.carbon_annual_tonnes)).scalar() or 0
    total_reports    = db.query(func.count(ReportRecord.id)).scalar()

    # Top ecosystems
    top_ecosystems = (
        db.query(ValuationRecord.ecosystem_name, func.count(ValuationRecord.id).label("count"))
        .group_by(ValuationRecord.ecosystem_name)
        .order_by(func.count(ValuationRecord.id).desc())
        .limit(5)
        .all()
    )

    # Top regions
    top_regions = (
        db.query(ValuationRecord.region, func.count(ValuationRecord.id).label("count"))
        .group_by(ValuationRecord.region)
        .order_by(func.count(ValuationRecord.id).desc())
        .limit(5)
        .all()
    )

    return {
        "total_valuations":      total_valuations,
        "total_area_valuated_ha": round(total_area_ha, 2),
        "total_npv_inr":         round(total_npv, 2),
        "total_carbon_tonnes_yr": round(total_carbon, 2),
        "total_reports_generated": total_reports,
        "top_ecosystems": [{"name": r[0], "count": r[1]} for r in top_ecosystems],
        "top_regions":    [{"region": r[0], "count": r[1]} for r in top_regions],
    }
