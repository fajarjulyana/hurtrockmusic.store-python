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
                const response = await fetch('/api/chat/token');
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

    async getChatToken() {
        try {
            const response = await fetch('/api/chat/token');
            if (response.ok) {
                const data = await response.json();
                this.chatToken = data.token;
                this.currentUser = data.user;
            } else {
                throw new Error('Failed to get chat token');
            }
        } catch (error) {
            console.error('Error getting chat token:', error);
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

        const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        let wsUrl;

        // Adjust host for Replit environment
        if (window.location.hostname.includes('replit.dev')) {
            // For Replit deployment - use same hostname with port 8000
            let wsHost = window.location.hostname.replace(/:\d+/, '');
            wsUrl = `${wsProtocol}//${wsHost}:8000/ws/chat/${roomName}/?token=${this.chatToken}`;
        } else {
            // Local development environment
            wsUrl = `ws://127.0.0.1:8000/ws/chat/${roomName}/?token=${this.chatToken}`;
        }

        console.log('Buyer connecting to WebSocket:', wsUrl);

        try {
            this.ws = new WebSocket(wsUrl);

            this.ws.onopen = (event) => {
                console.log('WebSocket connected');
                this.isConnected = true;
                this.updateConnectionStatus('connected');
                this.loadChatHistory(); // Load history upon connection
            };

            this.ws.onmessage = (event) => {
                const data = JSON.parse(event.data);
                this.handleWebSocketMessage(data);
            };

            this.ws.onclose = (event) => {
                console.log('WebSocket closed:', event.code, event.reason);
                this.isConnected = false;
                this.updateConnectionStatus('disconnected');
                // Attempt to reconnect after 5 seconds
                setTimeout(() => this.setupWebSocket(), 5000);
            };

            this.ws.onerror = (error) => {
                console.error('WebSocket error:', error);
                this.updateConnectionStatus('error');
            };

        } catch (error) {
            console.error('Error creating WebSocket:', error);
            this.updateConnectionStatus('error');
        }
    }

    handleWebSocketMessage(data) {
        console.log('Buyer received WebSocket message:', data);

        switch (data.type) {
            case 'connection_established':
                console.log('Chat connection established:', data.message);
                break;

            case 'chat_message':
                if (data.message && typeof data.message === 'object') {
                    this.displayMessage(data.message);
                } else {
                    console.error('Received malformed chat_message data:', data);
                }
                break;

            case 'typing_indicator':
                this.updateTypingIndicator(data);
                break;

            case 'error':
                console.error('Chat error:', data.message);
                this.displaySystemMessage(data.message, 'error');
                break;

            default:
                console.log('Unknown message type:', data);
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
                <div class="product-tag" onclick="window.open('${productUrl}', '_blank')" style="cursor: pointer;">
                    <img src="${productImage}" alt="${productName}" onerror="this.src='/static/images/placeholder.jpg'">
                    <div class="product-tag-info">
                        <h6>${productName}</h6>
                        <p>Rp ${productPrice}</p>
                        <small>Klik untuk lihat detail</small>
                    </div>
                </div>
            `;
        } else if (data.product_id) {
            productTagHtml = `
                <div class="product-tag">
                    <img src="/static/images/placeholder.jpg" alt="Product" onerror="this.src='/static/images/placeholder.jpg'">
                    <div class="product-tag-info">
                        <h6>Produk #${data.product_id}</h6>
                        <p>Klik untuk lihat detail</p>
                    </div>
                </div>
            `;
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
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
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
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
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
            const response = await fetch(`/api/rooms/${roomName}/messages/`, {
                headers: {
                    'Authorization': `Bearer ${this.chatToken}`,
                    'Content-Type': 'application/json'
                }
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
            } else {
                console.error('Failed to load chat history');
            }
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
        if (!timestamp) {
            const now = new Date();
            return now.toLocaleTimeString('id-ID', {
                hour: '2-digit',
                minute: '2-digit'
            });
        }

        try {
            // Handle different timestamp formats
            let date;
            if (typeof timestamp === 'string') {
                // Remove any timezone info and parse
                const cleanTimestamp = timestamp.replace(/\+.*$/, '').replace(/Z$/, '');
                date = new Date(cleanTimestamp);
            } else {
                date = new Date(timestamp);
            }

            // Check if date is valid
            if (isNaN(date.getTime())) {
                console.warn('Invalid timestamp received:', timestamp);
                const now = new Date();
                return now.toLocaleTimeString('id-ID', {
                    hour: '2-digit',
                    minute: '2-digit'
                });
            }

            return date.toLocaleTimeString('id-ID', {
                hour: '2-digit',
                minute: '2-digit'
            });
        } catch (error) {
            console.error('Error formatting time:', error, timestamp);
            const now = new Date();
            return now.toLocaleTimeString('id-ID', {
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