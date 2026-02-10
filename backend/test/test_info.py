import requests
import msgpack

# Test the info endpoint
print("Testing /info endpoint...")
r = requests.get('http://localhost:8080/api/v1/index/ecommerce_products/info')
print(f'Status: {r.status_code}')
print(f'Content-Type: {r.headers.get("Content-Type")}')

try:
    data = msgpack.unpackb(r.content, raw=False)
    print(f'Decoded successfully!')
    print(f'Type: {type(data)}')
    print(f'Data: {data}')
except Exception as e:
    print(f'Error: {e}')
    print(f'Raw content (first 200 bytes): {r.content[:200]}')
