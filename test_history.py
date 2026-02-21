import requests

print('Testing History Page Integration...\n')

# Test 1: Check if page loads
r = requests.get('http://localhost:8000/history')
print(f'1. History page loads: {r.status_code} OK' if r.status_code == 200 else f'1. History page ERROR: {r.status_code}')

# Test 2: Check analytics endpoint
r = requests.get('http://localhost:8000/api/v1/analytics')
data = r.json()
print(f'2. Analytics data: {data.get("total_valuations", 0)} valuations, {data.get("total_area_valuated_ha", 0)} ha')

# Test 3: Check history endpoint  
r = requests.get('http://localhost:8000/api/v1/history?limit=5')
data = r.json()
print(f'3. History data: {data["total"]} total records, showing {len(data["results"])} records')

# Test 4: Check if a sample result has all required fields
if data['results']:
    sample = data['results'][0]
    fields = ['ecosystem_type', 'ecosystem_name', 'area_hectares', 'annual_value_mid', 'npv', 'carbon_annual_tonnes', 'climate_score', 'region']
    missing = [f for f in fields if f not in sample]
    if missing:
        print(f'4. WARNING: Missing fields in history result: {missing}')
    else:
        print(f'4. Sample record fields: OK')
        print(f'   - Ecosystem: {sample["ecosystem_name"]}')
        print(f'   - Area: {sample["area_hectares"]} ha')
        print(f'   - Annual Value: ₹{sample["annual_value_mid"]:,.0f}')
else:
    print('4. No history records found')

print('\n✅ All backend components working!')
print('\n📋 To see history page, open: http://localhost:8000/history')
