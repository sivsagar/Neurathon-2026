"""Service for analyzing historical task performance and predicting energy peaks."""
from typing import List, Dict, Any
import aiosqlite
from datetime import datetime
from database import db

class SchedulerService:
    """Service to analyze energy behavior and suggest best times."""
    
    async def get_energy_insights(self) -> Dict[str, Any]:
        """
        Analyze historical steps to find patterns in efficiency.
        Returns average duration per energy level.
        """
        async with aiosqlite.connect(db.db_path) as conn:
            conn.row_factory = aiosqlite.Row
            
            # 1. Efficiency per Energy Level
            query = """
                SELECT 
                    t.energy_level,
                    AVG(s.actual_duration_seconds) as avg_duration,
                    AVG(s.estimated_seconds) as avg_est,
                    COUNT(s.id) as step_count
                FROM tasks t
                JOIN steps s ON t.id = s.task_id
                WHERE s.completed = TRUE AND s.actual_duration_seconds IS NOT NULL
                GROUP BY t.energy_level
            """
            
            insights = []
            async with conn.execute(query) as cursor:
                rows = await cursor.fetchall()
                for row in rows:
                    efficiency = (row["avg_est"] / row["avg_duration"]) * 100 if row["avg_duration"] > 0 else 0
                    insights.append({
                        "level": row["energy_level"],
                        "efficiency": round(efficiency, 1),
                        "count": row["step_count"]
                    })
            
            # 2. Peak Hours Analysis
            peak_query = """
                SELECT 
                    strftime('%H', s.completed_at) as hour,
                    COUNT(s.id) as count
                FROM steps s
                WHERE s.completed = TRUE
                GROUP BY hour
                ORDER BY count DESC
                LIMIT 3
            """
            
            peak_hours = []
            async with conn.execute(peak_query) as cursor:
                rows = await cursor.fetchall()
                peak_hours = [row["hour"] for row in rows]
                
            return {
                "efficiency_log": insights,
                "peak_hours": peak_hours,
                "best_time_to_start": peak_hours[0] if peak_hours else "No data"
            }

scheduler_service = SchedulerService()
