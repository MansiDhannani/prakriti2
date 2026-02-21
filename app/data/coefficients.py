"""
India Ecosystem Services Coefficient Database
Sources: TEEB India (Sukhdev 2008), FSI ISFR 2023, TERI, MoEFCC NATCOM,
         IIFM Verma 2000, Hussain & Badola 2010, CPCB, ATREE, CPR India
All values: INR / hectare / year
"""

ECOSYSTEMS: dict = {
    "tropical_moist_forest": {
        "name": "Tropical Moist Forest",
        "regions": "Western Ghats, Northeast India, Andaman Islands",
        "carbon_rate_tonnes_ha_yr": 6.25,   # FSI ISFR 2023 mid-range
        "climate_resilience_score": 92,
        "biodiversity_index": 95,
        "services": {
            "carbon_sequestration": {
                "min": 45000, "mid": 82500, "max": 120000,
                "method": "Social cost of carbon × sequestration rate (4.5–8 tCO₂/ha/yr)",
                "source": "FSI ISFR 2023 + MoEFCC NATCOM"
            },
            "water_regulation": {
                "min": 35000, "mid": 65000, "max": 95000,
                "method": "Replacement cost of watershed services",
                "source": "TERI 2018, Sukhdev et al. 2008"
            },
            "flood_control": {
                "min": 55000, "mid": 107500, "max": 160000,
                "method": "Avoided damage cost method",
                "source": "TERI 2018, ATREE Western Ghats"
            },
            "biodiversity_habitat": {
                "min": 80000, "mid": 165000, "max": 250000,
                "method": "Willingness-to-pay surveys + species richness index",
                "source": "ATREE 2019, Sukhdev et al. 2008"
            },
            "pollination": {
                "min": 12000, "mid": 28500, "max": 45000,
                "method": "Crop value × pollination dependency ratio (avg 0.35)",
                "source": "TERI 2016"
            },
            "soil_formation": {
                "min": 8000, "mid": 16500, "max": 25000,
                "method": "Replacement cost of soil nutrients",
                "source": "Sukhdev et al. 2008"
            },
            "recreation_tourism": {
                "min": 15000, "mid": 37500, "max": 60000,
                "method": "Travel cost method + visitor expenditure survey",
                "source": "MoEFCC Forest Tourism Reports"
            },
            "timber_nwfp": {
                "min": 20000, "mid": 47500, "max": 75000,
                "method": "Market price method",
                "source": "FSI ISFR 2023"
            },
        }
    },

    "tropical_dry_forest": {
        "name": "Tropical Dry Deciduous Forest",
        "regions": "Madhya Pradesh, Maharashtra, Odisha, Jharkhand",
        "carbon_rate_tonnes_ha_yr": 3.75,
        "climate_resilience_score": 78,
        "biodiversity_index": 78,
        "services": {
            "carbon_sequestration": {
                "min": 25000, "mid": 47500, "max": 70000,
                "method": "Social cost of carbon × 2.5–5 tCO₂/ha/yr",
                "source": "FSI ISFR 2023"
            },
            "water_regulation": {
                "min": 18000, "mid": 36500, "max": 55000,
                "method": "Replacement cost of water regulation",
                "source": "IIFM Verma 2000, TERI"
            },
            "flood_control": {
                "min": 30000, "mid": 60000, "max": 90000,
                "method": "Avoided damage cost",
                "source": "MoEFCC, TERI"
            },
            "biodiversity_habitat": {
                "min": 35000, "mid": 72500, "max": 110000,
                "method": "Willingness-to-pay surveys",
                "source": "Sukhdev et al. 2008"
            },
            "pollination": {
                "min": 8000, "mid": 19000, "max": 30000,
                "method": "Crop value × dependency ratio",
                "source": "TERI 2016"
            },
            "soil_formation": {
                "min": 5000, "mid": 11500, "max": 18000,
                "method": "Replacement cost",
                "source": "Sukhdev et al. 2008"
            },
            "recreation_tourism": {
                "min": 8000, "mid": 21500, "max": 35000,
                "method": "Travel cost method",
                "source": "MoEFCC"
            },
            "timber_nwfp": {
                "min": 25000, "mid": 52500, "max": 80000,
                "method": "Market price method",
                "source": "FSI ISFR 2023"
            },
        }
    },

    "wetlands_inland": {
        "name": "Inland Wetlands",
        "regions": "Chilika Lake, Loktak Lake, Indo-Gangetic Floodplains, Keoladeo",
        "carbon_rate_tonnes_ha_yr": 4.75,
        "climate_resilience_score": 88,
        "biodiversity_index": 82,
        "services": {
            "flood_control": {
                "min": 80000, "mid": 165000, "max": 250000,
                "method": "Avoided damage — 1 ha wetland protects ~7 ha downstream",
                "source": "Hussain & Badola 2010, TERI"
            },
            "water_filtration": {
                "min": 40000, "mid": 70000, "max": 100000,
                "method": "Replacement cost of equivalent water treatment plant",
                "source": "CPCB, Hussain & Badola 2010"
            },
            "carbon_sequestration": {
                "min": 30000, "mid": 57500, "max": 85000,
                "method": "Social cost × 3.0–6.5 tCO₂/ha/yr",
                "source": "MoEFCC NATCOM"
            },
            "biodiversity_habitat": {
                "min": 55000, "mid": 117500, "max": 180000,
                "method": "WTP surveys + bird-watching ecotourism value",
                "source": "Hussain & Badola 2010, ATREE"
            },
            "fisheries": {
                "min": 35000, "mid": 77500, "max": 120000,
                "method": "Market price of fish production dependent on wetland",
                "source": "TERI, State Fisheries Departments"
            },
            "groundwater_recharge": {
                "min": 20000, "mid": 42500, "max": 65000,
                "method": "Replacement cost of groundwater",
                "source": "CGWB Reports"
            },
            "recreation_tourism": {
                "min": 15000, "mid": 35000, "max": 55000,
                "method": "Travel cost + visitor expenditure",
                "source": "MoEFCC, State Tourism Boards"
            },
        }
    },

    "mangroves": {
        "name": "Mangrove Forests",
        "regions": "Sundarbans, Gujarat Coast, Odisha Coast, Andhra Pradesh",
        "carbon_rate_tonnes_ha_yr": 9.0,   # Blue carbon premium
        "climate_resilience_score": 95,
        "biodiversity_index": 88,
        "services": {
            "coastal_protection": {
                "min": 150000, "mid": 325000, "max": 500000,
                "method": "Avoided storm/cyclone damage cost per ha",
                "source": "TERI, MoEFCC Coastal Management"
            },
            "carbon_sequestration": {
                "min": 70000, "mid": 135000, "max": 200000,
                "method": "Blue carbon × 6–12 tCO₂/ha/yr (3–5× tropical forests)",
                "source": "FSI ISFR 2023, MoEFCC Blue Carbon Initiative"
            },
            "fisheries_nursery": {
                "min": 80000, "mid": 165000, "max": 250000,
                "method": "Market value of fish/shrimp dependent on mangrove nursery",
                "source": "CMFRI Reports"
            },
            "biodiversity_habitat": {
                "min": 90000, "mid": 185000, "max": 280000,
                "method": "WTP studies + species richness index",
                "source": "ATREE, Sukhdev et al. 2008"
            },
            "water_filtration": {
                "min": 30000, "mid": 60000, "max": 90000,
                "method": "Replacement cost method",
                "source": "CPCB, TERI"
            },
            "timber_nwfp": {
                "min": 15000, "mid": 32500, "max": 50000,
                "method": "Market price method",
                "source": "FSI Reports"
            },
        }
    },

    "grasslands_savanna": {
        "name": "Grasslands & Savannas",
        "regions": "Deccan Plateau, Rajasthan, Gujarat, Himalayan meadows",
        "carbon_rate_tonnes_ha_yr": 1.75,
        "climate_resilience_score": 60,
        "biodiversity_index": 55,
        "services": {
            "carbon_sequestration": {
                "min": 8000, "mid": 19000, "max": 30000,
                "method": "Social cost × 1.0–2.5 tCO₂/ha/yr",
                "source": "MoEFCC NATCOM, TERI"
            },
            "biodiversity_habitat": {
                "min": 10000, "mid": 25000, "max": 40000,
                "method": "WTP surveys for grassland-dependent species",
                "source": "Sukhdev et al. 2008, ATREE"
            },
            "grazing_livestock": {
                "min": 12000, "mid": 28500, "max": 45000,
                "method": "Market value of livestock products supported by grazing",
                "source": "MoAFW Reports"
            },
            "pollination": {
                "min": 5000, "mid": 12500, "max": 20000,
                "method": "Crop value × dependency ratio",
                "source": "TERI 2016"
            },
            "soil_formation": {
                "min": 3000, "mid": 7500, "max": 12000,
                "method": "Replacement cost of soil nutrients",
                "source": "Sukhdev et al. 2008"
            },
            "water_regulation": {
                "min": 6000, "mid": 14000, "max": 22000,
                "method": "Replacement cost",
                "source": "TERI"
            },
        }
    },

    "agricultural_land": {
        "name": "Agricultural Land (Traditional)",
        "regions": "Indo-Gangetic Plain, Deccan, Krishna-Godavari Delta",
        "carbon_rate_tonnes_ha_yr": 0.65,
        "climate_resilience_score": 35,
        "biodiversity_index": 30,
        "services": {
            "food_production": {
                "min": 40000, "mid": 95000, "max": 150000,
                "method": "Net farm income (varies by crop/region)",
                "source": "CACP Price Policy Reports 2023"
            },
            "pollination": {
                "min": 15000, "mid": 37500, "max": 60000,
                "method": "Crop value × pollination dependency (avg 0.30)",
                "source": "TERI 2016, ICAR"
            },
            "carbon_sequestration": {
                "min": 3000, "mid": 7500, "max": 12000,
                "method": "Social cost × 0.3–1.0 tCO₂/ha/yr",
                "source": "ICAR, MoEFCC"
            },
            "soil_formation": {
                "min": 5000, "mid": 11500, "max": 18000,
                "method": "Replacement cost of soil nutrients",
                "source": "Sukhdev et al. 2008"
            },
            "cultural_value": {
                "min": 5000, "mid": 12500, "max": 20000,
                "method": "Rural livelihood and cultural heritage proxy value",
                "source": "CPR India"
            },
        }
    },

    "himalayan_alpine": {
        "name": "Himalayan Alpine Ecosystems",
        "regions": "Uttarakhand, Himachal Pradesh, Ladakh, Sikkim",
        "carbon_rate_tonnes_ha_yr": 3.5,
        "climate_resilience_score": 85,
        "biodiversity_index": 90,
        "services": {
            "water_supply": {
                "min": 60000, "mid": 130000, "max": 200000,
                "method": "Downstream water value — feeds Ganga, Yamuna, Brahmaputra",
                "source": "IIFM Verma 2000, MoEFCC Himalayan Policy"
            },
            "carbon_sequestration": {
                "min": 20000, "mid": 42500, "max": 65000,
                "method": "Social cost of carbon × regional rate",
                "source": "FSI ISFR 2023"
            },
            "biodiversity_habitat": {
                "min": 50000, "mid": 112500, "max": 175000,
                "method": "WTP + high endemic species richness premium",
                "source": "ATREE, Sukhdev et al. 2008"
            },
            "climate_regulation": {
                "min": 40000, "mid": 85000, "max": 130000,
                "method": "Glacier preservation + albedo effect valuation",
                "source": "TERI, MoEFCC"
            },
            "tourism_recreation": {
                "min": 25000, "mid": 57500, "max": 90000,
                "method": "Visitor spend + travel cost method",
                "source": "State Tourism Boards, MoT India"
            },
            "medicinal_plants": {
                "min": 10000, "mid": 25000, "max": 40000,
                "method": "Market value + cultural heritage proxy",
                "source": "TERI, Ayush Ministry Reports"
            },
        }
    },

    "urban_green_spaces": {
        "name": "Urban Green Spaces",
        "regions": "Delhi, Mumbai, Bengaluru, Chennai, Hyderabad",
        "carbon_rate_tonnes_ha_yr": 1.0,
        "climate_resilience_score": 55,
        "biodiversity_index": 35,
        "services": {
            "air_purification": {
                "min": 25000, "mid": 57500, "max": 90000,
                "method": "Health cost savings from reduced PM2.5 and NO₂",
                "source": "CPR India, TERI Urban"
            },
            "urban_heat_mitigation": {
                "min": 20000, "mid": 45000, "max": 70000,
                "method": "Energy savings from cooling + health benefit reduction",
                "source": "CPR India, NIUA"
            },
            "flood_control": {
                "min": 30000, "mid": 65000, "max": 100000,
                "method": "Avoided stormwater infrastructure cost",
                "source": "TERI Urban, CPR India"
            },
            "recreation_wellbeing": {
                "min": 15000, "mid": 35000, "max": 55000,
                "method": "Hedonic pricing + WTP surveys",
                "source": "CPR India"
            },
            "carbon_sequestration": {
                "min": 5000, "mid": 12500, "max": 20000,
                "method": "Urban tree cover sequestration rates",
                "source": "FSI Urban Tree Cover"
            },
            "noise_reduction": {
                "min": 8000, "mid": 16500, "max": 25000,
                "method": "Hedonic pricing — property value premium near green spaces",
                "source": "CPR India"
            },
        }
    },

    "degraded_land": {
        "name": "Degraded / Wasteland",
        "regions": "Chambal Ravines, Degraded Mining Areas, Over-grazed Zones",
        "carbon_rate_tonnes_ha_yr": 0.1,
        "climate_resilience_score": 5,
        "biodiversity_index": 5,
        "services": {
            "carbon_sequestration": {
                "min": 500, "mid": 1750, "max": 3000,
                "method": "Minimal sparse vegetation",
                "source": "MoEFCC"
            },
            "biodiversity_habitat": {
                "min": 500, "mid": 2750, "max": 5000,
                "method": "Very low species richness",
                "source": "Sukhdev et al. 2008"
            },
            "soil_erosion_cost": {
                "min": -8000, "mid": -5000, "max": -1000,
                "method": "Negative value — net annual soil erosion loss",
                "source": "ICAR Soil Health Reports"
            },
        }
    },
}

REGIONAL_MULTIPLIERS: dict = {
    "western_ghats":       1.40,
    "northeast_india":     1.35,
    "sundarbans":          1.50,
    "indo_gangetic_plain": 0.90,
    "deccan_plateau":      0.85,
    "rajasthan_arid":      0.60,
    "himalayan_region":    1.30,
    "coastal_regions":     1.20,
    "urban_metro":         1.60,
}

CARBON_PRICES: dict = {
    "social_cost":      3500,   # INR/tonne (MoEFCC, PPP-adjusted EPA SCC)
    "market_price":     1500,   # INR/tonne (BEE Carbon Credits India)
    "voluntary_market": 2200,   # INR/tonne (Gold Standard, VCS average)
}

LAND_USE_ALTERNATIVES: dict = {
    "preserve": {
        "name": "Preserve / Conserve",
        "description": "Designate as protected area or conservation zone",
        "revenue_ha_yr": 55000,      # ecotourism + carbon credits
        "eco_services_retained": 0.95,
        "recommendation_threshold": 0.8,
    },
    "restore": {
        "name": "Rewild / Ecological Restoration",
        "description": "Active restoration to native ecosystem",
        "revenue_ha_yr": 40000,
        "eco_services_retained": 0.65,   # mid-point — grows over time
        "recommendation_threshold": 0.7,
    },
    "solar": {
        "name": "Solar Energy Farm",
        "description": "Utility-scale photovoltaic installation",
        "revenue_ha_yr": 260000,
        "eco_services_retained": 0.40,
        "recommendation_threshold": 0.4,
    },
    "agriculture": {
        "name": "Intensive Commercial Agriculture",
        "description": "Mechanised monoculture farming",
        "revenue_ha_yr": 110000,
        "eco_services_retained": 0.60,
        "recommendation_threshold": 0.5,
    },
    "development": {
        "name": "Urban / Real Estate Development",
        "description": "Residential or commercial construction",
        "revenue_ha_yr": 800000,
        "eco_services_retained": 0.15,
        "recommendation_threshold": 0.2,
    },
    "industrial": {
        "name": "Industrial / Manufacturing Zone",
        "description": "Heavy industry or industrial estate",
        "revenue_ha_yr": 700000,
        "eco_services_retained": 0.10,
        "recommendation_threshold": 0.1,
    },
}

SOURCES = [
    "Sukhdev et al. (2008) — TEEB India Study",
    "Forest Survey of India — ISFR 2023",
    "TERI Ecosystem Services Publications",
    "MoEFCC — National Communication to UNFCCC",
    "IIFM Verma (2000) — HP Forest Valuation",
    "Hussain & Badola (2010) — Wetland Services",
    "CPCB Water Quality Reports",
    "ATREE — Western Ghats Studies",
    "CPR India — Urban Ecosystem Services",
    "CACP Price Policy Reports 2023",
    "BEE Carbon Market India",
    "CMFRI Fisheries Reports",
]
