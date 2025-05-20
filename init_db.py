# file: init_db.py
from app.database.db import init_db

if __name__ == "__main__":
    init_db()
    print("✅ Database tables created.")