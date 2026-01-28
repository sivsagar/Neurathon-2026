"""AI prompt templates for Micro-Win generation."""


SYSTEM_PROMPT = """You are an AI assistant specialized in helping neurodivergent users (ADHD, Autism, Dyslexia) overcome task initiation paralysis.

Your ONLY job is to convert abstract goals into MICRO-WINS - ultra-specific, physically executable actions that:
- Take ≤10 seconds to complete
- Require ZERO decision-making
- Use concrete action verbs (pick, grab, open, tap, walk, touch)
- NEVER use abstract verbs (organize, plan, prepare, think, decide)

You must respond ONLY with valid JSON in this exact format:
{"step": "action description", "estimated_seconds": number}

CRITICAL RULES:
- Generate ONLY ONE step at a time
- Each step must be immediately actionable
- No choices, no planning, no thinking required
- Focus on the absolute first physical movement"""


def get_initial_step_prompt(goal: str) -> str:
    """Generate prompt for first micro-step."""
    return f"""TASK: {goal}

Generate the FIRST physically executable micro-step to start this task.

EXAMPLES OF GOOD MICRO-WINS:
- "Pick up the first item you see on the floor"
- "Walk to the kitchen sink"
- "Open your email app"
- "Grab the closest pen"
- "Stand up from your chair"

EXAMPLES OF BAD STEPS (too abstract):
- "Start cleaning your room"
- "Plan your email response"
- "Organize your thoughts"
- "Prepare to work"

Return ONLY valid JSON: {{"step": "...", "estimated_seconds": ...}}"""


def get_next_step_prompt(goal: str, previous_step: str) -> str:
    """Generate prompt for next micro-step."""
    return f"""ORIGINAL TASK: {goal}
PREVIOUS STEP COMPLETED: {previous_step}

Generate the NEXT physically executable micro-step.

This step should logically follow the previous one but remain:
- ≤10 seconds
- Concrete and physical
- No decision-making required

Return ONLY valid JSON: {{"step": "...", "estimated_seconds": ...}}"""


def get_simplification_prompt(current_step: str, simplification_level: int) -> str:
    """Generate prompt for simplifying a 'Too Hard' step."""
    return f"""The user found this step TOO HARD:
"{current_step}"

This is simplification level {simplification_level + 1}.

Break it into an EVEN SIMPLER physical action. Requirements:
- Must be SMALLER than the original step
- Target ≤5 seconds (even faster!)
- Remove ALL decision-making
- Focus on the absolute first micro-movement

EXAMPLES:
Original: "Pick up the first item on the floor"
Simplified: "Walk to the nearest visible item"
Ultra-simplified: "Take one step toward the floor"

Return ONLY valid JSON: {{"step": "...", "estimated_seconds": ...}}"""


def sanitize_goal_for_llm(goal: str) -> str:
    """
    Privacy filter: Remove potential PII from goal text.
    This is a simple pattern-based filter. In production, use more sophisticated NER.
    """
    # For hackathon MVP, we'll just pass through
    # In production, implement proper PII detection/removal
    return goal.strip()
