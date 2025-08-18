// PMCELL Catalog - Main JavaScript

// Global app state with Alpine.js
document.addEventListener('alpine:init', () => {
    Alpine.data('pmcellApp', () => ({
        // App state
        cartCount: 0,
        searchQuery: '',
        selectedCategory: 'all',
        sortBy: 'name',
        pricesUnlocked: false,
        
        // WhatsApp modal state
        showWhatsAppModal: false,
        whatsappNumber: '',
        whatsappError: '',
        isSubmittingWhatsApp: false,

        // Journey tracking state
        sessaoId: '',
        timeOnSite: 0,
        startTime: Date.now(),
        categoriesVisited: new Set(),
        searchesPerformed: [],
        productsViewed: [],
        abandonedCartTimer: null,

        // Initialize app
        init() {
            this.loadCartCount();
            this.checkPricesUnlocked();
            this.initializeTracking();
            
            // Listen for cart updates
            document.addEventListener('cart:updated', (e) => {
                this.cartCount = e.detail.count;
                this.trackCartChange(e.detail);
            });

            // Track page visibility changes
            document.addEventListener('visibilitychange', () => {
                if (document.hidden) {
                    this.trackSiteExit();
                } else {
                    this.updateTimeOnSite();
                }
            });

            // Track before unload
            window.addEventListener('beforeunload', () => {
                this.trackSiteExit();
            });

            // Update time every 30 seconds
            setInterval(() => {
                this.updateTimeOnSite();
            }, 30000);
        },

        // Initialize journey tracking
        initializeTracking() {
            this.sessaoId = this.generateSessionId();
            this.trackEvent('entrada', {
                url: window.location.href,
                timestamp: new Date().toISOString()
            });
        },

        // Load cart count from localStorage with animation
        loadCartCount() {
            const oldCount = this.cartCount;
            const cart = JSON.parse(localStorage.getItem('pmcell_cart') || '[]');
            this.cartCount = cart.reduce((total, item) => total + item.quantity, 0);
            
            // Animate cart counter if it changed
            if (oldCount !== this.cartCount) {
                const cartBadge = document.querySelector('.cart-badge');
                if (cartBadge) {
                    cartBadge.classList.add('cart-counter-update');
                    setTimeout(() => cartBadge.classList.remove('cart-counter-update'), 600);
                }
            }
        },

        // Check if prices are unlocked (7-day cookie)
        checkPricesUnlocked() {
            const unlocked = this.getCookie('prices_unlocked');
            this.pricesUnlocked = unlocked === 'true';
            
            if (!this.pricesUnlocked) {
                // Show blurred prices
                this.blurPrices();
            }
        },

        // Show WhatsApp modal for price liberation
        requestPriceUnlock() {
            this.showWhatsAppModal = true;
            this.whatsappNumber = '';
            this.whatsappError = '';
        },

        // Validate and submit WhatsApp number
        async submitWhatsApp() {
            if (this.isSubmittingWhatsApp) return;
            
            const cleaned = this.cleanWhatsAppNumber(this.whatsappNumber);
            
            if (!this.validateWhatsAppNumber(cleaned)) {
                this.whatsappError = 'Por favor, insira um número válido: (XX) XXXXX-XXXX';
                return;
            }

            this.isSubmittingWhatsApp = true;
            this.whatsappError = '';

            try {
                // Send to webhook for price liberation
                await this.sendPriceLiberationWebhook(cleaned);
                
                // Set 7-day cookie
                this.setCookie('prices_unlocked', 'true', 7);
                this.setCookie('user_whatsapp', cleaned, 7);
                
                // Update state
                this.pricesUnlocked = true;
                this.showWhatsAppModal = false;
                
                // Unblur prices
                this.unblurPrices();
                
                // Track price liberation event
                this.trackEvent('liberacao_preco', {
                    whatsapp: cleaned,
                    timestamp: new Date().toISOString()
                });
                
                // Show success message
                this.showNotification('Preços liberados com sucesso!', 'success');
                
            } catch (error) {
                this.whatsappError = 'Erro ao liberar preços. Tente novamente.';
                console.error('Price liberation error:', error);
            } finally {
                this.isSubmittingWhatsApp = false;
            }
        },

        // Clean WhatsApp number (remove non-digits)
        cleanWhatsAppNumber(number) {
            return number.replace(/\D/g, '');
        },

        // Validate Brazilian WhatsApp number
        validateWhatsAppNumber(number) {
            // Should be 10-11 digits: DDD + 8/9 digits
            if (number.length < 10 || number.length > 11) return false;
            
            // Should start with valid DDD (11-99)
            const ddd = parseInt(number.substring(0, 2));
            if (ddd < 11 || ddd > 99) return false;
            
            // If 11 digits, 3rd digit should be 9 (mobile)
            if (number.length === 11 && number[2] !== '9') return false;
            
            return true;
        },

        // Format WhatsApp number for display
        formatWhatsAppNumber(number) {
            const cleaned = this.cleanWhatsAppNumber(number);
            
            if (cleaned.length === 10) {
                return `(${cleaned.substring(0, 2)}) ${cleaned.substring(2, 6)}-${cleaned.substring(6)}`;
            } else if (cleaned.length === 11) {
                return `(${cleaned.substring(0, 2)}) ${cleaned.substring(2, 7)}-${cleaned.substring(7)}`;
            }
            
            return number;
        },

        // Send price liberation webhook
        async sendPriceLiberationWebhook(whatsappNumber) {
            const response = await fetch('/api/liberate-prices/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken(),
                },
                body: JSON.stringify({
                    whatsapp: whatsappNumber,
                    timestamp: new Date().toISOString(),
                })
            });

            if (!response.ok) {
                throw new Error('Failed to liberate prices');
            }

            return response.json();
        },

        // Blur prices when locked
        blurPrices() {
            document.querySelectorAll('.price').forEach(el => {
                el.classList.add('price-blurred');
            });
        },

        // Unblur prices when unlocked
        unblurPrices() {
            document.querySelectorAll('.price').forEach(el => {
                el.classList.remove('price-blurred');
            });
        },

        // Journey tracking methods
        generateSessionId() {
            return 'sess_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
        },

        updateTimeOnSite() {
            this.timeOnSite = Math.floor((Date.now() - this.startTime) / 1000);
        },

        async trackEvent(evento, dados = {}) {
            try {
                await fetch('/api/track-journey/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': this.getCSRFToken(),
                    },
                    body: JSON.stringify({
                        evento,
                        dados: {
                            ...dados,
                            time_on_site: this.timeOnSite,
                            categories_visited: Array.from(this.categoriesVisited),
                            searches_performed: this.searchesPerformed.slice(-5), // Last 5 searches
                            products_viewed: this.productsViewed.slice(-10) // Last 10 products
                        },
                        sessao_id: this.sessaoId,
                    })
                });
            } catch (error) {
                console.error('Error tracking event:', error);
            }
        },

        trackCategoryVisit(categorySlug, categoryName) {
            this.categoriesVisited.add(categorySlug);
            this.trackEvent('categoria_visitada', {
                category_slug: categorySlug,
                category_name: categoryName
            });
        },

        trackSearch(query) {
            this.searchesPerformed.push({
                query,
                timestamp: new Date().toISOString()
            });
            this.trackEvent('pesquisa', {
                search_query: query,
                results_count: document.querySelectorAll('.product-card').length
            });
        },

        trackProductView(productId, productType, productName) {
            this.productsViewed.push({
                id: productId,
                type: productType,
                name: productName,
                timestamp: new Date().toISOString()
            });
            this.trackEvent('produto_visualizado', {
                product_id: productId,
                product_type: productType,
                product_name: productName
            });
        },

        trackCartChange(detail) {
            const eventMap = {
                'add': 'item_adicionado',
                'update': 'item_atualizado',
                'remove': 'item_removido',
                'clear': 'carrinho_limpo'
            };

            const evento = eventMap[detail.action];
            if (evento) {
                this.trackEvent(evento, {
                    cart_count: detail.count,
                    action_detail: detail
                });
            }

            // Reset/start abandoned cart timer
            this.resetAbandonedCartTimer();
        },

        resetAbandonedCartTimer() {
            if (this.abandonedCartTimer) {
                clearTimeout(this.abandonedCartTimer);
            }

            // Set 30-minute timer for abandoned cart
            this.abandonedCartTimer = setTimeout(() => {
                this.trackAbandonedCart();
            }, 30 * 60 * 1000); // 30 minutes
        },

        async trackAbandonedCart() {
            const cart = this.getCart();
            if (cart.length === 0) return;

            // Calculate estimated value
            let estimatedValue = 0;
            try {
                const response = await fetch('/api/get-cart-items/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': this.getCSRFToken(),
                    },
                    body: JSON.stringify({ cart })
                });
                
                const data = await response.json();
                estimatedValue = data.items.reduce((total, item) => 
                    total + (item.unitPrice * item.quantity), 0
                );
            } catch (error) {
                console.error('Error calculating cart value:', error);
            }

            // Send abandoned cart tracking
            try {
                await fetch('/api/track-abandoned-cart/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': this.getCSRFToken(),
                    },
                    body: JSON.stringify({
                        cart_data: cart,
                        estimated_value: estimatedValue,
                        sessao_id: this.sessaoId
                    })
                });
            } catch (error) {
                console.error('Error tracking abandoned cart:', error);
            }
        },

        trackSiteExit() {
            this.updateTimeOnSite();
            this.trackEvent('saida', {
                total_time_on_site: this.timeOnSite,
                final_url: window.location.href
            });
        },

        // Search functionality
        performSearch() {
            if (this.searchQuery.length < 2 && this.searchQuery.length > 0) return;
            
            // Track search
            if (this.searchQuery.length >= 2) {
                this.trackSearch(this.searchQuery);
            }
            
            // HTMX will handle the actual search request
            htmx.trigger('#search-form', 'submit');
        },

        // Category filter
        filterByCategory(category, categoryName = '') {
            this.selectedCategory = category;
            
            // Track category visit
            if (category !== 'all' && categoryName) {
                this.trackCategoryVisit(category, categoryName);
            }
            
            htmx.trigger('#search-form', 'submit');
        },

        // Cart management
        addToCart(productId, productType, quantity = 1, modelId = null) {
            const cart = JSON.parse(localStorage.getItem('pmcell_cart') || '[]');
            
            const cartKey = modelId ? `${productId}_${modelId}` : productId.toString();
            const existingItem = cart.find(item => item.key === cartKey);
            
            if (existingItem) {
                existingItem.quantity += quantity;
            } else {
                cart.push({
                    key: cartKey,
                    productId: productId,
                    productType: productType,
                    modelId: modelId,
                    quantity: quantity,
                    addedAt: new Date().toISOString()
                });
            }
            
            localStorage.setItem('pmcell_cart', JSON.stringify(cart));
            this.loadCartCount();
            
            // Dispatch event
            document.dispatchEvent(new CustomEvent('cart:updated', {
                detail: { count: this.cartCount, action: 'add', productId, quantity }
            }));
            
            this.showNotification('Produto adicionado ao carrinho!', 'success');
        },

        // Update cart item quantity
        updateCartQuantity(cartKey, newQuantity) {
            const cart = JSON.parse(localStorage.getItem('pmcell_cart') || '[]');
            const item = cart.find(item => item.key === cartKey);
            
            if (item) {
                if (newQuantity <= 0) {
                    this.removeFromCart(cartKey);
                    return;
                }
                
                item.quantity = newQuantity;
                localStorage.setItem('pmcell_cart', JSON.stringify(cart));
                this.loadCartCount();
                
                document.dispatchEvent(new CustomEvent('cart:updated', {
                    detail: { count: this.cartCount, action: 'update', cartKey, quantity: newQuantity }
                }));
            }
        },

        // Remove item from cart
        removeFromCart(cartKey) {
            const cart = JSON.parse(localStorage.getItem('pmcell_cart') || '[]');
            const filtered = cart.filter(item => item.key !== cartKey);
            
            localStorage.setItem('pmcell_cart', JSON.stringify(filtered));
            this.loadCartCount();
            
            document.dispatchEvent(new CustomEvent('cart:updated', {
                detail: { count: this.cartCount, action: 'remove', cartKey }
            }));
        },

        // Clear entire cart
        clearCart() {
            localStorage.removeItem('pmcell_cart');
            this.cartCount = 0;
            
            document.dispatchEvent(new CustomEvent('cart:updated', {
                detail: { count: 0, action: 'clear' }
            }));
        },

        // Get cart contents
        getCart() {
            return JSON.parse(localStorage.getItem('pmcell_cart') || '[]');
        },

        // Utility functions
        getCookie(name) {
            const value = `; ${document.cookie}`;
            const parts = value.split(`; ${name}=`);
            if (parts.length === 2) return parts.pop().split(';').shift();
            return null;
        },

        setCookie(name, value, days) {
            const expires = new Date();
            expires.setTime(expires.getTime() + (days * 24 * 60 * 60 * 1000));
            document.cookie = `${name}=${value};expires=${expires.toUTCString()};path=/;SameSite=Lax`;
        },

        getCSRFToken() {
            return document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
        },

        // Show notification with enhanced animations
        showNotification(message, type = 'info') {
            // Create notification element
            const notification = document.createElement('div');
            notification.className = `fixed top-4 right-4 z-50 p-4 rounded-lg text-white font-medium notification-enter shadow-lg ${
                type === 'success' ? 'bg-green-500' : 
                type === 'error' ? 'bg-red-500' : 
                'bg-blue-500'
            }`;
            notification.textContent = message;
            
            document.body.appendChild(notification);
            
            // Add icon based on type
            const icon = document.createElement('span');
            icon.className = 'mr-2';
            icon.innerHTML = type === 'success' ? '✓' : type === 'error' ? '✗' : 'ℹ';
            notification.prepend(icon);
            
            // Remove after 3 seconds with exit animation
            setTimeout(() => {
                notification.className = notification.className.replace('notification-enter', 'notification-exit');
                setTimeout(() => notification.remove(), 300);
            }, 3000);
        },

        // Format price for display
        formatPrice(price) {
            return new Intl.NumberFormat('pt-BR', {
                style: 'currency',
                currency: 'BRL',
                minimumFractionDigits: 2
            }).format(price);
        },

        // Close modal by clicking outside
        closeModalOnClickOutside(event) {
            if (event.target === event.currentTarget) {
                this.showWhatsAppModal = false;
            }
        }
    }));
});

// HTMX Configuration
document.addEventListener('DOMContentLoaded', function() {
    // Configure HTMX
    htmx.config.globalViewTransitions = true;
    htmx.config.requestClass = 'htmx-request';
    htmx.config.timeout = 10000;
    
    // Enhanced loading states for buttons
    document.addEventListener('htmx:beforeRequest', function(evt) {
        const btn = evt.detail.elt;
        if (btn.tagName === 'BUTTON') {
            btn.disabled = true;
            btn.classList.add('btn-press');
            const originalText = btn.textContent;
            btn.dataset.originalText = originalText;
            btn.innerHTML = '<div class="loading-spinner mx-auto"></div>';
        }
    });
    
    document.addEventListener('htmx:afterRequest', function(evt) {
        const btn = evt.detail.elt;
        if (btn.tagName === 'BUTTON' && btn.dataset.originalText) {
            btn.disabled = false;
            btn.classList.remove('btn-press');
            btn.textContent = btn.dataset.originalText;
            delete btn.dataset.originalText;
        }
    });
});

// Global functions for use in templates
window.addToCart = function(productId, productType, quantity = 1) {
    const app = Alpine.$data(document.querySelector('[x-data="pmcellApp()"]'));
    app.addToCart(productId, productType, quantity);
};

window.addToCartModel = function(productId, modelId, quantity = 1) {
    const app = Alpine.$data(document.querySelector('[x-data="pmcellApp()"]'));
    app.addToCart(productId, 'capa_pelicula', quantity, modelId);
};

window.requestPriceUnlock = function() {
    const app = Alpine.$data(document.querySelector('[x-data="pmcellApp()"]'));
    app.requestPriceUnlock();
};

window.showNotification = function(message, type = 'info') {
    const app = Alpine.$data(document.querySelector('[x-data="pmcellApp()"]'));
    app.showNotification(message, type);
};

window.updateCartCounter = function() {
    const app = Alpine.$data(document.querySelector('[x-data="pmcellApp()"]'));
    app.loadCartCount();
};

// Journey tracking global functions
window.trackProductView = function(productId, productType, productName) {
    const app = Alpine.$data(document.querySelector('[x-data="pmcellApp()"]'));
    app.trackProductView(productId, productType, productName);
};

window.trackCategoryFilter = function(category, categoryName) {
    const app = Alpine.$data(document.querySelector('[x-data="pmcellApp()"]'));
    app.filterByCategory(category, categoryName);
};

window.trackCheckoutInitiated = function() {
    const app = Alpine.$data(document.querySelector('[x-data="pmcellApp()"]'));
    app.trackEvent('checkout_iniciado', {
        cart_items: app.getCart().length,
        timestamp: new Date().toISOString()
    });
};

// Debounce function for search
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Initialize search debouncing
document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.querySelector('#search-input');
    if (searchInput) {
        const debouncedSearch = debounce(() => {
            htmx.trigger('#search-form', 'submit');
        }, 300);
        
        searchInput.addEventListener('input', debouncedSearch);
    }
});