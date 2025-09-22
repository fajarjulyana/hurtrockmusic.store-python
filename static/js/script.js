// Hurtrock Music Store - Interactive JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Theme Toggle Functionality
    const themeToggle = document.getElementById('themeToggle');
    const body = document.body;

    // Load saved theme
    const savedTheme = localStorage.getItem('theme') || 'dark';
    body.setAttribute('data-theme', savedTheme);
    updateThemeIcon(savedTheme);

    themeToggle.addEventListener('click', function() {
        const currentTheme = body.getAttribute('data-theme');
        const newTheme = currentTheme === 'light' ? 'dark' : 'light';

        body.setAttribute('data-theme', newTheme);
        localStorage.setItem('theme', newTheme);
        updateThemeIcon(newTheme);
    });

    function updateThemeIcon(theme) {
        const icon = themeToggle.querySelector('i');
        if (theme === 'dark') {
            icon.className = 'fas fa-sun';
        } else {
            icon.className = 'fas fa-moon';
        }
    }

    // Real-time Search Functionality
    const searchInput = document.getElementById('searchInput');
    const searchResults = document.getElementById('searchResults');
    let searchTimeout;
    let currentFocus = -1;

    if (searchInput) {
        searchInput.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            const query = this.value.trim();
            currentFocus = -1;

            if (query.length < 2) {
                hideSearchResults();
                return;
            }

            // Show loading state
            searchResults.innerHTML = '<div class="search-result-item text-center"><i class="fas fa-spinner fa-spin"></i> Mencari...</div>';
            searchResults.style.display = 'block';

            searchTimeout = setTimeout(() => {
                performSearch(query);
            }, 300);
        });

        searchInput.addEventListener('blur', function() {
            setTimeout(hideSearchResults, 200);
        });

        // Keyboard navigation
        searchInput.addEventListener('keydown', function(e) {
            const items = searchResults.querySelectorAll('.search-result-item');
            
            if (e.key === 'ArrowDown') {
                e.preventDefault();
                currentFocus++;
                if (currentFocus >= items.length) currentFocus = 0;
                addActive(items);
            } else if (e.key === 'ArrowUp') {
                e.preventDefault();
                currentFocus--;
                if (currentFocus < 0) currentFocus = items.length - 1;
                addActive(items);
            } else if (e.key === 'Enter') {
                e.preventDefault();
                if (currentFocus > -1 && items[currentFocus]) {
                    items[currentFocus].click();
                }
            } else if (e.key === 'Escape') {
                hideSearchResults();
                this.blur();
            }
        });
    }

    function addActive(items) {
        if (!items) return;
        removeActive(items);
        if (currentFocus >= 0 && items[currentFocus]) {
            items[currentFocus].classList.add('search-active');
        }
    }

    function removeActive(items) {
        items.forEach(item => item.classList.remove('search-active'));
    }

    function performSearch(query) {
        fetch(`/search?q=${encodeURIComponent(query)}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                displaySearchResults(data);
            })
            .catch(error => {
                console.error('Search error:', error);
                searchResults.innerHTML = '<div class="search-result-item text-center text-muted">Terjadi kesalahan saat mencari. Silakan coba lagi.</div>';
                searchResults.style.display = 'block';
            });
    }

    function displaySearchResults(products) {
        if (!products || products.length === 0) {
            hideSearchResults();
            return;
        }

        // Handle error response
        if (products.error) {
            console.error('Search error:', products.error);
            hideSearchResults();
            return;
        }

        const resultsHTML = products.map(product => `
            <div class="search-result-item" onclick="goToProduct(${product.id})" data-product-id="${product.id}">
                <div class="d-flex align-items-center">
                    <img src="${product.image_url}" alt="${product.name}" 
                         style="width: 40px; height: 40px; object-fit: cover; border-radius: 5px; margin-right: 10px;"
                         onerror="this.src='https://via.placeholder.com/40x40/FF6B35/FFFFFF?text=P'">
                    <div class="flex-grow-1">
                        <div class="fw-bold">${product.name}</div>
                        ${product.brand ? `<div class="text-muted small">${product.brand}</div>` : ''}
                        <div class="text-orange small fw-bold">Rp ${parseFloat(product.price).toLocaleString('id-ID')}</div>
                    </div>
                </div>
            </div>
        `).join('');

        searchResults.innerHTML = resultsHTML;
        searchResults.style.display = 'block';
    }

    function hideSearchResults() {
        if (searchResults) {
            searchResults.style.display = 'none';
        }
    }

    window.goToProduct = function(productId) {
        window.location.href = `/product/${productId}`;
    };

    // Cart Count Update
    updateCartCount();

    function updateCartCount() {
        const cartBadge = document.getElementById('cartCount');
        if (cartBadge) {
            // Make AJAX call to get actual cart count
            fetch('/api/cart/count')
                .then(response => response.json())
                .then(data => {
                    cartBadge.textContent = data.count || '0';
                    // Hide badge if count is 0
                    if (data.count > 0) {
                        cartBadge.style.display = 'inline';
                    } else {
                        cartBadge.style.display = 'none';
                    }
                })
                .catch(error => {
                    console.error('Error fetching cart count:', error);
                    cartBadge.textContent = '0';
                    cartBadge.style.display = 'none';
                });
        }
    }

    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            const href = this.getAttribute('href');
            if (href && href !== '#') {
                e.preventDefault();
                const target = document.querySelector(href);
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth'
                    });
                }
            }
        });
    });

    // Add animation classes when elements come into view
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in-up');
            }
        });
    }, observerOptions);

    // Observe cards and feature boxes
    document.querySelectorAll('.card, .feature-box').forEach(el => {
        observer.observe(el);
    });

    // Form validation enhancements
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const inputs = form.querySelectorAll('input[required]');
            let isValid = true;

            inputs.forEach(input => {
                if (!input.value.trim()) {
                    input.classList.add('is-invalid');
                    isValid = false;
                } else {
                    input.classList.remove('is-invalid');
                }
            });

            if (!isValid) {
                e.preventDefault();
            }
        });
    });

    // Quantity controls for product pages
    const quantityControls = document.querySelectorAll('.quantity-control');
    quantityControls.forEach(control => {
        const decreaseBtn = control.querySelector('.decrease');
        const increaseBtn = control.querySelector('.increase');
        const input = control.querySelector('input');

        if (decreaseBtn) {
            decreaseBtn.addEventListener('click', function() {
                const currentValue = parseInt(input.value) || 1;
                if (currentValue > 1) {
                    input.value = currentValue - 1;
                }
            });
        }

        if (increaseBtn) {
            increaseBtn.addEventListener('click', function() {
                const currentValue = parseInt(input.value) || 1;
                const maxValue = parseInt(input.getAttribute('max')) || 999;
                if (currentValue < maxValue) {
                    input.value = currentValue + 1;
                }
            });
        }
    });

    // Toast notifications for better UX
    function showToast(message, type = 'success') {
        const toast = document.createElement('div');
        toast.className = `toast align-items-center text-white bg-${type === 'success' ? 'success' : 'danger'} border-0`;
        toast.setAttribute('role', 'alert');
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        `;

        document.body.appendChild(toast);
        const bsToast = new bootstrap.Toast(toast);
        bsToast.show();

        toast.addEventListener('hidden.bs.toast', function() {
            document.body.removeChild(toast);
        });
    }

    // Make showToast globally available
    window.showToast = showToast;

    // Floating Chat Widget
    const chatToggle = document.getElementById('chatToggle');
    const chatWidget = document.getElementById('chatWidget');
    const closeChatWidget = document.getElementById('closeChatWidget');
    const floatingChatMessages = document.getElementById('floatingChatMessages');
    const floatingChatInput = document.getElementById('floatingChatInput');
    const sendFloatingMessage = document.getElementById('sendFloatingMessage');
    const clearChatBtn = document.getElementById('clearChatBtn');
    const tagProductBtn = document.getElementById('tagProductBtn');
    const productTagSection = document.querySelector('.product-tag-section');
    const productSearchInput = document.getElementById('productSearchInput');
    const cancelProductTag = document.getElementById('cancelProductTag');
    const productSearchResults = document.getElementById('productSearchResults');
    const unreadBadge = document.getElementById('unreadBadge');

    let floatingChatSocket = null;
    let isFloatingChatOpen = false;
    let unreadCount = 0;

    if (chatToggle) {
        chatToggle.addEventListener('click', function() {
            isFloatingChatOpen = !isFloatingChatOpen;
            chatWidget.style.display = isFloatingChatOpen ? 'block' : 'none';

            if (isFloatingChatOpen) {
                loadFloatingChatMessages();
                // Reset unread count when opening chat
                unreadCount = 0;
                updateUnreadBadge();
            }
        });
    }

    if (closeChatWidget) {
        closeChatWidget.addEventListener('click', function() {
            isFloatingChatOpen = false;
            chatWidget.style.display = 'none';
        });
    }

    // Send message functionality
    if (sendFloatingMessage && floatingChatInput) {
        sendFloatingMessage.addEventListener('click', sendFloatingChatMessage);
        floatingChatInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                sendFloatingChatMessage();
            }
        });
    }

    // Clear chat functionality
    if (clearChatBtn) {
        clearChatBtn.addEventListener('click', function() {
            if (confirm('Yakin ingin menghapus semua chat? Tindakan ini tidak dapat dibatalkan.')) {
                clearFloatingChat();
            }
        });
    }

    // Product tagging functionality
    if (tagProductBtn) {
        tagProductBtn.addEventListener('click', function() {
            productTagSection.style.display = 'block';
            productSearchInput.focus();
        });
    }

    if (cancelProductTag) {
        cancelProductTag.addEventListener('click', function() {
            productTagSection.style.display = 'none';
            productSearchInput.value = '';
            productSearchResults.innerHTML = '';
        });
    }

    // Product search functionality
    if (productSearchInput) {
        let productSearchTimeout;
        productSearchInput.addEventListener('input', function() {
            clearTimeout(productSearchTimeout);
            const query = this.value.trim();

            if (query.length < 2) {
                productSearchResults.innerHTML = '';
                return;
            }

            productSearchTimeout = setTimeout(() => {
                searchProductsForTag(query);
            }, 300);
        });
    }

    // Close chat widget when clicking outside
    document.addEventListener('click', function(e) {
        if (chatWidget && chatToggle && isFloatingChatOpen) {
            if (!chatWidget.contains(e.target) && !chatToggle.contains(e.target)) {
                isFloatingChatOpen = false;
                chatWidget.style.display = 'none';
            }
        }
    });

    function connectFloatingChatSocket() {
        if (typeof io !== 'undefined' && !floatingChatSocket) {
            floatingChatSocket = io();

            floatingChatSocket.emit('join', {});

            floatingChatSocket.on('new_message', function(data) {
                if (data.sender_type === 'admin') {
                    // Only add message to DOM if chat is open
                    if (isFloatingChatOpen) {
                        addFloatingMessage(data.message, 'admin', data.timestamp, data.product_id);
                        scrollFloatingChatToBottom();
                    } else {
                        // Update unread count if chat is closed
                        unreadCount++;
                        updateUnreadBadge();
                    }
                }
            });
        }
    }


    function loadFloatingChatMessages() {
        fetch('/api/chat/messages')
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.text();
            })
            .then(text => {
                try {
                    const data = JSON.parse(text);
                    if (data.success && data.messages) {
                        floatingChatMessages.innerHTML = '';
                        if (data.messages.length > 0) {
                            data.messages.forEach(msg => {
                                addFloatingMessage(msg.message, msg.sender_type, msg.timestamp, msg.product_id);
                            });
                            scrollFloatingChatToBottom();

                            // Update unread count - count unread admin messages
                            const unreadAdminMessages = data.messages.filter(msg => 
                                msg.sender_type === 'admin' && !msg.is_read
                            );
                            unreadCount = unreadAdminMessages.length;
                        } else {
                            // No messages found, reset unread count
                            unreadCount = 0;
                            floatingChatMessages.innerHTML = '<div class="text-center text-muted py-3">Belum ada percakapan</div>';
                        }
                        updateUnreadBadge();
                    } else {
                        throw new Error(data.error || 'Failed to load messages');
                    }
                } catch (parseError) {
                    console.error('JSON parse error:', parseError);
                    console.error('Response text:', text);
                    floatingChatMessages.innerHTML = '<div class="text-center text-muted py-3">Gagal memuat percakapan</div>';
                    unreadCount = 0;
                    updateUnreadBadge();
                }
            })
            .catch(error => {
                console.error('Chat loading error:', error);
                floatingChatMessages.innerHTML = '<div class="text-center text-muted py-3">Gagal memuat percakapan</div>';
                unreadCount = 0;
                updateUnreadBadge();
            });
    }

    function sendFloatingChatMessage() {
        const message = floatingChatInput.value.trim();
        if (!message) return;

        // Add message to chat immediately
        const timestamp = new Date().toLocaleTimeString('id-ID', {hour: '2-digit', minute: '2-digit'});
        addFloatingMessage(message, 'user', timestamp);

        // Send to server
        fetch('/api/chat/send', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            },
            body: JSON.stringify({ message: message })
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.text();
        })
        .then(text => {
            try {
                const data = JSON.parse(text);
                if (data.success) {
                    floatingChatInput.value = '';
                    loadFloatingChatMessages();
                } else {
                    showToast(data.error || 'Gagal mengirim pesan', 'error');
                }
            } catch (parseError) {
                console.error('JSON parse error:', parseError);
                console.error('Response text:', text);
                showToast('Gagal mengirim pesan', 'error');
            }
        })
        .catch(error => {
            console.error('Error sending message:', error);
            showToast('Gagal mengirim pesan', 'error');
        });

        floatingChatInput.value = '';
        scrollFloatingChatToBottom();
    }

    function addFloatingMessage(message, sender, timestamp, productId = null) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `floating-message ${sender}`;

        let messageContent = message;

        // Add product tag if exists
        if (productId) {
            messageContent += `<br><a href="/product/${productId}" class="product-tag" target="_blank">Lihat Produk <i class="fas fa-external-link-alt ms-1"></i></a>`;
        }

        messageDiv.innerHTML = `
            <div class="floating-message-content">
                <div>${messageContent}</div>
                <div class="floating-message-time">${timestamp}</div>
            </div>
        `;

        floatingChatMessages.appendChild(messageDiv);
    }

    function scrollFloatingChatToBottom() {
        if (floatingChatMessages) {
            floatingChatMessages.scrollTop = floatingChatMessages.scrollHeight;
        }
    }

    function clearFloatingChat() {
        fetch('/api/chat/clear', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                floatingChatMessages.innerHTML = '';
                showToast('Chat berhasil dihapus', 'success');
            } else {
                showToast('Gagal menghapus chat', 'error');
            }
        })
        .catch(error => {
            console.error('Error clearing chat:', error);
            showToast('Gagal menghapus chat', 'error');
        });
    }

    function searchProductsForTag(query) {
        fetch(`/search?q=${encodeURIComponent(query)}`)
            .then(response => response.json())
            .then(products => {
                displayProductSearchResults(products);
            })
            .catch(error => console.error('Product search error:', error));
    }

    function displayProductSearchResults(products) {
        if (products.length === 0) {
            productSearchResults.innerHTML = '<div class="p-2 text-muted">Tidak ada produk ditemukan</div>';
            return;
        }

        const resultsHTML = products.slice(0, 5).map(product => `
            <div class="product-search-item" onclick="tagProduct(${product.id}, '${product.name.replace(/'/g, "\\'")}')" data-product-id="${product.id}">
                <div class="d-flex align-items-center">
                    <img src="${product.image_url}" alt="${product.name}" 
                         style="width: 30px; height: 30px; object-fit: cover; border-radius: 3px; margin-right: 8px;"
                         onerror="this.src='https://via.placeholder.com/30x30/FF6B35/FFFFFF?text=P'">
                    <div>
                        <div class="fw-bold" style="font-size: 0.9em;">${product.name}</div>
                        <div class="text-muted" style="font-size: 0.8em;">Rp ${parseFloat(product.price).toLocaleString('id-ID')}</div>
                    </div>
                </div>
            </div>
        `).join('');

        productSearchResults.innerHTML = resultsHTML;
    }

    function updateUnreadBadge() {
        if (unreadBadge) {
            if (unreadCount > 0) {
                unreadBadge.textContent = unreadCount > 99 ? '99+' : unreadCount;
                unreadBadge.style.display = 'block';
            } else {
                unreadBadge.style.display = 'none';
            }
        }
    }

    window.tagProduct = function(productId, productName) {
        const message = `Saya tertarik dengan produk: ${productName}`;

        // Send message with product tag
        fetch('/api/chat/send', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ 
                message: message,
                product_id: productId 
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const timestamp = new Date().toLocaleTimeString('id-ID', {hour: '2-digit', minute: '2-digit'});
                addFloatingMessage(message, 'user', timestamp, productId);
                scrollFloatingChatToBottom();

                // Hide product tag section
                productTagSection.style.display = 'none';
                productSearchInput.value = '';
                productSearchResults.innerHTML = '';
            } else {
                showToast('Gagal mengirim pesan', 'error');
            }
        })
        .catch(error => {
            console.error('Error sending message:', error);
            showToast('Gagal mengirim pesan', 'error');
        });
    };

    // Add loading states to buttons
    document.querySelectorAll('form').forEach(form => {
        form.addEventListener('submit', function() {
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Memproses...';
                submitBtn.disabled = true;
            }
        });
    });

    // Initialize Socket.IO connection on page load for authenticated users
    if (typeof userAuthenticated !== 'undefined' && userAuthenticated) {
        connectFloatingChatSocket();
    }
});

// Add to cart functionality
function addToCart(productId, quantity = 1) {
    fetch('/add_to_cart/' + productId, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: 'quantity=' + quantity
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showToast('Produk berhasil ditambahkan ke keranjang!');
            updateCartCount();
        } else {
            showToast(data.message || 'Terjadi kesalahan', 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showToast('Terjadi kesalahan saat menambahkan ke keranjang', 'error');
    });
}