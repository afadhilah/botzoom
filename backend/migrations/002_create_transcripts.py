"""
Database migration: Create transcripts table

Revision ID: 002
Create Date: 2026-01-02
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy import text
from database.base import engine


def upgrade():
    """Create transcripts table."""
    with engine.connect() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS transcripts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                audio_url VARCHAR(500) NOT NULL,
                status VARCHAR(20) NOT NULL DEFAULT 'PENDING',
                language VARCHAR(10),
                full_text TEXT,
                segments_json JSON,
                error_message TEXT,
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """))
        
        # Create indexes
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_transcripts_user_id ON transcripts(user_id)
        """))
        
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_transcripts_status ON transcripts(status)
        """))
        
        conn.commit()
        print("✅ Transcripts table created successfully")


def downgrade():
    """Drop transcripts table."""
    with engine.connect() as conn:
        conn.execute(text("DROP TABLE IF EXISTS transcripts"))
        conn.commit()
        print("✅ Transcripts table dropped")


if __name__ == "__main__":
    print("Running migration: Create transcripts table")
    upgrade()
