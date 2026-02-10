const API_BASE_URL = 'http://localhost:5000/api';

// State
let currentQuery = '';
let currentFilters = {
    category: 'All',
    min_price: 0,
    max_price: 1000,
    min_rating: 0
};
let currentResults = [];

// DOM Elements
const searchInput = document.getElementById('searchInput');
const searchBtn = document.getElementById('searchBtn');
const quickChips = document.querySelectorAll('.quick-chip');
const filtersSection = document.getElementById('filtersSection');
const resultsSection = document.getElementById('resultsSection');
const resultsGrid = document.getElementById('resultsGrid');
const loadingSpinner = document.getElementById('loadingSpinner');
const noResults = document.getElementById('noResults');
const categoryFilter = document.getElementById('categoryFilter');
const minPriceInput = document.getElementById('minPrice');
const maxPriceInput = document.getElementById('maxPrice');
const ratingFilter = document.getElementById('ratingFilter');
const resultsCount = document.getElementById('resultsCount');
const applyFiltersBtn = document.getElementById('applyFilters');
const productModal = document.getElementById('productModal');
const closeModal = document.getElementById('closeModal');
const modalBody = document.getElementById('modalBody');

// Assets
const fallbackImage = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="400" height="400"%3E%3Cdefs%3E%3ClinearGradient id="grad" x1="0%25" y1="0%25" x2="100%25" y2="100%25"%3E%3Cstop offset="0%25" style="stop-color:%23667eea;stop-opacity:1" /%3E%3Cstop offset="100%25" style="stop-color:%23764ba2;stop-opacity:1" /%3E%3C/linearGradient%3E%3C/defs%3E%3Crect width="400" height="400" fill="url(%23grad)"/%3E%3Ctext x="50%25" y="50%25" font-family="Arial" font-size="80" fill="white" text-anchor="middle" dy=".3em"%3E📦%3C/text%3E%3C/svg%3E';

// Initialize
async function init() {
    await loadStats();
    await loadCategories();
    setupEventListeners();
}

// Load stats
async function loadStats() {
    try {
        const response = await fetch(`${API_BASE_URL}/stats`);
        if (response.ok) {
            const data = await response.json();
            document.getElementById('productCount').textContent = data.vector_count || '---';
        }
    } catch (error) {
        console.error('Error loading stats:', error);
    }
}

// Load categories
async function loadCategories() {
    try {
        const response = await fetch(`${API_BASE_URL}/categories`);
        if (response.ok) {
            const data = await response.json();
            const categories = data.categories || [];

            categoryFilter.innerHTML = '<option value="All">All Categories</option>';
            categories.forEach(cat => {
                if (cat !== 'All') {
                    const option = document.createElement('option');
                    option.value = cat;
                    option.textContent = cat.charAt(0).toUpperCase() + cat.slice(1);
                    categoryFilter.appendChild(option);
                }
            });
        }
    } catch (error) {
        console.error('Error loading categories:', error);
    }
}

// Setup event listeners
function setupEventListeners() {
    searchBtn.addEventListener('click', handleSearch);
    searchInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') handleSearch();
    });

    quickChips.forEach(chip => {
        chip.addEventListener('click', () => {
            searchInput.value = chip.dataset.query;
            handleSearch();
        });
    });

    applyFiltersBtn.addEventListener('click', applyFilters);

    closeModal.addEventListener('click', () => {
        productModal.style.display = 'none';
    });

    productModal.querySelector('.modal-overlay').addEventListener('click', () => {
        productModal.style.display = 'none';
    });
}

// Handle search
async function handleSearch() {
    const query = searchInput.value.trim();

    if (!query) {
        alert('Please enter a search query');
        return;
    }

    currentQuery = query;

    // Show sections
    filtersSection.style.display = 'block';
    resultsSection.style.display = 'block';
    loadingSpinner.style.display = 'block';
    resultsGrid.innerHTML = '';
    noResults.style.display = 'none';

    // Update filters from inputs
    currentFilters = {
        category: categoryFilter.value,
        min_price: parseFloat(minPriceInput.value) || 0,
        max_price: parseFloat(maxPriceInput.value) || 10000,
        min_rating: parseFloat(ratingFilter.value) || 0
    };

    const k = parseInt(resultsCount.value) || 10;

    try {
        const response = await fetch(`${API_BASE_URL}/search`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                query: query,
                k: k,
                filters: currentFilters
            })
        });

        if (response.ok) {
            const data = await response.json();
            currentResults = data.results || [];
            displayResults(currentResults, query);
        } else {
            throw new Error('Search failed');
        }
    } catch (error) {
        console.error('Search error:', error);
        alert('Search failed. Please make sure the backend server is running.');
    } finally {
        loadingSpinner.style.display = 'none';
    }
}

// Apply filters
function applyFilters() {
    if (currentQuery) {
        handleSearch();
    }
}

// Display results
function displayResults(results, query) {
    resultsGrid.innerHTML = '';

    document.getElementById('resultsTitle').textContent = `Results for "${query}"`;
    document.getElementById('resultsSubtitle').textContent = `Found ${results.length} products`;

    if (results.length === 0) {
        noResults.style.display = 'block';
        return;
    }

    results.forEach((result, index) => {
        const card = createProductCard(result, index);
        resultsGrid.appendChild(card);
    });
}

// Create product card
function createProductCard(result, index) {
    const card = document.createElement('div');
    card.className = 'product-card';
    card.style.animationDelay = `${index * 0.05}s`;

    const meta = result.meta || {};
    const filter = result.filter || {};
    const score = result.score || 0;

    // Filter out via.placeholder.com URLs
    let imageUrl = meta.image || fallbackImage;
    if (imageUrl && imageUrl.includes('via.placeholder.com')) {
        imageUrl = fallbackImage;
    }

    card.innerHTML = `
        <img 
            src="${imageUrl}" 
            alt="${meta.title || 'Product'}"
            class="product-image"
            onerror="this.src='${fallbackImage}'"
        />
        <div class="product-content">
            ${score > 0 ? `<div class="similarity-score">${(score * 100).toFixed(1)}% match</div>` : ''}
            <div class="product-category">${filter.category || 'Product'}</div>
            <h3 class="product-title">${meta.title || 'Untitled Product'}</h3>
            <p class="product-description">${meta.description || 'No description available'}</p>
            <div class="product-footer">
                <div class="product-price">$${filter.price?.toFixed(2) || '0.00'}</div>
                <div class="product-rating">
                    ⭐ ${filter.rating?.toFixed(1) || 'N/A'}
                </div>
            </div>
        </div>
    `;

    card.addEventListener('click', () => showProductModal(result));

    return card;
}

// Show product modal
async function showProductModal(product) {
    const meta = product.meta || {};
    const filter = product.filter || {};

    // Get similar products
    let similarProducts = [];
    try {
        const response = await fetch(`${API_BASE_URL}/similar/${product.id}?k=4`);
        if (response.ok) {
            const data = await response.json();
            similarProducts = data.similar_products || [];
        }
    } catch (error) {
        console.error('Error fetching similar products:', error);
    }

    modalBody.innerHTML = `
        <div style="padding: 2rem;">
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 2rem; margin-bottom: 2rem;">
                <div>
                    <img 
                        src="${meta.image || fallbackImage}" 
                        alt="${meta.title}"
                        style="width: 100%; border-radius: 12px; background: white; padding: 2rem; box-sizing: border-box; object-fit: contain; max-height: 400px;"
                        onerror="this.src='${fallbackImage}'"
                    />
                </div>
                <div>
                    <div style="font-size: 0.875rem; color: var(--primary); text-transform: uppercase; font-weight: 600; margin-bottom: 0.5rem;">
                        ${filter.category || 'Product'}
                    </div>
                    <h2 style="font-size: 2rem; margin-bottom: 1rem;">${meta.title || 'Untitled'}</h2>
                    <p style="color: var(--text-secondary); margin-bottom: 1.5rem; line-height: 1.8;">
                        ${meta.description || 'No description available'}
                    </p>
                    
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-bottom: 1.5rem;">
                        <div style="background: var(--bg-tertiary); padding: 1rem; border-radius: 8px;">
                            <div style="font-size: 0.75rem; color: var(--text-muted); margin-bottom: 0.25rem;">Price</div>
                            <div style="font-size: 1.75rem; font-weight: 700; background: var(--gradient-primary); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
                                $${filter.price?.toFixed(2) || '0.00'}
                            </div>
                        </div>
                        <div style="background: var(--bg-tertiary); padding: 1rem; border-radius: 8px;">
                            <div style="font-size: 0.75rem; color: var(--text-muted); margin-bottom: 0.25rem;">Rating</div>
                            <div style="font-size: 1.75rem; font-weight: 700; color: var(--warning);">
                                ⭐ ${filter.rating?.toFixed(1) || 'N/A'}
                            </div>
                        </div>
                    </div>
                    
                    ${meta.brand ? `
                        <div style="margin-bottom: 1rem;">
                            <span style="color: var(--text-muted);">Brand:</span>
                            <span style="color: var(--text-primary); font-weight: 600; margin-left: 0.5rem;">${meta.brand}</span>
                        </div>
                    ` : ''}
                    
                    <div style="margin-bottom: 1rem;">
                        <span style="color: var(--text-muted);">Stock:</span>
                        <span style="color: ${filter.stock > 0 ? 'var(--success)' : 'var(--error)'}; font-weight: 600; margin-left: 0.5rem;">
                            ${filter.stock > 0 ? `${filter.stock} available` : 'Out of stock'}
                        </span>
                    </div>
                </div>
            </div>
            
            ${similarProducts.length > 0 ? `
                <div style="border-top: 1px solid var(--border); padding-top: 2rem;">
                    <h3 style="font-size: 1.5rem; margin-bottom: 1.5rem;">Similar Products</h3>
                    <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 1rem;">
                        ${similarProducts.map(similar => {
        const sMeta = similar.meta || {};
        const sFilter = similar.filter || {};
        const sId = similar.id;
        // Stringify metadata to pass back to showProductModal if needed, 
        // or better yet, fetch full details by ID. 
        // For simplicity, we just pass the object.
        return `
                                <div class="similar-card" style="background: var(--bg-tertiary); border-radius: 8px; overflow: hidden; cursor: pointer; transition: transform 0.2s;" data-id="${sId}">
                                    <img 
                                        src="${sMeta.image || fallbackImage}" 
                                        alt="${sMeta.title}"
                                        style="width: 100%; height: 150px; object-fit: contain; background: white; padding: 0.5rem; box-sizing: border-box;"
                                        onerror="this.src='${fallbackImage}'"
                                    />
                                    <div style="padding: 1rem;">
                                        <div style="font-size: 0.875rem; font-weight: 600; margin-bottom: 0.5rem; color: var(--text-primary); white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">
                                            ${sMeta.title || 'Product'}
                                        </div>
                                        <div style="display: flex; justify-content: space-between; align-items: center;">
                                            <span style="font-weight: 700; color: var(--primary);">$${sFilter.price?.toFixed(2) || '0.00'}</span>
                                            <span style="font-size: 0.875rem; color: var(--warning);">⭐ ${sFilter.rating?.toFixed(1) || 'N/A'}</span>
                                        </div>
                                    </div>
                                </div>
                            `;
    }).join('')}
                    </div>
                </div>
            ` : ''}
        </div>
    `;

    // Add event listeners for similar products
    const similarCards = modalBody.querySelectorAll('.similar-card');
    similarCards.forEach((card, i) => {
        card.addEventListener('click', () => {
            showProductModal(similarProducts[i]);
            modalBody.scrollTop = 0;
        });

        card.addEventListener('mouseenter', () => card.style.transform = 'translateY(-4px)');
        card.addEventListener('mouseleave', () => card.style.transform = 'translateY(0)');
    });

    productModal.style.display = 'flex';
}

// Initialize app
init();
