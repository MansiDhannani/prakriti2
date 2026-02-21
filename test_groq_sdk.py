import requests
import json

print("Testing Narrative Endpoint with Official Groq SDK")
print("=" * 70)

BASE = "http://localhost:8000"

# Test valuation
vals = {
    "ecosystem_type": "wetlands_inland",
    "ecosystem_name": "Inland Wetlands",
    "area_hectares": 100,
    "region": "indo_gangetic_plain",
    "annual_value_min": 45000000,
    "annual_value_mid": 50850000,
    "annual_value_max": 56700000,
    "npv": 341207639,
    "carbon_annual_tonnes": 475,
    "carbon_annual_value_inr": 1045000,
    "climate_resilience_score": 85,
    "biodiversity_index": 88,
    "projection_years": 10,
    "discount_rate": 0.08,
    "regional_multiplier": 1.2,
    "services": [
        {"service_name": "freshwater_supply", "adjusted_value": 250000, "total_for_area": 25000000, "contribution_pct": 25, "method": "Replacement cost", "source": "TEEB"},
        {"service_name": "flood_mitigation", "adjusted_value": 150000, "total_for_area": 15000000, "contribution_pct": 15, "method": "Defensive expenditure", "source": "FSI ISFR"}
    ]
}

print("\n1️⃣ Sending narrative request to /api/v1/report/narrative...")
try:
    resp = requests.post(
        f"{BASE}/api/v1/report/narrative",
        json={"valuation_result": vals, "scenario_results": None, "location_name": "Test Wetland"},
        timeout=60
    )
    
    print(f"Status: {resp.status_code}")
    
    if resp.status_code == 200:
        data = resp.json()
        print("\n✅ SUCCESS! Narrative generated with official Groq SDK!")
        print(f"\nNarrative (first 300 chars):")
        print(data.get("narrative", "")[:300] + "...")
        print(f"\nKey findings: {len(data.get('key_findings', []))} items")
        print(f"Recommendations: {len(data.get('policy_recommendations', []))} items")
        print("\n🎉 Groq API + Official SDK is now working!")
    else:
        print(f"\nError: {resp.status_code}")
        print(f"Response: {resp.text[:500]}")
        
except Exception as e:
    print(f"\n❌ Error: {str(e)[:200]}")

print("\n" + "=" * 70)
