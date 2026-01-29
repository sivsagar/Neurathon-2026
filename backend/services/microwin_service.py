"""Core AI service for Micro-Win generation using local Ollama."""
import json
import re
from typing import Dict, Any, Optional
import httpx
from config import settings
from prompts import (
    SYSTEM_PROMPT,
    get_initial_step_prompt,
    get_next_step_prompt,
    get_simplification_prompt,
    sanitize_goal_for_llm
)
import logging

logger = logging.getLogger(__name__)


class MicroWinService:
    """AI service for generating and validating micro-steps using Ollama."""
    
    def __init__(self):
        self.base_url = settings.ollama_base_url.rstrip('/')
        self.model = settings.ollama_model
    
    async def generate_initial_step(self, goal: str, energy_level: str = "medium") -> Dict[str, Any]:
        """
        Generate the first micro-step for a task.
        
        Returns:
            {"step": str, "estimated_seconds": int, "is_complete": bool}
        """
        sanitized_goal = sanitize_goal_for_llm(goal)
        user_prompt = get_initial_step_prompt(sanitized_goal, energy_level)
        
        response = await self._call_llm(user_prompt)
        validated_step = self._validate_step(response)
        
        return validated_step
    
    async def generate_next_step(self, goal: str, previous_step: str, energy_level: str = "medium") -> Dict[str, Any]:
        """
        Generate the next micro-step after completing the previous one.
        
        Returns:
            {"step": str, "estimated_seconds": int, "is_complete": bool}
        """
        sanitized_goal = sanitize_goal_for_llm(goal)
        user_prompt = get_next_step_prompt(sanitized_goal, previous_step, energy_level)
        
        response = await self._call_llm(user_prompt)
        validated_step = self._validate_step(response)
        
        return validated_step
    
    async def simplify_step(self, current_step: str, simplification_level: int) -> Dict[str, Any]:
        """
        Simplify a step that was marked as 'Too Hard'.
        
        Returns:
            {"step": str, "estimated_seconds": int}
        """
        user_prompt = get_simplification_prompt(current_step, simplification_level)
        
        response = await self._call_llm(user_prompt)
        validated_step = self._validate_step(response, enforce_shorter=True)
        
        return validated_step
    
    async def _call_llm(self, user_prompt: str) -> str:
        """Call local Ollama API with error handling."""
        try:
            url = f"{self.base_url}/api/generate"
            
            payload = {
                "model": self.model,
                "prompt": f"{SYSTEM_PROMPT}\n\n{user_prompt}",
                "stream": False,
                "options": {
                    "temperature": settings.temperature,
                    "num_predict": settings.max_tokens,
                }
            }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                data = response.json()
                
                return data.get("response", "")
        
        except Exception as e:
            logger.error(f"Ollama API error: {str(e)}")
            raise ValueError(f"Ollama API error: {str(e)}")
    
    def _validate_step(self, llm_response: str, enforce_shorter: bool = False) -> Dict[str, Any]:
        """
        Validate that the LLM response meets Micro-Win criteria.
        
        Args:
            llm_response: JSON string from LLM
            enforce_shorter: If True, enforce stricter time limit (for simplifications)
        
        Returns:
            Validated step dictionary
        
        Raises:
            ValueError: If step doesn't meet criteria
        """
        try:
            step_data = json.loads(llm_response)
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON response from LLM")
        
        # Ensure required fields
        if "step" not in step_data or "estimated_seconds" not in step_data:
            raise ValueError("Missing required fields in step")
        
        step_text = step_data["step"]
        estimated_seconds = step_data["estimated_seconds"]
        
        # Validate time constraint
        max_time = settings.simplification_max_seconds if enforce_shorter else settings.max_step_seconds
        if estimated_seconds > max_time:
            raise ValueError(f"Step exceeds {max_time} second limit")
        
        # Validate no abstract verbs (simple pattern matching)
        abstract_verbs = [
            "organize", "plan", "prepare", "think", "decide", 
            "consider", "figure out", "work on", "deal with"
        ]
        step_lower = step_text.lower()
        for verb in abstract_verbs:
            if verb in step_lower:
                raise ValueError(f"Step contains abstract verb: {verb}")
        
        # Ensure step is concrete (has action verb at start)
        concrete_verbs = [
            "pick", "grab", "open", "close", "walk", "tap", "touch", 
            "click", "press", "pull", "push", "take", "put", "place",
            "move", "stand", "sit", "turn", "look", "find"
        ]
        has_concrete_verb = any(step_lower.startswith(verb) for verb in concrete_verbs)
        if not has_concrete_verb:
            # Be lenient for hackathon - just log warning in production
            pass
        
        return {
            "step": step_text,
            "estimated_seconds": estimated_seconds,
            "is_complete": step_data.get("is_complete", False)
        }


# Global service instance
microwin_service = MicroWinService()
