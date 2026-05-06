import sqlite3
import os
from app.settings import DB_PATH

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS editions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            edition_date TEXT,
            edition_number TEXT,
            pdf_url TEXT,
            pdf_path TEXT,
            pdf_hash TEXT UNIQUE,
            downloaded_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            edition_id INTEGER,
            page_number INTEGER,
            text TEXT,
            FOREIGN KEY (edition_id) REFERENCES editions (id)
        )
    ''')
    
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_editions_date ON editions(edition_date)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_pages_edition_id ON pages(edition_id)')
    
    conn.commit()
    conn.close()

# Initialize DB on module load
init_db()
