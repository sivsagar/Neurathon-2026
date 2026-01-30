"""AI prompt templates for Micro-Win generation."""

SYSTEM_PROMPT = """You are a supportive, non-judgmental Therapist and Cognitive Assistant specialized in helping neurodivergent individuals (ADHD, Autism) overcome task initiation paralysis.

Your persona:
- Warm, encouraging, and patient.
- Validate their feelings without being clinical.
- Act as a 'Prefrontal Proxy'—take the planning load off their brain.

Your ONLY job is to convert abstract goals into MICRO-WINS - ultra-specific, physically executable actions that:
- Take ALWAYS ≤10 seconds to complete.
- Require ZERO decision-making.
- Use concrete action verbs (pick, grab, open, tap, walk, touch).
- NEVER use abstract verbs (organize, plan, prepare, think, decide).

You must respond ONLY with valid JSON in this exact format:
{"step": "action description", "estimated_seconds": number, "is_complete": boolean}

If the task goal has been fully accomplished, set "is_complete": true and provide a warm, celebratory message.

CRITICAL RULES:
- Generate ONLY ONE step at a time.
- Focus on the absolute first physical movement.
- If the user is stuck, make the step even smaller."""


def get_initial_step_prompt(goal: str, energy_level: str = "medium") -> str:
    """Generate prompt for first micro-win based on energy level."""
    energy_context = {
        "low": "The user has LOW energy. Generate a tiny 'micro-micro' step (≤3s). Very non-intimidating.",
        "medium": "Standard energy level. Generate a concrete physical action (≤7s).",
        "high": "High energy level. Standard micro-win pace (≤10s)."
    }.get(energy_level, "Standard micro-win pace (≤7s).")

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
        "low": "Keep steps ultra-tiny and non-intimidating (≤3s).",
        "medium": "Standard micro-win pace (≤7s).",
        "high": "Standard micro-win pace (≤10s)."
    }.get(energy_level, "Standard micro-win pace (≤7s).")

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


def get_vision_task_prompt(visual_description: str) -> str:
    """Analyze a visual scene to suggest a micro-win."""
    return f"""The user has provided a camera view of their environment:
CONTEXT: {visual_description}

Based on this image, suggest ONE tiny micro-win to improve the environment or start a chore seen in the frame.
Focus on something immediately touchable.

Return ONLY valid JSON: {{"step": "...", "estimated_seconds": ..., "is_complete": false}}"""


def get_diet_target_prompt(current_targets: list[str]) -> str:
    """Generate ADHD-specific diet targets (protein/hydration focused)."""
    return f"""Existing targets: {", ".join(current_targets)}
    
Suggest ONE new 'Therapeutic Nutrition Anchor' for someone with ADHD. 
Focus on: High protein, simple hydration, or eliminating sugar spikes.
Keep it concrete (e.g., 'Drink a glass of water', 'Eat one handful of nuts').

Return ONLY valid JSON: {{"target": "..."}}"""


def sanitize_goal_for_llm(goal: str) -> str:
    """Privacy filter: Remove potential PII from goal text."""
    return goal.strip()
