document.addEventListener('DOMContentLoaded', function() {
    // Product search functionality
    const searchForm = document.getElementById('search-form');
    if (searchForm) {
        searchForm.addEventListener('submit', function(e) {
            const searchInput = document.getElementById('search-input');
            if (!searchInput.value.trim()) {
                e.preventDefault();
                alert('Please enter a search term');
            }
        });
    }
    
    // Filter price range on search page
    const priceRangeMin = document.getElementById('price-range-min');
    const priceRangeMax = document.getElementById('price-range-max');
    const priceRangeValue = document.getElementById('price-range-value');
    
    if (priceRangeMin && priceRangeMax && priceRangeValue) {
        const updatePriceRangeLabel = () => {
            const min = parseInt(priceRangeMin.value);
            const max = parseInt(priceRangeMax.value);
            priceRangeValue.textContent = `₹${min} - ₹${max}`;
        };
        
        priceRangeMin.addEventListener('input', updatePriceRangeLabel);
        priceRangeMax.addEventListener('input', updatePriceRangeLabel);
        
        // Initialize
        updatePriceRangeLabel();
    }
    
    // Product sorting on search page
    const sortSelect = document.getElementById('sort-select');
    if (sortSelect) {
        sortSelect.addEventListener('change', function() {
            const productsContainer = document.querySelector('.row.product-grid');
            if (!productsContainer) return;
            
            const products = Array.from(productsContainer.querySelectorAll('.col-md-4'));
            
            products.sort((a, b) => {
                const aPrice = parseFloat(a.querySelector('.product-price').textContent.replace('₹', '').replace(',', ''));
                const bPrice = parseFloat(b.querySelector('.product-price').textContent.replace('₹', '').replace(',', ''));
                
                if (sortSelect.value === 'price-low-high') {
                    return aPrice - bPrice;
                } else if (sortSelect.value === 'price-high-low') {
                    return bPrice - aPrice;
                }
                return 0;
            });
            
            productsContainer.innerHTML = '';
            products.forEach(product => {
                productsContainer.appendChild(product);
            });
        });
    }
    
    // Product image zoom effect
    const productDetailImg = document.querySelector('.product-detail-img');
    if (productDetailImg) {
        productDetailImg.addEventListener('mousemove', function(e) {
            const { left, top, width, height } = this.getBoundingClientRect();
            const x = (e.clientX - left) / width;
            const y = (e.clientY - top) / height;
            
            this.style.transformOrigin = `${x * 100}% ${y * 100}%`;
            this.style.transform = 'scale(1.5)';
        });
        
        productDetailImg.addEventListener('mouseleave', function() {
            this.style.transform = 'scale(1)';
        });
    }
    
    // "Buy Now" button effects
    const buyButtons = document.querySelectorAll('.btn-buy');
    buyButtons.forEach(button => {
        button.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-2px)';
            this.style.boxShadow = '0 5px 15px rgba(0,0,0,0.1)';
        });
        
        button.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
            this.style.boxShadow = 'none';
        });
    });
    
    // API call to get cheapest price for a product
    const getCheapestPrice = async (productName) => {
        try {
            const response = await fetch(`/api/cheapest?product=${encodeURIComponent(productName)}`);
            if (!response.ok) throw new Error('Failed to fetch cheapest price');
            return await response.json();
        } catch (error) {
            console.error('Error getting cheapest price:', error);
            return null;
        }
    };
    
    // Highlight cheapest price in comparison table
    const highlightCheapestPrice = () => {
        const priceTable = document.querySelector('.price-comparison-table');
        if (!priceTable) return;
        
        const rows = Array.from(priceTable.querySelectorAll('tbody tr'));
        if (rows.length <= 1) return;
        
        // Find the cheapest price
        let cheapestRow = rows[0];
        let cheapestPrice = parseFloat(rows[0].querySelector('td:nth-child(2)').textContent.replace('₹', '').replace(',', ''));
        
        rows.forEach(row => {
            const price = parseFloat(row.querySelector('td:nth-child(2)').textContent.replace('₹', '').replace(',', ''));
            if (price < cheapestPrice) {
                cheapestPrice = price;
                cheapestRow = row;
            }
        });
        
        // Mark the cheapest row
        cheapestRow.classList.add('best-price');
        const badge = document.createElement('span');
        badge.className = 'badge bg-success ms-2';
        badge.textContent = 'Best Price!';
        cheapestRow.querySelector('td:nth-child(2)').appendChild(badge);
    };
    
    // Execute highlight on product detail page
    if (document.querySelector('.price-comparison-table')) {
        highlightCheapestPrice();
    }
    
    // Search suggestions
    const searchInput = document.getElementById('search-input');
    const suggestionsContainer = document.getElementById('search-suggestions');
    
    if (searchInput && suggestionsContainer) {
        const popularSearches = [
            'moisturizer', 'face wash', 'sunscreen', 'serum', 'face mask', 
            'toner', 'cleanser', 'night cream', 'eye cream', 'lip balm'
        ];
        
        searchInput.addEventListener('focus', function() {
            if (!this.value) {
                showSuggestions(popularSearches);
            }
        });
        
        searchInput.addEventListener('input', function() {
            const value = this.value.toLowerCase();
            if (!value) {
                showSuggestions(popularSearches);
                return;
            }
            
            const filtered = popularSearches.filter(item => 
                item.toLowerCase().includes(value)
            );
            
            showSuggestions(filtered);
        });
        
        searchInput.addEventListener('blur', function() {
            // Delay hiding to allow for clicks on suggestions
            setTimeout(() => {
                suggestionsContainer.innerHTML = '';
                suggestionsContainer.style.display = 'none';
            }, 200);
        });
        
        function showSuggestions(items) {
            suggestionsContainer.innerHTML = '';
            
            if (items.length === 0) {
                suggestionsContainer.style.display = 'none';
                return;
            }
            
            items.forEach(item => {
                const div = document.createElement('div');
                div.className = 'suggestion-item';
                div.textContent = item;
                div.addEventListener('click', function() {
                    searchInput.value = item;
                    suggestionsContainer.innerHTML = '';
                    suggestionsContainer.style.display = 'none';
                    searchForm.submit();
                });
                suggestionsContainer.appendChild(div);
            });
            
            suggestionsContainer.style.display = 'block';
        }
    }
});
