#!/usr/bin/env python3

from app.core.database import get_db
from sqlalchemy import text

# Get database session
db_session = next(get_db())

try:
    # Try direct SQL query to list tables
    result = db_session.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
    tables = [row[0] for row in result.fetchall()]

    print("=== ALL TABLES IN DATABASE ===")
    if tables:
        for table in sorted(tables):
            print(f"- {table}")
        
        # Check for task-related tables specifically
        task_tables = [t for t in tables if 'task' in t.lower() or 'ai_' in t.lower() or 'intelligence' in t.lower()]
        print(f"\n=== TASK-RELATED TABLES ===")
        for table in task_tables:
            print(f"- {table}")
            
            # Show table structure
            result = db_session.execute(text(f"PRAGMA table_info({table})"))
            columns = result.fetchall()
            for col in columns:
                print(f"  - {col[1]}: {col[2]}")
            print()
            
    else:
        print("No tables found in database!")
        
    # Check if we can access the ai_tasks table specifically
    print("\n=== TESTING ai_tasks TABLE ACCESS ===")
    try:
        result = db_session.execute(text("SELECT COUNT(*) FROM ai_tasks"))
        count = result.fetchone()[0]
        print(f"ai_tasks table exists with {count} records")
    except Exception as e:
        print(f"ai_tasks table does not exist: {e}")
        
    # Check if we can access the intelligence_content table
    print("\n=== TESTING intelligence_content TABLE ACCESS ===")
    try:
        result = db_session.execute(text("SELECT COUNT(*) FROM intelligence_content"))
        count = result.fetchone()[0]
        print(f"intelligence_content table exists with {count} records")
    except Exception as e:
        print(f"intelligence_content table does not exist: {e}")
        
except Exception as e:
    print(f"Database error: {e}")
    
finally:
    db_session.close()