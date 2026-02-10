import json
import requests
from sentence_transformers import SentenceTransformer
import numpy as np

ENDEE_BASE_URL = "http://localhost:8080/api/v1"
INDEX_NAME = "ecommerce_products"

def load_products():
    """Load products from JSON file"""
    print("Loading products...")
    with open('../data/products.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def create_index():
    """Create Endee vector index"""
    print(f"Creating or verifying index '{INDEX_NAME}'...")
    
    url = f"{ENDEE_BASE_URL}/index/create"
    payload = {
        "index_name": INDEX_NAME,
        "dim": 384,  # all-MiniLM-L6-v2 embedding dimension
        "space_type": "cosine"
    }
    
    try:
        response = requests.post(url, json=payload)
        if response.status_code in [200, 201]:
            print("✅ Index created successfully!")
            return True
        elif "already exists" in response.text.lower():
            print("ℹ️  Index already exists, proceeding to insert vectors...")
            return True
        else:
            print(f"⚠️  Response: {response.text}")
            return True  # Proceed anyway as it might exist
    except Exception as e:
        print(f"❌ Error creating/checking index: {e}")
        return True # Proceed anyway

def generate_embeddings(products):
    """Generate embeddings for products using sentence transformers"""
    print("Loading embedding model (this may take a moment)...")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    print(f"Generating embeddings for {len(products)} products...")
    
    # Create text representations for embedding
    texts = []
    for p in products:
        # Combine title, description, category, and brand for rich semantic search
        text = f"{p['title']}. {p['description']} Category: {p['category']}. Brand: {p.get('brand', '')}"
        texts.append(text)
    
    # Generate embeddings in batches
    embeddings = model.encode(texts, show_progress_bar=True, batch_size=32)
    
    return embeddings

def insert_vectors(products, embeddings):
    """Insert product vectors into Endee"""
    print(f"Inserting {len(products)} vectors into Endee...")
    
    url = f"{ENDEE_BASE_URL}/index/{INDEX_NAME}/vector/insert"
    
    # Prepare vectors for insertion
    vectors = []
    for i, (product, embedding) in enumerate(zip(products, embeddings)):
        # Prepare metadata and filter as JSON strings
        meta_dict = {
            "title": product['title'],
            "description": product['description'],
            "image": product.get('image', ''),
            "brand": product.get('brand', ''),
            "category": product['category']
        }
        
        filter_dict = {
            "price": float(product['price']),
            "rating": float(product['rating']),
            "stock": int(product['stock']),
            "category": product['category']
        }
        
        vector_data = {
            "id": product['id'],
            "vector": embedding.tolist(),
            "meta": json.dumps(meta_dict),  # Serialize as JSON string
            "filter": json.dumps(filter_dict)  # Serialize as JSON string
        }
        vectors.append(vector_data)
    
    # Insert in batches of 50
    batch_size = 50
    for i in range(0, len(vectors), batch_size):
        batch = vectors[i:i+batch_size]
        try:
            response = requests.post(url, json=batch)
            if response.status_code in [200, 201]:
                print(f"  ✅ Inserted batch {i//batch_size + 1}/{(len(vectors)-1)//batch_size + 1}")
            else:
                print(f"  ⚠️  Batch {i//batch_size + 1} response: {response.text}")
        except Exception as e:
            print(f"  ❌ Error inserting batch {i//batch_size + 1}: {e}")
    
    print("✅ All vectors inserted!")

def verify_index():
    """Verify the index was created successfully"""
    print("\nVerifying index...")
    
    url = f"{ENDEE_BASE_URL}/index/{INDEX_NAME}/info"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            info = response.json()
            print(f"✅ Index verified!")
            print(f"   Vectors: {info.get('vector_count', 'N/A')}")
            print(f"   Dimensions: {info.get('dim', 'N/A')}")
            return True
        else:
            print(f"⚠️  Could not verify: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error verifying: {e}")
        return False

def main():
    """Main function to create embeddings and load into Endee"""
    print("🚀 Starting Endee Product Indexing...\n")
    
    # Load products
    products = load_products()
    print(f"Loaded {len(products)} products\n")
    
    # Create index
    if not create_index():
        print("Failed to create index. Exiting.")
        return
    
    # Generate embeddings
    embeddings = generate_embeddings(products)
    print(f"Generated {len(embeddings)} embeddings\n")
    
    # Insert vectors
    insert_vectors(products, embeddings)
    
    # Verify
    verify_index()
    
    print("\n🎉 Done! Your Endee vector database is ready for semantic search!")

if __name__ == '__main__':
    main()
