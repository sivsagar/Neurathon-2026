/**
 * MicroWin - Frontend Application
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
        insightsModal: document.getElementById('insightsModal'),
        closeModal: document.getElementById('closeModal'),
        insightsLoading: document.getElementById('insightsLoading'),
        insightsData: document.getElementById('insightsData'),
        peakHourValue: document.getElementById('peakHourValue'),
        bestEnergyValue: document.getElementById('bestEnergyValue'),
        totalWins: document.getElementById('totalWins'),
        resumeTaskBtn: document.getElementById('resumeTaskBtn'),
        newTaskLinks: document.querySelectorAll('.newTaskLink')
    };
}

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
        const response = await apiCall('/api/task/start', 'POST', {
            goal,
            energy_level: state.energyLevel
        });

        state.currentTaskId = response.task_id;
        state.currentStepId = response.step_id;
        state.currentGoal = goal;
        state.stepsCompleted = 0;
        state.stepStartTime = Date.now();

        displayStep(response);
        updateProgress(0);
        showScreen('step');

        // Auto-speak first step
        speakText(response.step_text);
    } catch (error) {
        console.error('Error starting task:', error);
        showScreen('input');
    } finally {
        state.isLoading = false;
    }
}

async function completeStepAndGetNext() {
    state.isLoading = true;
    const duration = Math.round((Date.now() - state.stepStartTime) / 1000);

    try {
        const response = await apiCall('/api/task/next', 'POST', {
            task_id: state.currentTaskId,
            step_id: state.currentStepId,
            action: 'done',
            duration_seconds: duration
        });

        state.currentStepId = response.step_id;
        state.stepsCompleted++;
        state.stepStartTime = Date.now();

        if (response.is_complete) {
            updateProgress(10); // Force 100%
            showVictory();
        } else {
            displayStep(response);
            updateProgress(state.stepsCompleted);

            // Pop effect
            elements.dopamineBar.parentElement.classList.add('dopamine-pop');
            setTimeout(() => elements.dopamineBar.parentElement.classList.remove('dopamine-pop'), 600);

            speakText(response.step_text);
        }
    } catch (error) {
        console.error('Error getting next step:', error);
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

// ========== Insights Modal ==========
async function openInsights() {
    elements.insightsModal.classList.add('active');
    elements.insightsLoading.style.display = 'block';
    elements.insightsData.style.display = 'none';

    try {
        const data = await apiCall('/api/insights');

        // Update UI
        elements.peakHourValue.textContent = data.best_time_to_start !== "No data"
            ? `${data.best_time_to_start}:00`
            : "--:00";

        const topEfficiency = data.efficiency_log.sort((a, b) => b.efficiency - a.efficiency)[0];
        elements.bestEnergyValue.textContent = topEfficiency
            ? topEfficiency.level.charAt(0).toUpperCase() + topEfficiency.level.slice(1)
            : "No data";

        elements.insightsLoading.style.display = 'none';
        elements.insightsData.style.display = 'grid';
    } catch (error) {
        elements.insightsLoading.textContent = "Complete a few tasks to see your patterns!";
    }
}

function closeInsights() {
    elements.insightsModal.classList.remove('active');
}

function showVictory() {
    elements.totalWins.textContent = state.stepsCompleted;
    showScreen('victory');

    // Play celebratory sound or logic here
    speakText("Task crushed! well done!");

    // Trigger confetti if library was here, but for now we have the CSS celebrate animation
}

// ========== Gamification & Voice ==========
function updateProgress(count) {
    // Assuming a typical task is 10-15 micro-steps, but let's make it 
    // feel rewarding by capping at 100% after 15 steps or just incremental
    const progress = Math.min((count / 10) * 100, 100);
    elements.dopamineBar.style.width = `${progress}%`;
}

function speakText(text) {
    if ('speechSynthesis' in window) {
        // Cancel any ongoing speech
        window.speechSynthesis.cancel();

        const utterance = new SpeechSynthesisUtterance(text);
        utterance.rate = 0.9; // Slightly slower for better processing
        utterance.pitch = 1.1; // Friendly tone
        window.speechSynthesis.speak(utterance);
    }
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
function setupEventListeners() {
    // Helper to safely add listeners
    const addListener = (element, event, callback) => {
        if (element) {
            element.addEventListener(event, callback);
        } else {
            console.warn(`Could not find element for ${event} listener`);
        }
    };

    addListener(elements.taskInput, 'input', (e) => {
        const hasValue = e.target.value.trim().length > 0;
        elements.startBtn.disabled = !hasValue;
    });

    addListener(elements.taskInput, 'keydown', (e) => {
        if (e.key === 'Enter' && e.ctrlKey && !elements.startBtn.disabled) {
            handleStartTask();
        }
    });

    addListener(elements.startBtn, 'click', handleStartTask);
    addListener(elements.doneBtn, 'click', completeStepAndGetNext);
    addListener(elements.tooHardBtn, 'click', simplifyCurrentStep);
    addListener(elements.pauseBtn, 'click', pauseTask);
    addListener(elements.resumeTaskBtn, 'click', () => showScreen('step'));

    // Use the plurals for the new task links
    if (elements.newTaskLinks) {
        elements.newTaskLinks.forEach(link => {
            addListener(link, 'click', resetToInput);
        });
    }

    addListener(elements.fontToggle, 'click', toggleFont);
    addListener(elements.speakBtn, 'click', () => {
        if (elements.stepText) speakText(elements.stepText.textContent);
    });
    addListener(elements.insightsToggle, 'click', openInsights);
    addListener(elements.closeModal, 'click', closeInsights);

    // Close modal on outside click
    window.addEventListener('click', (e) => {
        if (elements.insightsModal && e.target === elements.insightsModal) closeInsights();
    });

    // Energy Selector Listeners
    if (elements.energyBtns) {
        elements.energyBtns.forEach(btn => {
            addListener(btn, 'click', () => {
                const level = btn.dataset.level;
                state.energyLevel = level;

                // Sync all energy buttons with this level
                elements.energyBtns.forEach(b => {
                    if (b.dataset.level === level) {
                        b.classList.add('active');
                    } else {
                        b.classList.remove('active');
                    }
                });

                console.log("Energy level updated to:", state.energyLevel);
            });
        });
    }
}

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
    initElements();
    setupEventListeners();
    loadFontPreference();
    showScreen('input');

    // Focus input on load
    if (elements.taskInput) {
        elements.taskInput.focus();
    }
}

// Start the app when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}
