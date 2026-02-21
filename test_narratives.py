import requests
import json

base_url = 'http://localhost:8000'

# Test 1: Mangroves
print("=" * 70)
print("TEST 1: MANGROVES")
print("=" * 70)

val1 = {
    "ecosystem_type": "mangroves",
    "area_hectares": 100,
    "region": "coastal_regions",
    "ecosystem_name": "Mangrove Forest - Coastal Region",
    "annual_value_mid": 5000000,
    "carbon_annual_tonnes": 500,
    "biodiversity_index": 88,
    "climate_resilience_score": 75,
    "services": []
}

r = requests.post(f'{base_url}/api/v1/valuate', json={
    "ecosystem_type": "mangroves",
    "area_hectares": 100,
    "region": "coastal_regions"
}, timeout=5)

if r.status_code == 200:
    val_result = r.json()
else:
    print(f"Valuate error: {r.status_code}")
    val_result = val1

narrative_data = {"valuation_result": val_result}
r = requests.post(f'{base_url}/api/v1/report/narrative', json=narrative_data, timeout=15)
print(f'Status: {r.status_code}')
if r.status_code == 200:
    data = r.json()
    narrative = data.get('narrative', '')
    print(f'Narrative (first 300 chars): {narrative[:300]}...')
else:
    print(f'Error: {r.text[:300]}')

# Test 2: Tropical forest
print("\n" + "=" * 70)
print("TEST 2: TROPICAL FOREST")
print("=" * 70)

r = requests.post(f'{base_url}/api/v1/valuate', json={
    "ecosystem_type": "tropical_moist_forest",
    "area_hectares": 500,
    "region": "western_ghats"
}, timeout=5)

if r.status_code == 200:
    val_result = r.json()
    print(f'Valuate: OK')
    
    narrative_data = {"valuation_result": val_result}
    r = requests.post(f'{base_url}/api/v1/report/narrative', json=narrative_data, timeout=15)
    print(f'Status: {r.status_code}')
    if r.status_code == 200:
        data = r.json()
        narrative = data.get('narrative', '')
        print(f'Narrative (first 300 chars): {narrative[:300]}...')
    else:
        print(f'Error: {r.text[:300]}')
else:
    print(f'Valuate error: {r.status_code}')

# Test 3: Wetlands
print("\n" + "=" * 70)
print("TEST 3: WETLANDS")
print("=" * 70)

r = requests.post(f'{base_url}/api/v1/valuate', json={
    "ecosystem_type": "wetlands_inland",
    "area_hectares": 200,
    "region": "indo_gangetic_plain"
}, timeout=5)

if r.status_code == 200:
    val_result = r.json()
    print(f'Valuate: OK')
    
    narrative_data = {"valuation_result": val_result}
    r = requests.post(f'{base_url}/api/v1/report/narrative', json=narrative_data, timeout=15)
    print(f'Status: {r.status_code}')
    if r.status_code == 200:
        data = r.json()
        narrative = data.get('narrative', '')
        print(f'Narrative (first 300 chars): {narrative[:300]}...')
    else:
        print(f'Error: {r.text[:300]}')
else:
    print(f'Valuate error: {r.status_code}')

print("\n" + "=" * 70)
print("Check if different narratives are being generated for different ecosystems")
print("=" * 70)
