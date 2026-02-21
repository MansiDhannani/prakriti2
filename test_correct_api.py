import requests
import json

base_url = 'http://localhost:8000'

# CORRECT test data (ecosystem_type: "mangroves" not "mangrove")
test_val = {
    "ecosystem_type": "mangroves",  # ← Must be "mangroves" with 's'
    "area_hectares": 100,
    "region": "west_coast"
}

print("=" * 60)
print("TESTING WITH CORRECT DATA")
print("=" * 60)

# Test 1: Valuate (CORRECT)
print("\n1. POST /api/v1/valuate")
try:
    r = requests.post(f'{base_url}/api/v1/valuate', json=test_val, timeout=5)
    print(f"   Status: {r.status_code}")
    if r.status_code == 200:
        print(f"   ✅ Working!")
        data = r.json()
        print(f"      Annual Value: ₹{data.get('annual_value_mid', 0):,.0f}")
        print(f"      NPV (10yr): ₹{data.get('npv', 0):,.0f}")
        print(f"      Carbon: {data.get('carbon_annual_tonnes', 0)} tonnes/year")
    else:
        print(f"   ❌ Error: {r.text[:300]}")
except Exception as e:
    print(f"   ❌ Exception: {str(e)[:200]}")

# Test 2: Scenarios (CORRECT)
print("\n2. POST /api/v1/scenarios/compare")
try:
    r = requests.post(f'{base_url}/api/v1/scenarios/compare', json=test_val, timeout=5)
    print(f"   Status: {r.status_code}")
    if r.status_code == 200:
        print(f"   ✅ Working!")
        data = r.json()
        print(f"      Scenarios generated: {len(data.get('scenarios', []))}")
    else:
        print(f"   ❌ Error: {r.text[:300]}")
except Exception as e:
    print(f"   ❌ Exception: {str(e)[:200]}")

# Test 3: Narrative (REQUIRES full valuation result)
print("\n3. POST /api/v1/report/narrative")
try:
    # First, get a valuation result
    val_resp = requests.post(f'{base_url}/api/v1/valuate', json=test_val, timeout=5)
    if val_resp.status_code == 200:
        valuation = val_resp.json()
        
        # Now use it for narrative (structure matters!)
        narrative_data = {
            "valuation_result": valuation  # ← This is what it expects
        }
        
        r = requests.post(f'{base_url}/api/v1/report/narrative', json=narrative_data, timeout=10)
        print(f"   Status: {r.status_code}")
        if r.status_code == 200:
            print(f"   ✅ Working!")
            data = r.json()
            print(f"      Narrative generated: {len(data.get('narrative', ''))} chars")
        else:
            print(f"   ❌ Error: {r.text[:300]}")
    else:
        print(f"   ❌ Could not get valuation data first")
except Exception as e:
    print(f"   ❌ Exception: {str(e)[:200]}")

print("\n" + "=" * 60)
print("VALID ECOSYSTEM TYPES:")
print("=" * 60)
print("""
  • tropical_moist_forest
  • tropical_dry_forest
  • wetlands_inland
  • mangroves ✅ (use this, not "mangrove")
  • grasslands_savanna
  • agricultural_land
  • himalayan_alpine
  • urban_green_spaces
  • degraded_land
""")
