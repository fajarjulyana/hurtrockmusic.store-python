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
        
        // Enhanced product tag handling for both admin and buyer messages
        if (data.product_info || data.product_id) {
            if (data.product_info) {
                // Full product info available
                const productName = this.escapeHtml(data.product_info.name || 'Unknown Product');
                const productPrice = data.product_info.price !== undefined ? 
                    new Intl.NumberFormat('id-ID').format(data.product_info.price) : 'N/A';
                const productImage = data.product_info.image_url || '/static/images/placeholder.jpg';
                const productUrl = `/product/${data.product_info.id}`;

                productTagHtml = `
                    <div class="product-tag" onclick="window.open('${productUrl}', '_blank')" 
                         style="cursor: pointer; background: ${isAdmin ? 'rgba(255,255,255,0.9)' : '#f8f9fa'}; 
                         border: 1px solid ${isAdmin ? '#ddd' : '#e9ecef'}; border-radius: 8px; padding: 12px; 
                         margin-top: 12px; display: flex; align-items: center; gap: 12px;">
                        <img src="${productImage}" alt="${productName}" 
                             onerror="this.src='/static/images/placeholder.jpg'"
                             style="width: 50px; height: 50px; object-fit: cover; border-radius: 6px; flex-shrink: 0;">
                        <div class="product-tag-info" style="flex: 1; min-width: 0;">
                            <h6 style="margin: 0 0 4px; font-size: 14px; color: ${isAdmin ? '#2d3748' : '#1a202c'}; 
                                       font-weight: 600; line-height: 1.2; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">${productName}</h6>
                            <p style="margin: 0 0 4px; font-size: 13px; color: ${isAdmin ? '#4299e1' : '#3182ce'}; 
                                      font-weight: 600;">Rp ${productPrice}</p>
                            <small style="color: ${isAdmin ? '#718096' : '#4a5568'}; font-size: 11px;">
                                <i class="fas fa-external-link-alt" style="margin-right: 4px;"></i>
                                Klik untuk lihat detail
                            </small>
                        </div>
                    </div>
                `;
            } else if (data.product_id) {
                // Only product ID available, try to fetch product info
                this.fetchProductInfo(data.product_id).then(productInfo => {
                    if (productInfo) {
                        // Update the message with full product info
                        const existingTag = messageDiv.querySelector('.product-tag-placeholder');
                        if (existingTag) {
                            const productName = this.escapeHtml(productInfo.name || 'Unknown Product');
                            const productPrice = productInfo.price !== undefined ? 
                                new Intl.NumberFormat('id-ID').format(productInfo.price) : 'N/A';
                            const productImage = productInfo.image_url || '/static/images/placeholder.jpg';
                            const productUrl = `/product/${productInfo.id}`;

                            existingTag.outerHTML = `
                                <div class="product-tag" onclick="window.open('${productUrl}', '_blank')" 
                                     style="cursor: pointer; background: ${isAdmin ? 'rgba(255,255,255,0.9)' : '#f8f9fa'}; 
                                     border: 1px solid ${isAdmin ? '#ddd' : '#e9ecef'}; border-radius: 8px; padding: 12px; 
                                     margin-top: 12px; display: flex; align-items: center; gap: 12px;">
                                    <img src="${productImage}" alt="${productName}" 
                                         onerror="this.src='/static/images/placeholder.jpg'"
                                         style="width: 50px; height: 50px; object-fit: cover; border-radius: 6px; flex-shrink: 0;">
                                    <div class="product-tag-info" style="flex: 1; min-width: 0;">
                                        <h6 style="margin: 0 0 4px; font-size: 14px; color: ${isAdmin ? '#2d3748' : '#1a202c'}; 
                                                   font-weight: 600; line-height: 1.2; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">${productName}</h6>
                                        <p style="margin: 0 0 4px; font-size: 13px; color: ${isAdmin ? '#4299e1' : '#3182ce'}; 
                                                  font-weight: 600;">Rp ${productPrice}</p>
                                        <small style="color: ${isAdmin ? '#718096' : '#4a5568'}; font-size: 11px;">
                                            <i class="fas fa-external-link-alt" style="margin-right: 4px;"></i>
                                            Klik untuk lihat detail
                                        </small>
                                    </div>
                                </div>
                            `;
                        }
                    }
                });

                // Show placeholder while loading
                productTagHtml = `
                    <div class="product-tag-placeholder" style="background: ${isAdmin ? 'rgba(255,255,255,0.8)' : 'rgba(66, 153, 225, 0.1)'}; 
                         border: 1px solid ${isAdmin ? '#cbd5e0' : '#bee3f8'}; border-radius: 6px; padding: 8px; 
                         margin-top: 8px; display: flex; align-items: center; gap: 8px;">
                        <div style="width: 16px; height: 16px; border: 2px solid ${isAdmin ? '#a0aec0' : '#4299e1'}; 
                                    border-top-color: transparent; border-radius: 50%; animation: spin 1s linear infinite;"></div>
                        <small style="color: ${isAdmin ? '#4a5568' : '#2d3748'}; font-size: 12px;">
                            Memuat produk #${data.product_id}...
                        </small>
                        <style>
                            @keyframes spin {
                                to { transform: rotate(360deg); }
                            }
                        </style>
                    </div>
                `;
            }
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
        
        // Smooth scroll to bottom with proper timing
        setTimeout(() => {
            messagesWrapper.scrollTo({
                top: messagesWrapper.scrollHeight,
                behavior: 'smooth'
            });
        }, 100);
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
        
        // Smooth scroll to bottom with proper timing
        setTimeout(() => {
            messagesWrapper.scrollTo({
                top: messagesWrapper.scrollHeight,
                behavior: 'smooth'
            });
        }, 100);
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
        if (data.is_typing && data.user_name && data.user_name !== this.currentUser.name && data.user_id != this.currentUser.id) {
            typingUserNameSpan.textContent = data.user_name;
            typingIndicator.style.display = 'flex';
        } else if (!data.is_typing || data.user_name === this.currentUser.name || data.user_id == this.currentUser.id) {
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
            // Show loading indicator
            const roomsList = document.getElementById('chat-rooms-list');
            if (roomsList && searchQuery) {
                roomsList.innerHTML = `
                    <div class="text-center py-4">
                        <div class="spinner-border spinner-border-sm text-primary" role="status">
                            <span class="visually-hidden">Loading...</span>
                        </div>
                        <p class="mt-2 mb-0 text-muted">Mencari "${searchQuery}"...</p>
                    </div>
                `;
            }

            const url = `/api/admin/buyer-rooms/${searchQuery ? `?search=${encodeURIComponent(searchQuery)}` : ''}`;
            const response = await fetch(url, {
                headers: {
                    'Authorization': `Bearer ${this.chatToken}`,
                    'Content-Type': 'application/json'
                },
                timeout: 10000 // 10 second timeout
            });

            if (response.ok) {
                const data = await response.json();
                
                // Validate response data
                if (!data.rooms || !Array.isArray(data.rooms)) {
                    throw new Error('Invalid response format');
                }

                // Sort rooms: unread first, then by latest message time
                const sortedRooms = data.rooms.sort((a, b) => {
                    // Unread messages priority
                    if (a.unread_count > 0 && b.unread_count === 0) return -1;
                    if (a.unread_count === 0 && b.unread_count > 0) return 1;
                    
                    // Then by latest message time
                    const aTime = a.last_message?.timestamp ? new Date(a.last_message.timestamp) : new Date(a.created_at);
                    const bTime = b.last_message?.timestamp ? new Date(b.last_message.timestamp) : new Date(b.created_at);
                    return bTime - aTime;
                });
                
                this.displayChatRooms(sortedRooms);
                this.updateTotalUnreadCount(sortedRooms);
                
                // Update search result info
                if (searchQuery) {
                    const resultCount = sortedRooms.length;
                    console.log(`Found ${resultCount} rooms matching "${searchQuery}"`);
                }
            } else {
                const errorText = await response.text();
                console.error(`Failed to load chat rooms: ${response.status} - ${errorText}`);
                this.displayChatRooms([]);
                
                // Show error message for search
                if (searchQuery) {
                    const roomsList = document.getElementById('chat-rooms-list');
                    if (roomsList) {
                        roomsList.innerHTML = `
                            <div class="text-center py-4">
                                <i class="fas fa-exclamation-triangle fa-2x text-warning mb-3"></i>
                                <h6 class="text-muted">Gagal memuat hasil pencarian</h6>
                                <p class="text-muted small">Silakan coba lagi</p>
                            </div>
                        `;
                    }
                }
            }
        } catch (error) {
            console.error('Error loading chat rooms:', error);
            this.displayChatRooms([]);
            
            // Show network error for search
            if (searchQuery) {
                const roomsList = document.getElementById('chat-rooms-list');
                if (roomsList) {
                    roomsList.innerHTML = `
                        <div class="text-center py-4">
                            <i class="fas fa-wifi fa-2x text-danger mb-3"></i>
                            <h6 class="text-muted">Koneksi bermasalah</h6>
                            <p class="text-muted small">Periksa koneksi internet Anda</p>
                        </div>
                    `;
                }
            }
        }
    }

    displayChatRooms(rooms) {
        const roomsList = document.getElementById('chat-rooms-list');
        if (!roomsList) return;

        if (rooms.length === 0) {
            roomsList.innerHTML = `
                <div class="empty-state text-center py-5">
                    <div class="empty-icon mb-3">
                        <i class="fas fa-inbox fa-3x text-muted"></i>
                    </div>
                    <h6 class="text-muted">Belum ada percakapan</h6>
                    <p class="text-muted small">Chat akan muncul di sini ketika ada pesan masuk</p>
                </div>
            `;
            return;
        }

        roomsList.innerHTML = rooms.map(room => {
            const lastMessage = room.last_message;
            
            // Handle timestamp safely
            let timeAgo = 'Belum ada pesan';
            if (lastMessage && lastMessage.timestamp) {
                timeAgo = this.getTimeAgo(lastMessage.timestamp);
            } else if (lastMessage && lastMessage.created_at) {
                timeAgo = this.getTimeAgo(lastMessage.created_at);
            } else if (room.created_at) {
                timeAgo = this.getTimeAgo(room.created_at);
            }
            
            const unreadBadge = room.unread_count > 0 ? `<span class="unread-badge">${room.unread_count}</span>` : '';
            
            // Truncate message for display - use 'message' field if 'content' not available
            let messagePreview = 'Belum ada pesan';
            if (lastMessage) {
                const content = lastMessage.content || lastMessage.message || '';
                messagePreview = content.length > 40 ? content.substring(0, 40) + '...' : content;
            }

            // Get initials for avatar
            const initials = room.buyer_name ? room.buyer_name.split(' ').map(n => n[0]).join('').toUpperCase().substring(0, 2) : 'U';

            return `
                <div class="chat-room-item ${room.unread_count > 0 ? 'unread' : ''}"
                     onclick="adminChat.selectBuyerRoom('${room.name}', '${room.buyer_name}', '${room.buyer_email}', ${room.buyer_id})"
                     data-room-name="${room.name}">
                    <div class="room-info">
                        <div class="room-avatar">
                            ${initials}
                        </div>
                        <div class="room-details">
                            <div class="room-name">${this.escapeHtml(room.buyer_name || 'Customer')}</div>
                            <div class="room-email">${this.escapeHtml(room.buyer_email || '')}</div>
                            <div class="room-last-message">${this.escapeHtml(messagePreview)}</div>
                        </div>
                        <div class="room-meta">
                            <div class="room-time">${timeAgo}</div>
                            ${unreadBadge}
                        </div>
                    </div>
                </div>
            `;
        }).join('');
    }

    getTimeAgo(timestamp) {
        try {
            if (!timestamp) return 'Belum ada pesan';
            
            const now = new Date();
            let messageTime;
            
            // Handle different timestamp formats
            if (typeof timestamp === 'string') {
                // Try parsing ISO format first
                if (timestamp.includes('T') || timestamp.includes('-')) {
                    messageTime = new Date(timestamp);
                } else if (!isNaN(timestamp)) {
                    // Unix timestamp string
                    messageTime = new Date(parseInt(timestamp) * (timestamp.length === 10 ? 1000 : 1));
                } else {
                    messageTime = new Date(timestamp);
                }
            } else if (typeof timestamp === 'number') {
                // Unix timestamp
                messageTime = new Date(timestamp * (timestamp.toString().length === 10 ? 1000 : 1));
            } else {
                messageTime = new Date(timestamp);
            }

            // Validate the date
            if (!messageTime || isNaN(messageTime.getTime())) {
                console.warn('Invalid timestamp for getTimeAgo:', timestamp);
                return 'Baru saja';
            }

            const diffMs = now - messageTime;
            const diffMins = Math.floor(diffMs / 60000);
            const diffHours = Math.floor(diffMs / 3600000);
            const diffDays = Math.floor(diffMs / 86400000);

            if (diffMins < 1) return 'Baru saja';
            if (diffMins < 60) return `${diffMins} menit lalu`;
            if (diffHours < 24) return `${diffHours} jam lalu`;
            if (diffDays < 7) return `${diffDays} hari lalu`;

            return messageTime.toLocaleDateString('id-ID');
        } catch (error) {
            console.error('Error in getTimeAgo:', error, 'timestamp:', timestamp);
            return 'Baru saja';
        }
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
        if (customerStatus) customerStatus.textContent = buyerEmail;

        // Update room selection UI and remove unread status
        this.updateRoomSelection(roomName);
        
        // Remove unread status from the selected room immediately
        const selectedRoomElement = document.querySelector(`[data-room-name="${roomName}"]`);
        if (selectedRoomElement) {
            selectedRoomElement.classList.remove('unread');
            const unreadBadge = selectedRoomElement.querySelector('.unread-badge');
            if (unreadBadge) {
                unreadBadge.remove();
            }
        }

        // Close sidebar on mobile after selection
        if (window.innerWidth <= 768) {
            const sidebar = document.getElementById('chatSidebar');
            if (sidebar) {
                sidebar.classList.remove('open');
            }
        }
    }

    setupWebSocketForRoom(roomName) {
        if (!this.chatToken) {
            console.error('No chat token available');
            return;
        }

        this.currentRoomName = roomName;
        this.updateConnectionStatus('connecting');

        const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        let wsUrls = [];

        // Universal dynamic chat URL construction for any domain
        const currentHost = window.location.hostname;
        const currentPort = window.location.port;
        
        // For domains with chat path routing (like tunnel configurations)
        if (window.location.hostname !== 'localhost' && window.location.hostname !== '127.0.0.1') {
            // Primary: Use /chat path for proxy routing (domain.com/chat -> port 8000)
            wsUrls.push(`${wsProtocol}//${currentHost}/chat/ws/chat/${roomName}/?token=${this.chatToken}`);
            
            // Secondary: Direct port 8000 access for fallback
            wsUrls.push(`${wsProtocol}//${currentHost}:8000/ws/chat/${roomName}/?token=${this.chatToken}`);
            
            // Additional fallback: try without /chat prefix
            wsUrls.push(`${wsProtocol}//${currentHost}/ws/chat/${roomName}/?token=${this.chatToken}`);
        } else {
            // Local development environment
            wsUrls.push(`ws://127.0.0.1:8000/ws/chat/${roomName}/?token=${this.chatToken}`);
            wsUrls.push(`ws://localhost:8000/ws/chat/${roomName}/?token=${this.chatToken}`);
        }

        console.log('Admin attempting WebSocket connection with URLs:', wsUrls);
        this.tryAdminConnectWithFallback(wsUrls, 0, roomName);
    }

    tryAdminConnectWithFallback(urls, urlIndex, roomName) {
        if (urlIndex >= urls.length) {
            console.error('All admin WebSocket URLs failed');
            this.updateConnectionStatus('error');
            this.displaySystemMessage('Tidak dapat terhubung ke server chat. Silakan refresh halaman.', 'error');
            return;
        }

        const wsUrl = urls[urlIndex];
        console.log(`Admin trying WebSocket URL ${urlIndex + 1}/${urls.length}:`, wsUrl);

        try {
            this.ws = new WebSocket(wsUrl);
            this.adminReconnectAttempts = 0;
            this.maxAdminReconnectAttempts = 10;
            this.adminReconnectDelay = 1000;
            this.adminHeartbeatInterval = null;

            this.ws.onopen = (event) => {
                console.log('Admin WebSocket connected to buyer room');
                this.isConnected = true;
                this.adminReconnectAttempts = 0;
                this.adminReconnectDelay = 1000; // Reset delay
                this.updateConnectionStatus('connected');
                this.startAdminHeartbeat();
                this.loadChatHistory(roomName); // Load history upon connection
                this.markRoomAsRead(roomName); // Mark as read after history is loaded
            };

            this.ws.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    this.handleWebSocketMessage(data);
                } catch (error) {
                    console.error('Error parsing admin WebSocket message:', error);
                }
            };

            this.ws.onclose = (event) => {
                console.log('Admin WebSocket closed:', event.code, event.reason);
                this.isConnected = false;
                this.stopAdminHeartbeat();
                
                if (event.code !== 1000 && event.code !== 1001) {
                    // Connection lost unexpectedly
                    this.updateConnectionStatus('disconnected');
                    // Attempt to reconnect if the room is still selected
                    if (this.selectedRoomId === roomName) {
                        this.attemptAdminReconnect(roomName);
                    }
                } else {
                    // Normal close
                    this.updateConnectionStatus('disconnected');
                }
            };

            this.ws.onerror = (error) => {
                console.error('Admin WebSocket error:', error);
                this.updateConnectionStatus('error');
                this.isConnected = false;
            };

        } catch (error) {
            console.error('Error creating admin WebSocket for buyer room:', error);
            this.updateConnectionStatus('error');
            this.attemptAdminReconnect(roomName);
        }
    }

    attemptAdminReconnect(roomName) {
        if (this.adminReconnectAttempts >= this.maxAdminReconnectAttempts) {
            console.error('Max admin reconnection attempts reached');
            this.updateConnectionStatus('error');
            this.displaySystemMessage('Koneksi chat gagal. Silakan refresh halaman.', 'error');
            return;
        }

        this.adminReconnectAttempts++;
        const delay = Math.min(this.adminReconnectDelay * Math.pow(2, this.adminReconnectAttempts - 1), 30000);
        
        console.log(`Admin attempting to reconnect... (${this.adminReconnectAttempts}/${this.maxAdminReconnectAttempts}) in ${delay}ms`);
        this.updateConnectionStatus('connecting');
        
        setTimeout(() => {
            if (!this.isConnected && this.selectedRoomId === roomName) {
                this.setupWebSocketForRoom(roomName);
            }
        }, delay);
    }

    startAdminHeartbeat() {
        this.stopAdminHeartbeat(); // Clear any existing heartbeat
        this.adminHeartbeatInterval = setInterval(() => {
            if (this.isConnected && this.ws.readyState === WebSocket.OPEN) {
                this.ws.send(JSON.stringify({
                    type: 'heartbeat',
                    timestamp: new Date().toISOString()
                }));
            }
        }, 30000); // Send heartbeat every 30 seconds
    }

    stopAdminHeartbeat() {
        if (this.adminHeartbeatInterval) {
            clearInterval(this.adminHeartbeatInterval);
            this.adminHeartbeatInterval = null;
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

    updateTotalUnreadCount(rooms) {
        const totalUnread = rooms.reduce((sum, room) => sum + room.unread_count, 0);
        this.unreadCount = totalUnread;
        this.updateUnreadBadge();
        
        // Update total unread badge in sidebar
        const totalUnreadBadge = document.getElementById('totalUnreadBadge');
        if (totalUnreadBadge) {
            const badge = totalUnreadBadge.querySelector('.badge');
            if (badge) {
                badge.textContent = totalUnread;
                badge.style.display = totalUnread > 0 ? 'inline' : 'none';
            }
        }
    }

    filterRooms(type) {
        // This method will filter rooms based on type
        const searchQuery = document.getElementById('buyer-search')?.value || '';
        
        // Store filter type for use in loadChatRooms
        this.currentFilter = type;
        
        // Reload rooms with filter
        this.loadChatRooms(searchQuery);
    }

    setupBuyerSearch() {
        const searchInput = document.getElementById('buyer-search');
        if (searchInput) {
            // Search on input with debouncing
            searchInput.addEventListener('input', (e) => {
                const query = e.target.value.trim();
                clearTimeout(this.searchTimer);
                
                // Immediate search for empty query to show all rooms
                if (query === '') {
                    this.loadChatRooms('');
                    return;
                }
                
                // Debounced search for non-empty queries
                this.searchTimer = setTimeout(() => {
                    this.loadChatRooms(query);
                }, 300);
            });

            // Search on Enter key - immediate search
            searchInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    e.preventDefault();
                    clearTimeout(this.searchTimer);
                    this.loadChatRooms(e.target.value.trim());
                }
            });

            // Clear search with Escape key
            searchInput.addEventListener('keydown', (e) => {
                if (e.key === 'Escape') {
                    e.target.value = '';
                    this.loadChatRooms('');
                    e.target.focus(); // Keep focus on input
                }
            });
            
            // Add focus styling
            searchInput.addEventListener('focus', () => {
                searchInput.parentElement.style.borderColor = '#4299e1';
            });
            
            searchInput.addEventListener('blur', () => {
                searchInput.parentElement.style.borderColor = '#e2e8f0';
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
                    const numTimestamp = parseInt(timestamp);
                    date = new Date(numTimestamp * (timestamp.length === 10 ? 1000 : 1));
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

            // Format with fallback
            const timeString = date.toLocaleTimeString('id-ID', {
                hour: '2-digit',
                minute: '2-digit'
            });
            
            // Double-check the result isn't "Invalid Date"
            if (timeString === 'Invalid Date' || timeString.includes('Invalid')) {
                return new Date().toLocaleTimeString('id-ID', {
                    hour: '2-digit',
                    minute: '2-digit'
                });
            }
            
            return timeString;
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
        // Ensure text is a string, handle null/undefined gracefully
        div.textContent = String(text || '');
        return div.innerHTML;
    }

    async fetchProductInfo(productId) {
        try {
            const response = await fetch(`/api/products/${productId}`, {
                headers: {
                    'Authorization': `Bearer ${this.chatToken}`,
                    'Content-Type': 'application/json'
                }
            });

            if (response.ok) {
                return await response.json();
            } else {
                console.error(`Failed to fetch product ${productId}: ${response.status}`);
                return null;
            }
        } catch (error) {
            console.error(`Error fetching product ${productId}:`, error);
            return null;
        }
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