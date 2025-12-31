import sqlite3
import datetime
import os
from contextlib import contextmanager

class DBManager:
    def __init__(self, db_filename: str = "password_keeper.db"):
        # Determine user data directory
        home = os.path.expanduser("~")
        app_data_dir = os.path.join(home, "Library", "Application Support", "PwKeeper")
        
        # Create directory if it doesn't exist
        os.makedirs(app_data_dir, exist_ok=True)
        
        self.db_path = os.path.join(app_data_dir, db_filename)
        self._init_db()

    def _init_db(self):
        """Initializes the database tables."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            # Table for Credentials
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS credentials (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category TEXT,
                    site_name TEXT,
                    username TEXT,
                    encrypted_password TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            # Table for App Settings (e.g., Master Salt, Verification Hash)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT
                )
            """)
            conn.commit()

            # Run migration to add new columns if needed
            self._migrate_database()

    @contextmanager
    def get_connection(self):
        """Context manager for SQLite connection."""
        conn = sqlite3.connect(self.db_path)
        try:
            yield conn
        finally:
            conn.close()

    def add_credential(self, category: str, site_name: str, username: str, encrypted_password: str):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO credentials (category, site_name, username, encrypted_password, created_at)
                VALUES (?, ?, ?, ?, ?)
            """, (category, site_name, username, encrypted_password, datetime.datetime.now()))
            conn.commit()
            return cursor.lastrowid

    def get_all_credentials(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, category, site_name, username, encrypted_password FROM credentials")
            return cursor.fetchall()
            
    def get_credential_by_id(self, cred_id: int):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, category, site_name, username, encrypted_password FROM credentials WHERE id = ?", (cred_id,))
            return cursor.fetchone()

    def delete_credential(self, cred_id: int):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM credentials WHERE id = ?", (cred_id,))
            conn.commit()

    def update_credential(self, cred_id: int, category: str, site_name: str, username: str, encrypted_password: str):
         with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE credentials 
                SET category = ?, site_name = ?, username = ?, encrypted_password = ?
                WHERE id = ?
            """, (category, site_name, username, encrypted_password, cred_id))
            conn.commit()

    # Settings Helpers
    def get_setting(self, key: str):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
            row = cursor.fetchone()
            return row[0] if row else None

    def set_setting(self, key: str, value: str):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, value))
            conn.commit()

    # Preferences (alias for settings with default support)
    def get_preference(self, key: str, default=None):
        """Get a user preference with optional default value"""
        value = self.get_setting(key)
        return value if value is not None else default

    def set_preference(self, key: str, value: str):
        """Set a user preference"""
        self.set_setting(key, value)

    # Migration
    def _migrate_database(self):
        """Migrate database schema to add new columns if they don't exist"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Get existing columns
            cursor.execute("PRAGMA table_info(credentials)")
            existing_columns = {row[1] for row in cursor.fetchall()}

            # Add missing columns
            migrations = [
                ("is_favorite", "INTEGER DEFAULT 0"),
                ("url", "TEXT DEFAULT ''"),
                ("notes", "TEXT DEFAULT ''"),
                ("updated_at", "TIMESTAMP"),  # Can't use CURRENT_TIMESTAMP in ALTER TABLE
            ]

            for column_name, column_def in migrations:
                if column_name not in existing_columns:
                    try:
                        cursor.execute(f"ALTER TABLE credentials ADD COLUMN {column_name} {column_def}")
                        conn.commit()

                        # For updated_at, set current timestamp for existing rows
                        if column_name == "updated_at":
                            cursor.execute("UPDATE credentials SET updated_at = CURRENT_TIMESTAMP WHERE updated_at IS NULL")
                            conn.commit()
                    except sqlite3.Error as e:
                        # Column might already exist or other error
                        print(f"Migration warning for {column_name}: {e}")

    # Favorites
    def toggle_favorite(self, cred_id: int):
        """Toggle favorite status of a credential"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            # Get current status
            cursor.execute("SELECT is_favorite FROM credentials WHERE id = ?", (cred_id,))
            row = cursor.fetchone()
            if row is None:
                return False

            current_status = row[0] if row[0] is not None else 0
            new_status = 1 if current_status == 0 else 0

            # Update
            cursor.execute("UPDATE credentials SET is_favorite = ? WHERE id = ?", (new_status, cred_id))
            conn.commit()
            return new_status == 1

    def get_favorites(self):
        """Get all favorited credentials"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, category, site_name, username, encrypted_password, is_favorite, url, notes
                FROM credentials
                WHERE is_favorite = 1
                ORDER BY site_name
            """)
            return cursor.fetchall()

    # Enhanced credential methods
    def add_credential_extended(self, category: str, site_name: str, username: str,
                                encrypted_password: str, url: str = '', notes: str = '',
                                is_favorite: int = 0):
        """Add credential with extended fields"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            now = datetime.datetime.now()
            cursor.execute("""
                INSERT INTO credentials
                (category, site_name, username, encrypted_password, url, notes, is_favorite, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (category, site_name, username, encrypted_password, url, notes, is_favorite, now, now))
            conn.commit()
            return cursor.lastrowid

    def update_credential_extended(self, cred_id: int, category: str, site_name: str,
                                   username: str, encrypted_password: str, url: str = '',
                                   notes: str = ''):
        """Update credential with extended fields"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE credentials
                SET category = ?, site_name = ?, username = ?, encrypted_password = ?,
                    url = ?, notes = ?, updated_at = ?
                WHERE id = ?
            """, (category, site_name, username, encrypted_password, url, notes,
                  datetime.datetime.now(), cred_id))
            conn.commit()

    def get_all_credentials_extended(self):
        """Get all credentials with extended fields"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, category, site_name, username, encrypted_password, is_favorite, url, notes
                FROM credentials
                ORDER BY site_name
            """)
            return cursor.fetchall()

    def get_credential_by_id_extended(self, cred_id: int):
        """Get a single credential with extended fields"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, category, site_name, username, encrypted_password, is_favorite, url, notes
                FROM credentials
                WHERE id = ?
            """, (cred_id,))
            return cursor.fetchone()
