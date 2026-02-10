import requests
import json

# Test inserting a single vector with metadata
print("Testing vector insertion with metadata...")

test_vector = {
    "id": "test_product_123",
    "vector": [0.1] * 384,
    "meta": json.dumps({"title": "Test Product", "description": "Test Description"}),
    "filter": json.dumps({"price": 99.99, "category": "test"})
}

print(f"Inserting test vector...")
print(f"Payload: {json.dumps(test_vector, indent=2)[:500]}")

r = requests.post('http://localhost:8080/api/v1/index/ecommerce_products/vector/insert', json=[test_vector])
print(f"\nInsert Response Status: {r.status_code}")
print(f"Insert Response: {r.text}")

# Now try to retrieve it
print(f"\n\nRetrieving test vector...")
r2 = requests.post('http://localhost:8080/api/v1/index/ecommerce_products/vector/get', json={"id": "test_product_123"})
print(f"Get Response Status: {r2.status_code}")

if r2.status_code == 200:
    import msgpack
    data = msgpack.unpackb(r2.content, raw=False)
    print(f"Retrieved data type: {type(data)}")
    print(f"Retrieved data: {data}")
    
    if isinstance(data, list):
        print(f"\nList structure:")
        for i, item in enumerate(data):
            print(f"  [{i}]: {type(item)} = {item if not isinstance(item, (list, bytes)) or len(str(item)) < 100 else f'{type(item)} (length {len(item)})'}")
