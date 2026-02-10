import requests
import msgpack

# Test to see the actual structure
print("Testing MessagePack structure...")
search_payload = {
    "vector": [0.1] * 384,
    "k": 3,
    "include_vectors": False
}

r = requests.post('http://localhost:8080/api/v1/index/ecommerce_products/search', json=search_payload)
data = msgpack.unpackb(r.content, raw=False)

print(f"Type: {type(data)}")
print(f"Length: {len(data)}")
print(f"\nFirst result:")
print(f"  Type: {type(data[0])}")
print(f"  Value: {data[0]}")
print(f"\nAll results:")
for i, item in enumerate(data):
    print(f"{i}: {item}")
