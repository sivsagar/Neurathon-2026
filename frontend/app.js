/**
 * The Smart Companion - Frontend Application
 * Handles UI state management and API communication
 */

// API Configuration
const API_BASE_URL = window.location.origin.includes('localhost')
    ? 'http://localhost:8000'
    : window.location.origin;

// State Management
const state = {
    currentTaskId: null,
    currentStepId: null,
    currentGoal: null,
    isLoading: false
};

// DOM Elements
const screens = {
    input: document.getElementById('inputScreen'),
    loading: document.getElementById('loadingScreen'),
    step: document.getElementById('stepScreen'),
    paused: document.getElementById('pausedScreen')
};

const elements = {
    taskInput: document.getElementById('taskInput'),
    startBtn: document.getElementById('startBtn'),
    fontToggle: document.getElementById('fontToggle'),
    stepText: document.getElementById('stepText'),
    stepBadge: document.getElementById('stepBadge'),
    doneBtn: document.getElementById('doneBtn'),
    tooHardBtn: document.getElementById('tooHardBtn'),
    pauseBtn: document.getElementById('pauseBtn'),
    newTaskBtn: document.getElementById('newTaskBtn')
};

// ========== Screen Management ==========
function showScreen(screenName) {
    Object.values(screens).forEach(screen => screen.classList.remove('active'));
    screens[screenName].classList.add('active');
}

// ========== API Client ==========
async function apiCall(endpoint, method = 'GET', body = null) {
    try {
        const options = {
            method,
            headers: {
                'Content-Type': 'application/json'
            }
        };

        if (body) {
            options.body = JSON.stringify(body);
        }

        const response = await fetch(`${API_BASE_URL}${endpoint}`, options);

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'API request failed');
        }

        return await response.json();
    } catch (error) {
        console.error('API Error:', error);
        alert('Something went wrong. Please try again.');
        throw error;
    }
}

// ========== Task Management ==========
async function startTask(goal) {
    state.isLoading = true;
    showScreen('loading');

    try {
        const response = await apiCall('/api/task/start', 'POST', { goal });

        state.currentTaskId = response.task_id;
        state.currentStepId = response.step_id;
        state.currentGoal = goal;

        displayStep(response);
        showScreen('step');
    } catch (error) {
        console.error('Error starting task:', error);
        showScreen('input');
    } finally {
        state.isLoading = false;
    }
}

async function completeStepAndGetNext() {
    state.isLoading = true;
    showScreen('loading');

    try {
        const response = await apiCall('/api/task/next', 'POST', {
            task_id: state.currentTaskId,
            step_id: state.currentStepId,
            action: 'done'
        });

        state.currentStepId = response.step_id;
        displayStep(response);
        showScreen('step');
    } catch (error) {
        console.error('Error getting next step:', error);
        showScreen('step');
    } finally {
        state.isLoading = false;
    }
}

async function simplifyCurrentStep() {
    state.isLoading = true;
    showScreen('loading');

    try {
        const response = await apiCall('/api/task/simplify', 'POST', {
            task_id: state.currentTaskId,
            step_id: state.currentStepId
        });

        state.currentStepId = response.step_id;
        displayStep(response);
        showScreen('step');
    } catch (error) {
        console.error('Error simplifying step:', error);
        showScreen('step');
    } finally {
        state.isLoading = false;
    }
}

async function pauseTask() {
    try {
        await apiCall('/api/task/pause', 'POST', {
            task_id: state.currentTaskId,
            step_id: state.currentStepId,
            action: 'pause'
        });

        showScreen('paused');
    } catch (error) {
        console.error('Error pausing task:', error);
    }
}

function displayStep(stepData) {
    elements.stepText.textContent = stepData.step_text;
    elements.stepBadge.textContent = `~${stepData.estimated_seconds} sec`;

    // Update aria-label for accessibility
    elements.stepBadge.setAttribute('aria-label', `Estimated time: ${stepData.estimated_seconds} seconds`);
}

// ========== Font Toggle ==========
function toggleFont() {
    const isDyslexic = document.body.classList.toggle('dyslexic-font');
    localStorage.setItem('dyslexicFont', isDyslexic);

    // Update button aria-label
    const fontName = isDyslexic ? 'OpenDyslexic' : 'Lexend';
    elements.fontToggle.setAttribute('title', `Current font: ${fontName}. Click to toggle.`);
}

function loadFontPreference() {
    const isDyslexic = localStorage.getItem('dyslexicFont') === 'true';
    if (isDyslexic) {
        document.body.classList.add('dyslexic-font');
    }
}

// ========== Event Listeners ==========
elements.taskInput.addEventListener('input', (e) => {
    const hasValue = e.target.value.trim().length > 0;
    elements.startBtn.disabled = !hasValue;
});

elements.taskInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && e.ctrlKey && !elements.startBtn.disabled) {
        handleStartTask();
    }
});

elements.startBtn.addEventListener('click', handleStartTask);
elements.doneBtn.addEventListener('click', completeStepAndGetNext);
elements.tooHardBtn.addEventListener('click', simplifyCurrentStep);
elements.pauseBtn.addEventListener('click', pauseTask);
elements.newTaskBtn.addEventListener('click', resetToInput);
elements.fontToggle.addEventListener('click', toggleFont);

function handleStartTask() {
    const goal = elements.taskInput.value.trim();
    if (goal) {
        startTask(goal);
    }
}

function resetToInput() {
    state.currentTaskId = null;
    state.currentStepId = null;
    state.currentGoal = null;
    elements.taskInput.value = '';
    elements.startBtn.disabled = true;
    showScreen('input');
}

// ========== Initialization ==========
function init() {
    loadFontPreference();
    showScreen('input');

    // Focus input on load
    elements.taskInput.focus();
}

// Start the app when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}
