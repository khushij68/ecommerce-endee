import requests

# Try to decode the binary response
print("Testing binary decode...")
search_payload = {
    "vector": [0.1] * 384,
    "k": 5,
    "include_vectors": False
}

r = requests.post('http://localhost:8080/api/v1/index/ecommerce_products/search', json=search_payload)
print(f'Status: {r.status_code}')
print(f'Content length: {len(r.content)} bytes')
print(f'Raw bytes (first 200): {r.content[:200]}')
print()

# Try msgpack
try:
    import msgpack
    print("Trying MessagePack decode...")
    data = msgpack.unpackb(r.content, raw=False)
    print(f'Success! Data type: {type(data)}')
    print(f'Data: {data}')
except ImportError:
    print("msgpack not installed, trying to install...")
    import subprocess
    subprocess.run(['pip', 'install', '--user', 'msgpack'])
    import msgpack
    data = msgpack.unpackb(r.content, raw=False)
    print(f'Success! Data type: {type(data)}')
    print(f'Data: {data}')
except Exception as e:
    print(f'MessagePack failed: {e}')
    print()
    
    # Try protobuf or just analyze the bytes
    print("Analyzing byte patterns...")
    content = r.content
    # Look for readable strings
    readable = ''.join(chr(b) if 32 <= b < 127 else '.' for b in content[:500])
    print(f'Readable chars: {readable}')
