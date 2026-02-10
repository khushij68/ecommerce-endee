import requests
import json

# Test vector/get endpoint (should return JSON)
print("Testing vector/get endpoint...")
payload = {'id': 'dj_1'}
r = requests.post('http://localhost:8080/api/v1/index/ecommerce_products/vector/get', json=payload)
print(f'Status: {r.status_code}')
print(f'Content-Type: {r.headers.get("Content-Type")}')
print(f'Response: {r.text[:300]}')
print()

# Test search endpoint
print("Testing search endpoint...")
search_payload = {
    "vector": [0.1] * 384,  # Dummy vector
    "k": 5,
    "include_vectors": False
}
headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
r2 = requests.post('http://localhost:8080/api/v1/index/ecommerce_products/search', json=search_payload, headers=headers)
print(f'Status: {r2.status_code}')
print(f'Content-Type: {r2.headers.get("Content-Type")}')
print(f'Is binary: {r2.headers.get("Content-Type") != "application/json"}')
print(f'Response length: {len(r2.content)} bytes')
print(f'First 100 bytes: {r2.content[:100]}')
