import requests
import msgpack
import json

# Test to see what metadata actually looks like
print("Testing search response structure...")
search_payload = {
    "vector": [0.1] * 384,
    "k": 2,
    "include_vectors": False
}

r = requests.post('http://localhost:8080/api/v1/index/ecommerce_products/search', json=search_payload)
data = msgpack.unpackb(r.content, raw=False)

print(f"\nNumber of results: {len(data)}")
print(f"\nFirst result:")
result = data[0]
print(f"  Type: {type(result)}")
print(f"  Length: {len(result)}")
print(f"  [0] score: {result[0]}")
print(f"  [1] id: {result[1]}")
print(f"  [2] metadata type: {type(result[2])}")
print(f"  [2] metadata value: {result[2]}")
print(f"  [2] metadata (first 200 chars): {str(result[2])[:200]}")

# Try to decode metadata
if result[2]:
    try:
        if isinstance(result[2], bytes):
            metadata_str = result[2].decode('utf-8')
            print(f"\n  Decoded as string: {metadata_str[:200]}")
            metadata_dict = json.loads(metadata_str)
            print(f"  Parsed as JSON: {metadata_dict}")
        elif isinstance(result[2], str):
            metadata_dict = json.loads(result[2])
            print(f"  Parsed as JSON: {metadata_dict}")
    except Exception as e:
        print(f"  Error parsing: {e}")

print(f"\n  [3] filter type: {type(result[3])}")
print(f"  [3] filter value: {result[3]}")
print(f"  [3] filter (first 200 chars): {str(result[3])[:200]}")

# Try to decode filter
if result[3]:
    try:
        if isinstance(result[3], bytes):
            filter_str = result[3].decode('utf-8')
            print(f"\n  Decoded as string: {filter_str[:200]}")
            filter_dict = json.loads(filter_str)
            print(f"  Parsed as JSON: {filter_dict}")
        elif isinstance(result[3], str):
            filter_dict = json.loads(result[3])
            print(f"  Parsed as JSON: {filter_dict}")
    except Exception as e:
        print(f"  Error parsing: {e}")
