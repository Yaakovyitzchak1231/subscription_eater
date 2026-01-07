
import sqlite3
import os

def migrate():
    db_path = "subscription_eater.db"
    if not os.path.exists(db_path):
        print("Database not found, skipping migration (will be created by app).")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Check if category column exists
    cursor.execute("PRAGMA table_info(subscriptions)")
    columns = [info[1] for info in cursor.fetchall()]

    if "category" not in columns:
        print("Adding 'category' column to 'subscriptions' table...")
        try:
            cursor.execute("ALTER TABLE subscriptions ADD COLUMN category VARCHAR")
            conn.commit()
            print("Migration successful.")
        except Exception as e:
            print(f"Migration failed: {e}")
            conn.rollback()
    else:
        print("'category' column already exists.")

    conn.close()

if __name__ == "__main__":
    migrate()
