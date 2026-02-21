from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict
from enum import Enum


# ── Enums ────────────────────────────────────────────────────────────────────

class EcosystemType(str, Enum):
    tropical_moist_forest = "tropical_moist_forest"
    tropical_dry_forest   = "tropical_dry_forest"
    wetlands_inland       = "wetlands_inland"
    mangroves             = "mangroves"
    grasslands_savanna    = "grasslands_savanna"
    agricultural_land     = "agricultural_land"
    himalayan_alpine      = "himalayan_alpine"
    urban_green_spaces    = "urban_green_spaces"
    degraded_land         = "degraded_land"

class RegionType(str, Enum):
    western_ghats       = "western_ghats"
    northeast_india     = "northeast_india"
    sundarbans          = "sundarbans"
    indo_gangetic_plain = "indo_gangetic_plain"
    deccan_plateau      = "deccan_plateau"
    rajasthan_arid      = "rajasthan_arid"
    himalayan_region    = "himalayan_region"
    coastal_regions     = "coastal_regions"
    urban_metro         = "urban_metro"

class LandUseType(str, Enum):
    preserve    = "preserve"
    restore     = "restore"
    solar       = "solar"
    agriculture = "agriculture"
    development = "development"
    industrial  = "industrial"

class CarbonPricingMethod(str, Enum):
    social_cost      = "social_cost"       # ₹3500/tonne
    market_price     = "market_price"      # ₹1500/tonne
    voluntary_market = "voluntary_market"  # ₹2200/tonne (default)


# ── Request Models ────────────────────────────────────────────────────────────

class ValuationRequest(BaseModel):
    ecosystem_type:       EcosystemType
    area_hectares:        float = Field(..., gt=0, le=1_000_000, description="Land area in hectares")
    region:               RegionType
    carbon_pricing:       CarbonPricingMethod = CarbonPricingMethod.voluntary_market
    discount_rate:        float = Field(0.08, ge=0.01, le=0.20, description="NPV discount rate (default 8%)")
    projection_years:     int   = Field(10,   ge=1,   le=50,    description="Years for NPV projection")
    value_type:           str   = Field("midpoint", description="min | midpoint | max")
    location_name:        Optional[str] = Field(None, description="Optional place name for report")

    @validator("value_type")
    def check_value_type(cls, v):
        if v not in ("min", "midpoint", "max"):
            raise ValueError("value_type must be min, midpoint, or max")
        return v

class ScenarioCompareRequest(BaseModel):
    ecosystem_type:   EcosystemType
    area_hectares:    float = Field(..., gt=0)
    region:           RegionType
    scenarios:        List[LandUseType] = Field(
        default=["preserve","restore","solar","agriculture","development","industrial"]
    )
    projection_years: int = Field(10, ge=1, le=50)
    discount_rate:    float = Field(0.08)
    location_name:    Optional[str] = None

class NarrativeRequest(BaseModel):
    valuation_result: dict
    scenario_results: Optional[List[dict]] = None
    location_name:    Optional[str] = None
    policy_context:   Optional[str] = Field(None, description="Extra context for policymakers")

class PDFReportRequest(BaseModel):
    valuation_result: dict
    scenario_results: Optional[List[dict]] = None
    narrative:        Optional[str] = None
    location_name:    Optional[str] = None
    prepared_for:     Optional[str] = Field(None, description="Name of municipality / department")


# ── Response Models ───────────────────────────────────────────────────────────

class ServiceDetail(BaseModel):
    service_name:   str
    value_min:      float
    value_mid:      float
    value_max:      float
    adjusted_value: float        # after regional multiplier
    total_for_area: float
    contribution_pct: float
    method:         str
    source:         str

class ValuationResponse(BaseModel):
    # Input echo
    ecosystem_type:    str
    ecosystem_name:    str
    area_hectares:     float
    region:            str
    regional_multiplier: float

    # Annual values (INR)
    annual_value_min:  float
    annual_value_mid:  float
    annual_value_max:  float
    annual_value_used: float     # based on value_type param

    # NPV
    npv:               float
    discount_rate:     float
    projection_years:  int

    # Carbon
    carbon_rate_tonnes_ha_yr: float
    carbon_annual_tonnes:     float
    carbon_price_inr_tonne:   float
    carbon_annual_value_inr:  float

    # Indices
    climate_resilience_score: int
    biodiversity_index:       int

    # Breakdown
    services:          List[ServiceDetail]

    # Metadata
    currency:          str = "INR"
    value_type_used:   str
    sources:           List[str]

class ScenarioResult(BaseModel):
    scenario_key:        str
    scenario_name:       str
    revenue_ha_yr:       float
    total_revenue_annual: float
    ecosystem_retained_pct: float
    ecosystem_value_retained: float
    ecosystem_npv:       float
    revenue_npv:         float
    combined_npv:        float
    ecosystem_loss_pct:  float
    recommendation:      str

class ScenarioCompareResponse(BaseModel):
    ecosystem_name:    str
    area_hectares:     float
    region:            str
    baseline_eco_annual: float
    baseline_eco_npv:    float
    scenarios:         List[ScenarioResult]
    recommended:       str
    projection_years:  int

class NarrativeResponse(BaseModel):
    narrative:         str
    key_findings:      List[str]
    policy_recommendations: List[str]

class PDFResponse(BaseModel):
    pdf_base64:        str
    filename:          str
    size_bytes:        int
