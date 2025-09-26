// === Domain Config injected from config.txt ===
const CHAT_DOMAIN = 'chat.fajarmandiri.store';
const KASIR_DOMAIN = 'kasir.fajarmandiri.store';
const MAIN_DOMAIN  = 'fajarmandiri.store';
// =================================================

/**
 * Floating Chat Widget - JavaScript Handler
 * Handles WebSocket connection, messaging, product tagging, and real-time chat
 */

class FloatingChat {
    constructor() {
        this.ws = null;
        this.chatToken = null;
        this.currentUser = null;
        this.isConnected = false;
        this.selectedProduct = null;
        this.typingTimer = null;
        this.unreadCount = 0;
        this.roomName = '';
        this.last_heartbeat = null; // Track last heartbeat time

        // Initialize chat when DOM is ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.init());
        } else {
            this.init();
        }
    }

    async init() {
        try {
            await this.getCurrentUser();
            // Only initialize chat for buyer users
            if (this.currentUser && this.currentUser.role === 'buyer') {
                await this.getChatToken();
                this.setupEventListeners();
                this.generateRoomName();
                this.setupWebSocket();
            } else if (!this.currentUser || this.currentUser.role === 'admin' || this.currentUser.role === 'staff') {
                // Hide chat for non-buyers
                this.hideChatContainer();
            }
        } catch (error) {
            console.error('Failed to initialize chat:', error);
            this.hideChatContainer();
        }
    }

    async getCurrentUser() {
        try {
            // Check if user is logged in by checking for user data in DOM or making API call
            const userDataElement = document.querySelector('[data-user-id]');
            if (userDataElement) {
                this.currentUser = {
                    id: userDataElement.dataset.userId,
                    name: userDataElement.dataset.userName,
                    email: userDataElement.dataset.userEmail,
                    role: userDataElement.dataset.userRole
                };
            } else {
                // If no user data in DOM, check if user is authenticated via API
                const response = await fetch((window.location.hostname === KASIR_DOMAIN || window.location.hostname === MAIN_DOMAIN) ? `https://${CHAT_DOMAIN}/api/chat/token` : '/api/chat/token');
                if (response.ok) {
                    const data = await response.json();
                    this.currentUser = data.user;
                } else {
                    // User not authenticated, don't show chat
                    console.log('User not authenticated, hiding chat');
                    this.hideChatContainer();
                    return;
                }
            }

            // Hide chat for admin and staff users since they have admin chat interface
            if (this.currentUser && (this.currentUser.role === 'admin' || this.currentUser.role === 'staff')) {
                console.log('Admin/Staff user detected, hiding floating chat');
                this.hideChatContainer();
                return;
            }
        } catch (error) {
            console.error('Error getting current user:', error);
            this.hideChatContainer();
        }
    }

    hideChatContainer() {
        const chatContainer = document.getElementById('floating-chat-container');
        if (chatContainer) {
            chatContainer.style.display = 'none';
        }
    }

    getChatApiUrl() {
        // Determine the correct chat API URL based on domain configuration
        const currentHost = window.location.hostname;
        const currentPort = window.location.port;
        const protocol = window.location.protocol;
        
        // Check if using Cloudflare tunnel domains (kasir.fajarmandiri.store, fajarmandiri.store)
        if (currentHost === 'kasir.fajarmandiri.store' || currentHost === 'fajarmandiri.store') {
            // Cloudflare tunnel routing - chat service available via /chat path
            return `${protocol}//${currentHost}/api/chat/token`;
        } else if (currentHost !== 'localhost' && currentHost !== '127.0.0.1') {
            // Replit environment or other cloud hosting - try direct port access first
            return `${protocol}//${currentHost}:8000/api/chat/token`;
        } else {
            // Local development environment - use localhost:8000
            return 'http://localhost:8000/api/chat/token';
        }
    }

    async getChatToken() {
        try {
            // Try primary URL first
            let chatApiUrl = this.getChatApiUrl();
            let response = await fetch(chatApiUrl, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                },
                credentials: 'same-origin'
            });

            // If primary URL fails and we're not on tunnel domains, try fallback
            if (!response.ok && !window.location.hostname.includes('fajarmandiri.store')) {
                console.log('Primary chat API URL failed, trying fallback...');
                // Try with /chat path as fallback
                const fallbackUrl = `${window.location.protocol}//${window.location.hostname}/api/chat/token`;
                response = await fetch(fallbackUrl, {
                    method: 'GET',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    credentials: 'same-origin'
                });
                
                if (response.ok) {
                    chatApiUrl = fallbackUrl;
                }
            }
            
            if (response.ok) {
                const data = await response.json();
                this.chatToken = data.token;
                this.currentUser = data.user;
                console.log('Chat token obtained successfully from:', chatApiUrl);
            } else {
                const errorText = await response.text();
                console.error('Chat token request failed:', response.status, errorText);
                throw new Error(`Failed to get chat token: ${response.status}`);
            }
        } catch (error) {
            console.error('Error getting chat token:', error);
            // Try to show a more user-friendly message
            if (error.message.includes('Failed to fetch')) {
                console.error('Network error - chat service may not be available');
            }
            throw error;
        }
    }

    generateRoomName() {
        // Create room name based on user role
        if (this.currentUser.role === 'admin' || this.currentUser.role === 'staff') {
            this.roomName = 'support_room';
        } else {
            this.roomName = `user_${this.currentUser.id}`;
        }
    }

    setupWebSocket() {
        if (!this.chatToken) {
            console.error('No chat token available');
            return;
        }

        // Use consistent room naming pattern: buyer_{user_id}
        const roomName = `buyer_${this.currentUser.id}`;
        this.roomName = roomName;

        const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        let wsUrls = [];

        // Universal dynamic chat URL construction for any domain
        const currentHost = window.location.hostname;
        const currentPort = window.location.port;
        
        // Check if using Cloudflare tunnel domains
        if (currentHost === 'kasir.fajarmandiri.store' || currentHost === 'fajarmandiri.store') {
            // Cloudflare tunnel routing - chat service di /chat path
            wsUrls.push(`${wsProtocol}//${CHAT_DOMAIN}/ws/chat/${roomName}/?token=${this.chatToken}`);
        } else if (window.location.hostname !== 'localhost' && window.location.hostname !== '127.0.0.1') {
            // Replit environment - try multiple patterns
            // Primary: Direct port 8000 access (most reliable for Replit)
            wsUrls.push(`${wsProtocol}//${currentHost}:8000/ws/chat/${roomName}/?token=${this.chatToken}`);
            
            // Secondary: Use /chat path for proxy routing if available
            wsUrls.push(`${wsProtocol}//${CHAT_DOMAIN}/ws/chat/${roomName}/?token=${this.chatToken}`);
            
            // Tertiary: Direct websocket path
            wsUrls.push(`${wsProtocol}//${currentHost}/ws/chat/${roomName}/?token=${this.chatToken}`);
        } else {
            // Local development environment
            wsUrls.push(`ws://127.0.0.1:8000/ws/chat/${roomName}/?token=${this.chatToken}`);
            wsUrls.push(`ws://localhost:8000/ws/chat/${roomName}/?token=${this.chatToken}`);
            wsUrls.push(`ws://0.0.0.0:8000/ws/chat/${roomName}/?token=${this.chatToken}`);
        }

        console.log('Buyer attempting WebSocket connection with URLs:', wsUrls);
        this.updateConnectionStatus('connecting');

        this.tryConnectWithFallback(wsUrls, 0);
    }

    tryConnectWithFallback(urls, urlIndex) {
        if (urlIndex >= urls.length) {
            console.error('All WebSocket URLs failed');
            this.updateConnectionStatus('error');
            this.displaySystemMessage('Tidak dapat terhubung ke server chat. Silakan refresh halaman.', 'error');
            return;
        }

        const wsUrl = urls[urlIndex];
        console.log(`Trying WebSocket URL ${urlIndex + 1}/${urls.length}:`, wsUrl);

        try {
            this.ws = new WebSocket(wsUrl);
            this.reconnectAttempts = 0;
            this.maxReconnectAttempts = 10;
            this.reconnectDelay = 1000;
            this.heartbeatInterval = null;

            this.ws.onopen = (event) => {
                console.log('WebSocket connected successfully to:', wsUrl);
                this.isConnected = true;
                this.reconnectAttempts = 0;
                this.reconnectDelay = 1000; // Reset delay
                this.updateConnectionStatus('connected');
                this.startHeartbeat();
                this.loadChatHistory(); // Load history upon connection
            };

            this.ws.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    this.handleWebSocketMessage(data);
                } catch (error) {
                    console.error('Error parsing WebSocket message:', error);
                }
            };

            this.ws.onclose = (event) => {
                console.log('WebSocket closed:', event.code, event.reason);
                this.isConnected = false;
                this.stopHeartbeat();

                if (event.code !== 1000 && event.code !== 1001) {
                    // Connection lost unexpectedly - try next URL
                    console.log('Connection failed, trying next URL...');
                    setTimeout(() => {
                        this.tryConnectWithFallback(urls, urlIndex + 1);
                    }, 1000);
                } else {
                    // Normal close
                    this.updateConnectionStatus('disconnected');
                }
            };

            this.ws.onerror = (error) => {
                console.error('WebSocket error for URL:', wsUrl, error);
                // Don't change status here, let onclose handle it
                this.isConnected = false;
            };

        } catch (error) {
            console.error('Error creating WebSocket for URL:', wsUrl, error);
            // Try next URL immediately
            setTimeout(() => {
                this.tryConnectWithFallback(urls, urlIndex + 1);
            }, 500);
        }
    }

    attemptReconnect() {
        if (this.reconnectAttempts >= this.maxReconnectAttempts) {
            console.error('Max reconnection attempts reached');
            this.updateConnectionStatus('error');
            this.displaySystemMessage('Koneksi chat gagal. Silakan refresh halaman.', 'error');
            return;
        }

        this.reconnectAttempts++;
        const delay = Math.min(this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1), 30000); // Max 30 seconds

        console.log(`Attempting to reconnect... (${this.reconnectAttempts}/${this.maxReconnectAttempts}) in ${delay}ms`);
        this.updateConnectionStatus('connecting');

        setTimeout(() => {
            if (!this.isConnected) {
                this.setupWebSocket();
            }
        }, delay);
    }

    startHeartbeat() {
        this.stopHeartbeat(); // Clear any existing heartbeat
        this.heartbeatInterval = setInterval(() => {
            if (this.isConnected && this.ws.readyState === WebSocket.OPEN) {
                this.ws.send(JSON.stringify({
                    type: 'heartbeat',
                    timestamp: new Date().toISOString()
                }));
                this.last_heartbeat = new Date(); // Record send time
            }
        }, 30000); // Send heartbeat every 30 seconds
    }

    stopHeartbeat() {
        if (this.heartbeatInterval) {
            clearInterval(this.heartbeatInterval);
            this.heartbeatInterval = null;
        }
    }

    handleWebSocketMessage(data) {
        console.log('Buyer received WebSocket message:', data);

        switch (data.type) {
            case 'connection_established':
                console.log('Chat connection established:', data.message);
                this.displaySystemMessage('Terhubung ke customer service', 'success');
                break;

            case 'chat_message':
                if (data.message && typeof data.message === 'object') {
                    this.displayMessage(data.message);
                    // Show notification if message is from admin/staff and chat is minimized
                    if (data.message.sender_type !== 'buyer' && this.isChatMinimized()) {
                        this.showNotification('Pesan baru dari customer service', data.message.message);
                        this.incrementUnreadCount();
                    }
                } else {
                    console.error('Received malformed chat_message data:', data);
                }
                break;

            case 'typing_indicator':
                this.updateTypingIndicator(data);
                break;

            case 'typing_status':
                // Handle typing status from channel layer
                this.updateTypingIndicator(data);
                break;

            case 'heartbeat_ack':
                // Handle heartbeat acknowledgment
                console.debug('Heartbeat acknowledged:', data);
                this.last_heartbeat = new Date();
                break;

            case 'error':
                console.error('Chat error:', data.message);
                this.displaySystemMessage(data.message || 'Terjadi kesalahan', 'error');
                break;

            default:
                console.log('Unknown message type:', data);
        }
    }

    isChatMinimized() {
        const chatWindow = document.getElementById('chat-window');
        return chatWindow.style.display === 'none';
    }

    handleNotification(notification) {
        switch (notification.type) {
            case 'message_read':
                // Remove unread indicator if exists
                this.handleMessageRead(notification.message_id);
                break;
            case 'new_message':
                if (this.isChatMinimized()) {
                    this.showNotification(notification.title, notification.body);
                    this.incrementUnreadCount();
                }
                break;
        }
    }

    handleMessageRead(messageId) {
        // Mark message as read in UI
        const messageElement = document.querySelector(`[data-message-id="${messageId}"]`);
        if (messageElement) {
            const readIndicator = messageElement.querySelector('.read-indicator');
            if (readIndicator) {
                readIndicator.classList.add('read');
                readIndicator.innerHTML = '<i class="fas fa-check-double text-primary"></i>';
            }
        }
    }

    updateConnectionStatus(status) {
        const statusElement = document.getElementById('connection-status');
        if (statusElement) {
            statusElement.className = `connection-status ${status}`;
            switch (status) {
                case 'connected':
                    statusElement.textContent = 'Terhubung';
                    break;
                case 'connecting':
                    statusElement.textContent = 'Menghubungkan...';
                    break;
                case 'disconnected':
                    statusElement.textContent = 'Terputus - mencoba menyambung kembali...';
                    break;
                case 'error':
                    statusElement.textContent = 'Koneksi bermasalah';
                    break;
            }
        }
    }

    setupEventListeners() {
        // Chat message input
        const messageInput = document.getElementById('chat-message-input');
        if (messageInput) {
            messageInput.addEventListener('keypress', (e) => this.handleChatKeyPress(e));
            messageInput.addEventListener('input', () => this.handleTyping());
        }

        // Send button
        const sendBtn = document.getElementById('send-message-btn');
        if (sendBtn) {
            sendBtn.addEventListener('click', () => this.sendChatMessage());
        }

        // Product search
        const productSearch = document.getElementById('product-search');
        if (productSearch) {
            productSearch.addEventListener('keyup', () => this.searchProducts());
        }
    }

    handleChatKeyPress(event) {
        if (event.key === 'Enter' && !event.shiftKey) {
            event.preventDefault();
            this.sendChatMessage();
        }
    }

    sendChatMessage() {
        const messageInput = document.getElementById('chat-message-input');
        const message = messageInput.value.trim();

        if (!message) return;

        if (!this.isConnected) {
            this.displaySystemMessage('Chat tidak terhubung. Mencoba menyambung kembali...', 'warning');
            this.setupWebSocket();
            return;
        }

        const messageData = {
            type: 'chat_message',
            message: message,
            product_id: this.selectedProduct ? this.selectedProduct.id : null
        };

        this.ws.send(JSON.stringify(messageData));
        messageInput.value = '';

        // Clear product tag after sending
        if (this.selectedProduct) {
            this.clearProductTag();
        }
    }

    handleTyping() {
        if (!this.isConnected) return;

        // Send typing start indicator
        this.ws.send(JSON.stringify({
            type: 'typing_indicator',
            is_typing: true
        }));

        // Clear existing timer
        if (this.typingTimer) {
            clearTimeout(this.typingTimer);
        }

        // Send typing stop indicator after 2 seconds
        this.typingTimer = setTimeout(() => {
            if (this.isConnected) {
                this.ws.send(JSON.stringify({
                    type: 'typing_indicator',
                    is_typing: false
                }));
            }
        }, 2000);
    }

    displayMessage(data) {
        const messagesContainer = document.getElementById('chat-messages');
        if (!messagesContainer) return;

        const welcomeMsg = messagesContainer.querySelector('.chat-welcome-msg');

        // Remove welcome message when first message arrives
        if (welcomeMsg) {
            welcomeMsg.remove();
        }

        const messageDiv = document.createElement('div');
        const isSent = data.user_id == this.currentUser.id;
        messageDiv.className = `chat-message ${isSent ? 'sent' : 'received'}`;

        let productTagHtml = '';
        // Check for product info first, then fallback to product_id
        if (data.product_info) {
            const productName = this.escapeHtml(data.product_info.name || 'Unknown Product');
            const productPrice = data.product_info.price ? this.formatPrice(data.product_info.price) : 'N/A';
            const productImage = data.product_info.image_url || '/static/images/placeholder.jpg';
            const productUrl = `/product/${data.product_info.id}`;

            productTagHtml = `
                <div class="product-tag" data-product-url="${productUrl}" style="cursor: pointer;">
                    <img src="${productImage}" alt="${productName}" onerror="this.src='/static/images/placeholder.jpg'">
                    <div class="product-tag-info">
                        <h6>${productName}</h6>
                        <p>Rp ${productPrice}</p>
                        <small>Klik untuk lihat detail</small>
                    </div>
                </div>
            `;
        } else if (data.product_id) {
            // Create placeholder and try to fetch product info
            const fallbackUrl = `/product/${data.product_id}`;
            productTagHtml = `
                <div class="product-tag loading" data-product-url="${fallbackUrl}" data-product-id="${data.product_id}" style="cursor: pointer;">
                    <img src="/static/images/placeholder.jpg" alt="Loading..." onerror="this.src='/static/images/placeholder.jpg'">
                    <div class="product-tag-info">
                        <h6>Memuat produk...</h6>
                        <p>Klik untuk lihat detail</p>
                    </div>
                </div>
            `;

            // Fetch product info asynchronously
            this.fetchProductInfo(data.product_id).then(productInfo => {
                if (productInfo && messageDiv) {
                    this.updateProductTagDisplay(messageDiv, productInfo);
                }
            }).catch(error => {
                console.error('Failed to fetch product info:', error);
                // Keep the fallback display
            });
        }

        const timestamp = data.timestamp || data.created_at || new Date().toISOString();
        const timeFormatted = this.formatTime(timestamp);

        messageDiv.innerHTML = `
            <div class="message-content">
                ${this.escapeHtml(data.message)}
                ${productTagHtml}
                <div class="message-meta">
                    <strong>${this.escapeHtml(data.user_name || 'User')}</strong> • ${timeFormatted}
                </div>
            </div>
        `;

        messagesContainer.appendChild(messageDiv);

        // Add click event listener to product tags after they're added to DOM
        const productTags = messageDiv.querySelectorAll('.product-tag[data-product-url]');
        productTags.forEach(tag => {
            tag.addEventListener('click', function(e) {
                e.preventDefault();
                const productUrl = this.getAttribute('data-product-url');
                window.open(productUrl, '_blank');
            });
        });

        // Smooth scroll to bottom with proper timing
        setTimeout(() => {
            messagesContainer.scrollTo({
                top: messagesContainer.scrollHeight,
                behavior: 'smooth'
            });
        }, 100);
    }

    async fetchProductInfo(productId) {
        try {
            const response = await fetch(`/api/products/${productId}`);
            if (response.ok) {
                return await response.json();
            }
            return null;
        } catch (error) {
            console.error('Error fetching product info:', error);
            return null;
        }
    }

    updateProductTagDisplay(messageDiv, productInfo) {
        const productTag = messageDiv.querySelector('.product-tag[data-product-id]');
        if (productTag && productInfo) {
            const productName = this.escapeHtml(productInfo.name || 'Unknown Product');
            const productPrice = productInfo.price ? this.formatPrice(productInfo.price) : 'N/A';
            const productImage = productInfo.image_url || '/static/images/placeholder.jpg';
            const productUrl = `/product/${productInfo.id}`;

            productTag.classList.remove('loading');
            productTag.setAttribute('data-product-url', productUrl);

            productTag.innerHTML = `
                <img src="${productImage}" alt="${productName}" onerror="this.src='/static/images/placeholder.jpg'">
                <div class="product-tag-info">
                    <h6>${productName}</h6>
                    <p>Rp ${productPrice}</p>
                    <small>Klik untuk lihat detail</small>
                </div>
            `;

            // Re-add click event listener
            productTag.addEventListener('click', function(e) {
                e.preventDefault();
                window.open(productUrl, '_blank');
            });
        }
    }

    displaySystemMessage(message, type = 'info') {
        const messagesContainer = document.getElementById('chat-messages');
        const messageDiv = document.createElement('div');
        messageDiv.className = `chat-message system ${type}`;
        messageDiv.innerHTML = `
            <div class="message-content system-message">
                <i class="fas fa-info-circle"></i>
                ${this.escapeHtml(message)}
            </div>
        `;
        messagesContainer.appendChild(messageDiv);

        // Smooth scroll to bottom with proper timing
        setTimeout(() => {
            messagesContainer.scrollTo({
                top: messagesContainer.scrollHeight,
                behavior: 'smooth'
            });
        }, 100);
    }

    updateTypingIndicator(data) {
        const typingIndicator = document.getElementById('typing-indicator');
        if (!typingIndicator) return;

        if (data.is_typing && data.user_id != this.currentUser.id) {
            typingIndicator.querySelector('.typing-user').textContent = data.user_name;
            typingIndicator.style.display = 'flex';
        } else {
            typingIndicator.style.display = 'none';
        }
    }

    incrementUnreadCount() {
        this.unreadCount++;
        this.updateChatBadge();

        // If chat is minimized, show notification
        const chatWindow = document.getElementById('chat-window');
        if (chatWindow.style.display === 'none') {
            this.showNotification();
        }
    }

    updateChatBadge() {
        const badge = document.getElementById('chat-badge');
        if (this.unreadCount > 0) {
            badge.textContent = this.unreadCount > 99 ? '99+' : this.unreadCount;
            badge.style.display = 'block';
        } else {
            badge.style.display = 'none';
        }
    }

    showNotification() {
        // Simple browser notification (if permission granted)
        if (Notification.permission === 'granted') {
            new Notification('Pesan chat baru', {
                body: 'Anda mendapat pesan baru dari customer service.',
                icon: '/static/images/favicon.ico'
            });
        }
    }

    async loadChatHistory() {
        try {
            const roomName = `buyer_${this.currentUser.id}`;
            
            // Try multiple endpoints for loading chat history
            const currentHost = window.location.hostname;
            let endpoints = [];
            
            if (currentHost === 'kasir.fajarmandiri.store' || currentHost === 'fajarmandiri.store') {
                // Cloudflare tunnel routing
                endpoints = [
                    `/api/rooms/${roomName}/messages/`,
                    `/api/rooms/${roomName}/messages/`
                ];
            } else {
                // Replit/local environment
                endpoints = [
                    `/api/rooms/${roomName}/messages/`,
                    `/api/rooms/${roomName}/messages/`
                ];
            }
            
            let lastError = null;
            
            for (const endpoint of endpoints) {
                try {
                    const response = await fetch(endpoint, {
                        headers: {
                            'Authorization': `Bearer ${this.chatToken}`,
                            'Content-Type': 'application/json'
                        },
                        timeout: 5000
                    });

                    if (response.ok) {
                        const data = await response.json();
                        console.log('Chat history loaded:', data);

                        const messages = data.results || data; // Handle pagination
                        if (Array.isArray(messages)) {
                            messages.forEach(message => {
                                if (message && typeof message === 'object') {
                                    this.displayMessage(message);
                                }
                            });
                        } else {
                            console.error("Received non-array message data:", messages);
                        }
                        return; // Success, exit the loop
                    } else {
                        lastError = `HTTP ${response.status}`;
                        continue;
                    }
                } catch (error) {
                    lastError = error.message;
                    continue;
                }
            }
            
            console.error('Failed to load chat history from all endpoints:', lastError);
        } catch (error) {
            console.error('Error loading chat history:', error);
        }
    }

    async searchProducts() {
        const searchInput = document.getElementById('product-search');
        const query = searchInput.value.trim();

        if (query.length < 2) {
            document.getElementById('products-list').innerHTML = '';
            return;
        }

        try {
            const response = await fetch(`/search?q=${encodeURIComponent(query)}`);
            if (response.ok) {
                const products = await response.json();
                this.displayProductResults(products);
            }
        } catch (error) {
            console.error('Error searching products:', error);
        }
    }

    displayProductResults(products) {
        const productsList = document.getElementById('products-list');

        if (products.length === 0) {
            productsList.innerHTML = '<p class="text-muted">Tidak ada produk ditemukan.</p>';
            return;
        }

        productsList.innerHTML = products.map(product => `
            <div class="product-item" onclick="floatingChat.selectProduct(${product.id}, '${this.escapeHtml(product.name)}', '${product.price}', '${product.image_url}')">
                <img src="${product.image_url || '/static/images/placeholder.jpg'}" alt="${this.escapeHtml(product.name)}">
                <div class="product-item-info">
                    <h6>${this.escapeHtml(product.name)}</h6>
                    <p class="product-item-price">Rp ${this.formatPrice(product.price)}</p>
                    <p>${this.escapeHtml(product.brand || '')}</p>
                </div>
            </div>
        `).join('');
    }

    selectProduct(id, name, price, imageUrl) {
        this.selectedProduct = { id, name, price, imageUrl };
        this.showProductTagPreview();

        // Close modal
        const modal = bootstrap.Modal.getInstance(document.getElementById('product-selector-modal'));
        if (modal) modal.hide();
    }

    showProductTagPreview() {
        const preview = document.getElementById('product-tag-preview');
        const image = document.getElementById('tagged-product-image');
        const name = document.getElementById('tagged-product-name');
        const price = document.getElementById('tagged-product-price');

        if (this.selectedProduct) {
            image.src = this.selectedProduct.imageUrl || '/static/images/placeholder.jpg';
            name.textContent = this.selectedProduct.name;
            price.textContent = `Rp ${this.formatPrice(this.selectedProduct.price)}`;
            preview.style.display = 'block';
        }
    }

    clearProductTag() {
        this.selectedProduct = null;
        const preview = document.getElementById('product-tag-preview');
        preview.style.display = 'none';
    }

    formatPrice(price) {
        return new Intl.NumberFormat('id-ID').format(price);
    }

    formatTime(timestamp) {
        try {
            let date;

            if (!timestamp) {
                date = new Date();
            } else if (typeof timestamp === 'string') {
                // Handle ISO strings, timestamp with timezone, and other formats
                if (timestamp.includes('T') || timestamp.includes('-')) {
                    // ISO format or date string - parse directly
                    date = new Date(timestamp);
                } else if (!isNaN(timestamp)) {
                    // Unix timestamp string
                    date = new Date(parseInt(timestamp) * (timestamp.length === 10 ? 1000 : 1));
                } else {
                    // Try direct parsing
                    date = new Date(timestamp);
                }
            } else if (typeof timestamp === 'number') {
                // Unix timestamp - check if seconds or milliseconds
                date = new Date(timestamp * (timestamp.toString().length === 10 ? 1000 : 1));
            } else {
                date = new Date(timestamp);
            }

            // Validate the date
            if (!date || isNaN(date.getTime()) || date.getTime() === 0) {
                console.warn('Invalid timestamp, using current time:', timestamp);
                date = new Date();
            }

            // Ensure we have a reasonable date (not too far in past/future)
            const now = new Date();
            const diffYears = Math.abs(now.getFullYear() - date.getFullYear());
            if (diffYears > 10) {
                console.warn('Timestamp too far from current time, using current time:', timestamp);
                date = new Date();
            }

            return date.toLocaleTimeString('id-ID', {
                hour: '2-digit',
                minute: '2-digit'
            });
        } catch (error) {
            console.error('Error formatting time:', error, 'timestamp:', timestamp);
            return new Date().toLocaleTimeString('id-ID', {
                hour: '2-digit',
                minute: '2-digit'
            });
        }
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Global functions for HTML onclick events
function toggleChat() {
    const chatWindow = document.getElementById('chat-window');
    const isVisible = chatWindow.style.display !== 'none';

    if (isVisible) {
        chatWindow.style.display = 'none';
    } else {
        chatWindow.style.display = 'block';
        // Reset unread count when opening chat
        if (window.floatingChat) {
            window.floatingChat.unreadCount = 0;
            window.floatingChat.updateChatBadge();
        }
    }
}

function handleChatKeyPress(event) {
    if (window.floatingChat) {
        window.floatingChat.handleChatKeyPress(event);
    }
}

function sendChatMessage() {
    if (window.floatingChat) {
        window.floatingChat.sendChatMessage();
    }
}

function handleTyping() {
    if (window.floatingChat) {
        window.floatingChat.handleTyping();
    }
}

function showProductSelector() {
    const modal = new bootstrap.Modal(document.getElementById('product-selector-modal'));
    modal.show();
}

function searchProducts() {
    if (window.floatingChat) {
        window.floatingChat.searchProducts();
    }
}

function clearProductTag() {
    if (window.floatingChat) {
        window.floatingChat.clearProductTag();
    }
}

// Request notification permission
if (Notification.permission === 'default') {
    Notification.requestPermission();
}

// Initialize chat when page loads
window.floatingChat = new FloatingChat();