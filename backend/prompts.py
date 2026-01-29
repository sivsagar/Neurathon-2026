"""AI prompt templates for Micro-Win generation."""


SYSTEM_PROMPT = """You are an AI assistant specialized in helping neurodivergent users (ADHD, Autism, Dyslexia) overcome task initiation paralysis.

Your ONLY job is to convert abstract goals into MICRO-WINS - ultra-specific, physically executable actions that:
- Take ≤10 seconds to complete
- Require ZERO decision-making
- Use concrete action verbs (pick, grab, open, tap, walk, touch)
- NEVER use abstract verbs (organize, plan, prepare, think, decide)

You must respond ONLY with valid JSON in this exact format:
{"step": "action description", "estimated_seconds": number, "is_complete": boolean}

If the task goal has been fully accomplished by the previous steps, set "is_complete": true and provide a final encouraging message in "step". Otherwise, set "is_complete": false.

CRITICAL RULES:
- Generate ONLY ONE step at a time
- Each step must be immediately actionable
- No choices, no planning, no thinking required
- Focus on the absolute first physical movement"""


def get_initial_step_prompt(goal: str, energy_level: str = "medium") -> str:
    """Generate prompt for first micro-win based on energy level."""
    energy_context = {
        "low": "The user has LOW energy. Generate an ultra-simple, non-intimidating step (≤5s). Focus on the smallest possible movement.",
        "medium": "Standard energy level. Generate a concrete physical action (≤10s).",
        "high": "High energy level. Can handle a slightly broader physical action (≤15s)."
    }.get(energy_level, "Standard energy (≤10s).")

    return f"""TASK: {goal}
ENERGY LEVEL: {energy_level.upper()}
CONSTRAINT: {energy_context}

Generate the FIRST physically executable micro-step to start this task.

EXAMPLES:
- "Touch the handle of your laptop"
- "Pick up the nearest blue item"
- "Open the lid of your water bottle"

Return ONLY valid JSON: {{"step": "...", "estimated_seconds": ..., "is_complete": false}}"""


def get_next_step_prompt(goal: str, previous_step: str, energy_level: str = "medium") -> str:
    """Generate prompt for next micro-step based on energy level."""
    energy_context = {
        "low": "Keep steps ultra-tiny and non-intimidating (≤5s).",
        "medium": "Standard micro-win pace (≤10s).",
        "high": "Handle slightly larger physical actions (≤15s)."
    }.get(energy_level, "Standard micro-win pace (≤10s).")

    return f"""ORIGINAL TASK: {goal}
PREVIOUS STEP COMPLETED: {previous_step}
ENERGY LEVEL: {energy_level.upper()}
CONSTRAINT: {energy_context}

Generate the NEXT physically executable micro-step.

If the goal is finished, return is_complete: true.

Return ONLY valid JSON: {{"step": "...", "estimated_seconds": ..., "is_complete": boolean}}"""


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

Return ONLY valid JSON: {{"step": "...", "estimated_seconds": ..., "is_complete": false}}"""


def sanitize_goal_for_llm(goal: str) -> str:
    """
    Privacy filter: Remove potential PII from goal text.
    This is a simple pattern-based filter. In production, use more sophisticated NER.
    """
    # For hackathon MVP, we'll just pass through
    # In production, implement proper PII detection/removal
    return goal.strip()
