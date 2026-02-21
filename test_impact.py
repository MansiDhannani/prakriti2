import requests
import json

print("Testing Impact Endpoint")
print("=" * 60)

# Use valuation response structure
valuation = {
    "ecosystem_type": "wetlands_inland",
    "ecosystem_name": "Inland Wetlands",
    "area_hectares": 100,
    "region": "indo_gangetic_plain",
    "annual_value_min": 45000000,
    "annual_value_mid": 50850000,
    "annual_value_max": 56700000,
    "npv": 341207639,
    "carbon_annual_tonnes": 475,
    "climate_resilience_score": 85,
    "biodiversity_index": 88,
    "services": [
        {"service_name": "freshwater_supply", "total_for_area": 25000000},
        {"service_name": "flood_mitigation", "total_for_area": 15000000}
    ]
}

try:
    resp = requests.post("http://localhost:8000/api/v1/impact", json=valuation)
    print(f"Status: {resp.status_code}")
    
    if resp.status_code == 200:
        data = resp.json()
        print(f"✅ Impact API OK")
        print(f"Cards returned: {len(data)}")
        for i, card in enumerate(data, 1):
            print(f"\n  Card {i}: {card.get('icon')} {card.get('metric')}")
            print(f"    Label: {card.get('label')}")
            print(f"    Source: {card.get('source')}")
    else:
        print(f"❌ Error: {resp.text}")
except Exception as e:
    print(f"❌ Connection error: {e}")
