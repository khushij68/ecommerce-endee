import requests
import json

# Test if backend has product data loaded
print("Testing backend...")

# Test stats endpoint
print("\n1. Testing /api/stats:")
try:
    r = requests.get('http://localhost:5000/api/stats')
    print(f"Status: {r.status_code}")
    print(f"Response: {r.json()}")
except Exception as e:
    print(f"Error: {e}")

# Test search endpoint
print("\n2. Testing /api/search:")
try:
    r = requests.post('http://localhost:5000/api/search', 
                     json={"query": "shoes", "k": 2})
    print(f"Status: {r.status_code}")
    data = r.json()
    print(f"Results count: {len(data.get('results', []))}")
    if data.get('results'):
        first_result = data['results'][0]
        print(f"\nFirst result:")
        print(f"  ID: {first_result.get('id')}")
        print(f"  Title: {first_result.get('meta', {}).get('title')}")
        print(f"  Image: {first_result.get('meta', {}).get('image', 'NO IMAGE')[:80]}")
        print(f"  Price: ${first_result.get('filter', {}).get('price')}")
except Exception as e:
    print(f"Error: {e}")
