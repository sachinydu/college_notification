import os
from app import init_db, app, DB

# Remove the existing database file to ensure a clean start
if os.path.exists(DB):
    print(f"[*] Removing old database: {DB}")
    os.remove(DB)

with app.app_context():
    init_db()
    print("[OK] Database initialized with all tables.")
