import sqlite3

db = sqlite3.connect('college.db')
db.row_factory = sqlite3.Row
users = db.execute('SELECT * FROM users').fetchall()
print('Users in database:')
for u in users:
    print(f'  {u["username"]}: role={u["role"]}')
db.close()
