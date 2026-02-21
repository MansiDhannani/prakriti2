import requests
import json

# Test valuation endpoint
print("=" * 60)
print("Testing Valuation Endpoint")
print("=" * 60)

url1 = 'http://localhost:8000/api/v1/valuate'
payload1 = {
    'ecosystem_type': 'wetlands_inland',
    'area_hectares': 100,
    'region': 'indo_gangetic_plain',
    'carbon_pricing': 'voluntary_market',
    'value_type': 'midpoint',
    'projection_years': 10,
    'location_name': 'Test'
}

try:
    r = requests.post(url1, json=payload1, timeout=10)
    if r.status_code == 200:
        data = r.json()
        print('✅ Valuation API OK')
        print('Keys returned:', len(list(data.keys())))
        print('annual_value_mid:', data.get('annual_value_mid'))
        print('npv:', data.get('npv'))
        print('services count:', len(data.get('services', [])))
    else:
        print(f'❌ Status {r.status_code}')
except Exception as e:
    print(f'❌ Error: {e}')

# Test scenarios endpoint
print("\n" + "=" * 60)
print("Testing Scenarios Endpoint")
print("=" * 60)

url2 = 'http://localhost:8000/api/v1/scenarios/compare'
payload2 = {
    'ecosystem_type': 'wetlands_inland',
    'area_hectares': 100,
    'region': 'indo_gangetic_plain',
    'scenarios': ['preserve', 'restore', 'solar', 'agriculture', 'development', 'industrial'],
    'projection_years': 10
}

try:
    r = requests.post(url2, json=payload2, timeout=10)
    if r.status_code == 200:
        data = r.json()
        print('✅ Scenarios API OK')
        print('Top-level keys:', list(data.keys()))
        if 'scenarios' in data:
            print('Number of scenarios:', len(data['scenarios']))
            if len(data['scenarios']) > 0:
                s = data['scenarios'][0]
                print('First scenario:', s.get('scenario_name'))
                print('First scenario keys:', list(s.keys()))
                print('Sample values:')
                print('  - scenario_name:', s.get('scenario_name'))
                print('  - combined_npv:', s.get('combined_npv'))
                print('  - ecosystem_npv:', s.get('ecosystem_npv'))
                print('  - revenue_npv:', s.get('revenue_npv'))
    else:
        print(f'Status {r.status_code}')
        print(r.text[:300])
except Exception as e:
    print(f'Error: {e}')
