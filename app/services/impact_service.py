COST_PER_LITER_INR          = 0.05
ANNUAL_LITERS_PER_PERSON    = 135 * 365
CO2_PER_TREE_KG_YR          = 22
AVG_FLOOD_DAMAGE_PER_PERSON = 15000
KWH_PER_TONNE_CO2           = 820
SOLAR_PANEL_KWH_YR          = 400

def _fmt(n):
    if n >= 1_00_00_000: return f"{n/1_00_00_000:.1f} Cr"
    if n >= 1_00_000:    return f"{n/1_00_00_000:.1f} L"
    if n >= 1000:        return f"{n/1000:.1f}K"
    return str(int(n))

def calculate_impact(ecosystem_type, area_hectares, annual_value_inr,
                     carbon_tonnes_yr, biodiversity_index, climate_score, services):
    impacts = []

    water_value = sum(s.get("total_for_area", 0) for s in services
        if any(k in s.get("service_name","").lower() for k in ["water","filtration","recharge","supply"]))
    if water_value > 0:
        people = int((water_value / COST_PER_LITER_INR) / ANNUAL_LITERS_PER_PERSON)
        impacts.append({"icon":"💧","color":"#3a9bd5","metric":_fmt(people),
            "label":"people supplied clean water","source":f"Water services worth ₹{_fmt(water_value)}/yr"})

    trees = int(carbon_tonnes_yr * 1000 / CO2_PER_TREE_KG_YR)
    solar = int(carbon_tonnes_yr * KWH_PER_TONNE_CO2 / SOLAR_PANEL_KWH_YR)
    impacts.append({"icon":"🌳","color":"#52b36b","metric":_fmt(trees),
        "label":"mature trees equivalent","source":f"= {_fmt(solar)} solar panels worth of carbon offset"})

    flood_value = sum(s.get("total_for_area", 0) for s in services
        if "flood" in s.get("service_name","").lower())
    if flood_value > 0:
        people = int(flood_value / AVG_FLOOD_DAMAGE_PER_PERSON)
        impacts.append({"icon":"🛡️","color":"#f0b429","metric":_fmt(people),
            "label":"people protected from floods","source":f"Avoided damage: ₹{_fmt(flood_value)}/yr"})

    eco = ecosystem_type.lower()
    if "wetland" in eco or "mangrove" in eco: n, kind = int(area_hectares*0.8), "fisher families"
    elif "forest" in eco:                      n, kind = int(area_hectares*0.15), "forest livelihoods"
    elif "agri" in eco:                        n, kind = int(area_hectares*2.1), "farmers (pollination)"
    else:                                      n, kind = int(area_hectares*0.1), "direct livelihoods"
    if n > 0:
        impacts.append({"icon":"👨‍👩‍👧","color":"#b36bd4","metric":_fmt(n),
            "label":kind,"source":"directly supported by this ecosystem"})

    if biodiversity_index >= 70:
        impacts.append({"icon":"🦋","color":"#e05c8a","metric":_fmt(int(area_hectares*0.12)),
            "label":"wildlife species habitat","source":f"Biodiversity Index: {biodiversity_index}/100"})

    if climate_score >= 60:
        impacts.append({"icon":"🌡️","color":"#52b36b","metric":str(max(1,int(area_hectares/50))),
            "label":"villages climate-buffered","source":f"Climate Resilience Score: {climate_score}/100"})

    impacts.append({"icon":"⚠️","color":"#e05c2a","metric":f"₹{_fmt(annual_value_inr*6.71)}",
        "label":"lost forever if developed","source":"10-year ecosystem NPV that cannot be recovered"})

    return {
        "impacts": impacts,
        "total_annual_inr": annual_value_inr,
        "carbon_trees_eq": trees,
        "headline": (f"This {area_hectares:,.0f} ha ecosystem provides services worth "
                     f"₹{_fmt(annual_value_inr)} every year — "
                     f"equivalent to {_fmt(trees)} trees working round the clock.")
    }