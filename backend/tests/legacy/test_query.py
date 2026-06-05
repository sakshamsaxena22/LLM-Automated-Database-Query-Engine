"""Quick end-to-end test for the query API."""
import requests
import json

BASE = "http://127.0.0.1:8000"

tests = [
    "Show all failed transactions",
    "Transactions above 5000",
    "Total successful payment amount",
    "Average transaction amount by merchant",
    "Count of pending UPI payments",
]

print("=" * 60)
for q in tests:
    print(f"\nQuery: {q}")
    print("-" * 40)
    try:
        r = requests.post(f"{BASE}/query", json={"query": q}, timeout=30)
        r.raise_for_status()
        d = r.json()
        print(f"  Status: {r.status_code}")
        print(f"  Count:  {d['count']}")
        print(f"  Time:   {d.get('execution_time_ms', '?')} ms")
        print(f"  Query:  {json.dumps(d['generated_query'], indent=2)[:200]}")
        if d["results"]:
            print(f"  Sample: {json.dumps(d['results'][0])[:150]}")
        print("  PASS")
    except Exception as e:
        print(f"  FAIL: {e}")

print("\n" + "=" * 60)
print("All tests done.")
