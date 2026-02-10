import requests
import json
import msgpack

# Test different field names
print("Testing different metadata field names...\n")

test_cases = [
    {"id": "test_1", "vector": [0.1] * 384, "metadata": json.dumps({"title": "Test 1"}), "filter": json.dumps({"price": 10})},
    {"id": "test_2", "vector": [0.1] * 384, "data": json.dumps({"title": "Test 2"}), "filter_data": json.dumps({"price": 20})},
    {"id": "test_3", "vector": [0.1] * 384, "meta": {"title": "Test 3"}, "filter": {"price": 30}},  # Try dict directly
    {"id": "test_4", "vector": [0.1] * 384, "metadata": {"title": "Test 4"}, "filter": {"price": 40}},  # Try dict directly
]

for i, test_vector in enumerate(test_cases, 1):
    print(f"Test {i}: {list(test_vector.keys())}")
    r = requests.post('http://localhost:8080/api/v1/index/ecommerce_products/vector/insert', json=[test_vector])
    print(f"  Insert status: {r.status_code}")
    
    # Retrieve
    r2 = requests.post('http://localhost:8080/api/v1/index/ecommerce_products/vector/get', json={"id": test_vector['id']})
    if r2.status_code == 200:
        data = msgpack.unpackb(r2.content, raw=False)
        if isinstance(data, list) and len(data) >= 3:
            print(f"  Retrieved [1] (metadata): {data[1]}")
            print(f"  Retrieved [2] (filter): {data[2]}")
    print()
