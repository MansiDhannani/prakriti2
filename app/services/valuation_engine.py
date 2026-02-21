"""
Core Ecosystem Services Valuation Engine
"""
import math
from typing import List
from app.data.coefficients import (
    ECOSYSTEMS, REGIONAL_MULTIPLIERS, CARBON_PRICES,
    LAND_USE_ALTERNATIVES, SOURCES
)
from app.models.schemas import (
    ValuationRequest, ValuationResponse, ServiceDetail,
    ScenarioCompareRequest, ScenarioCompareResponse, ScenarioResult
)


def _pv_annuity_factor(rate: float, years: int) -> float:
    """Present Value annuity factor: (1 - (1+r)^-n) / r"""
    if rate == 0:
        return float(years)
    return (1 - math.pow(1 + rate, -years)) / rate


def compute_valuation(req: ValuationRequest) -> ValuationResponse:
    eco  = ECOSYSTEMS[req.ecosystem_type]
    mult = REGIONAL_MULTIPLIERS[req.region]
    carbon_price = CARBON_PRICES[req.carbon_pricing]
    pv_factor = _pv_annuity_factor(req.discount_rate, req.projection_years)

    # ── Per-service calculation ──────────────────────────────────────────────
    services: List[ServiceDetail] = []
    total_min = total_mid = total_max = 0.0

    for svc_key, svc in eco["services"].items():
        raw_min = svc.get("min", 0)
        raw_mid = svc.get("mid", 0)
        raw_max = svc.get("max", 0)

        adj_min = raw_min * mult
        adj_mid = raw_mid * mult
        adj_max = raw_max * mult

        total_min += adj_min
        total_mid += adj_mid
        total_max += adj_max

        services.append(ServiceDetail(
            service_name    = svc_key.replace("_", " ").title(),
            value_min       = raw_min,
            value_mid       = raw_mid,
            value_max       = raw_max,
            adjusted_value  = adj_mid,
            total_for_area  = adj_mid * req.area_hectares,
            contribution_pct= 0.0,   # filled below
            method          = svc.get("method", ""),
            source          = svc.get("source", ""),
        ))

    # Fill contribution percentages
    for s in services:
        s.contribution_pct = round(
            (s.adjusted_value / total_mid * 100) if total_mid else 0, 2
        )

    # ── Aggregate values ────────────────────────────────────────────────────
    value_map = {"min": total_min, "midpoint": total_mid, "max": total_max}
    annual_used = value_map[req.value_type]
    annual_total_used = annual_used * req.area_hectares
    npv = annual_total_used * pv_factor

    # ── Carbon ──────────────────────────────────────────────────────────────
    carbon_rate   = eco["carbon_rate_tonnes_ha_yr"]
    carbon_annual = carbon_rate * req.area_hectares
    carbon_value  = carbon_annual * carbon_price

    return ValuationResponse(
        ecosystem_type       = req.ecosystem_type,
        ecosystem_name       = eco["name"],
        area_hectares        = req.area_hectares,
        region               = req.region,
        regional_multiplier  = mult,

        annual_value_min     = total_min * req.area_hectares,
        annual_value_mid     = total_mid * req.area_hectares,
        annual_value_max     = total_max * req.area_hectares,
        annual_value_used    = annual_total_used,

        npv                  = round(npv, 2),
        discount_rate        = req.discount_rate,
        projection_years     = req.projection_years,

        carbon_rate_tonnes_ha_yr = carbon_rate,
        carbon_annual_tonnes     = round(carbon_annual, 2),
        carbon_price_inr_tonne   = carbon_price,
        carbon_annual_value_inr  = round(carbon_value, 2),

        climate_resilience_score = eco["climate_resilience_score"],
        biodiversity_index       = eco["biodiversity_index"],

        services         = services,
        value_type_used  = req.value_type,
        sources          = SOURCES,
    )


def compute_scenario_comparison(req: ScenarioCompareRequest) -> ScenarioCompareResponse:
    eco  = ECOSYSTEMS[req.ecosystem_type]
    mult = REGIONAL_MULTIPLIERS[req.region]
    pv_factor = _pv_annuity_factor(req.discount_rate, req.projection_years)

    # Baseline midpoint ecosystem value
    baseline_per_ha = sum(s.get("mid", 0) for s in eco["services"].values()) * mult
    baseline_annual  = baseline_per_ha * req.area_hectares
    baseline_npv     = baseline_annual * pv_factor

    results: List[ScenarioResult] = []
    best_combined_npv = -1
    recommended = ""

    for key in req.scenarios:
        alt = LAND_USE_ALTERNATIVES[key]
        retain = alt["eco_services_retained"]

        eco_annual  = baseline_annual * retain
        rev_annual  = alt["revenue_ha_yr"] * req.area_hectares
        eco_npv     = eco_annual * pv_factor
        rev_npv     = rev_annual * pv_factor
        combined    = eco_npv + rev_npv
        loss_pct    = round((1 - retain) * 100, 1)

        # Recommendation logic
        if combined > baseline_npv * 0.9:
            rec = "✅ Strong — combined value near or above conservation baseline"
        elif combined > baseline_npv * 0.6:
            rec = "⚠️ Moderate — significant ecosystem value lost; partial mitigation needed"
        else:
            rec = "❌ Poor — ecosystem losses outweigh direct revenue over 10-year horizon"

        results.append(ScenarioResult(
            scenario_key          = key,
            scenario_name         = alt["name"],
            revenue_ha_yr         = alt["revenue_ha_yr"],
            total_revenue_annual  = round(rev_annual, 2),
            ecosystem_retained_pct= round(retain * 100, 1),
            ecosystem_value_retained = round(eco_annual, 2),
            ecosystem_npv         = round(eco_npv, 2),
            revenue_npv           = round(rev_npv, 2),
            combined_npv          = round(combined, 2),
            ecosystem_loss_pct    = loss_pct,
            recommendation        = rec,
        ))

        if combined > best_combined_npv:
            best_combined_npv = combined
            recommended = alt["name"]

    return ScenarioCompareResponse(
        ecosystem_name      = eco["name"],
        area_hectares       = req.area_hectares,
        region              = req.region,
        baseline_eco_annual = round(baseline_annual, 2),
        baseline_eco_npv    = round(baseline_npv, 2),
        scenarios           = results,
        recommended         = recommended,
        projection_years    = req.projection_years,
    )
