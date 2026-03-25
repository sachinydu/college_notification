import sqlite3
from flask import current_app

def migrate_add_user_settings_columns():
    db = current_app.extensions['sqlite_db']() if hasattr(current_app, 'extensions') and 'sqlite_db' in current_app.extensions else None
    if db is None:
        from ..app import get_db
        db = get_db()
    # Email notifications
    try:
        db.execute('SELECT email_notifications_enabled FROM users LIMIT 1')
    except sqlite3.OperationalError:
        db.execute('ALTER TABLE users ADD COLUMN email_notifications_enabled INTEGER DEFAULT 0')
        db.commit()
    # Dark mode
    try:
        db.execute('SELECT dark_mode_enabled FROM users LIMIT 1')
    except sqlite3.OperationalError:
        db.execute('ALTER TABLE users ADD COLUMN dark_mode_enabled INTEGER DEFAULT 0')
        db.commit()
    # Language
    try:
        db.execute('SELECT language_pref FROM users LIMIT 1')
    except sqlite3.OperationalError:
        db.execute('ALTER TABLE users ADD COLUMN language_pref TEXT DEFAULT "en"')
        db.commit()
