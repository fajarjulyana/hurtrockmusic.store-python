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
                this.setupWebSocket();
                this.updateConnectionStatus('connecting');
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

    setupWebSocket() {
        if (!this.chatToken) {
            console.error('No chat token available');
            return;
        }

        // Connect to support room for admin
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        let wsHost = window.location.hostname;
        
        // In Replit environment, use the same host but different port
        if (wsHost.includes('replit.dev') || wsHost.includes('replit.co')) {
            wsHost = `${wsHost}:8000`;
        } else {
            wsHost = `${wsHost}:8000`;
        }

        const wsUrl = `${protocol}//${wsHost}/ws/chat/support_room/?token=${this.chatToken}`;

        console.log('Admin connecting to WebSocket:', wsUrl);

        try {
            this.ws = new WebSocket(wsUrl);

            this.ws.onopen = (event) => {
                console.log('Admin WebSocket connected');
                this.isConnected = true;
                this.updateConnectionStatus('connected');
            };

            this.ws.onmessage = (event) => {
                const data = JSON.parse(event.data);
                this.handleWebSocketMessage(data);
            };

            this.ws.onclose = (event) => {
                console.log('Admin WebSocket closed:', event);
                this.isConnected = false;
                this.updateConnectionStatus('disconnected');

                // Attempt to reconnect after 3 seconds
                setTimeout(() => {
                    console.log('Admin attempting to reconnect...');
                    this.setupWebSocket();
                }, 3000);
            };

            this.ws.onerror = (error) => {
                console.error('Admin WebSocket error:', error);
                this.updateConnectionStatus('error');
            };

        } catch (error) {
            console.error('Error creating admin WebSocket:', error);
            this.updateConnectionStatus('error');
        }
    }

    handleWebSocketMessage(data) {
        switch (data.type) {
            case 'connection_established':
                console.log('Admin chat connection established:', data.message);
                break;

            case 'chat_message':
                this.displayMessage(data);
                this.updateRoomLastMessage(data);
                if (data.user_id !== this.currentUser.id) {
                    this.incrementUnreadCount();
                }
                break;

            case 'typing_indicator':
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
            this.displaySystemMessage('Chat tidak terhubung. Mencoba menyambung kembali...', 'warning');
            this.setupWebSocket();
            return;
        }

        const messageData = {
            type: 'chat_message',
            message: message
        };

        this.ws.send(JSON.stringify(messageData));
        messageInput.value = '';
    }

    handleAdminTyping() {
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
        const messagesWrapper = document.getElementById('messages-wrapper');
        if (!messagesWrapper) return;

        // Show active chat if hidden
        this.showActiveChat();

        const messageDiv = document.createElement('div');
        messageDiv.className = `chat-message ${data.user_id == this.currentUser.id ? 'admin-message' : 'customer-message'}`;

        const isAdmin = data.user_id == this.currentUser.id;
        const avatarClass = isAdmin ? 'admin' : 'customer';

        messageDiv.innerHTML = `
            <div class="message-avatar ${avatarClass}">
                <i class="fas fa-${isAdmin ? 'user-tie' : 'user-circle'}"></i>
            </div>
            <div class="message-content">
                ${this.escapeHtml(data.message)}
                <div class="message-meta">
                    <strong>${this.escapeHtml(data.user_name)}</strong> • ${this.formatTime(data.timestamp)}
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

        if (noChat && activeChat) {
            noChat.style.display = 'none';
            activeChat.style.display = 'flex';
        }
    }

    updateTypingIndicator(data) {
        const typingIndicator = document.getElementById('typing-indicator-admin');
        if (!typingIndicator) return;

        if (data.is_typing && data.user_id != this.currentUser.id) {
            document.getElementById('typing-user-name').textContent = data.user_name;
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

    selectRoom(roomId) {
        this.selectedRoomId = roomId;
        this.showActiveChat();

        // Update customer info
        const customerName = document.getElementById('customer-name');
        const customerStatus = document.getElementById('customer-status');

        if (customerName) customerName.textContent = 'Customer Support';
        if (customerStatus) customerStatus.textContent = 'Online';

        // Reset unread count for this room
        this.unreadCount = 0;
        this.updateUnreadBadge();
    }

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

        // Mark messages as read
        this.markRoomAsRead(roomName);

        // Load messages for this room
        this.loadRoomMessages(roomName);

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

        if (window.location.hostname.includes('replit.dev')) {
            wsUrl = `${wsProtocol}//${window.location.hostname}:8000/ws/chat/${roomName}/?token=${this.chatToken}`;
        } else {
            wsUrl = `ws://localhost:8000/ws/chat/${roomName}/?token=${this.chatToken}`;
        }

        console.log('Admin connecting to buyer room:', wsUrl);

        try {
            this.ws = new WebSocket(wsUrl);

            this.ws.onopen = (event) => {
                console.log('Admin WebSocket connected to buyer room');
                this.isConnected = true;
                this.updateConnectionStatus('connected');
            };

            this.ws.onmessage = (event) => {
                const data = JSON.parse(event.data);
                this.handleWebSocketMessage(data);
            };

            this.ws.onclose = (event) => {
                console.log('Admin WebSocket closed:', event);
                this.isConnected = false;
                this.updateConnectionStatus('disconnected');
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
            await fetch(`/api/rooms/${roomName}/mark-read/`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${this.chatToken}`,
                    'Content-Type': 'application/json'
                }
            });
        } catch (error) {
            console.error('Error marking room as read:', error);
        }
    }

    async loadRoomMessages(roomName) {
        try {
            const messagesWrapper = document.getElementById('messages-wrapper');
            if (messagesWrapper) {
                messagesWrapper.innerHTML = '';
            }

            const response = await fetch(`/api/rooms/${roomName}/messages/`, {
                headers: {
                    'Authorization': `Bearer ${this.chatToken}`
                }
            });

            if (response.ok) {
                const data = await response.json();
                data.results.forEach(message => this.displayMessage(message));
            }
        } catch (error) {
            console.error('Error loading room messages:', error);
        }
    }

    updateRoomSelection(selectedRoomName) {
        const roomItems = document.querySelectorAll('.chat-room-item');
        roomItems.forEach(item => {
            item.classList.remove('active');
            if (item.onclick && item.onclick.toString().includes(selectedRoomName)) {
                item.classList.add('active');
                item.classList.remove('unread');
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

    updateRoomLastMessage(data) {
        // Update room list with last message
        console.log('Updating room with last message:', data);
    }

    formatTime(timestamp) {
        return new Date(timestamp).toLocaleTimeString('id-ID', {
            hour: '2-digit',
            minute: '2-digit'
        });
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
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
    // Placeholder for customer info functionality
    console.log('Loading customer info...');
}

function markAsResolved() {
    // Placeholder for mark as resolved functionality
    console.log('Marking chat as resolved...');
}

function showProductSelector() {
    // Placeholder for product selector
    console.log('Showing product selector...');
}

function clearProductPreview() {
    const preview = document.getElementById('product-preview-admin');
    if (preview) {
        preview.style.display = 'none';
    }
}

function sendQuickReply(message) {
    const messageInput = document.getElementById('admin-message-input');
    if (messageInput && window.adminChat) {
        messageInput.value = message;
        window.adminChat.sendAdminMessage();
    }
}

// Initialize admin chat when page loads
window.adminChat = new AdminChat();