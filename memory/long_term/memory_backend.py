"""
Memory system for Teddy AI
Handles both short-term (conversation) and long-term (persistent) memory.
"""

import sqlite3
import json
import datetime
from pathlib import Path
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict


@dataclass
class Memory:
    """A single memory entry."""
    id: str
    category: str  # favorite_animals, interests, recurring_characters, etc.
    content: str
    created_at: str
    updated_at: str
    relevance_score: float = 1.0
    metadata: Optional[Dict[str, Any]] = None


class MemoryBackend(ABC):
    """Abstract base class for memory storage."""
    
    @abstractmethod
    def store(self, category: str, content: str, metadata: Optional[Dict] = None) -> str:
        """Store a memory and return its ID."""
        pass
    
    @abstractmethod
    def retrieve(self, category: Optional[str] = None, limit: int = 10) -> List[Memory]:
        """Retrieve memories, optionally filtered by category."""
        pass
    
    @abstractmethod
    def retrieve_by_id(self, memory_id: str) -> Optional[Memory]:
        """Retrieve a specific memory by ID."""
        pass
    
    @abstractmethod
    def update(self, memory_id: str, content: str, metadata: Optional[Dict] = None) -> bool:
        """Update an existing memory."""
        pass
    
    @abstractmethod
    def delete(self, memory_id: str) -> bool:
        """Delete a memory."""
        pass
    
    @abstractmethod
    def get_categories(self) -> List[str]:
        """Get all memory categories."""
        pass


class SQLiteMemoryBackend(MemoryBackend):
    """SQLite-based memory storage."""
    
    def __init__(self, db_path: str = "./data/teddy.db"):
        """Initialize SQLite memory backend."""
        self.db_path = db_path
        db_dir = Path(self.db_path).parent
        if db_dir != Path(""):
            db_dir.mkdir(parents=True, exist_ok=True)
        self._initialize_db()
    
    def _initialize_db(self):
        """Create database schema if it doesn't exist."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS memories (
                    id TEXT PRIMARY KEY,
                    category TEXT NOT NULL,
                    content TEXT NOT NULL,
                    relevance_score REAL DEFAULT 1.0,
                    metadata TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_category ON memories(category)
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_relevance ON memories(relevance_score DESC)
            """)
            
            conn.commit()
    
    def store(self, category: str, content: str, metadata: Optional[Dict] = None) -> str:
        """Store a memory."""
        import uuid
        memory_id = str(uuid.uuid4())
        now = datetime.datetime.utcnow().isoformat()
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO memories (id, category, content, created_at, updated_at, metadata)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                memory_id,
                category,
                content,
                now,
                now,
                json.dumps(metadata) if metadata else None,
            ))
            conn.commit()
        
        return memory_id
    
    def retrieve(self, category: Optional[str] = None, limit: int = 10) -> List[Memory]:
        """Retrieve memories."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            if category:
                cursor = conn.execute("""
                    SELECT * FROM memories
                    WHERE category = ?
                    ORDER BY relevance_score DESC, updated_at DESC
                    LIMIT ?
                """, (category, limit))
            else:
                cursor = conn.execute("""
                    SELECT * FROM memories
                    ORDER BY relevance_score DESC, updated_at DESC
                    LIMIT ?
                """, (limit,))
            
            memories = []
            for row in cursor:
                memories.append(Memory(
                    id=row['id'],
                    category=row['category'],
                    content=row['content'],
                    created_at=row['created_at'],
                    updated_at=row['updated_at'],
                    relevance_score=row['relevance_score'],
                    metadata=json.loads(row['metadata']) if row['metadata'] else None,
                ))
            
            return memories
    
    def retrieve_by_id(self, memory_id: str) -> Optional[Memory]:
        """Retrieve a specific memory."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT * FROM memories WHERE id = ?",
                (memory_id,)
            )
            row = cursor.fetchone()
            
            if row:
                return Memory(
                    id=row['id'],
                    category=row['category'],
                    content=row['content'],
                    created_at=row['created_at'],
                    updated_at=row['updated_at'],
                    relevance_score=row['relevance_score'],
                    metadata=json.loads(row['metadata']) if row['metadata'] else None,
                )
            return None
    
    def update(self, memory_id: str, content: str, metadata: Optional[Dict] = None) -> bool:
        """Update a memory."""
        now = datetime.datetime.utcnow().isoformat()
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT id FROM memories WHERE id = ?",
                (memory_id,)
            )
            if not cursor.fetchone():
                return False
            
            conn.execute("""
                UPDATE memories
                SET content = ?, metadata = ?, updated_at = ?
                WHERE id = ?
            """, (
                content,
                json.dumps(metadata) if metadata else None,
                now,
                memory_id,
            ))
            conn.commit()
            return True
    
    def delete(self, memory_id: str) -> bool:
        """Delete a memory."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "DELETE FROM memories WHERE id = ?",
                (memory_id,)
            )
            conn.commit()
            return cursor.rowcount > 0
    
    def get_categories(self) -> List[str]:
        """Get all memory categories."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT DISTINCT category FROM memories ORDER BY category"
            )
            return [row[0] for row in cursor]


class ShortTermMemory:
    """Short-term memory for current conversation context."""
    
    def __init__(self, max_turns: int = 10):
        """Initialize short-term memory."""
        self.max_turns = max_turns
        self.context: List[Dict[str, str]] = []
    
    def add(self, role: str, message: str):
        """Add a turn to conversation history."""
        self.context.append({"role": role, "message": message})
        # Keep only recent turns
        if len(self.context) > self.max_turns * 2:
            self.context = self.context[-self.max_turns * 2:]
    
    def get_context(self) -> str:
        """Get formatted context for LLM."""
        lines = []
        for turn in self.context:
            lines.append(f"{turn['role']}: {turn['message']}")
        return "\n".join(lines)
    
    def clear(self):
        """Clear short-term memory."""
        self.context = []
