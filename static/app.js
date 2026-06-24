// Global State Management
let projects = [];
let expandedProjects = {}; // Keeps track of expanded project folders in the tree
let activeProject = null;
let activeConversation = null;
let assistants = [];
let activeAssistant = null;
let memories = [];
let kbDocuments = [];
let activeArtifact = null;

// ===== BLUWHALE PROPER WHALE SVG =====
// A clean horizontal blue whale side-profile (facing right, tail on left)
// Used everywhere instead of robot icons or the old ellipse-based turtle shape
const WHALE_SVG_SM = `<svg viewBox="0 0 200 90" xmlns="http://www.w3.org/2000/svg" fill="none" style="width:14px;height:auto;vertical-align:middle;">
  <path d="M42,41 C36,34 26,26 10,20 C6,18 5,23 9,25 C19,29 28,36 35,43 Z" fill="currentColor"/>
  <path d="M42,50 C36,57 26,65 10,70 C6,72 5,67 9,66 C19,63 28,57 35,49 Z" fill="currentColor"/>
  <path d="M38,42 C48,25 78,14 118,13 C152,12 176,22 192,38 C198,44 199,50 196,56 C191,66 170,74 145,77 C116,80 82,78 58,68 C44,62 38,54 38,50 Z" fill="currentColor"/>
  <path d="M82,62 C110,72 158,69 190,52 C195,49 196,56 192,62 C185,72 165,78 138,80 C110,82 78,78 58,68 C50,64 68,58 82,62 Z" fill="#81c3d7" opacity="0.45"/>
  <path d="M150,56 C160,68 162,82 155,87 C148,86 146,70 148,60 Z" fill="currentColor" opacity="0.85"/>
  <circle cx="185" cy="38" r="4" fill="var(--bg-main,#0a2233)" opacity="0.85"/>
</svg>`;

const WHALE_SVG_MD = `<svg viewBox="0 0 200 90" xmlns="http://www.w3.org/2000/svg" fill="none" style="width:20px;height:auto;vertical-align:middle;">
  <path d="M42,41 C36,34 26,26 10,20 C6,18 5,23 9,25 C19,29 28,36 35,43 Z" fill="currentColor"/>
  <path d="M42,50 C36,57 26,65 10,70 C6,72 5,67 9,66 C19,63 28,57 35,49 Z" fill="currentColor"/>
  <path d="M38,42 C48,25 78,14 118,13 C152,12 176,22 192,38 C198,44 199,50 196,56 C191,66 170,74 145,77 C116,80 82,78 58,68 C44,62 38,54 38,50 Z" fill="currentColor"/>
  <path d="M82,62 C110,72 158,69 190,52 C195,49 196,56 192,62 C185,72 165,78 138,80 C110,82 78,78 58,68 C50,64 68,58 82,62 Z" fill="#81c3d7" opacity="0.45"/>
  <path d="M150,56 C160,68 162,82 155,87 C148,86 146,70 148,60 Z" fill="currentColor" opacity="0.85"/>
  <circle cx="185" cy="38" r="4" fill="var(--bg-main,#0a2233)" opacity="0.85"/>
  <circle cx="184" cy="37" r="1.5" fill="#e8f4f8" opacity="0.7"/>
</svg>`;

const WHALE_SVG_LG = `<svg viewBox="0 0 200 90" xmlns="http://www.w3.org/2000/svg" fill="none" style="width:60px;height:auto;filter:drop-shadow(0 0 12px rgba(58,124,165,0.5));">
  <path d="M42,41 C36,34 26,26 10,20 C6,18 5,23 9,25 C19,29 28,36 35,43 Z" fill="var(--logo-color,#3a7ca5)"/>
  <path d="M42,50 C36,57 26,65 10,70 C6,72 5,67 9,66 C19,63 28,57 35,49 Z" fill="var(--logo-color,#3a7ca5)"/>
  <path d="M38,42 C48,25 78,14 118,13 C152,12 176,22 192,38 C198,44 199,50 196,56 C191,66 170,74 145,77 C116,80 82,78 58,68 C44,62 38,54 38,50 Z" fill="var(--logo-color,#3a7ca5)"/>
  <path d="M82,62 C110,72 158,69 190,52 C195,49 196,56 192,62 C185,72 165,78 138,80 C110,82 78,78 58,68 C50,64 68,58 82,62 Z" fill="#81c3d7" opacity="0.5"/>
  <path d="M150,56 C160,68 162,82 155,87 C148,86 146,70 148,60 Z" fill="var(--logo-color,#3a7ca5)" opacity="0.85"/>
  <circle cx="185" cy="38" r="5" fill="var(--bg-main,#0a2233)" opacity="0.85"/>
  <circle cx="184" cy="37" r="2" fill="#e8f4f8" opacity="0.7"/>
  <path d="M172,48 C178,56 180,64 178,70" stroke="var(--bg-main,#0a2233)" stroke-width="2" stroke-linecap="round" fill="none" opacity="0.3"/>
</svg>`;



// Apply theme immediately on startup
const savedTheme = localStorage.getItem('bluwhale_theme') || 'dark';
if (savedTheme === 'light') {
    document.body.classList.add('light-theme');
}

// DOM Elements
const projectsTreeEl = document.getElementById('projects-tree');
const activeBotNameEl = document.getElementById('active-bot-name');
const activeBotDescEl = document.getElementById('active-bot-description');
const activeBotControlsEl = document.getElementById('active-bot-controls');
const messagesContainerEl = document.getElementById('messages-container');
const chatFormEl = document.getElementById('chat-form');
const userInputEl = document.getElementById('user-input');
const sendBtnEl = document.getElementById('send-btn');
const themeToggleBtn = document.getElementById('theme-toggle-btn');
const settingsDrawer = document.getElementById('settings-drawer');
const toggleSettingsBtn = document.getElementById('toggle-settings-btn');
const saveKeysBtn = document.getElementById('save-keys-btn');

const canvasPanel = document.getElementById('canvas-panel');
const canvasTypeBadge = document.getElementById('canvas-type-badge');
const canvasTitle = document.getElementById('canvas-title');
const canvasCodeBlock = document.getElementById('canvas-code-block');
const canvasExpandBtn = document.getElementById('canvas-expand-btn');

const consoleModelBadge = document.getElementById('console-model-badge');
const consoleRagBadge = document.getElementById('console-rag-badge');
const consoleModeToggle = document.getElementById('console-mode-toggle');
const consoleKbBtn = document.getElementById('console-kb-btn');

// Initialize Application
document.addEventListener('DOMContentLoaded', () => {
    // Setup initial theme icon
    const themeIcon = themeToggleBtn.querySelector('i');
    if (themeIcon) {
        themeIcon.className = savedTheme === 'light' ? 'fa-solid fa-sun' : 'fa-solid fa-moon';
    }

    // Theme Toggle Handler
    themeToggleBtn.addEventListener('click', () => {
        document.body.classList.toggle('light-theme');
        const isLight = document.body.classList.contains('light-theme');
        localStorage.setItem('bluwhale_theme', isLight ? 'light' : 'dark');
        
        if (themeIcon) {
            themeIcon.className = isLight ? 'fa-solid fa-sun' : 'fa-solid fa-moon';
        }
        showToast(`Switched to ${isLight ? 'Light' : 'Dark'} Mode`);
    });

    // Settings Drawer Handler
    if (toggleSettingsBtn && settingsDrawer) {
        toggleSettingsBtn.addEventListener('click', () => {
            settingsDrawer.classList.toggle('open');
        });
    }

    // Load persisted Access Keys
    const savedAppKey = localStorage.getItem('bluwhale_app_key');
    const savedGrokKey = localStorage.getItem('bluwhale_grok_key');
    if (savedAppKey) document.getElementById('app-api-key').value = savedAppKey;
    if (savedGrokKey) document.getElementById('grok-api-key').value = savedGrokKey;

    saveKeysBtn.addEventListener('click', saveApiKeys);

    // Chat Input console listeners
    chatFormEl.addEventListener('submit', handleSendChat);
    userInputEl.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            chatFormEl.requestSubmit();
        }
    });

    // Textarea auto-grow as user types
    userInputEl.addEventListener('input', () => {
        userInputEl.style.height = '48px';
        userInputEl.style.height = Math.min(userInputEl.scrollHeight, 180) + 'px';
    });

    // Click anywhere on the chat console when disabled → helpful hint
    // NOTE: disabled elements don't fire click events, so we listen on the PARENT form
    chatFormEl.addEventListener('click', () => {
        if (userInputEl.disabled) {
            showToast('👈 Select or create a conversation thread on the left to start chatting.', 'info');
        }
    });

    // Load App Data Workspace
    loadProjects();
    loadAssistants();
    loadMemories();
});

// Save Keys to LocalStorage
function saveApiKeys() {
    const appKey = document.getElementById('app-api-key').value.trim();
    const grokKey = document.getElementById('grok-api-key').value.trim();
    
    localStorage.setItem('bluwhale_app_key', appKey);
    localStorage.setItem('bluwhale_grok_key', grokKey);
    
    showToast('API keys saved successfully. Reloading workspace...');
    if (settingsDrawer) {
        settingsDrawer.classList.remove('open');
    }
    loadProjects();
    loadAssistants();
    loadMemories();
}

// Password Visibility toggle helper
function togglePasswordVisibility(inputId) {
    const input = document.getElementById(inputId);
    const button = input.nextElementSibling;
    const icon = button.querySelector('i');
    
    if (input.type === 'password') {
        input.type = 'text';
        icon.classList.replace('fa-regular', 'fa-solid');
        icon.classList.replace('fa-eye', 'fa-eye-slash');
    } else {
        input.type = 'password';
        icon.classList.replace('fa-solid', 'fa-regular');
        icon.classList.replace('fa-eye-slash', 'fa-eye');
    }
}

// AJAX Request Helper
async function apiRequest(url, method = 'GET', body = null, isFormData = false) {
    const appKey = document.getElementById('app-api-key').value.trim();
    const grokKey = document.getElementById('grok-api-key').value.trim();
    
    const headers = {};
    if (appKey) {
        headers['X-API-Key'] = appKey;
    }
    if (grokKey && url.includes('/messages')) {
        headers['X-Grok-API-Key'] = grokKey;
    }
    
    const options = { method, headers };
    
    if (body) {
        if (isFormData) {
            options.body = body;
        } else {
            headers['Content-Type'] = 'application/json';
            options.body = JSON.stringify(body);
        }
    }
    
    try {
        const response = await fetch(url, options);
        if (response.status === 401) {
            throw new Error("Unauthorized: Invalid Access Token. Please configure X-API-Key in settings.");
        }
        if (response.status === 204) {
            return null;
        }
        const data = await response.json();
        if (!response.ok) {
            throw new Error(data.detail || `Server returned error status ${response.status}`);
        }
        return data;
    } catch (err) {
        showToast(err.message, 'error');
        throw err;
    }
}

// ----------------- PROJECTS & TREE WORKSPACE -----------------

async function loadProjects() {
    try {
        const data = await apiRequest('/api/v1/projects?size=100');
        projects = data.items;
        
        // Fetch all conversations to map inside projects
        const convData = await apiRequest('/api/v1/conversations?size=100');
        const conversations = convData.items;

        // Group conversations under project IDs
        projects.forEach(proj => {
            proj.conversations = conversations.filter(c => c.project_id === proj.id);
        });

        // Collect conversations without project folders
        const unassigned = conversations.filter(c => !c.project_id);

        renderProjectsTree(unassigned);
    } catch (err) {
        projectsTreeEl.innerHTML = `<div class="loading-state text-danger"><i class="fa-solid fa-triangle-exclamation"></i> Error loading workspace tree.</div>`;
    }
}

function renderProjectsTree(unassignedConvs) {
    projectsTreeEl.innerHTML = '';

    if (projects.length === 0 && unassignedConvs.length === 0) {
        projectsTreeEl.innerHTML = `<div class="loading-state">No workspaces active. Create a project to start.</div>`;
        return;
    }

    // Render Project Folders
    projects.forEach((project, idx) => {
        // Default first project folder to expanded if not set
        if (expandedProjects[project.id] === undefined) {
            expandedProjects[project.id] = (idx === 0);
        }

        const isOpen = expandedProjects[project.id];
        
        const folder = document.createElement('div');
        folder.className = `project-folder ${isOpen ? 'open' : ''}`;
        folder.setAttribute('data-project-id', project.id);
        
        // Add drop listeners for drag and drop thread transfers
        folder.addEventListener('dragover', handleDragOver);
        folder.addEventListener('drop', (e) => handleDrop(e, project.id));

        folder.innerHTML = `
            <div class="project-folder-header" onclick="toggleProjectCollapse(${project.id})">
                <div class="project-folder-title">
                    <i class="fa-solid fa-chevron-right"></i>
                    <i class="fa-solid ${isOpen ? 'fa-folder-open' : 'fa-folder'}"></i>
                    <span>${escapeHTML(project.name)}</span>
                </div>
                <div class="project-folder-actions">
                    <button class="btn-action edit-action" onclick="openEditProjectModal(event, ${project.id})" title="Rename Project Workspace"><i class="fa-solid fa-pen"></i></button>
                    <button class="btn-action edit-action" onclick="openCreateConvModal(event, ${project.id})" title="Add Thread"><i class="fa-solid fa-plus"></i></button>
                    <button class="btn-action delete-action" onclick="deleteProject(event, ${project.id})" title="Delete Workspace Folder"><i class="fa-solid fa-trash-can"></i></button>
                </div>
            </div>
            <div class="project-folder-content">
                <!-- Thread items populate here -->
            </div>
        `;

        const contentEl = folder.querySelector('.project-folder-content');
        if (project.conversations && project.conversations.length > 0) {
            project.conversations.forEach(conv => {
                const convItem = createConvTreeItem(conv);
                contentEl.appendChild(convItem);
            });
        } else {
            contentEl.innerHTML = `<div class="loading-state" style="padding: 10px 0;">No active threads.</div>`;
        }

        projectsTreeEl.appendChild(folder);
    });

    // Render Unassigned Section if there are standalone chats
    if (unassignedConvs && unassignedConvs.length > 0) {
        const unassignedFolder = document.createElement('div');
        unassignedFolder.className = 'project-folder open';
        unassignedFolder.innerHTML = `
            <div class="project-folder-header">
                <div class="project-folder-title">
                    <i class="fa-solid fa-hashtag"></i>
                    <span>Unassigned Chats</span>
                </div>
            </div>
            <div class="project-folder-content" style="display: block;">
                <!-- Populate unassigned threads -->
            </div>
        `;
        const contentEl = unassignedFolder.querySelector('.project-folder-content');
        unassignedConvs.forEach(conv => {
            const convItem = createConvTreeItem(conv);
            contentEl.appendChild(convItem);
        });
        projectsTreeEl.appendChild(unassignedFolder);
    }
}

function createConvTreeItem(conv) {
    const item = document.createElement('div');
    const isActive = activeConversation && activeConversation.id === conv.id;
    item.className = `project-conv-item ${isActive ? 'active' : ''}`;
    item.setAttribute('draggable', 'true');
    
    // Bind Drag & Drop event triggers
    item.addEventListener('dragstart', (e) => handleDragStart(e, conv.id));
    item.onclick = () => selectConversation(conv.id);

    // Get avatar class — use whale SVG if default robot
    const rawAvatar = conv.assistant_avatar;
    const isRobot = !rawAvatar || rawAvatar === 'fa-solid fa-robot';
    const avatarClass = isRobot ? null : rawAvatar;

    const convIconHtml = avatarClass
        ? `<i class="${avatarClass} conv-icon"></i>`
        : `<span class="conv-icon" style="display:inline-flex;align-items:center;color:currentColor;">${WHALE_SVG_SM}</span>`;
    item.innerHTML = `
        <div class="project-conv-meta">
            ${convIconHtml}
            <span>${escapeHTML(conv.title)}</span>
        </div>
        <div class="project-conv-actions">
            <button class="btn-action edit-action" onclick="openMoveConvModal(event, ${conv.id})" title="Move Thread"><i class="fa-solid fa-folder-minus"></i></button>
            <button class="btn-action delete-action" onclick="deleteConversation(event, ${conv.id})" title="Delete Thread"><i class="fa-solid fa-trash-can"></i></button>
        </div>
    `;
    return item;
}

function toggleProjectCollapse(projectId) {
    expandedProjects[projectId] = !expandedProjects[projectId];
    const folderEl = document.querySelector(`.project-folder[data-project-id="${projectId}"]`);
    if (folderEl) {
        folderEl.classList.toggle('open');
        const icon = folderEl.querySelector('.project-folder-title i.fa-folder, .project-folder-title i.fa-folder-open');
        if (icon) {
            icon.className = folderEl.classList.contains('open') ? 'fa-solid fa-folder-open' : 'fa-solid fa-folder';
        }
    }
}

// ----------------- DRAG & DROP THREAD MOVES -----------------

function handleDragStart(e, convId) {
    e.dataTransfer.setData('text/plain', convId);
    e.dataTransfer.effectAllowed = 'move';
}

function handleDragOver(e) {
    e.preventDefault();
    e.dataTransfer.dropEffect = 'move';
}

async function handleDrop(e, targetProjectId) {
    e.preventDefault();
    const convId = parseInt(e.dataTransfer.getData('text/plain'));
    if (isNaN(convId)) return;

    try {
        await apiRequest(`/api/v1/conversations/${convId}`, 'PUT', { project_id: targetProjectId });
        showToast('Moved thread successfully.');
        loadProjects();
    } catch (err) {
        showToast('Failed to transfer thread.', 'error');
    }
}

// ----------------- PROJECTS ACTIONS -----------------

function openCreateProjectModal() {
    document.getElementById('project-modal-title').textContent = 'Create New Project Folder';
    document.getElementById('edit-project-id').value = '';
    document.getElementById('project-form').reset();
    document.getElementById('project-modal').classList.add('open');
}

function openEditProjectModal(event, projectId) {
    event.stopPropagation();
    const project = projects.find(p => p.id === projectId);
    if (!project) return;

    document.getElementById('project-modal-title').textContent = 'Rename Project Workspace';
    document.getElementById('edit-project-id').value = project.id;
    document.getElementById('project-name').value = project.name;
    document.getElementById('project-description').value = project.description || '';
    document.getElementById('project-modal').classList.add('open');
}

async function saveProject(event) {
    event.preventDefault();
    const projectId = document.getElementById('edit-project-id').value;
    const payload = {
        name: document.getElementById('project-name').value.trim(),
        description: document.getElementById('project-description').value.trim()
    };

    try {
        if (projectId) {
            await apiRequest(`/api/v1/projects/${projectId}`, 'PUT', payload);
            showToast('Workspace project renamed.');
        } else {
            await apiRequest('/api/v1/projects', 'POST', payload);
            showToast('New project folder created.');
        }
        closeModal('project-modal');
        loadProjects();
    } catch (err) {
        showToast('Failed to save project settings.', 'error');
    }
}

async function deleteProject(event, projectId) {
    event.stopPropagation();
    if (!confirm("Are you sure you want to delete this workspace? This will cascade-delete all associated threads, messages, and artifacts!")) {
        return;
    }

    try {
        await apiRequest(`/api/v1/projects/${projectId}`, 'DELETE');
        showToast('Workspace project deleted.');
        if (activeConversation && projects.find(p => p.id === projectId)?.conversations?.some(c => c.id === activeConversation.id)) {
            activeConversation = null;
            resetChatWorkspace();
        }
        loadProjects();
    } catch (err) {
        showToast('Failed to delete workspace folder.', 'error');
    }
}

// ----------------- CONVERSATIONS THREADS ACTIONS -----------------

function openCreateConvModal(event, projectId) {
    if (event) event.stopPropagation();
    
    document.getElementById('create-conv-project-id').value = projectId || '';
    document.getElementById('conv-title').value = 'New Conversation';
    
    // Populate Assistants dropdown
    const select = document.getElementById('conv-assistant-id');
    select.innerHTML = '';
    
    if (assistants.length === 0) {
        select.innerHTML = `<option value="">No assistants available. Create one first!</option>`;
    } else {
        assistants.forEach(ast => {
            select.innerHTML += `<option value="${ast.id}">${escapeHTML(ast.name)}</option>`;
        });
    }

    document.getElementById('create-conv-modal').classList.add('open');
}

async function saveConversation(event) {
    event.preventDefault();
    const projectIdVal = document.getElementById('create-conv-project-id').value;
    const assistantIdVal = document.getElementById('conv-assistant-id').value;

    if (!assistantIdVal) {
        showToast('Please select or create an AI Assistant first.', 'error');
        return;
    }

    const payload = {
        project_id: projectIdVal ? parseInt(projectIdVal) : null,
        assistant_id: parseInt(assistantIdVal),
        title: document.getElementById('conv-title').value.trim(),
        chat_mode: document.getElementById('conv-chat-mode').value
    };

    try {
        const created = await apiRequest('/api/v1/conversations', 'POST', payload);
        showToast('Initialized new chat session.');
        closeModal('create-conv-modal');
        
        // Auto expand parent project folder to show the new thread
        if (payload.project_id) {
            expandedProjects[payload.project_id] = true;
        }

        await loadProjects();
        selectConversation(created.id);
    } catch (err) {
        showToast('Failed to create thread.', 'error');
    }
}

async function deleteConversation(event, convId) {
    event.stopPropagation();
    if (!confirm("Are you sure you want to delete this conversation session? All message history will be lost.")) {
        return;
    }

    try {
        await apiRequest(`/api/v1/conversations/${convId}`, 'DELETE');
        showToast('Conversation thread removed.');
        if (activeConversation && activeConversation.id === convId) {
            activeConversation = null;
            resetChatWorkspace();
        }
        loadProjects();
    } catch (err) {
        showToast('Failed to delete conversation thread.', 'error');
    }
}

// Move Conversation modal controls
function openMoveConvModal(event, convId) {
    event.stopPropagation();
    document.getElementById('move-conv-id').value = convId;
    
    // Populate projects selection list
    const select = document.getElementById('move-conv-project-id');
    select.innerHTML = '';
    
    projects.forEach(p => {
        select.innerHTML += `<option value="${p.id}">${escapeHTML(p.name)}</option>`;
    });

    document.getElementById('move-conv-modal').classList.add('open');
}

async function executeMoveConversation(event) {
    event.preventDefault();
    const convId = document.getElementById('move-conv-id').value;
    const projectId = document.getElementById('move-conv-project-id').value;

    try {
        await apiRequest(`/api/v1/conversations/${convId}`, 'PUT', { project_id: parseInt(projectId) });
        showToast('Thread moved between project folders.');
        closeModal('move-conv-modal');
        loadProjects();
    } catch (err) {
        showToast('Failed to move thread.', 'error');
    }
}

// ----------------- SELECT & RENDER THREAD CHAT -----------------

async function selectConversation(convId) {
    try {
        const conv = await apiRequest(`/api/v1/conversations/${convId}`);
        activeConversation = conv;
        
        // Render project workspace tree to update active highlighting
        loadProjects();

        // 1. Setup Chat Header details
        const avatarContainer = document.getElementById('active-ast-avatar-container');
        const avatarClass = conv.assistant_avatar;
        const isDefaultRobot = !avatarClass || avatarClass === 'fa-solid fa-robot';
        avatarContainer.innerHTML = isDefaultRobot ? WHALE_SVG_MD : `<i class="${avatarClass}"></i>`;
        activeBotNameEl.textContent = conv.title;
        activeBotDescEl.textContent = `Active Assistant: ${conv.assistant_name || 'Assistant'}`;

        // 2. Enable Chat Console
        userInputEl.disabled = false;
        userInputEl.placeholder = `Message ${conv.assistant_name || 'Assistant'}...`;
        sendBtnEl.disabled = false;
        consoleModeToggle.disabled = false;
        consoleKbBtn.disabled = false;

        // 3. Update Console Badges
        consoleModelBadge.innerHTML = `<i class="fa-solid fa-microchip"></i> GROK-BETA`;
        updateConsoleBadges(conv);

        // 4. Fetch Message Logs
        const messages = await apiRequest(`/api/v1/conversations/${convId}/messages`);
        chatHistories[convId] = messages;
        renderChatHistory(messages);

        // 5. Fetch Artifacts list to show latest canvas item if it exists
        const artifacts = await apiRequest(`/api/v1/conversations/${convId}/artifacts`);
        if (artifacts && artifacts.length > 0) {
            renderArtifactCanvas(artifacts[0]);
        } else {
            closeCanvas();
        }

    } catch (err) {
        showToast('Failed to load selected conversation session.', 'error');
    }
}

function updateConsoleBadges(conv) {
    // Mode badge setup
    if (conv.chat_mode === 'web_search') {
        consoleModeToggle.innerHTML = `<i class="fa-solid fa-globe"></i> MODE: WEB SEARCH`;
        consoleModeToggle.classList.add('active');
    } else {
        consoleModeToggle.innerHTML = `<i class="fa-solid fa-comments"></i> MODE: NORMAL`;
        consoleModeToggle.classList.remove('active');
    }

    // RAG docs badge fetch
    consoleRagBadge.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> RAG SEARCHING...`;
    apiRequest(`/api/v1/knowledge-bases/?assistant_id=${conv.assistant_id}&size=100`)
        .then(data => {
            const count = data.items ? data.items.length : 0;
            if (count > 0) {
                consoleRagBadge.innerHTML = `<i class="fa-solid fa-database"></i> RAG ACTIVE (${count} DOCS)`;
            } else {
                consoleRagBadge.innerHTML = `<i class="fa-solid fa-database"></i> RAG INACTIVE`;
            }
        })
        .catch(() => {
            consoleRagBadge.innerHTML = `<i class="fa-solid fa-database"></i> RAG OFFLINE`;
        });
}

function toggleChatMode() {
    if (!activeConversation) return;

    const newMode = activeConversation.chat_mode === 'web_search' ? 'normal' : 'web_search';
    
    apiRequest(`/api/v1/conversations/${activeConversation.id}`, 'PUT', { chat_mode: newMode })
        .then(updated => {
            activeConversation.chat_mode = updated.chat_mode;
            updateConsoleBadges(updated);
            showToast(`Switched mode to ${newMode === 'web_search' ? 'Web Search Mode' : 'Normal Conversation'}`);
        })
        .catch(() => {
            showToast('Failed to switch chat mode.', 'error');
        });
}

function resetChatWorkspace() {
    // Header Reset
    const avatarContainer = document.getElementById('active-ast-avatar-container');
    avatarContainer.innerHTML = WHALE_SVG_MD;
    activeBotNameEl.textContent = 'Select a Conversation';
    activeBotDescEl.textContent = 'Choose a workspace thread from the project list on the left to begin.';
    
    // Console Inputs disable
    userInputEl.disabled = true;
    userInputEl.placeholder = 'Select a conversation thread to begin...';
    sendBtnEl.disabled = true;
    consoleModeToggle.disabled = true;
    consoleKbBtn.disabled = true;

    consoleModelBadge.innerHTML = `<i class="fa-solid fa-microchip"></i> NO CHAT ACTIVE`;
    consoleRagBadge.innerHTML = `<i class="fa-solid fa-database"></i> RAG INACTIVE`;
    consoleModeToggle.innerHTML = `<i class="fa-solid fa-globe"></i> MODE: NORMAL`;

    // Welcome Screen reset
    messagesContainerEl.innerHTML = `
        <div class="welcome-message-panel">
            <div class="welcome-whale-icon">${WHALE_SVG_LG}</div>
            <h2>Welcome to the BluWhale AI Workspace</h2>
            <p>Select a RAG conversation thread from the left or create a new one to begin chatting.</p>
        </div>
    `;

    closeCanvas();
}

// Render Messages bubbles
function renderChatHistory(messages) {
    messagesContainerEl.innerHTML = '';
    
    if (!messages || messages.length === 0) {
        messagesContainerEl.innerHTML = `
            <div class="welcome-message-panel">
                <div class="welcome-whale-icon" style="width:60px;height:50px;">${WHALE_SVG_LG}</div>
                <h2>Chat Session Initialized</h2>
                <p>Send a message below. RAG context indexing and memories are active for this thread.</p>
            </div>
        `;
        return;
    }

    messages.forEach(msg => {
        // Parse sources from message JSON string
        let sourcesList = null;
        if (msg.sources) {
            try {
                sourcesList = JSON.parse(msg.sources);
            } catch(e) {
                sourcesList = null;
            }
        }
        appendMessageBubble(msg.role, msg.content, sourcesList);
    });

    scrollToBottom();
}

function appendMessageBubble(role, content, sources = null) {
    const welcome = messagesContainerEl.querySelector('.welcome-message-panel');
    if (welcome) welcome.remove();

    const wrapper = document.createElement('div');
    wrapper.className = `message-bubble-wrapper ${role}`;

    const isUser = role === 'user';
    const whaleSvg = WHALE_SVG_SM;
    const assistantAvatar = activeConversation?.assistant_avatar;
    const avatarIsDefault = !assistantAvatar || assistantAvatar === 'fa-solid fa-robot';
    const avatar = isUser ? '<i class="fa-solid fa-user"></i>' : (avatarIsDefault ? whaleSvg : `<i class="${assistantAvatar}"></i>`);

    // Process content text line breaks safely
    let contentHtml = escapeHTML(content).replace(/\n/g, '<br>');
    
    // Look for Artifact Canvas link note wrapper to style it beautifully as a premium action link
    if (contentHtml.includes('Artifact Canvas')) {
        contentHtml = contentHtml.replace(
            /\*\(I have generated a `(\w+)` document\. You can view, copy, and download the full output in the Artifact Canvas panel on the right\.\)\*/g,
            `<div class="canvas-extracted-badge" onclick="openCanvas()"><i class="fa-solid fa-square-terminal"></i> <span>View Generated $1 Output on Artifact Canvas</span> <i class="fa-solid fa-arrow-right"></i></div>`
        );
    }

    wrapper.innerHTML = `
        <div class="bubble-avatar">
            ${avatar}
        </div>
        <div class="bubble-main">
            <div class="bubble-content">
                ${contentHtml}
            </div>
        </div>
    `;

    // If Web Search Mode sources are present, append links below the bubble
    if (!isUser && sources && sources.length > 0) {
        const bubbleMain = wrapper.querySelector('.bubble-main');
        const container = document.createElement('div');
        container.className = 'search-sources-container';
        
        let linksHtml = '';
        sources.forEach(src => {
            let domain = src.url;
            try {
                domain = new URL(src.url).hostname;
            } catch(e) {}
            linksHtml += `
                <a href="${src.url}" target="_blank" class="search-source-link" title="${escapeHTML(src.title)}">
                    <i class="fa-solid fa-link"></i> ${escapeHTML(domain)}
                </a>
            `;
        });

        container.innerHTML = `
            <div class="search-sources-title"><i class="fa-solid fa-square-rss"></i> Search Sources</div>
            <div class="search-sources-list">
                ${linksHtml}
            </div>
        `;
        bubbleMain.appendChild(container);
    }

    messagesContainerEl.appendChild(wrapper);
}

// ----------------- SEND CHAT LOGIC -----------------

async function handleSendChat(event) {
    event.preventDefault();
    if (!activeConversation) return;

    const text = userInputEl.value.trim();
    if (!text) return;

    // Reset textarea layout
    userInputEl.value = '';
    userInputEl.style.height = '38px';

    // Disable input interface during completion
    userInputEl.disabled = true;
    sendBtnEl.disabled = true;

    // Append user query bubble
    appendMessageBubble('user', text);
    scrollToBottom();

    // Create & append typing indicator bubble
    const typingBubble = document.createElement('div');
    typingBubble.className = 'message-bubble-wrapper assistant typing-indicator-bubble';
    typingBubble.innerHTML = `
        <div class="bubble-avatar">${(activeConversation.assistant_avatar && activeConversation.assistant_avatar !== 'fa-solid fa-robot') ? `<i class="${activeConversation.assistant_avatar}"></i>` : WHALE_SVG_SM}</div>
        <div class="bubble-main">
            <div class="bubble-content" style="padding: 10px 14px;">
                <div class="typing-dots">
                    <span></span><span></span><span></span>
                </div>
            </div>
        </div>
    `;
    messagesContainerEl.appendChild(typingBubble);
    scrollToBottom();

    try {
        const result = await apiRequest(`/api/v1/conversations/${activeConversation.id}/messages`, 'POST', { content: text });
        
        // Remove typing indicator bubble
        typingBubble.remove();

        // Enable input interface
        userInputEl.disabled = false;
        sendBtnEl.disabled = false;
        userInputEl.focus();

        // Render assistant response bubble
        appendMessageBubble('assistant', result.response, result.sources);
        scrollToBottom();

        // Trigger right split-screen Canvas if code document was parsed
        if (result.artifact) {
            renderArtifactCanvas(result.artifact);
            showToast('Extracted script output loaded into Artifact Canvas panel!');
        }

        // Silent refresh of memories in backend
        loadMemories();

        if (result.warning) {
            showToast(result.warning, 'warning');
        }

    } catch (err) {
        typingBubble.remove();
        userInputEl.disabled = false;
        sendBtnEl.disabled = false;
        appendMessageBubble('assistant', `[Completion Error] Failed to contact LLM Engine: ${err.message}`);
        scrollToBottom();
    }
}

// ----------------- ARTIFACTS CANVAS WORKSPACE -----------------

function renderArtifactCanvas(artifact) {
    activeArtifact = artifact;
    canvasTypeBadge.textContent = artifact.type.toUpperCase();
    canvasTitle.textContent = `${activeConversation?.title || 'Workspace'} - ${artifact.type}`;
    canvasCodeBlock.textContent = artifact.content;
    
    // Render split panel layout
    canvasPanel.style.display = 'flex';
}

function copyCanvasContent() {
    if (!activeArtifact) return;
    navigator.clipboard.writeText(activeArtifact.content)
        .then(() => showToast('Artifact content copied to clipboard!'))
        .catch(() => showToast('Copy failed.', 'error'));
}

function downloadCanvasContent() {
    if (!activeArtifact) return;
    
    // Guess file extension matching the type
    let ext = '.txt';
    if (activeArtifact.type === 'code') ext = '.py';
    else if (activeArtifact.type === 'sql') ext = '.sql';
    else if (activeArtifact.type === 'json') ext = '.json';
    else if (activeArtifact.type === 'markdown') ext = '.md';

    const filename = `bluwhale_artifact_${activeArtifact.id}${ext}`;
    const blob = new Blob([activeArtifact.content], { type: 'text/plain' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = filename;
    link.click();
    
    showToast(`Downloading artifact document: ${filename}...`);
}

function toggleCanvasExpand() {
    canvasPanel.classList.toggle('maximized');
    const isMax = canvasPanel.classList.contains('maximized');
    canvasExpandBtn.innerHTML = isMax ? `<i class="fa-solid fa-compress"></i> Restore` : `<i class="fa-solid fa-expand"></i> Maximize`;
}

function closeCanvas() {
    canvasPanel.style.display = 'none';
    canvasPanel.classList.remove('maximized');
    if (canvasExpandBtn) {
        canvasExpandBtn.innerHTML = `<i class="fa-solid fa-expand"></i> Maximize`;
    }
}

function openCanvas() {
    if (activeArtifact) {
        canvasPanel.style.display = 'flex';
    }
}

// ----------------- RAG KNOWLEDGE INGUSTION -----------------

async function openManageKbModal() {
    if (!activeConversation) return;
    const assistantId = activeConversation.assistant_id;
    const name = activeConversation.assistant_name || 'Assistant';

    document.getElementById('kb-bot-title').textContent = name;
    
    // Reset forms
    document.getElementById('kb-text-form').reset();
    document.getElementById('kb-file-form').reset();
    document.getElementById('kb-url-form').reset();

    // Default tab state
    switchKbTab('text-tab');

    document.getElementById('kb-modal').classList.add('open');
    loadKbDocuments(assistantId);
}

async function loadKbDocuments(assistantId) {
    const listEl = document.getElementById('kb-docs-list');
    listEl.innerHTML = '<div class="loading-state"><i class="fa-solid fa-spinner fa-spin"></i> Fetching docs...</div>';

    try {
        const data = await apiRequest(`/api/v1/knowledge-bases/?assistant_id=${assistantId}&size=100`);
        kbDocuments = data.items;
        document.getElementById('kb-docs-count').textContent = kbDocuments.length;
        renderKbDocsList(assistantId);
    } catch (err) {
        listEl.innerHTML = '<div class="loading-state text-danger">Error loading document list.</div>';
    }
}

function renderKbDocsList(assistantId) {
    const listEl = document.getElementById('kb-docs-list');
    if (kbDocuments.length === 0) {
        listEl.innerHTML = '<div class="loading-state">No context documents ingested.</div>';
        return;
    }

    listEl.innerHTML = '';
    kbDocuments.forEach(doc => {
        const item = document.createElement('div');
        item.className = 'kb-doc-item';
        item.innerHTML = `
            <div class="kb-doc-info">
                <div class="kb-doc-title">${escapeHTML(doc.name)}</div>
                <div class="kb-doc-source">
                    <span class="${doc.data_source}-source">${escapeHTML(doc.data_source)}</span>
                    <span>${escapeHTML(doc.description || 'No description')}</span>
                </div>
            </div>
            <div class="kb-doc-actions">
                <button class="btn-action delete-action" onclick="deleteKbDocument(${doc.id}, ${assistantId})" title="Delete Source Document"><i class="fa-solid fa-trash-can"></i></button>
            </div>
        `;
        listEl.appendChild(item);
    });
}

async function deleteKbDocument(kbId, assistantId) {
    if (!confirm("Are you sure you want to delete this RAG source? Linked vectors will be wiped!")) {
        return;
    }

    try {
        await apiRequest(`/api/v1/knowledge-bases/${kbId}`, 'DELETE');
        showToast('RAG document source wiped.');
        loadKbDocuments(assistantId);
        // Refresh active chat info
        if (activeConversation) {
            updateConsoleBadges(activeConversation);
        }
    } catch (err) {
        showToast('Failed to delete document.', 'error');
    }
}

function switchKbTab(tabId) {
    // Tab toggler
    const tabs = document.querySelectorAll('#kb-modal .tab-btn');
    const panes = document.querySelectorAll('#kb-modal .tab-pane');
    
    tabs.forEach(tab => tab.classList.remove('active'));
    panes.forEach(pane => pane.classList.remove('active'));
    
    // Find active trigger target
    const currentBtn = Array.from(tabs).find(b => b.outerHTML.includes(`'${tabId}'`));
    if (currentBtn) currentBtn.classList.add('active');
    
    document.getElementById(tabId).classList.add('active');
}

// KB Submission forms
async function addKbText(event) {
    event.preventDefault();
    if (!activeConversation) return;
    const assistantId = activeConversation.assistant_id;

    const payload = {
        name: document.getElementById('kb-txt-name').value.trim(),
        description: document.getElementById('kb-txt-desc').value.trim(),
        data_source: 'text',
        content: document.getElementById('kb-txt-content').value.trim(),
        assistant_id: assistantId
    };

    try {
        await apiRequest('/api/v1/knowledge-bases/', 'POST', payload);
        showToast('Text source chunked & ingested.');
        document.getElementById('kb-text-form').reset();
        loadKbDocuments(assistantId);
        updateConsoleBadges(activeConversation);
    } catch (err) {
        showToast('Failed to save text.', 'error');
    }
}

async function addKbFile(event) {
    event.preventDefault();
    if (!activeConversation) return;
    const assistantId = activeConversation.assistant_id;

    const fileInput = document.getElementById('kb-file-input');
    if (fileInput.files.length === 0) return;

    const formData = new FormData();
    formData.append('file', fileInput.files[0]);
    formData.append('assistant_id', assistantId);
    formData.append('name', document.getElementById('kb-file-name').value.trim());
    formData.append('description', document.getElementById('kb-file-desc').value.trim());

    try {
        await apiRequest('/api/v1/knowledge-bases/upload', 'POST', formData, true);
        showToast('File document parsed successfully.');
        document.getElementById('kb-file-form').reset();
        loadKbDocuments(assistantId);
        updateConsoleBadges(activeConversation);
    } catch (err) {
        showToast('Upload parsed error.', 'error');
    }
}

async function addKbUrl(event) {
    event.preventDefault();
    if (!activeConversation) return;
    const assistantId = activeConversation.assistant_id;

    const payload = {
        url: document.getElementById('kb-url-input').value.trim(),
        assistant_id: assistantId,
        name: document.getElementById('kb-url-name').value.trim(),
        description: document.getElementById('kb-url-desc').value.trim()
    };

    try {
        await apiRequest('/api/v1/knowledge-bases/scrape', 'POST', payload);
        showToast('Webpage crawled and indexed.');
        document.getElementById('kb-url-form').reset();
        loadKbDocuments(assistantId);
        updateConsoleBadges(activeConversation);
    } catch (err) {
        showToast('Crawler index error.', 'error');
    }
}

// ----------------- ASSISTANTS (CUSTOM GPTs) -----------------

async function loadAssistants() {
    try {
        const data = await apiRequest('/api/v1/assistants/?size=100');
        assistants = data.items;
    } catch (err) {
        showToast('Failed to load assistants list.', 'error');
    }
}

function openAssistantMgrModal() {
    document.getElementById('assistant-form').reset();
    document.getElementById('edit-assistant-id').value = '';
    document.getElementById('assistant-mgr-modal').classList.add('open');
    renderAssistantsList();
}

function renderAssistantsList() {
    const container = document.getElementById('assistants-list');
    container.innerHTML = '';

    if (assistants.length === 0) {
        container.innerHTML = `<div class="loading-state">No custom assistant personas configured.</div>`;
        return;
    }

    assistants.forEach(ast => {
        const card = document.createElement('div');
        card.className = 'kb-doc-item';
        card.innerHTML = `
            <div class="kb-doc-info" style="cursor: pointer;" onclick="editAssistant(${ast.id})">
                <div class="kb-doc-title"><i class="${escapeHTML(ast.avatar)}"></i> ${escapeHTML(ast.name)}</div>
                <div class="kb-doc-source">
                    <span>${escapeHTML(ast.description || 'No description')}</span>
                </div>
            </div>
            <div class="kb-doc-actions">
                <button class="btn-action edit-action" onclick="editAssistant(${ast.id})" title="Edit Assistant Persona"><i class="fa-solid fa-pen-to-square"></i></button>
                <button class="btn-action delete-action" onclick="deleteAssistant(event, ${ast.id})" title="Delete Assistant"><i class="fa-solid fa-trash-can"></i></button>
            </div>
        `;
        container.appendChild(card);
    });
}

function editAssistant(astId) {
    const ast = assistants.find(a => a.id === astId);
    if (!ast) return;

    document.getElementById('edit-assistant-id').value = ast.id;
    document.getElementById('ast-name').value = ast.name;
    document.getElementById('ast-description').value = ast.description || '';
    document.getElementById('ast-avatar').value = ast.avatar || 'fa-solid fa-wand-magic-sparkles';
    document.getElementById('ast-prompt').value = ast.system_prompt || '';
}

async function saveAssistant(event) {
    event.preventDefault();
    const astId = document.getElementById('edit-assistant-id').value;
    const payload = {
        name: document.getElementById('ast-name').value.trim(),
        description: document.getElementById('ast-description').value.trim(),
        avatar: document.getElementById('ast-avatar').value,
        system_prompt: document.getElementById('ast-prompt').value.trim()
    };

    try {
        if (astId) {
            await apiRequest(`/api/v1/assistants/${astId}`, 'PUT', payload);
            showToast('Assistant settings modified.');
        } else {
            await apiRequest('/api/v1/assistants/', 'POST', payload);
            showToast('New Custom Assistant agent registered.');
        }
        document.getElementById('assistant-form').reset();
        document.getElementById('edit-assistant-id').value = '';
        await loadAssistants();
        renderAssistantsList();
        
        // Reload side workspace tree to update names
        loadProjects();
    } catch (err) {
        showToast('Error registering assistant.', 'error');
    }
}

async function deleteAssistant(event, astId) {
    event.stopPropagation();
    if (!confirm("Are you sure you want to delete this assistant? All linked threads will be cascade-deleted!")) {
        return;
    }

    try {
        await apiRequest(`/api/v1/assistants/${astId}`, 'DELETE');
        showToast('Assistant deleted.');
        
        // If the active conversation uses this assistant, reset chat workspace
        if (activeConversation && activeConversation.assistant_id === astId) {
            activeConversation = null;
            resetChatWorkspace();
        }

        await loadAssistants();
        renderAssistantsList();
        loadProjects();
    } catch (err) {
        showToast('Error deleting assistant.', 'error');
    }
}

// ----------------- USER PROFILE MEMORIES -----------------

async function loadMemories() {
    try {
        const data = await apiRequest('/api/v1/memories/?size=100');
        memories = data.items;
    } catch (err) {
        showToast('Failed to load user memories.', 'error');
    }
}

function openMemoryMgrModal() {
    document.getElementById('memory-form').reset();
    document.getElementById('edit-memory-id').value = '';
    document.getElementById('memory-mgr-modal').classList.add('open');
    renderMemoriesList();
}

function renderMemoriesList() {
    const container = document.getElementById('memories-list');
    container.innerHTML = '';

    if (memories.length === 0) {
        container.innerHTML = `<div class="loading-state">No profile memories registered yet. Try disclosing some stack details in chat!</div>`;
        return;
    }

    memories.forEach(mem => {
        const card = document.createElement('div');
        card.className = 'memory-card';
        card.innerHTML = `
            <div class="kb-doc-info" style="flex-grow:1;">
                <div class="memory-text">${escapeHTML(mem.memory_text)}</div>
                <div class="memory-meta">
                    <span class="memory-category-tag">${escapeHTML(mem.category)}</span>
                </div>
            </div>
            <div class="kb-doc-actions">
                <button class="btn-action delete-action" onclick="deleteMemory(${mem.id})" title="Delete Memory Fact"><i class="fa-solid fa-trash-can"></i></button>
            </div>
        `;
        container.appendChild(card);
    });
}

async function saveMemory(event) {
    event.preventDefault();
    const memId = document.getElementById('edit-memory-id').value;
    const payload = {
        memory_text: document.getElementById('mem-text').value.trim(),
        category: document.getElementById('mem-category').value
    };

    try {
        if (memId) {
            await apiRequest(`/api/v1/memories/${memId}`, 'PUT', payload);
            showToast('User memory fact updated.');
        } else {
            await apiRequest('/api/v1/memories/', 'POST', payload);
            showToast('New user memory manually saved.');
        }
        document.getElementById('memory-form').reset();
        document.getElementById('edit-memory-id').value = '';
        await loadMemories();
        renderMemoriesList();
    } catch (err) {
        showToast('Error saving user memory card.', 'error');
    }
}

async function deleteMemory(memId) {
    if (!confirm("Are you sure you want to forget this fact about the user?")) {
        return;
    }

    try {
        await apiRequest(`/api/v1/memories/${memId}`, 'DELETE');
        showToast('Memory forgotten.');
        await loadMemories();
        renderMemoriesList();
    } catch (err) {
        showToast('Error removing memory fact.', 'error');
    }
}

// ----------------- UTILITIES -----------------

function closeModal(modalId) {
    document.getElementById(modalId).classList.remove('open');
}

function scrollToBottom() {
    messagesContainerEl.scrollTop = messagesContainerEl.scrollHeight;
}

function showToast(message, type = 'success') {
    // Remove existing toast if any
    const existing = document.querySelector('.toast-msg');
    if (existing) existing.remove();

    const toast = document.createElement('div');
    toast.className = 'toast-msg';
    toast.style.cssText = `
        position: fixed;
        bottom: 24px;
        right: 24px;
        padding: 12px 20px;
        font-family: var(--font-body);
        font-size: 12px;
        font-weight: 700;
        z-index: 99999;
        animation: bubbleIn 200ms cubic-bezier(0.16, 1, 0.3, 1);
        background-color: var(--bg-card);
        color: var(--text-primary);
        border-radius: 10px;
        box-shadow: 0 8px 24px rgba(10,34,51,0.4);
        display: flex;
        align-items: center;
        gap: 9px;
        max-width: 340px;
        backdrop-filter: blur(12px);
    `;
    
    let accentColor, iconName;
    if (type === 'success') {
        accentColor = 'var(--accent-green)';
        iconName = 'fa-circle-check';
    } else if (type === 'warning') {
        accentColor = '#f59e0b';
        iconName = 'fa-triangle-exclamation';
    } else if (type === 'info') {
        accentColor = 'var(--accent-sky)';
        iconName = 'fa-circle-info';
    } else {
        accentColor = 'var(--accent-red)';
        iconName = 'fa-circle-xmark';
    }

    toast.style.border = `1px solid rgba(255,255,255,0.06)`;
    toast.style.borderLeft = `3px solid ${accentColor}`;
    toast.innerHTML = `<i class="fa-solid ${iconName}" style="color:${accentColor};font-size:13px;"></i> ${message}`;
    
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transition = 'opacity 400ms ease';
        setTimeout(() => toast.remove(), 400);
    }, 4000);
}

function escapeHTML(str) {
    if (!str) return '';
    return str.replace(/[&<>'"]/g, 
        tag => ({
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            "'": '&#39;',
            '"': '&quot;'
        }[tag] || tag)
    );
}
