import requests
import json
import random

import requests
import json
import random

def fetch_platzi_products():
    """Fetch products from Platzi Fake Store API"""
    print("Fetching products from Platzi Fake Store API...")
    try:
        response = requests.get('https://api.escuelajs.co/api/v1/products')
        products = response.json()
        print(f"  Fetched {len(products)} products from Platzi")
        return products
    except Exception as e:
        print(f"  Error fetching from Platzi: {e}")
        return []

def normalize_products(platzi_products):
    """Normalize products to a consistent format"""
    print("Normalizing product data...")
    normalized = []
    
    # Normalize Platzi products
    for p in platzi_products:
        # Platzi sometimes has invalid images or incomplete data
        if not p.get('title') or not p.get('images'):
            continue
            
        # Extract category name
        category = "Product"
        if isinstance(p.get('category'), dict):
            category = p['category'].get('name', 'Product')
        elif isinstance(p.get('category'), str):
            category = p['category']

        # Get first image, cleanup URL if needed
        image_url = p['images'][0]
        # Cleanup common Platzi image glitches (sometimes images are double-quoted or in brackets)
        if isinstance(image_url, str):
            image_url = image_url.replace('["', '').replace('"]', '').replace('"', '')

        normalized.append({
            'id': f'pl_{p["id"]}',
            'title': p['title'],
            'description': p['description'],
            'price': float(p['price']),
            'category': category,
            'rating': round(random.uniform(3.8, 5.0), 1), # Platzi doesn't provide ratings
            'stock': random.randint(5, 100),
            'brand': 'Platzi Collection',
            'image': image_url
        })
    
    return normalized

def main():
    """Main function to fetch and combine all product data"""
    try:
        # Fetch from Platzi API
        platzi_products = fetch_platzi_products()
        
        # Normalize
        all_products = normalize_products(platzi_products)
        
        # Save to JSON file
        output_file = '../data/products.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(all_products, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ Successfully created {len(all_products)} products with valid URLs!")
        print(f"📁 Saved to: {output_file}")
        
        # Print summary
        categories = {}
        for p in all_products:
            cat = p.get('category', 'Unknown')
            categories[cat] = categories.get(cat, 0) + 1
        
        print("\n📊 Product Categories:")
        for cat, count in sorted(categories.items()):
            print(f"  - {cat}: {count} products")
        
        return all_products
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

if __name__ == '__main__':
    main()

if __name__ == '__main__':
    main()
