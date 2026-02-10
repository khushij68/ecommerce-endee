# 🛒 E-commerce Product Discovery with Endee

A high-performance semantic search-powered e-commerce application. This project demonstrates how to use the **Endee Vector Database** to build a modern discovery experience where users can find products based on meaning, not just keywords.

---

## 🌟 Key Features
- **Semantic Search**: Understands intent (e.g., search "winter vibes" to find sweaters and boots).
- **Enriched Dataset**: 320 products with high-quality image mappings.
- **Similar Products**: Real-time vector similarity recommendations.
- **Smart Filtering**: Multi-stage filtering by price, category, and rating.
- **Modern UI**: A premium dark-themed experience with micro-animations.

---

## 🧠 How it Works: Semantic Search & RAG

This application leverages **Retrieval-Augmented Generation (RAG)** principles to provide a superior product discovery experience.

### 1. Vector Embeddings (The "Brain")
We use the `all-MiniLM-L6-v2` model to convert product titles and descriptions into high-dimensional vectors (384 dimensions). This captures the **semantic meaning** of the text.
*   *Example*: "Running shoes" and "Athletic footwear" result in similar vectors because they share the same meaning, even if they share no common keywords.

### 2. Endee Vector Database (The "Retrieval")
All product vectors are stored in **Endee**. When a user types a query:
1.  The query is converted into a vector using the same model.
2.  Endee performs a **Cosine Similarity Search** to find the nearest vectors.
3.  Endee returns the IDs of the products that most closely match the *intent* of the query.

### 3. Discovery-Driven RAG
Unlike traditional search that looks for exact character matches, this architecture retrieves relevant products as "context" for the user interface.
*   **Similar Products**: When viewing a product, we use its stored vector to query Endee: *"What else is like this?"* This creates a seamless discovery loop.
*   **Metadata Enrichment**: Endee handles the heavy lifting of spatial mathematics, allowing the backend to focus on enriching those results with structured metadata (price, images, brand) for the final UI presentation.

---

## 🏗️ Tech Stack
- **Vector DB**: [Endee](https://github.com/endee-io/endee) (384D Cosine Similarity)
- **Backend**: Python (Flask, Sentence-Transformers, NumPy)
- **Frontend**: Vanilla JS (Modern CSS/HTML5)
- **Model**: `all-MiniLM-L6-v2` (Lightweight and accurate)

---

## ⚙️ Setup Instructions

### 1. Endee Setup (High-Performance Vector DB)
Endee (nD) is a specialized, high-performance vector database built for speed and efficiency.

#### Supported Platforms
- **Linux**: Ubuntu (22.04+), Debian (12+), Rocky, CentOS, Fedora.
- **macOS**: Apple Silicon (M Series) only.
- **Dependencies**: `clang-19`, `cmake`, `build-essential`, `libssl-dev`, `libcurl4-openssl-dev`.

#### Choose Your Building Method:

**A. Quick Installation (Recommended)**
```bash
chmod +x ./install.sh
./install.sh --release --avx2  # For Intel/AMD
# OR 
./install.sh --release --neon  # For Apple Silicon
```

**B. Running with Docker (Easiest)**
```bash
# Run from Docker Hub
docker run -p 8080:8080 -v endee-data:/data --name endee-server endeeio/endee-server:latest
```

**C. Manual Build (Advanced)**
```bash
mkdir build && cd build
cmake -DCMAKE_BUILD_TYPE=Release -DUSE_AVX2=ON ..
make -j$(nproc)
```

#### Running the Server
Use the helper script to start Endee:
```bash
chmod +x ./run.sh
./run.sh ndd_data_dir=./data
```

For detailed build flags and optimization options (AVX512, SVE2, etc.), refer to the [official Endee documentation](https://docs.endee.io).

### 2. Python Environment
```bash
cd backend
pip install -r requirements.txt
```

### 3. Start the Frontend
```bash
cd frontend
python serve_frontend.py
```
Then visit **http://localhost:3000** in your browser.

---

## 🚀 Running the Application(Backend)

There are two ways to initialize the data depending on whether you want to fetch fresh data or use the optimized local dataset.

### 4. Flow A: Full Data Pipeline (Fresh Pull) 
Use this if you want to pull data from APIs and run the full enrichment script. Delete data/products.json before running this.
1. **Fetch**: `python fetch_products.py` (Downloads from DummyJSON/FakeStore).
2. **Fix & Ingest**: `python fix_product_links.py` (Maps synthetic categories to high-quality images).
3. **Index**: `python create_embeddings.py` (Generates vectors and pushes to Endee).
4. **Run**: `python app.py`

### 4. Flow B: Optimized Local Dataset (Fast Start)
Use this if you already have `data/products.json` and want to skip external API calls.
1. **Index**: `python create_embeddings.py` (Reads directly from `data/products.json` and ingests to Endee).
2. **Run**: `python app.py`

*Note: Once ingested, you only need to run `python app.py` for future sessions.*

### 5. Access frontend for the app
Visit **http://localhost:3000** in your browser.

---

## 🖼️ Image Generation Logic
In the large 320-product dataset, many products are **synthetic** (generated to provide search variety). Since synthetic products don't have real-world URLs, we use a **Keyword-Based Unsplash Generator**.

- **How it works**: When a product is indexed, our pipeline scans the title for keywords like `Jeans`, `Hoodie`, or `Laptop`.
- **Mapping**: Based on the match, we assign a verified high-resolution Unsplash ID.
- **Why?**: This ensures the UI stays beautiful and professional without broken placeholder images.
- **Note**: Some images might feel slightly generic as they are high-quality stock photography representing the product category.

---

## 🧹 Cleanup Recommendations
Before pushing to GitHub, you may want to delete the following temporary scripts and test files:
- `backend/fix_product_links.py` (One-time utility)
- `backend/test_*.py` (Assorted internal tests)
- `data/products copy.json` (Backup artifact)
- `data/provided_products.json` (Backup artifact)

---

## 📁 Project Structure
```text
.
├── backend/
│   ├── app.py              # Main API Server
│   ├── create_embeddings.py # Vector Enrichment & Ingestion
│   ├── fetch_products.py   # API Data Fetcher
│   └── start.bat           # Quickstart script
├── data/
│   └── products.json       # Production Dataset
└── frontend/
    ├── index.html          # Discovery UI
    ├── style.css           # Premium Aesthetics
    └── app.js              # Vector Search Logic
```

Developed with ❤️ using **Endee Vector Database**.

