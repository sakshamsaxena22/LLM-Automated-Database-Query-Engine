import requests, json
r = requests.post("http://127.0.0.1:8000/query", json={"query": "Show all failed transactions"}, timeout=30)
print(f"Status: {r.status_code}")
print(f"Body: {json.dumps(r.json(), indent=2)}")
