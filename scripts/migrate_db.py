
import sqlite3
import os

def migrate():
    db_path = os.environ.get("SUBSCRIPTION_EATER_DB_PATH", "subscription_eater.db")
    if not os.path.exists(db_path):
        print("Database not found, skipping migration (will be created by app).")
        return

    conn = sqlite3.connect(db_path)
    try:
        cursor = conn.cursor()

        # Check if category column exists
        cursor.execute("PRAGMA table_info(subscriptions)")
        columns = [info[1] for info in cursor.fetchall()]

        if "category" not in columns:
            print("Adding 'category' column to 'subscriptions' table...")
            # SQLite DDL is transactional in recent versions, but explicit safety is good
            cursor.execute("ALTER TABLE subscriptions ADD COLUMN category VARCHAR")
            conn.commit()
            print("Migration successful.")
        else:
            print("'category' column already exists.")

    except Exception as e:
        print(f"Migration failed: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
