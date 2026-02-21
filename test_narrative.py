import requests
import json

url = 'http://localhost:8000/api/v1/report/narrative'
payload = {
    'valuation_result': {
        'ecosystem_type': 'wetlands_inland',
        'ecosystem_name': 'Inland Wetlands',
        'area_hectares': 100,
        'region': 'indo_gangetic_plain',
        'annual_value_mid': 50850000,
        'npv': 341207639.14,
        'carbon_annual_tonnes': 475.0,
        'climate_resilience_score': 88,
        'biodiversity_index': 82
    },
    'location_name': 'Test Wetland'
}

try:
    print('Testing narrative API endpoint...')
    r = requests.post(url, json=payload, timeout=30)
    
    print(f'Status: {r.status_code}')
    
    if r.status_code == 200:
        data = r.json()
        print('✅ SUCCESS!')
        print('\nNarrative generated:')
        print(data.get('narrative', 'No narrative')[:300])
    else:
        print(f'❌ Error: {r.status_code}')
        print(r.text[:500])
        
except Exception as e:
    print(f'❌ Exception: {e}')
