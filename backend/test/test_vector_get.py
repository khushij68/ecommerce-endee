import requests
import msgpack

# Test vector/get endpoint
print("Testing vector/get endpoint...")
get_payload = {"id": "dj_1"}
r = requests.post('http://localhost:8080/api/v1/index/ecommerce_products/vector/get', json=get_payload)
print(f'Status: {r.status_code}')

if r.status_code == 200:
    data = msgpack.unpackb(r.content, raw=False)
    print(f'Type: {type(data)}')
    print(f'Data: {data}')
    
    if isinstance(data, list):
        print(f'\nList length: {len(data)}')
        for i, item in enumerate(data):
            print(f'  [{i}]: {type(item)} - {item if not isinstance(item, list) else f"list of {len(item)} items"}')
    elif isinstance(data, dict):
        print(f'\nDict keys: {data.keys()}')
else:
    print(f'Error: {r.text}')
