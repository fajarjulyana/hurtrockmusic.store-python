/**
 * Admin Chat Interface - JavaScript Handler
 * Handles admin chat functionality for customer service
 */

class AdminChat {
    constructor() {
        this.ws = null;
        this.chatToken = null;
        this.currentUser = null;
        this.isConnected = false;
        this.selectedRoomId = null;
        this.rooms = new Map();
        this.unreadCount = 0;
        this.selectedProduct = null;
        this.productSearchTimer = null;
        this.typingTimer = null; // Added typingTimer

        // Initialize when DOM is ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.init());
        } else {
            this.init();
        }
    }

    async init() {
        try {
            await this.getCurrentUser();
            if (this.currentUser) {
                await this.getChatToken();
                this.setupEventListeners();
                this.loadChatRooms();
                // Removed initial setupWebSocket() call here, as it's handled in selectBuyerRoom
                this.updateConnectionStatus('connecting'); // Set initial status to connecting
            }
        } catch (error) {
            console.error('Failed to initialize admin chat:', error);
            this.displaySystemMessage('Gagal menginisialisasi chat admin', 'error');
        }
    }

    async getCurrentUser() {
        try {
            const userDataElement = document.querySelector('#user-data');
            if (userDataElement) {
                this.currentUser = {
                    id: userDataElement.dataset.userId,
                    name: userDataElement.dataset.userName,
                    email: userDataElement.dataset.userEmail,
                    role: userDataElement.dataset.userRole
                };
            } else {
                throw new Error('User data not found');
            }
        } catch (error) {
            console.error('Error getting current user:', error);
            throw error;
        }
    }

    async getChatToken() {
        try {
            const response = await fetch('/api/chat/token');
            if (response.ok) {
                const data = await response.json();
                this.chatToken = data.token;
            } else {
                throw new Error('Failed to get chat token');
            }
        } catch (error) {
            console.error('Error getting chat token:', error);
            throw error;
        }
    }

    // Removed the original setupWebSocket method as it's replaced by setupWebSocketForRoom

    handleWebSocketMessage(data) {
        console.log('Admin received WebSocket message:', data);
        
        switch (data.type) {
            case 'connection_established':
                console.log('Admin chat connection established:', data.message);
                break;

            case 'chat_message':
                // Ensure message object has sender_type or infer it
                if (data.message && typeof data.message === 'object') {
                     if (!data.message.sender_type) {
                        // Infer sender_type if not present, assuming admin if sender_id matches admin's id
                        if (data.message.user_id == this.currentUser.id) {
                            data.message.sender_type = 'admin';
                        } else {
                            data.message.sender_type = 'customer';
                        }
                    }
                    this.displayMessage(data.message);
                    if (data.message.user_id != this.currentUser.id) {
                        this.incrementUnreadCount();
                    }
                    this.updateRoomLastMessage(data.message); // Update last message in the room list
                } else {
                    console.error('Received malformed chat_message data:', data);
                }
                break;

            case 'typing_indicator': // Renamed from 'typing' to 'typing_indicator' for consistency
                this.updateTypingIndicator(data);
                break;

            case 'error':
                console.error('Admin chat error:', data.message);
                this.displaySystemMessage(data.message, 'error');
                break;

            default:
                console.log('Unknown admin message type:', data);
        }
    }

    updateConnectionStatus(status) {
        const statusElement = document.getElementById('connection-status-admin');
        if (statusElement) {
            statusElement.className = `connection-status-admin ${status}`;
            switch (status) {
                case 'connected':
                    statusElement.innerHTML = '<i class="fas fa-wifi"></i> Terhubung';
                    break;
                case 'connecting':
                    statusElement.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Menghubungkan...';
                    break;
                case 'disconnected':
                    // Changed message for clarity on reconnection attempt
                    statusElement.innerHTML = '<i class="fas fa-wifi"></i> Terputus - mencoba menyambung kembali...';
                    break;
                case 'error':
                    statusElement.innerHTML = '<i class="fas fa-exclamation-triangle"></i> Koneksi bermasalah';
                    break;
            }
        }
    }

    setupEventListeners() {
        // Admin message input
        const messageInput = document.getElementById('admin-message-input');
        if (messageInput) {
            messageInput.addEventListener('keypress', (e) => this.handleAdminKeyPress(e));
            messageInput.addEventListener('input', () => this.handleAdminTyping());
        }

        // Send button
        const sendBtn = document.querySelector('.chat-input-container .btn-orange');
        if (sendBtn) {
            sendBtn.addEventListener('click', () => this.sendAdminMessage());
        }

        // Setup buyer search
        this.setupBuyerSearch();
        // Setup product search listener
        this.setupProductSearch();
    }

    handleAdminKeyPress(event) {
        if (event.key === 'Enter' && !event.shiftKey) {
            event.preventDefault();
            this.sendAdminMessage();
        }
    }

    sendAdminMessage() {
        const messageInput = document.getElementById('admin-message-input');
        const message = messageInput.value.trim();

        if (!message) return;

        if (!this.isConnected) {
            this.displaySystemMessage('Chat tidak terhubung. Silakan coba lagi.', 'warning');
            // Attempt to reconnect if not connected
            if (!this.ws || this.ws.readyState === WebSocket.CLOSED) {
                this.setupWebSocketForRoom(this.selectedRoomId); // Reconnect to the current room
            }
            return;
        }

        const messageData = {
            type: 'chat_message',
            message: message,
            // Ensure sender info is included if needed by the backend
            // user_id: this.currentUser.id,
            // user_name: this.currentUser.name,
            // sender_type: 'admin'
        };

        // Add product information if there's a product preview
        const productPreview = document.getElementById('product-preview-admin');
        if (productPreview && productPreview.style.display !== 'none') {
            const productId = productPreview.dataset.productId;
            if (productId) {
                messageData.product_id = parseInt(productId);
            }
        }

        this.ws.send(JSON.stringify(messageData));
        messageInput.value = '';

        // Clear product preview after sending
        this.clearProductPreview();
        // Optionally, clear typing indicator after sending message
        this.handleAdminTyping(); // Send typing false
    }

    handleAdminTyping() {
        if (!this.isConnected || !this.ws) return;

        // Send typing start indicator
        this.ws.send(JSON.stringify({
            type: 'typing_indicator', // Use 'typing_indicator'
            is_typing: true,
            user_name: this.currentUser.name // Include user name
        }));

        // Clear existing timer
        if (this.typingTimer) {
            clearTimeout(this.typingTimer);
        }

        // Send typing stop indicator after 2 seconds
        this.typingTimer = setTimeout(() => {
            if (this.isConnected && this.ws && this.ws.readyState === WebSocket.OPEN) {
                this.ws.send(JSON.stringify({
                    type: 'typing_indicator', // Use 'typing_indicator'
                    is_typing: false,
                    user_name: this.currentUser.name // Include user name
                }));
            }
        }, 2000);
    }

    displayMessage(data) {
        const messagesWrapper = document.getElementById('messages-wrapper');
        if (!messagesWrapper) return;

        // Show active chat if hidden
        this.showActiveChat();

        const messageDiv = document.createElement('div');
        // Determine if the message is from the admin or customer
        const isAdmin = data.sender_type === 'admin' || data.sender_type === 'staff' || (data.user_id == this.currentUser.id);
        messageDiv.className = `chat-message ${isAdmin ? 'admin-message' : 'customer-message'}`;

        const avatarClass = isAdmin ? 'admin' : 'customer';

        let productTagHtml = '';
        // Check if product_info is available to display product tag
        if (data.product_info) {
            const productName = this.escapeHtml(data.product_info.name || 'Unknown Product');
            const productPrice = data.product_info.price !== undefined ? new Intl.NumberFormat('id-ID').format(data.product_info.price) : 'N/A';
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
        } else if (data.product_id && !data.product_info) {
            productTagHtml = `
                <div class="product-tag-placeholder" style="background: rgba(255,255,255,0.1); padding: 8px; border-radius: 6px; margin-top: 8px;">
                    <small>Produk #${data.product_id}</small>
                </div>
            `;
        }

        // Use provided user_name, fallback to current user's name for admin, or 'Customer' for customer
        const senderName = data.user_name || (isAdmin ? this.currentUser.name : 'Customer');
        const messageTimestamp = data.timestamp || data.created_at || new Date().toISOString();
        const formattedTimestamp = this.formatTime(messageTimestamp);

        messageDiv.innerHTML = `
            <div class="message-avatar ${avatarClass}">
                <i class="fas fa-${isAdmin ? 'user-tie' : 'user-circle'}"></i>
            </div>
            <div class="message-content">
                ${this.escapeHtml(data.message)}
                ${productTagHtml}
                <div class="message-meta">
                    <strong>${this.escapeHtml(senderName)}</strong> • ${formattedTimestamp}
                </div>
            </div>
        `;

        messagesWrapper.appendChild(messageDiv);
        messagesWrapper.scrollTop = messagesWrapper.scrollHeight;
    }

    displaySystemMessage(message, type = 'info') {
        const messagesWrapper = document.getElementById('messages-wrapper');
        if (!messagesWrapper) return;

        const messageDiv = document.createElement('div');
        messageDiv.className = `chat-message system ${type}`;
        messageDiv.innerHTML = `
            <div class="message-content system-message">
                <i class="fas fa-info-circle"></i>
                ${this.escapeHtml(message)}
            </div>
        `;
        messagesWrapper.appendChild(messageDiv);
        messagesWrapper.scrollTop = messagesWrapper.scrollHeight;
    }

    showActiveChat() {
        const noChat = document.getElementById('no-chat-selected');
        const activeChat = document.getElementById('active-chat');

        if (noChat) noChat.style.display = 'none';
        if (activeChat) activeChat.style.display = 'flex';
    }

    updateTypingIndicator(data) {
        const typingIndicator = document.getElementById('typing-indicator-admin');
        const typingUserNameSpan = document.getElementById('typing-user-name');
        if (!typingIndicator || !typingUserNameSpan) return;

        // Check if the typing event is from someone else and if they are typing
        if (data.is_typing && data.user_name && data.user_name !== this.currentUser.name) {
            typingUserNameSpan.textContent = data.user_name;
            typingIndicator.style.display = 'flex';
        } else {
            typingIndicator.style.display = 'none';
        }
    }

    incrementUnreadCount() {
        this.unreadCount++;
        this.updateUnreadBadge();
    }

    updateUnreadBadge() {
        const badge = document.getElementById('unread-count');
        if (badge) {
            badge.textContent = this.unreadCount;
            badge.style.display = this.unreadCount > 0 ? 'inline' : 'none';
        }
    }

    async loadChatRooms(searchQuery = '') {
        try {
            const url = `/api/admin/buyer-rooms/${searchQuery ? `?search=${encodeURIComponent(searchQuery)}` : ''}`;
            const response = await fetch(url, {
                headers: {
                    'Authorization': `Bearer ${this.chatToken}`
                }
            });

            if (response.ok) {
                const data = await response.json();
                this.displayChatRooms(data.rooms);
            } else {
                console.error('Failed to load chat rooms');
                this.displayChatRooms([]);
            }
        } catch (error) {
            console.error('Error loading chat rooms:', error);
            this.displayChatRooms([]);
        }
    }

    displayChatRooms(rooms) {
        const roomsList = document.getElementById('chat-rooms-list');
        if (!roomsList) return;

        if (rooms.length === 0) {
            roomsList.innerHTML = `
                <div class="text-center p-4 text-muted">
                    <i class="fas fa-inbox fa-3x mb-3"></i>
                    <p>Belum ada percakapan dari buyer</p>
                </div>
            `;
            return;
        }

        roomsList.innerHTML = rooms.map(room => {
            const lastMessage = room.last_message;
            const timeAgo = lastMessage ? this.getTimeAgo(lastMessage.timestamp) : 'Belum ada pesan';
            const unreadBadge = room.unread_count > 0 ? `<span class="unread-count">${room.unread_count}</span>` : '';

            return `
                <div class="chat-room-item ${room.unread_count > 0 ? 'unread' : ''}"
                     onclick="adminChat.selectBuyerRoom('${room.name}', '${room.buyer_name}', '${room.buyer_email}', ${room.buyer_id})">
                    <div class="room-header">
                        <div class="customer-name">${this.escapeHtml(room.buyer_name)}</div>
                        ${unreadBadge}
                    </div>
                    <div class="customer-email">${this.escapeHtml(room.buyer_email)}</div>
                    <div class="last-message">${lastMessage ? this.escapeHtml(lastMessage.content) : 'Belum ada pesan'}</div>
                    <div class="message-time">${timeAgo}</div>
                </div>
            `;
        }).join('');
    }

    getTimeAgo(timestamp) {
        const now = new Date();
        const messageTime = new Date(timestamp);
        const diffMs = now - messageTime;
        const diffMins = Math.floor(diffMs / 60000);
        const diffHours = Math.floor(diffMs / 3600000);
        const diffDays = Math.floor(diffMs / 86400000);

        if (diffMins < 1) return 'Baru saja';
        if (diffMins < 60) return `${diffMins} menit lalu`;
        if (diffHours < 24) return `${diffHours} jam lalu`;
        if (diffDays < 7) return `${diffDays} hari lalu`;

        return messageTime.toLocaleDateString('id-ID');
    }

    // Removed the original selectRoom method

    selectBuyerRoom(roomName, buyerName, buyerEmail, buyerId) {
        this.selectedRoomId = roomName;
        this.currentBuyer = { id: buyerId, name: buyerName, email: buyerEmail };

        // Disconnect from current room if connected
        if (this.ws && this.isConnected) {
            this.ws.close();
        }

        // Connect to buyer's room
        this.setupWebSocketForRoom(roomName);
        this.showActiveChat();

        // Update customer info
        const customerName = document.getElementById('customer-name');
        const customerStatus = document.getElementById('customer-status');

        if (customerName) customerName.textContent = buyerName;
        // Update customer status to display email or other relevant info
        if (customerStatus) customerStatus.textContent = buyerEmail;


        // Mark messages as read (this functionality might need to be triggered after loading messages)
        // this.markRoomAsRead(roomName); // Moved to after successful connection and message load

        // Update room selection UI
        this.updateRoomSelection(roomName);
    }

    setupWebSocketForRoom(roomName) {
        if (!this.chatToken) {
            console.error('No chat token available');
            return;
        }

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

        console.log('Admin connecting to WebSocket:', wsUrl);

        try {
            this.ws = new WebSocket(wsUrl);

            this.ws.onopen = (event) => {
                console.log('Admin WebSocket connected to buyer room');
                this.isConnected = true;
                this.updateConnectionStatus('connected');
                this.loadChatHistory(roomName); // Load history upon connection
                this.markRoomAsRead(roomName); // Mark as read after history is loaded
            };

            this.ws.onmessage = (event) => {
                const data = JSON.parse(event.data);
                this.handleWebSocketMessage(data);
            };

            this.ws.onclose = (event) => {
                console.log('Admin WebSocket closed:', event.code, event.reason);
                this.isConnected = false;
                this.updateConnectionStatus('disconnected');
                // Attempt to reconnect if the room is still selected
                if (this.selectedRoomId === roomName) {
                    setTimeout(() => this.setupWebSocketForRoom(roomName), 5000); // Reconnect after 5 seconds
                }
            };

            this.ws.onerror = (error) => {
                console.error('Admin WebSocket error:', error);
                this.updateConnectionStatus('error');
            };

        } catch (error) {
            console.error('Error creating admin WebSocket for buyer room:', error);
            this.updateConnectionStatus('error');
        }
    }

    async markRoomAsRead(roomName) {
        try {
            const response = await fetch(`/api/rooms/${roomName}/mark-read/`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${this.chatToken}`,
                    'Content-Type': 'application/json'
                }
            });
            if (!response.ok) {
                 console.error(`Failed to mark room ${roomName} as read`);
            }
        } catch (error) {
            console.error('Error marking room as read:', error);
        }
    }

    async loadChatHistory(roomName) {
        try {
            const messagesWrapper = document.getElementById('messages-wrapper');
            if (messagesWrapper) {
                messagesWrapper.innerHTML = ''; // Clear previous messages
            }

            const response = await fetch(`/api/rooms/${roomName}/messages/`, {
                headers: {
                    'Authorization': `Bearer ${this.chatToken}`,
                    'Content-Type': 'application/json'
                }
            });

            if (response.ok) {
                const data = await response.json();
                console.log('Admin chat history loaded:', data);

                const messages = data.results || data; // Handle pagination if present (data.results) or flat list
                if (Array.isArray(messages)) {
                    messages.forEach(message => {
                        // Ensure message object is properly structured before displaying
                         if (message && typeof message === 'object') {
                             this.displayMessage(message);
                         }
                    });
                } else {
                    console.error("Received non-array message data:", messages);
                }
            } else {
                 console.error(`Failed to load messages for room ${roomName}. Status: ${response.status}`);
            }
        } catch (error) {
            console.error('Error loading room messages:', error);
        }
    }

    updateRoomSelection(selectedRoomName) {
        const roomItems = document.querySelectorAll('.chat-room-item');
        roomItems.forEach(item => {
            item.classList.remove('active');
            // Check if the room name matches the selected room
            // The onclick attribute contains the room name
            if (item.getAttribute('onclick') && item.getAttribute('onclick').includes(`'${selectedRoomName}'`)) {
                item.classList.add('active');
                item.classList.remove('unread'); // Remove unread status when selected
            }
        });
    }

    setupBuyerSearch() {
        const searchInput = document.getElementById('buyer-search');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => {
                const query = e.target.value.trim();
                clearTimeout(this.searchTimer);
                this.searchTimer = setTimeout(() => {
                    this.loadChatRooms(query);
                }, 300);
            });
        }
    }

    updateRoomLastMessage(messageData) {
        // Find the room item in the list and update its last message and time
        const roomList = document.getElementById('chat-rooms-list');
        if (!roomList || !messageData || !this.selectedRoomId) return;

        const roomItem = Array.from(roomList.children).find(item =>
            item.getAttribute('onclick').includes(`'${this.selectedRoomId}'`)
        );

        if (roomItem) {
            const lastMessageElement = roomItem.querySelector('.last-message');
            const messageTimeElement = roomItem.querySelector('.message-time');
            const unreadBadgeElement = roomItem.querySelector('.unread-count');

            if (lastMessageElement) {
                lastMessageElement.textContent = this.escapeHtml(messageData.message);
            }
            if (messageTimeElement) {
                // Update time using getTimeAgo for consistency
                messageTimeElement.textContent = this.getTimeAgo(messageData.timestamp || new Date().toISOString());
            }

            // Handle unread count update if this message is from the customer to the currently selected room
            if (!this.isAdminMessage(messageData) && this.selectedRoomId === messageData.room_name) {
                 let currentUnread = parseInt(unreadBadgeElement?.textContent || '0', 10);
                 currentUnread++;
                 if (unreadBadgeElement) {
                    unreadBadgeElement.textContent = currentUnread;
                    unreadBadgeElement.style.display = 'inline';
                 } else {
                     // If badge doesn't exist, create it
                     const newBadge = document.createElement('span');
                     newBadge.className = 'unread-count';
                     newBadge.textContent = currentUnread;
                     roomItem.querySelector('.room-header').appendChild(newBadge);
                 }
                 roomItem.classList.add('unread');
            }
        }
    }

    // Helper to determine if a message is from the admin
    isAdminMessage(message) {
        return message.sender_type === 'admin' || message.sender_type === 'staff' || (message.user_id == this.currentUser.id);
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
        // Ensure text is a string, handle null/undefined gracefully
        div.textContent = String(text || '');
        return div.innerHTML;
    }

    setupProductSearch() {
        const searchInput = document.getElementById('product-search-input');
        const confirmBtn = document.getElementById('confirm-product-selection');

        if (!searchInput || !confirmBtn) return;

        // Product search functionality
        searchInput.addEventListener('input', (e) => {
            const query = e.target.value.trim();

            clearTimeout(this.productSearchTimer);

            if (query.length < 2) {
                document.getElementById('product-search-results').innerHTML = `
                    <div class="text-center p-4 text-muted">
                        <i class="fas fa-search fa-2x mb-3"></i>
                        <p>Ketik minimal 2 karakter untuk mencari produk</p>
                    </div>
                `;
                return;
            }

            this.productSearchTimer = setTimeout(() => {
                this.searchProducts(query);
            }, 500);
        });

        // Confirm button functionality
        confirmBtn.addEventListener('click', () => {
            if (this.selectedProduct) {
                this.showProductPreview(this.selectedProduct);
                const modalElement = document.getElementById('productSelectorModal');
                if (modalElement) {
                    const modal = bootstrap.Modal.getInstance(modalElement);
                    if (modal) {
                        modal.hide();
                    }
                }
            }
        });
    }

    async searchProducts(query) {
        try {
            const resultsContainer = document.getElementById('product-search-results');
            if (!resultsContainer) return;

            resultsContainer.innerHTML = `
                <div class="text-center p-4">
                    <i class="fas fa-spinner fa-spin fa-2x mb-3"></i>
                    <p>Mencari produk...</p>
                </div>
            `;

            const response = await fetch(`/search?q=${encodeURIComponent(query)}`);

            if (response.ok) {
                const products = await response.json();
                this.displayProductResults(products);
            } else {
                throw new Error(`Search failed with status ${response.status}`);
            }
        } catch (error) {
            console.error('Product search error:', error);
            document.getElementById('product-search-results').innerHTML = `
                <div class="text-center p-4 text-muted">
                    <i class="fas fa-exclamation-triangle fa-2x mb-3"></i>
                    <p>Gagal mencari produk. Silakan coba lagi.</p>
                </div>
            `;
        }
    }

    displayProductResults(products) {
        const resultsContainer = document.getElementById('product-search-results');
        if (!resultsContainer) return;

        if (products.length === 0) {
            resultsContainer.innerHTML = `
                <div class="text-center p-4 text-muted">
                    <i class="fas fa-inbox fa-2x mb-3"></i>
                    <p>Tidak ada produk yang ditemukan</p>
                </div>
            `;
            return;
        }

        resultsContainer.innerHTML = products.map(product => `
            <div class="product-item" onclick="adminChat.selectProduct(${product.id}, this)">
                <img src="${product.image_url || '/static/images/placeholder.jpg'}" alt="${this.escapeHtml(product.name)}" class="product-item-image">
                <div class="product-item-info">
                    <div class="product-item-brand">${this.escapeHtml(product.brand)}</div>
                    <h6 class="product-item-name">${this.escapeHtml(product.name)}</h6>
                    <p class="product-item-price">Rp ${new Intl.NumberFormat('id-ID').format(product.price)}</p>
                    <p class="product-item-description">${this.escapeHtml(product.description)}</p>
                </div>
            </div>
        `).join('');
    }

    selectProduct(productId, element) {
        // Remove previous selection
        document.querySelectorAll('.product-item').forEach(item => {
            item.classList.remove('selected');
        });

        // Add selection to clicked item
        element.classList.add('selected');

        // Store selected product data
        const productInfo = {
            id: productId,
            name: element.querySelector('.product-item-name').textContent,
            brand: element.querySelector('.product-item-brand').textContent,
            price: parseFloat(element.querySelector('.product-item-price').textContent.replace('Rp ', '').replace(/\./g, '').replace(',', '.')), // Handle potential locale issues for price
            image_url: element.querySelector('.product-item-image').src,
            description: element.querySelector('.product-item-description').textContent
        };

        this.selectedProduct = productInfo;

        // Enable confirm button
        document.getElementById('confirm-product-selection').disabled = false;
    }

    showProductPreview(product) {
        const preview = document.getElementById('product-preview-admin');
        const previewImage = document.getElementById('preview-product-image');
        const previewName = document.getElementById('preview-product-name');
        const previewPrice = document.getElementById('preview-product-price');

        if (preview && previewImage && previewName && previewPrice) {
            previewImage.src = product.image_url;
            previewImage.alt = product.name;
            previewName.textContent = product.name;
            previewPrice.textContent = `Rp ${new Intl.NumberFormat('id-ID').format(product.price)}`;

            // Store product ID for message sending
            preview.dataset.productId = product.id;
            preview.style.display = 'block';
        }
    }

    clearProductPreview() {
        const preview = document.getElementById('product-preview-admin');
        if (preview) {
            preview.style.display = 'none';
            // Use delete or set to null/undefined for clarity
            delete preview.dataset.productId;
        }
        this.selectedProduct = null;
    }
}

// Global functions for HTML onclick events
function handleAdminKeyPress(event) {
    if (window.adminChat) {
        window.adminChat.handleAdminKeyPress(event);
    }
}

function sendAdminMessage() {
    if (window.adminChat) {
        window.adminChat.sendAdminMessage();
    }
}

function handleAdminTyping() {
    if (window.adminChat) {
        window.adminChat.handleAdminTyping();
    }
}

function loadCustomerInfo() {
    // Placeholder for customer info functionality, no changes needed based on provided snippet
    console.log('Load customer info clicked');
}

function markAsResolved() {
    // Placeholder for mark as resolved functionality, no changes needed based on provided snippet
    console.log('Mark as resolved clicked');
}

function showProductSelector() {
    const modalElement = document.getElementById('productSelectorModal');
    if (modalElement) {
        const modal = new bootstrap.Modal(modalElement);
        modal.show();

        // Reset the modal state
        const searchInput = document.getElementById('product-search-input');
        const searchResults = document.getElementById('product-search-results');
        const confirmBtn = document.getElementById('confirm-product-selection');

        if (searchInput) searchInput.value = '';
        if (searchResults) {
             searchResults.innerHTML = `
                <div class="text-center p-4 text-muted">
                    <i class="fas fa-search fa-2x mb-3"></i>
                    <p>Ketik minimal 2 karakter untuk mencari produk</p>
                </div>
            `;
        }
        if (confirmBtn) confirmBtn.disabled = true;
        if (window.adminChat) window.adminChat.selectedProduct = null;

        // Setup product search event listeners inside the modal
        if (window.adminChat) {
            window.adminChat.setupProductSearch();
        }
    }
}

function sendQuickReply(message) {
    const messageInput = document.getElementById('admin-message-input');
    if (messageInput) {
        messageInput.value = message;
        // Use the global sendAdminMessage function
        sendAdminMessage();
    }
}

function clearProductPreview() {
    if (window.adminChat) {
        window.adminChat.clearProductPreview();
    }
}

// Initialize admin chat when page loads
window.adminChat = new AdminChat();