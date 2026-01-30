"""SQLite database setup and operations."""
import aiosqlite
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
from config import settings


class Database:
    """Async SQLite database manager."""
    
    def __init__(self):
        self.db_path = settings.database_path
        # Ensure data directory exists
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
    
    async def init_db(self):
        """Initialize database schema."""
        async with aiosqlite.connect(self.db_path) as db:
            # Users Table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    avatar_url TEXT,
                    role TEXT DEFAULT 'patient', -- patient, therapist
                    xp INTEGER DEFAULT 0,
                    level INTEGER DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Tasks Table (with user_id)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id TEXT PRIMARY KEY,
                    user_id TEXT,
                    original_goal TEXT NOT NULL,
                    current_step_index INTEGER DEFAULT 0,
                    status TEXT DEFAULT 'active',
                    energy_level TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)
            
            # Check if user_id column exists (migration)
            try:
                await db.execute("ALTER TABLE tasks ADD COLUMN user_id TEXT REFERENCES users(id)")
            except:
                pass # Already exists

            await db.execute("""
                CREATE TABLE IF NOT EXISTS steps (
                    id TEXT PRIMARY KEY,
                    task_id TEXT NOT NULL,
                    step_text TEXT NOT NULL,
                    estimated_seconds INTEGER,
                    actual_duration_seconds INTEGER,
                    step_order INTEGER,
                    simplification_level INTEGER DEFAULT 0,
                    completed BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    completed_at TIMESTAMP,
                    FOREIGN KEY (task_id) REFERENCES tasks(id)
                )
            """)

            # Diet Targets Table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS diet_targets (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    target_text TEXT NOT NULL,
                    completed BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)

            # Rewards Table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS rewards (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    xp_cost INTEGER NOT NULL,
                    type TEXT -- theme, badge, etc
                )
            """)
            
            await db.commit()
    
    async def create_user(self, name: str, avatar_url: Optional[str] = None, role: str = "patient") -> str:
        """Create a new user profile."""
        user_id = str(uuid.uuid4())
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT INTO users (id, name, avatar_url, role) VALUES (?, ?, ?, ?)",
                (user_id, name, avatar_url, role)
            )
            await db.commit()
        return user_id

    async def get_users(self) -> list[Dict[str, Any]]:
        """List all users."""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("SELECT * FROM users") as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]

    async def add_xp(self, user_id: str, xp_to_add: int):
        """Award XP to user and handle leveling."""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "UPDATE users SET xp = xp + ? WHERE id = ?",
                (xp_to_add, user_id)
            )
            # Simple level calc: floor(sqrt(xp/100)) + 1
            await db.execute(
                "UPDATE users SET level = (CAST(SQRT(xp/100.0) AS INTEGER) + 1) WHERE id = ?",
                (user_id,)
            )
            await db.commit()

    async def create_task(self, goal: str, user_id: Optional[str] = None, energy_level: Optional[str] = None) -> str:
        """Create new task and return task_id."""
        task_id = str(uuid.uuid4())
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT INTO tasks (id, user_id, original_goal, status, energy_level) VALUES (?, ?, ?, ?, ?)",
                (task_id, user_id, goal, "active", energy_level)
            )
            await db.commit()
        return task_id
    
    async def create_step(
        self, 
        task_id: str, 
        step_text: str, 
        estimated_seconds: int,
        step_order: int,
        simplification_level: int = 0
    ) -> str:
        """Create new step and return step_id."""
        step_id = str(uuid.uuid4())
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """INSERT INTO steps 
                   (id, task_id, step_text, estimated_seconds, step_order, simplification_level)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (step_id, task_id, step_text, estimated_seconds, step_order, simplification_level)
            )
            await db.commit()
        return step_id
    
    async def mark_step_completed(self, step_id: str, duration: Optional[int] = None):
        """Mark step as completed with optional duration."""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """UPDATE steps 
                   SET completed = TRUE, 
                       completed_at = CURRENT_TIMESTAMP,
                       actual_duration_seconds = ? 
                   WHERE id = ?""",
                (duration, step_id)
            )
            await db.commit()
    
    async def update_task_status(self, task_id: str, status: str):
        """Update task status (active, paused, completed)."""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "UPDATE tasks SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (status, task_id)
            )
            await db.commit()
    
    async def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get task by ID."""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT * FROM tasks WHERE id = ?", (task_id,)
            ) as cursor:
                row = await cursor.fetchone()
                return dict(row) if row else None
    
    async def get_current_step(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get current uncompleted step for task."""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                """SELECT * FROM steps 
                   WHERE task_id = ? AND completed = FALSE 
                   ORDER BY step_order DESC LIMIT 1""",
                (task_id,)
            ) as cursor:
                row = await cursor.fetchone()
                return dict(row) if row else None
    
    async def get_step(self, step_id: str) -> Optional[Dict[str, Any]]:
        """Get step by ID."""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT * FROM steps WHERE id = ?", (step_id,)
            ) as cursor:
                row = await cursor.fetchone()
                return dict(row) if row else None
    
    async def get_next_step_order(self, task_id: str) -> int:
        """Get next step order number."""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                "SELECT MAX(step_order) FROM steps WHERE task_id = ?",
                (task_id,)
            ) as cursor:
                result = await cursor.fetchone()
                return (result[0] or -1) + 1

    async def create_diet_target(self, user_id: str, target_text: str) -> str:
        """Create a new diet target."""
        target_id = str(uuid.uuid4())
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT INTO diet_targets (id, user_id, target_text) VALUES (?, ?, ?)",
                (target_id, user_id, target_text)
            )
            await db.commit()
        return target_id

    async def get_diet_targets(self, user_id: str) -> list[Dict[str, Any]]:
        """Get diet targets for a user."""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT * FROM diet_targets WHERE user_id = ? ORDER BY created_at DESC",
                (user_id,)
            ) as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]


# Global database instance
db = Database()
