/**
 * MicroWin 2.0 - The Therapeutic Cognitive Prosthetic
 * Handles Multi-User Profiles, Gamification, and AI Assistance
 */

// API Configuration
const API_BASE_URL = window.location.origin.includes('localhost')
    ? 'http://localhost:8000'
    : window.location.origin;

// State Management
const state = {
    currentUser: null,
    userList: [],
    currentTaskId: null,
    currentStepId: null,
    currentGoal: null,
    energyLevel: 'medium',
    stepsCompleted: 0,
    stepStartTime: null,
    isLoading: false
};

// DOM Elements
const screens = {
    input: document.getElementById('inputScreen'),
    loading: document.getElementById('loadingScreen'),
    step: document.getElementById('stepScreen'),
    paused: document.getElementById('pausedScreen'),
    victory: document.getElementById('victoryScreen')
};

const modals = {
    insights: document.getElementById('insightsModal'),
    diet: document.getElementById('dietModal'),
    profile: document.getElementById('profileModal')
};

let elements = {};

function initElements() {
    elements = {
        taskInput: document.getElementById('taskInput'),
        startBtn: document.getElementById('startBtn'),
        fontToggle: document.getElementById('fontToggle'),
        stepText: document.getElementById('stepText'),
        stepBadge: document.getElementById('stepBadge'),
        doneBtn: document.getElementById('doneBtn'),
        tooHardBtn: document.getElementById('tooHardBtn'),
        pauseBtn: document.getElementById('pauseBtn'),
        speakBtn: document.getElementById('speakBtn'),
        dopamineBar: document.getElementById('dopamineBar'),
        energyBtns: document.querySelectorAll('.energy-btn'),
        insightsToggle: document.getElementById('insightsToggle'),
        dietToggle: document.getElementById('dietToggle'),
        totalWins: document.getElementById('totalWins'),
        resumeTaskBtn: document.getElementById('resumeTaskBtn'),
        newTaskLinks: document.querySelectorAll('.newTaskLink'),
        nextStepPreview: document.getElementById('nextStepPreview'),
        nextStepText: document.getElementById('nextStepText'),
        timelineSlices: document.getElementById('timelineSlices'),
        userName: document.getElementById('userName'),
        userLevel: document.getElementById('userLevel'),
        userAvatar: document.getElementById('userAvatar'),
        userXpBar: document.getElementById('userXpBar'),
        xpText: document.getElementById('xpText'),
        currentProfile: document.getElementById('currentProfile'),
        userList: document.getElementById('userList'),
        createProfileBtn: document.getElementById('createProfileBtn'),
        dietList: document.getElementById('dietList'),
        addDietTargetBtn: document.getElementById('addDietTargetBtn'),
        visionBtn: document.getElementById('visionBtn')
    };
}

// ========== Profile Management ==========
async function fetchUsers() {
    try {
        state.userList = await apiCall('/api/users');
        renderUserList();

        // Auto-select last used user, or first user
        const lastUserId = localStorage.getItem('microwin_lastUserId');
        const lastUser = state.userList.find(u => u.id === lastUserId);

        if (lastUser) {
            selectUser(lastUser);
        } else if (state.userList.length > 0) {
            selectUser(state.userList[0]);
        } else {
            showModal('profile');
        }
    } catch (error) {
        console.error("Failed to fetch users:", error);
    }
}

function renderUserList() {
    if (!elements.userList) return;
    elements.userList.innerHTML = '';
    state.userList.forEach(user => {
        const card = document.createElement('div');
        card.className = 'profile-card';
        card.innerHTML = `
            <img src="${user.avatar_url || `https://api.dicebear.com/7.x/avataaars/svg?seed=${user.name}`}" alt="Avatar">
            <p>${user.name}</p>
            <span class="user-level">Lvl ${user.level}</span>
        `;
        card.onclick = () => {
            selectUser(user);
            closeModals();
        };
        elements.userList.appendChild(card);
    });
}

function selectUser(user) {
    state.currentUser = user;
    if (elements.userName) elements.userName.textContent = user.name;
    if (elements.userLevel) elements.userLevel.textContent = `Lvl ${user.level}`;
    if (elements.userAvatar) elements.userAvatar.src = user.avatar_url || `https://api.dicebear.com/7.x/avataaars/svg?seed=${user.name}`;
    updateXpDisplay(user.xp, user.level);
    localStorage.setItem('microwin_lastUserId', user.id);
}

function updateXpDisplay(xp, level) {
    const nextLevelXp = Math.pow(level, 2) * 100;
    const progress = (xp / nextLevelXp) * 100;
    if (elements.userXpBar) elements.userXpBar.style.width = `${progress}%`;
    if (elements.xpText) elements.xpText.textContent = `${xp} / ${nextLevelXp} XP`;
}

// ========== Screen & Modal Management ==========
function showScreen(screenName) {
    Object.values(screens).forEach(screen => {
        if (screen) {
            screen.classList.remove('active');
            screen.classList.remove('screen-switch');
        }
    });
    if (screens[screenName]) {
        screens[screenName].classList.add('active');
        requestAnimationFrame(() => screens[screenName].classList.add('screen-switch'));
    }
}

function showModal(modalName) {
    if (modals[modalName]) modals[modalName].classList.add('active');
}

function closeModals() {
    Object.values(modals).forEach(m => {
        if (m) m.classList.remove('active');
    });
}

// ========== API Client ==========
async function apiCall(endpoint, method = 'GET', body = null) {
    try {
        const options = {
            method,
            headers: { 'Content-Type': 'application/json' }
        };
        if (body) options.body = JSON.stringify(body);
        const response = await fetch(`${API_BASE_URL}${endpoint}`, options);
        if (!response.ok) throw new Error('API request failed');
        return await response.json();
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
}

// ========== Task Management ==========
async function startTask(goal) {
    if (!state.currentUser) {
        showModal('profile');
        return;
    }
    state.isLoading = true;
    showScreen('loading');
    try {
        const response = await apiCall('/api/task/start', 'POST', {
            goal,
            user_id: state.currentUser.id,
            energy_level: state.energyLevel
        });
        state.currentTaskId = response.task_id;
        state.currentStepId = response.step_id;
        state.currentGoal = goal;
        state.stepsCompleted = 0;
        state.stepStartTime = Date.now();
        displayStep(response);
        updateProgress(0);
        renderTimeline(0, 5);
        showScreen('step');
        speakText(response.step_text);
    } catch (error) {
        showScreen('input');
    } finally {
        state.isLoading = false;
    }
}

async function completeStepAndGetNext() {
    const duration = Math.round((Date.now() - state.stepStartTime) / 1000);
    try {
        const response = await apiCall('/api/task/next', 'POST', {
            task_id: state.currentTaskId,
            step_id: state.currentStepId,
            action: 'done',
            duration_seconds: duration
        });

        // Update User Stats (XP Awarded)
        await refreshCurrentUser();

        state.currentStepId = response.step_id;
        state.stepsCompleted++;
        state.stepStartTime = Date.now();

        if (response.is_complete) {
            updateProgress(10);
            showVictory();
        } else {
            displayStep(response);
            updateProgress(state.stepsCompleted);
            renderTimeline(state.stepsCompleted, 10);
            triggerNudge();
            speakText(response.step_text);
        }
    } catch (error) {
        console.error('Error getting next step:', error);
    }
}

async function refreshCurrentUser() {
    const users = await apiCall('/api/users');
    const updated = users.find(u => u.id === state.currentUser.id);
    if (updated) selectUser(updated);
}

function displayStep(stepData) {
    if (elements.stepText) elements.stepText.textContent = stepData.step_text;
    if (elements.stepBadge) elements.stepBadge.textContent = `~${stepData.estimated_seconds} sec`;
    if (elements.nextStepPreview) {
        if (stepData.next_preview) {
            elements.nextStepPreview.style.display = 'block';
            if (elements.nextStepText) elements.nextStepText.textContent = stepData.next_preview;
        } else {
            elements.nextStepPreview.style.display = 'none';
        }
    }
}

// ========== Therapeutic Logic (Diet/Vision/Voice) ==========
async function openDietDashboard() {
    showModal('diet');
    if (state.currentUser && elements.dietList) {
        const targets = await apiCall(`/api/diet/targets/${state.currentUser.id}`);
        elements.dietList.innerHTML = '';
        targets.forEach(t => {
            const item = document.createElement('div');
            item.className = `diet-item ${t.completed ? 'completed' : ''}`;
            item.innerHTML = `<span>${t.target_text}</span>`;
            elements.dietList.appendChild(item);
        });
    }
}

async function suggestDietTarget() {
    if (!state.currentUser) return;
    try {
        const suggestions = [
            "Drink a full glass of water now",
            "Eat a handful of protein (nuts/jerky)",
            "Remove sugary drinks from your desk",
            "Eat one piece of fruit"
        ];
        const random = suggestions[Math.floor(Math.random() * suggestions.length)];
        await apiCall('/api/diet/targets', 'POST', {
            user_id: state.currentUser.id,
            target_text: random
        });
        openDietDashboard();
    } catch (e) { console.error(e); }
}

// ========== Insights Modal ==========
async function openInsights() {
    showModal('insights');
    const loading = document.getElementById('insightsLoading');
    const dataGrid = document.getElementById('insightsData');

    if (loading) loading.style.display = 'block';
    if (dataGrid) dataGrid.style.display = 'none';

    try {
        const data = await apiCall('/api/insights');

        const peakHour = document.getElementById('peakHourValue');
        const bestEnergy = document.getElementById('bestEnergyValue');

        if (peakHour) peakHour.textContent = data.best_time_to_start !== "No data" ? `${data.best_time_to_start}:00` : "--:00";

        if (bestEnergy) {
            const topEfficiency = data.efficiency_log.sort((a, b) => b.efficiency - a.efficiency)[0];
            bestEnergy.textContent = topEfficiency ? topEfficiency.level.toUpperCase() : "Medium";
        }

        if (loading) loading.style.display = 'none';
        if (dataGrid) dataGrid.style.display = 'grid';
    } catch (error) {
        if (loading) loading.textContent = "Complete a few tasks to see your patterns!";
    }
}

async function triggerVision() {
    speakText("Looking for micro-wins in your environment...");
    // Simulate Vision processing
    setTimeout(() => {
        if (elements.taskInput) {
            elements.taskInput.value = "Clean up the items on the table";
            if (elements.startBtn) elements.startBtn.disabled = false;
        }
        speakText("I noticed some clutter on your table. Shall we start there?");
    }, 2000);
}

function speakText(text) {
    if ('speechSynthesis' in window) {
        window.speechSynthesis.cancel();
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.rate = 0.85; // Therapeutic pace
        utterance.pitch = 1.05; // Friendly
        window.speechSynthesis.speak(utterance);
    }
}

// ========== Gamification & UI Utils ==========
function updateProgress(count) {
    const progress = Math.min((count / 10) * 100, 100);
    if (elements.dopamineBar) elements.dopamineBar.style.width = `${progress}%`;
}

function renderTimeline(current, total) {
    if (!elements.timelineSlices) return;
    elements.timelineSlices.innerHTML = '';
    for (let i = 0; i < 10; i++) {
        const slice = document.createElement('div');
        slice.className = `timeline-slice ${i < current ? 'past' : (i === current ? 'active' : '')}`;
        elements.timelineSlices.appendChild(slice);
    }
}

function triggerNudge() {
    if ('vibrate' in navigator) navigator.vibrate([10, 30, 10]);
}

function showVictory() {
    if (elements.totalWins) elements.totalWins.textContent = state.stepsCompleted;
    showScreen('victory');
    speakText("Task crushed! You've earned some XP. Well done!");
}

// ========== Event Listeners ==========
function setupEventListeners() {
    if (elements.taskInput) {
        elements.taskInput.addEventListener('input', (e) => {
            if (elements.startBtn) elements.startBtn.disabled = e.target.value.trim().length === 0;
        });
    }

    if (elements.startBtn) elements.startBtn.onclick = () => startTask(elements.taskInput.value.trim());
    if (elements.doneBtn) elements.doneBtn.onclick = completeStepAndGetNext;

    if (elements.tooHardBtn) {
        elements.tooHardBtn.onclick = async () => {
            try {
                const response = await apiCall('/api/task/simplify', 'POST', {
                    task_id: state.currentTaskId,
                    step_id: state.currentStepId
                });
                state.currentStepId = response.step_id;
                displayStep(response);
            } catch (e) {
                console.error("Simplification failed", e);
            }
        };
    }

    if (elements.pauseBtn) {
        elements.pauseBtn.onclick = async () => {
            await apiCall('/api/task/pause', 'POST', { task_id: state.currentTaskId, step_id: state.currentStepId, action: 'pause' });
            showScreen('paused');
        };
    }

    if (elements.speakBtn) {
        elements.speakBtn.onclick = () => {
            const text = elements.stepText ? elements.stepText.textContent : "";
            if (text) speakText(text);
        };
    }

    if (elements.fontToggle) {
        elements.fontToggle.onclick = () => {
            document.body.classList.toggle('dyslexic-font');
            elements.fontToggle.classList.toggle('active');
        };
    }

    if (elements.resumeTaskBtn) elements.resumeTaskBtn.onclick = () => showScreen('step');
    if (elements.insightsToggle) elements.insightsToggle.onclick = openInsights;
    if (elements.dietToggle) elements.dietToggle.onclick = openDietDashboard;
    if (elements.currentProfile) elements.currentProfile.onclick = () => showModal('profile');
    if (elements.addDietTargetBtn) elements.addDietTargetBtn.onclick = suggestDietTarget;
    if (elements.visionBtn) elements.visionBtn.onclick = triggerVision;

    if (elements.createProfileBtn) {
        elements.createProfileBtn.onclick = async () => {
            const name = prompt("Enter patient name:");
            if (name) {
                await apiCall('/api/users', 'POST', { name });
                fetchUsers();
            }
        };
    }

    document.querySelectorAll('.close-modal').forEach(btn => {
        btn.onclick = closeModals;
    });

    if (elements.newTaskLinks) {
        elements.newTaskLinks.forEach(link => {
            link.onclick = () => {
                if (elements.taskInput) elements.taskInput.value = '';
                showScreen('input');
            };
        });
    }

    if (elements.energyBtns) {
        elements.energyBtns.forEach(btn => {
            btn.onclick = () => {
                state.energyLevel = btn.dataset.level;
                elements.energyBtns.forEach(b => b.classList.toggle('active', b.dataset.level === state.energyLevel));
            };
        });
    }
}

// ========== Initialization ==========
function init() {
    initElements();
    setupEventListeners();
    fetchUsers();
    showScreen('input');
}

document.readyState === 'loading' ? document.addEventListener('DOMContentLoaded', init) : init();
