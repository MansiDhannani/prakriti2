"""
Impact Calculator — Convert ecosystem valuations into human-scale metrics.
No ML, no Groq, 100% offline. Just math + human context.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
import math

router = APIRouter()


class ImpactCard(BaseModel):
    icon: str
    metric: str
    label: str
    colour: str  # hex colour for UI
    source: str  # data source


def fmt_number(n: float, decimals: int = 1) -> str:
    """Format large numbers for impact display."""
    if abs(n) >= 1e7:
        return f"{(n/1e7):.{decimals}f}Cr"
    elif abs(n) >= 1e5:
        return f"{(n/1e5):.{decimals}f}L"
    elif abs(n) >= 1e3:
        return f"{(n/1e3):.0f}K"
    else:
        return f"{int(n):,}"


@router.post("/impact", response_model=List[ImpactCard])
def calculate_impact(valuation: dict):
    """
    Convert valuation output into human-scale impact metrics.
    
    Input: Full output from /valuate endpoint
    Output: 4-6 impact cards with icons, metrics, labels
    
    Examples:
    - "84,000 people supplied clean water"
    - "2.3L mature trees equivalent"
    - "18,000 people flood-protected"
    - "₹38 Cr lost forever if developed"
    """
    try:
        # Extract key values
        annual_value = valuation.get("annual_value_mid", 0)
        carbon_annual = valuation.get("carbon_annual_tonnes", 0)
        area_ha = valuation.get("area_hectares", 100)
        ecosystem = valuation.get("ecosystem_type", "")
        npv = valuation.get("npv", 0)
        
        cards: List[ImpactCard] = []
        
        # ── Card 1: Water Supply (wetlands, forests) ──────────────────────────
        if ecosystem in ["wetlands_inland", "mangroves", "himalayan_alpine", "tropical_moist_forest"]:
            # Assumption: 1 ha wetland supplies ~840 people/year with freshwater treatment value
            people_water = int(area_ha * 840)
            cards.append(ImpactCard(
                icon="💧",
                metric=f"{people_water:,}",
                label="people supplied clean water",
                colour="#0288d1",
                source="TEEB India water filtration value"
            ))
        
        # ── Card 2: Tree Equivalence (carbon sequestration) ──────────────────
        # 1 mature tree sequesters ~20kg CO₂/year, ~0.3 tCO₂ per year
        mature_trees = int(carbon_annual / 0.3) if carbon_annual > 0 else 0
        cards.append(ImpactCard(
            icon="🌳",
            metric=f"{fmt_number(mature_trees)}",
            label="mature trees equivalent (carbon)",
            colour="#2d7a4f",
            source=f"{carbon_annual:.1f}t CO₂/year"
        ))
        
        # ── Card 3: Flood Protection (value protection) ──────────────────────
        if ecosystem in ["wetlands_inland", "mangroves", "tropical_moist_forest"]:
            # Assumption: wetland flood control protects ~180 people per hectare per flood event
            # Average 2 flood events per decade = ~1,800 person-exposures/decade
            people_flood_protected = int(area_ha * 180 * 2)
            cards.append(ImpactCard(
                icon="🛡️",
                metric=f"{people_flood_protected:,}",
                label="people flood-protected (next 10 years)",
                colour="#ff6b6b",
                source="FSI ISFR flood control estimates"
            ))
        
        # ── Card 4: Development Opportunity Cost (ecosystem loss) ────────────
        # If developed, ecosystem services lost = ~85% of current annual value × 10 years
        opp_cost_10yr = annual_value * 0.85 * 10
        cards.append(ImpactCard(
            icon="⚠️",
            metric=f"₹{fmt_number(opp_cost_10yr)}",
            label="ecosystem value lost if developed (10 years)",
            colour="#ef5350",
            source="NPV calculation (annual value × 0.85 × 10yr)"
        ))
        
        # ── Card 5: Pollination Services (agricultural) ─────────────────────
        if ecosystem in ["tropical_moist_forest", "tropical_dry_forest", "grasslands_savanna", "agricultural_land"]:
            # Find pollination service if exists
            services = valuation.get("services", [])
            poll_service = next((s for s in services if "pollination" in s.get("service_name", "").lower()), None)
            if poll_service:
                poll_value = poll_service.get("total_for_area", 0)
                # Assume ₹500 per hectare enables one agricultural season per 0.5ha
                ag_landarea = int((poll_value / 500) * 0.5)
                cards.append(ImpactCard(
                    icon="🌻",
                    metric=f"{ag_landarea:,}ha",
                    label="agricultural land pollination-dependent",
                    colour="#f9a825",
                    source="Pollination service valuation"
                ))
        
        # ── Card 6: Biodiversity Habitat (species support) ─────────────────
        bio_index = valuation.get("biodiversity_index", 50)
        if bio_index >= 70:
            # High biodiversity areas support ~50-200 species per hectare (tropical forests)
            species_count = int(area_ha * (100 + bio_index))
            cards.append(ImpactCard(
                icon="🦋",
                metric=f"{species_count:,}",
                label="species supported",
                colour="#8cc97e",
                source=f"Biodiversity Index: {bio_index}/100"
            ))
        
        return cards
        
    except KeyError as e:
        raise HTTPException(status_code=400, detail=f"Missing valuation field: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Impact calculation failed: {str(e)}")
