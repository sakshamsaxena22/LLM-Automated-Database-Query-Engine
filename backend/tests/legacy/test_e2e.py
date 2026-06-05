"""Quick end-to-end test of the query endpoint."""
import requests
import json

BASE = "http://127.0.0.1:8000"

# Test 1: Health check
print("=" * 50)
print("TEST 1: DB Health")
r = requests.get(f"{BASE}/db-health")
print(f"  Status: {r.status_code}")
print(f"  Response: {r.json()}")

# Test 2: Natural language query
print("\n" + "=" * 50)
print("TEST 2: 'Show me 5 recent failed transactions'")
r = requests.post(f"{BASE}/query", json={"query": "Show me 5 recent failed transactions"})
data = r.json()
print(f"  Status: {r.status_code}")
if r.status_code == 200:
    print(f"  Count: {data.get('count')}")
    print(f"  Execution Time: {data.get('execution_time_ms')}ms")
    print(f"  Generated Query: {json.dumps(data.get('generated_query', {}), indent=4)}")
    if data.get("results"):
        print(f"  First Result: {json.dumps(data['results'][0], indent=4)}")
    else:
        print("  No results returned")
else:
    print(f"  Error: {data}")

# Test 3: Aggregation query
print("\n" + "=" * 50)
print("TEST 3: 'Total amount of successful transactions'")
r = requests.post(f"{BASE}/query", json={"query": "What is the total amount of successful transactions?"})
data = r.json()
print(f"  Status: {r.status_code}")
if r.status_code == 200:
    print(f"  Count: {data.get('count')}")
    print(f"  Execution Time: {data.get('execution_time_ms')}ms")
    print(f"  Generated Query: {json.dumps(data.get('generated_query', {}), indent=4)}")
    if data.get("results"):
        print(f"  Results: {json.dumps(data['results'], indent=4)}")
else:
    print(f"  Error: {data}")

print("\n" + "=" * 50)
print("ALL TESTS COMPLETE")
