// Global state
let currentPersona = 'default';
let sessionId = 'session_' + Date.now();
let personas = {};

// DOM elements
const personaList = document.getElementById('persona-list');
const chatMessages = document.getElementById('chat-messages');
const userInput = document.getElementById('user-input');
const sendBtn = document.getElementById('send-btn');
const clearBtn = document.getElementById('clear-btn');
const currentPersonaName = document.getElementById('current-persona-name');

// Initialize the app
async function init() {
    await loadPersonas();
    setupEventListeners();
}

// Load available personas
async function loadPersonas() {
    try {
        const response = await fetch('/api/personas');
        personas = await response.json();
        
        // Create persona buttons
        personaList.innerHTML = '';
        for (const [id, data] of Object.entries(personas)) {
            const btn = document.createElement('button');
            btn.className = 'persona-btn' + (id === currentPersona ? ' active' : '');
            btn.textContent = data.name;
            btn.dataset.personaId = id;
            btn.onclick = () => selectPersona(id);
            personaList.appendChild(btn);
        }
    } catch (error) {
        console.error('Error loading personas:', error);
    }
}

// Select a persona
function selectPersona(personaId) {
    currentPersona = personaId;
    currentPersonaName.textContent = personas[personaId].name;
    
    // Update active state
    document.querySelectorAll('.persona-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.personaId === personaId);
    });
    
    // Add system message about persona change
    addMessage('system', `Switched to ${personas[personaId].name} persona. Start chatting!`);
}

// Setup event listeners
function setupEventListeners() {
    sendBtn.addEventListener('click', sendMessage);
    clearBtn.addEventListener('click', clearChat);
    
    userInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });
}

// Send a message
async function sendMessage() {
    const message = userInput.value.trim();
    if (!message) return;
    
    // Disable input while processing
    userInput.disabled = true;
    sendBtn.disabled = true;
    
    // Add user message to chat
    addMessage('user', message);
    userInput.value = '';
    
    // Show loading indicator
    const loadingId = addMessage('bot', '...');
    
    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: message,
                persona: currentPersona,
                session_id: sessionId
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            // Remove loading indicator
            document.getElementById(loadingId).remove();
            // Add bot response
            addMessage('bot', data.message);
        } else {
            // Remove loading indicator
            document.getElementById(loadingId).remove();
            // Show error
            addMessage('error', `Error: ${data.error || 'Something went wrong'}`);
        }
    } catch (error) {
        // Remove loading indicator
        document.getElementById(loadingId).remove();
        // Show error
        addMessage('error', 'Network error. Please check your connection and API key.');
        console.error('Error:', error);
    } finally {
        // Re-enable input
        userInput.disabled = false;
        sendBtn.disabled = false;
        userInput.focus();
    }
}

// Add a message to the chat
function addMessage(type, content) {
    const messageDiv = document.createElement('div');
    const messageId = 'msg_' + Date.now() + '_' + Math.random();
    messageDiv.id = messageId;
    
    if (type === 'user') {
        messageDiv.className = 'message user-message';
        messageDiv.innerHTML = `
            <div class="message-content">
                <strong>You:</strong>
                ${escapeHtml(content)}
            </div>
        `;
    } else if (type === 'bot') {
        messageDiv.className = 'message bot-message';
        messageDiv.innerHTML = `
            <div class="message-content">
                <strong>${personas[currentPersona]?.name || 'Assistant'}:</strong>
                ${renderMarkdown(content)}
            </div>
        `;
    } else if (type === 'system') {
        messageDiv.className = 'message bot-message';
        messageDiv.innerHTML = `
            <div class="message-content">
                <strong>System:</strong>
                ${renderMarkdown(content)}
            </div>
        `;
    } else if (type === 'error') {
        messageDiv.className = 'message bot-message';
        messageDiv.innerHTML = `
            <div class="message-content" style="background: #ffe0e0; color: #c00;">
                <strong>Error:</strong>
                ${escapeHtml(content)}
            </div>
        `;
    }
    
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
    
    return messageId;
}

// Clear chat
async function clearChat() {
    if (!confirm('Are you sure you want to clear the chat history?')) {
        return;
    }
    
    try {
        await fetch('/api/clear', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                session_id: sessionId,
                persona: currentPersona
            })
        });
        
        // Clear chat UI
        chatMessages.innerHTML = '';
        addMessage('system', 'Chat cleared! Start a new conversation.');
    } catch (error) {
        console.error('Error clearing chat:', error);
        addMessage('error', 'Failed to clear chat.');
    }
}

// Escape HTML to prevent XSS
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML.replace(/\n/g, '<br>');
}

// Convert markdown formatting to HTML (after escaping)
function renderMarkdown(text) {
    // First escape HTML for security
    let html = escapeHtml(text);
    
    // Convert **bold** to <strong>
    html = html.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
    
    // Convert *italic* to <em>
    html = html.replace(/\*(.+?)\*/g, '<em>$1</em>');
    
    // Convert _italic_ to <em>
    html = html.replace(/_(.+?)_/g, '<em>$1</em>');
    
    // Convert `code` to <code>
    html = html.replace(/`(.+?)`/g, '<code>$1</code>');
    
    return html;
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}

