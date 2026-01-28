# Quick Start Guide

## Prerequisites

1. **Docker Desktop** installed ([Download here](https://www.docker.com/products/docker-desktop))
2. **Google Gemini API Key** ([Get one here](https://aistudio.google.com/app/apikey))

## Setup (3 minutes)

### Step 1: Configure API Key

```bash
# Copy the environment template
cp .env.example .env

# Open .env in your editor and add your API key
# Change this line:
# GEMINI_API_KEY=AIzaSy...your-key...
# To:
# GEMINI_API_KEY=AIzaSyAoZ1yA3yyvDYYqUMpHsfwsMh4VfAHAAKI
```

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

## Using The Smart Companion

### First Task

1. **Enter a task** that feels overwhelming:
   - "Clean my room"
   - "Reply to important email"
   - "Start homework"

2. **Click Start** and wait 3-5 seconds

3. **You'll see ONE action** like:
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
GEMINI_API_KEY=AIzaSyAoZ1yA3yyvDYYqUMpHsfwsMh4VfAHAAKI
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

✅ **What stays local:**
- All your task data
- Step completion history
- Font preferences

✅ **What gets sent to Google Gemini:**
- Only task descriptions (e.g., "Clean my room")
- NO personal info, NO timestamps, NO user ID

---

## For Judges

### Quick Demo Flow

1. Start Docker: `docker-compose up --build`
2. Open browser: `http://localhost:8000`
3. Try: "Clean my room"
4. See: "Pick up the first item you see on the floor"
5. Click "Too Hard" to see simplification
6. Click "Done" to see next step

**Total time:** <3 minutes to see core functionality

---

## Need Help?

Check the documentation:
- [README.md](README.md) - Full project overview
- [ARCHITECTURE.md](ARCHITECTURE.md) - Technical details
