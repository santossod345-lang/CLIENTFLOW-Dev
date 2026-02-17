#!/usr/bin/env python3
"""
Railway startup script - Runs Alembic migrations before starting the server
"""
import os
import sys
import subprocess
import time

def wait_for_db(max_attempts=10, delay=2):
    """Wait for database to be ready"""
    print(f"🔍 Checking database connectivity...")
    for attempt in range(1, max_attempts + 1):
        try:
            from backend.database import engine
            from sqlalchemy import text
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            print("✅ Database is ready!")
            return True
        except Exception as e:
            if attempt < max_attempts:
                print(f"⏳ Database not ready (attempt {attempt}/{max_attempts}), waiting {delay}s...")
                time.sleep(delay)
            else:
                print(f"⚠️  Database still not ready after {max_attempts} attempts: {e}", file=sys.stderr)
                return False
    return False

def run_migrations():
    """Run Alembic migrations"""
    print("🔄 Running Alembic migrations...")
    try:
        result = subprocess.run(
            ["alembic", "upgrade", "head"],
            check=True,
            capture_output=True,
            text=True,
            timeout=60
        )
        print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
        print("✅ Migrations completed successfully!")
        return True
    except subprocess.TimeoutExpired:
        print("⚠️  Migration timeout - continuing anyway...", file=sys.stderr)
        return False
    except subprocess.CalledProcessError as e:
        print(f"⚠️  Migration error (exit code {e.returncode}):", file=sys.stderr)
        print(e.stdout)
        print(e.stderr, file=sys.stderr)
        print("⏭️  Continuing with server startup despite migration issues...")
        return False
    except FileNotFoundError:
        print("⚠️  Alembic not found, skipping migrations", file=sys.stderr)
        return False

def main():
    # Wait for database to be ready (Railway may start container before Postgres is ready)
    # Comment out wait_for_db() if it causes issues
    # wait_for_db()
    
    # Run migrations
    run_migrations()
    
    print("🚀 Starting Gunicorn server...")
    port = os.getenv("PORT", "8000")
    
    # Start Gunicorn with exec to replace the process
    os.execvp("gunicorn", [
        "gunicorn",
        "backend.main:app",
        "--bind", f"0.0.0.0:{port}",
        "--workers", "2",
        "--worker-class", "uvicorn.workers.UvicornWorker",
        "--timeout", "120",
        "--access-logfile", "-",
        "--error-logfile", "-",
        "--log-level", "info"
    ])

if __name__ == "__main__":
    main()
