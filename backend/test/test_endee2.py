import requests
import json

# Try different endpoint variations
base_url = "http://localhost:8080/api/v1"
index_name = "ecommerce_products"

# Test 1: Try with format parameter
print("Test 1: Search with ?format=json parameter...")
search_payload = {
    "vector": [0.1] * 384,
    "k": 3,
    "include_vectors": False
}
r = requests.post(f'{base_url}/index/{index_name}/search?format=json', json=search_payload)
print(f'  Status: {r.status_code}')
print(f'  Content-Type: {r.headers.get("Content-Type")}')
print(f'  First 200 chars: {r.text[:200] if r.status_code == 200 else "N/A"}')
print()

# Test 2: Try GET method
print("Test 2: Try GET on /health...")
r2 = requests.get(f'{base_url}/health')
print(f'  Status: {r2.status_code}')
print(f'  Response: {r2.text}')
print()

# Test 3: Check if there's an API docs endpoint
print("Test 3: Try /api/v1/docs or /api/v1...")
r3 = requests.get(f'{base_url}/')
print(f'  Status: {r3.status_code}')
print(f'  Response: {r3.text[:200]}')
