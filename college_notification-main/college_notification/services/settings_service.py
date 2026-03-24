from flask import session
from .app import get_db

def get_user_settings(user_id):
    db = get_db()
    row = db.execute('SELECT email_notifications_enabled, dark_mode_enabled, language_pref FROM users WHERE id = ?', (user_id,)).fetchone()
    if not row:
        return {'email_notifications': False, 'dark_mode': False, 'language': 'en'}
    return {
        'email_notifications': bool(row['email_notifications_enabled']),
        'dark_mode': bool(row['dark_mode_enabled']),
        'language': row['language_pref'] or 'en'
    }

def set_user_settings(user_id, data):
    db = get_db()
    if 'email_notifications' in data:
        db.execute('UPDATE users SET email_notifications_enabled = ? WHERE id = ?', (1 if data['email_notifications'] else 0, user_id))
    if 'dark_mode' in data:
        db.execute('UPDATE users SET dark_mode_enabled = ? WHERE id = ?', (1 if data['dark_mode'] else 0, user_id))
    if 'language' in data:
        db.execute('UPDATE users SET language_pref = ? WHERE id = ?', (data['language'], user_id))
    db.commit()
