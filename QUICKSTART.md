# Quick Start Guide

## Prerequisites

1. **Ollama** installed ([Download here](https://ollama.ai))
2. **Mistral model** loaded (`ollama pull mistral`)

## Setup (3 minutes)

# Step 1: Initialize Ollama
# Run in your terminal:
ollama pull mistral

# Step 2: Configure Environment
cp .env.example .env
# Default settings work for localhost!

### Step 2: Start the Application

```bash
# Build and start with Docker Compose
docker-compose up --build

# You should see:
# ✅ Database initialized
# ✅ Application startup complete
# ✅ Uvicorn running on http://0.0.0.0:8000
```

### Step 3: Open in Browser

Navigate to: **http://localhost:8000**

---

## Using MicroWin

### First Task

1. **Enter a task** that feels overwhelming:
   - "Clean my room"
   - "Reply to important email"
   - "Start homework"

2. **Click Start** and wait 3-5 seconds

3. **Select your Energy Level**:
   - 🔋 **High**: Standard micro-steps.
   - 🪫 **Low**: "Micro-micro" steps (e.g., "Just sit down at your desk").

4. **You'll see ONE action** like:
   - "Pick up the first item you see on the floor"
   - Time estimate: ~8 seconds

4. **Three options:**
   - ✅ **Done** → Get next micro-step
   - ⚠️ **Too Hard** → Get simpler version
   - ⏸️ **Pause** → Save for later

### Example: "Too Hard" Flow

**Initial step:** "Pick up the first item on the floor"
↓ (Click "Too Hard")
**Simplified:** "Walk to the nearest visible item"
↓ (Click "Too Hard")
**Ultra-simplified:** "Take one step toward the floor"

The AI will keep breaking it down until it's trivially easy.

### Example: Complete Flow

```
1. Enter: "Clean my room"
2. Step 1: "Pick up the first item you see on the floor"
   → Click Done
3. Step 2: "Put the item in its proper place"
   → Click Done
4. Step 3: "Pick up the next visible item"
   → Click Done
...continue until room is clean
```

---

## Accessibility Features

### Font Toggle

Click the **icon in the top-right** to switch between:
- **Lexend** (modern, clean)
- **OpenDyslexic** (specialized for dyslexia)

Your preference is saved automatically.

### Keyboard Navigation

- **Tab** - Move between buttons
- **Enter** - Activate button
- **Ctrl+Enter** (in input) - Start task

---

## Troubleshooting

### Port 8000 Already in Use

```bash
# Stop the conflicting service or change port in docker-compose.yml
# Edit: "8001:8000" instead of "8000:8000"
```

### API Key Error

```bash
# Check your .env file
cat .env

# Make sure it shows:
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=mistral
```

### Docker Build Issues

```bash
# Clean rebuild
docker-compose down
docker-compose up --build
```

---

## Stopping the Application

```bash
# Press Ctrl+C in the terminal
# OR
docker-compose down
```

---

## Data Persistence

Your tasks are saved in:
```
./data/smart_companion.db
```

This file persists across Docker restarts. Your data never leaves your machine.

---

## Privacy

✅ **What stays on your machine:**
- Every single word you type
- Your task history
- AI-generated steps (locally processed)

✅ **External Data Flow:**
- **Zero.** No data is sent to any external server. This is 100% offline.

---

## For Judges

### Quick Demo Flow

1. Start Docker: `docker-compose up --build`
2. Open browser: `http://localhost:8000`
3. Try: "Clean my room"
4. Adjust Energy: Toggle between Low/High to see how the AI adapts.
5. See: "Pick up the first item you see on the floor"
6. Complete: Click "Done" and watch the **Dopamine Bar** pop!
7. Insights: Check the top-left icon to see performance analytics.

**Total time:** <3 minutes to see core functionality

---

## Need Help?

Check the documentation:
- [README.md](README.md) - Full project overview
- [ARCHITECTURE.md](ARCHITECTURE.md) - Technical details
