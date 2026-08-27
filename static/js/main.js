// document.getElementById('triggerBtn').addEventListener('click', async () => {
//       const output = document.getElementById('output');
//       output.innerText = "Running...";

//       try {
//         const res = await fetch('http://127.0.0.1:8000/api/action', {
//           method: 'POST',
//           headers: { 'Content-Type': 'application/json' },
//           body: JSON.stringify({ action: 'start_process', user_id: 42 })
//         });

//         const data = await res.json();
//         output.innerText = data.message;
//       } catch (err) {
//         output.innerText = `Error: ${err.message}`;
//       }
//     })
/**
 * API Service helper for backend communication
 */
const API = {
  // 1. Fetch Marketplace Trends (/api/marketplace/trends)
  async getTrends() {
    try {
      const response = await fetch('/api/marketplace/trends');
      if (!response.ok) throw new Error('Failed to load trends');
      return await response.json();
    } catch (error) {
      console.error('API Error (getTrends):', error);
      return null;
    }
  },

  // 2. Search items in marketplace (/marketplace/search?q=...&category=...)
  async searchMarketplace(query = '', category = '') {
    try {
      const params = new URLSearchParams();
      if (query) params.append('q', query);
      if (category) params.append('category', category);

      const response = await fetch(`/marketplace/search?${params.toString()}`);
      if (!response.ok) throw new Error('Search failed');
      return await response.json();
    } catch (error) {
      console.error('API Error (searchMarketplace):', error);
      return [];
    }
  },

  // 3. Add Sell/Rent Listing (/sell-rent/add)
  async addListing(listingData) {
    try {
      const response = await fetch('/sell-rent/add', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(listingData),
      });

      const result = await response.json();
      return { ok: response.ok, data: result };
    } catch (error) {
      console.error('API Error (addListing):', error);
      return { ok: false, error: error.message };
    }
  },

  // 4. Test Backend Health (/api/test)
  async checkBackendHealth() {
    try {
      const response = await fetch('/api/test');
      return await response.json();
    } catch (error) {
      console.error('Backend unreachable:', error);
      return null;
    }
  }
};

// ==========================================
// DOM Event Handlers & Page Controller
// ==========================================
document.addEventListener('DOMContentLoaded', () => {

  // --- A. SELL / RENT FORM HANDLER ---
  const sellForm = document.getElementById('sell-rent-form');
  if (sellForm) {
    sellForm.addEventListener('submit', async (event) => {
      event.preventDefault();

      const submitBtn = sellForm.querySelector('button[type="submit"]');
      if (submitBtn) submitBtn.disabled = true;

      const payload = {
        seller_id: document.getElementById('seller-id')?.value || 1,
        title: document.getElementById('item-title')?.value.trim(),
        category: document.getElementById('item-category')?.value,
        listing_type: document.getElementById('listing-type')?.value, // 'sell' or 'rent'
        price: parseFloat(document.getElementById('item-price')?.value || 0),
      };

      const result = await API.addListing(payload);

      if (submitBtn) submitBtn.disabled = false;

      const statusBox = document.getElementById('form-status');
      if (result.ok) {
        if (statusBox) statusBox.innerText = `Item listed successfully! ID: ${result.data.Item_id}`;
        sellForm.reset();
      } else {
        if (statusBox) statusBox.innerText = 'Failed to submit listing. Please try again.';
      }
    });
  }

  // --- B. LIVE SEARCH & FILTER (Marketplace Page) ---
  const searchInput = document.getElementById('search-input');
  const categoryFilter = document.getElementById('category-filter');
  const productContainer = document.getElementById('product-list');

  let debounceTimer;
  function handleSearchTrigger() {
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(async () => {
      const query = searchInput ? searchInput.value.trim() : '';
      const category = categoryFilter ? categoryFilter.value : '';

      const items = await API.searchMarketplace(query, category);
      renderProductList(items, productContainer);
    }, 300); // 300ms debounce
  }

  if (searchInput) searchInput.addEventListener('input', handleSearchTrigger);
  if (categoryFilter) categoryFilter.addEventListener('change', handleSearchTrigger);

  // --- C. AUTO-LOAD TRENDS (If widget container exists) ---
  const trendsContainer = document.getElementById('trends-container');
  if (trendsContainer) {
    API.getTrends().then((trends) => {
      if (trends) {
        trendsContainer.innerHTML = Array.isArray(trends)
          ? trends.map(t => `<span class="trend-tag">${t}</span>`).join('')
          : `<pre>${JSON.stringify(trends, null, 2)}</pre>`;
      }
    });
  }
});

/**
 * Render items dynamically into the DOM
 */
function renderProductList(items, container) {
  if (!container) return;

  if (!items || items.length === 0) {
    container.innerHTML = '<p class="no-results">No products found.</p>';
    return;
  }

  container.innerHTML = items.map(item => `
    <div class="product-card" data-id="${item.id || ''}">
      <h3>${item.title || 'Untitled Item'}</h3>
      <p class="category">Category: ${item.category || 'N/A'}</p>
      <p class="price">$${item.price || 0} (${item.listing_type || 'sale'})</p>
      <a href="/marketplace/${item.id}" class="view-btn">View Details</a>
    </div>
  `).join('');
}