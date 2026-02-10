from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from sentence_transformers import SentenceTransformer
import json
import msgpack

app = Flask(__name__)
CORS(app)

# Configuration
ENDEE_BASE_URL = "http://localhost:8080/api/v1"
INDEX_NAME = "ecommerce_products"

# Load embedding model once at startup
print("Loading embedding model...")
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
print("Model loaded!")

# Load product data for enrichment (Endee doesn't store metadata)
print("Loading product data...")
PRODUCTS_DB = {}
try:
    with open('../data/products.json', 'r', encoding='utf-8') as f:
        products_list = json.load(f)
        for product in products_list:
            PRODUCTS_DB[product['id']] = product
    print(f"✅ Loaded {len(PRODUCTS_DB)} products into memory")
except Exception as e:
    print(f"⚠️  Warning: Could not load products.json: {e}")
    PRODUCTS_DB = {}

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "service": "E-commerce Discovery API"})

@app.route('/api/search', methods=['POST'])
def semantic_search():
    """
    Semantic search endpoint
    Body: {
        "query": "cozy winter sweater",
        "k": 10,
        "filters": {
            "min_price": 0,
            "max_price": 1000,
            "category": "Fashion",
            "min_rating": 0
        }
    }
    """
    try:
        data = request.json
        query = data.get('query', '')
        k = data.get('k', 10)
        filters = data.get('filters', {})
        
        print(f"\n🔍 Search Request:")
        print(f"  Query: {query}")
        print(f"  K: {k}")
        print(f"  Filters: {filters}")
        
        if not query:
            return jsonify({"error": "Query is required"}), 400
        
        # Generate embedding for query
        print("  Generating embedding...")
        query_embedding = embedding_model.encode(query).tolist()
        print(f"  Embedding generated: {len(query_embedding)} dimensions")
        
        # Build filter conditions for Endee
        # NOTE: Simplified to avoid filter issues - search without filters first
        filter_conditions = []
        
        # Only add category filter if specified and not "All"
        if filters.get('category') and filters['category'] != 'All':
            filter_conditions.append({
                "category": {
                    "$eq": filters['category']
                }
            })
        
        # Search in Endee
        search_payload = {
            "vector": query_embedding,
            "k": k,
            "include_vectors": False
        }
        
        if filter_conditions:
            search_payload["filter"] = filter_conditions
        
        print(f"  Sending to Endee: {ENDEE_BASE_URL}/index/{INDEX_NAME}/search")
        print(f"  Payload keys: {search_payload.keys()}")
        
        # Add headers to ensure JSON response
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        response = requests.post(
            f"{ENDEE_BASE_URL}/index/{INDEX_NAME}/search",
            json=search_payload,
            headers=headers
        )
        
        print(f"  Endee Response Status: {response.status_code}")
        print(f"  Response Text: {response.text[:200] if response.text else 'EMPTY'}")
        
        if response.status_code == 200:
            # Check if response has content
            if not response.text or response.text.strip() == '':
                print("  ⚠️ Endee returned empty response")
                return jsonify({
                    "query": query,
                    "results": [],
                    "count": 0,
                    "warning": "Endee returned empty response - index may be empty or query failed"
                })
            
            try:
                # Decode MessagePack binary response
                results = msgpack.unpackb(response.content, raw=False)
                print(f"  Decoded MessagePack data type: {type(results)}")
            except Exception as decode_error:
                print(f"  ❌ MessagePack Decode Error: {decode_error}")
                print(f"  Raw response (first 200 bytes): {response.content[:200]}")
                return jsonify({
                    "error": f"Failed to decode Endee response: {str(decode_error)}",
                    "raw_response": str(response.content[:500])
                }), 500
            
            print(f"  ✅ Found {len(results)} results")
            print(f"  First result structure: {results[0] if results else 'N/A'}")
            
            # Parse Endee's list-based response format and enrich with product data
            # Each result is a list: [score, id, metadata, filter, ?, vectors]
            parsed_results = []
            for result in results:
                if isinstance(result, list) and len(result) >= 2:
                    score = result[0]
                    product_id = result[1]
                    
                    # Get product data from our database
                    product = PRODUCTS_DB.get(product_id, {})
                    
                    if product:
                        parsed_results.append({
                            'score': score,
                            'id': product_id,
                            'meta': {
                                'title': product.get('title', 'Untitled Product'),
                                'description': product.get('description', 'No description available'),
                                'image': product.get('image', ''),
                                'brand': product.get('brand', ''),
                                'category': product.get('category', 'Product')
                            },
                            'filter': {
                                'price': float(product.get('price', 0)),
                                'rating': float(product.get('rating', 0)),
                                'stock': int(product.get('stock', 0)),
                                'category': product.get('category', 'Product')
                            }
                        })
            
            print(f"  Enriched {len(parsed_results)} results with product data")
            
            # Apply client-side filtering for price and rating
            min_price = filters.get('min_price', 0)
            max_price = filters.get('max_price', 10000)
            min_rating = filters.get('min_rating', 0)
            
            filtered_results = []
            for result in parsed_results:
                filter_data = result.get('filter', {})
                price = filter_data.get('price', 0)
                rating = filter_data.get('rating', 0)
                
                if min_price <= price <= max_price and rating >= min_rating:
                    filtered_results.append(result)
            
            print(f"  After client-side filtering: {len(filtered_results)} results")
            
            return jsonify({
                "query": query,
                "results": filtered_results,
                "count": len(filtered_results)
            })
        else:
            error_msg = f"Endee search failed: {response.text}"
            print(f"  ❌ Error: {error_msg}")
            return jsonify({"error": error_msg}), 500
            
    except Exception as e:
        error_msg = str(e)
        print(f"  ❌ Exception: {error_msg}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": error_msg}), 500

@app.route('/api/similar/<product_id>', methods=['GET'])
def find_similar(product_id):
    """
    Find similar products to a given product
    """
    try:
        k = request.args.get('k', 5, type=int)
        
        # Get the product vector from Endee
        get_payload = {"id": product_id}
        response = requests.post(
            f"{ENDEE_BASE_URL}/index/{INDEX_NAME}/vector/get",
            json=get_payload
        )
        
        if response.status_code != 200:
            return jsonify({"error": "Product not found"}), 404
        
        # Decode MessagePack response
        # vector/get returns a list: [id, metadata, filter, vector, ?]
        product_data = msgpack.unpackb(response.content, raw=False)
        
        if isinstance(product_data, list) and len(product_data) >= 4:
            product_vector = product_data[3]  # Vector is at index 3
        else:
            return jsonify({"error": "Invalid product data format"}), 500
        
        if not product_vector:
            return jsonify({"error": "Product vector not found"}), 404
        
        # Search for similar products
        search_payload = {
            "vector": product_vector,
            "k": k + 1,  # +1 to exclude the product itself
            "include_vectors": False
        }
        
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        search_response = requests.post(
            f"{ENDEE_BASE_URL}/index/{INDEX_NAME}/search",
            json=search_payload,
            headers=headers
        )
        
        if search_response.status_code == 200:
            # Decode MessagePack response
            results = msgpack.unpackb(search_response.content, raw=False)
            
            # Parse list-based results and enrich with product data
            parsed_results = []
            for result in results:
                if isinstance(result, list) and len(result) >= 2:
                    score = result[0]
                    result_id = result[1]
                    
                    # Get product data from our database
                    product = PRODUCTS_DB.get(result_id, {})
                    
                    if product:
                        parsed_results.append({
                            'score': score,
                            'id': result_id,
                            'meta': {
                                'title': product.get('title', 'Untitled Product'),
                                'description': product.get('description', 'No description available'),
                                'image': product.get('image', ''),
                                'brand': product.get('brand', ''),
                                'category': product.get('category', 'Product')
                            },
                            'filter': {
                                'price': float(product.get('price', 0)),
                                'rating': float(product.get('rating', 0)),
                                'stock': int(product.get('stock', 0)),
                                'category': product.get('category', 'Product')
                            }
                        })
            
            # Filter out the original product
            similar_products = [r for r in parsed_results if r.get('id') != product_id][:k]
            
            return jsonify({
                "product_id": product_id,
                "similar_products": similar_products,
                "count": len(similar_products)
            })
        else:
            return jsonify({"error": "Search failed"}), 500
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/categories', methods=['GET'])
def get_categories():
    """Get all unique categories"""
    # For now, return hardcoded categories
    # In production, you might want to query Endee or maintain a separate list
    categories = [
        "All",
        "Electronics",
        "Fashion", 
        "Home",
        "Sports",
        "Books",
        "beauty",
        "fragrances",
        "furniture",
        "groceries",
        "home-decoration",
        "kitchen-accessories",
        "laptops",
        "mens-shirts",
        "mens-shoes",
        "mens-watches",
        "mobile-accessories",
        "motorcycle",
        "skin-care",
        "smartphones",
        "sports-accessories",
        "sunglasses",
        "tablets",
        "tops",
        "vehicle",
        "womens-bags",
        "womens-dresses",
        "womens-jewellery",
        "womens-shoes",
        "womens-watches",
        "jewelery",
        "men's clothing",
        "women's clothing",
        "electronics"
    ]
    return jsonify({"categories": sorted(set(categories))})

@app.route('/api/product/<product_id>', methods=['GET'])
def get_product(product_id):
    """Get product details by ID"""
    try:
        # Get product from our database
        product = PRODUCTS_DB.get(product_id)
        
        if product:
            return jsonify({
                'id': product_id,
                'meta': {
                    'title': product.get('title', 'Untitled Product'),
                    'description': product.get('description', 'No description available'),
                    'image': product.get('image', ''),
                    'brand': product.get('brand', ''),
                    'category': product.get('category', 'Product')
                },
                'filter': {
                    'price': float(product.get('price', 0)),
                    'rating': float(product.get('rating', 0)),
                    'stock': int(product.get('stock', 0)),
                    'category': product.get('category', 'Product')
                }
            })
        else:
            return jsonify({"error": "Product not found"}), 404
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get index statistics"""
    try:
        # Return stats from our product database
        return jsonify({
            "vector_count": len(PRODUCTS_DB),
            "total_elements": len(PRODUCTS_DB),
            "dim": 384,
            "space_type": "cosine"
        })
    except Exception as e:
        return jsonify({"error": str(e), "vector_count": len(PRODUCTS_DB)}), 200

if __name__ == '__main__':
    print("🚀 Starting E-commerce Discovery API...")
    print(f"📊 Endee URL: {ENDEE_BASE_URL}")
    print(f"📦 Index: {INDEX_NAME}")
    print("🌐 Server running on http://localhost:5000")
    app.run(debug=True, port=5000)
