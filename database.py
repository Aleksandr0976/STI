import sqlite3
from datetime import datetime

class Database:
    def __init__(self):
        self.conn = sqlite3.connect('avito_monitor.db')
        self.create_tables()
    
    def create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                created_at TIMESTAMP
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS listings (
                listing_id TEXT PRIMARY KEY,
                model TEXT,
                title TEXT,
                price INTEGER,
                mileage INTEGER,
                year INTEGER,
                city TEXT,
                url TEXT,
                found_at TIMESTAMP
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sent_listings (
                user_id INTEGER,
                listing_id TEXT,
                sent_at TIMESTAMP,
                PRIMARY KEY (user_id, listing_id)
            )
        ''')
        self.conn.commit()
    
    def add_user(self, user_id, username, first_name):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT OR IGNORE INTO users (user_id, username, first_name, created_at)
            VALUES (?, ?, ?, ?)
        ''', (user_id, username, first_name, datetime.now()))
        self.conn.commit()
    
    def get_all_users(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT user_id FROM users')
        return [row[0] for row in cursor.fetchall()]
    
    def add_listing(self, listing_data):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT OR IGNORE INTO listings 
            (listing_id, model, title, price, mileage, year, city, url, found_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            listing_data['id'],
            listing_data['model'],
            listing_data['title'],
            listing_data['price'],
            listing_data['mileage'],
            listing_data['year'],
            listing_data['city'],
            listing_data['url'],
            datetime.now()
        ))
        self.conn.commit()
    
    def was_sent_to_user(self, user_id, listing_id):
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT 1 FROM sent_listings 
            WHERE user_id = ? AND listing_id = ?
        ''', (user_id, listing_id))
        return cursor.fetchone() is not None
    
    def mark_as_sent(self, user_id, listing_id):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT OR IGNORE INTO sent_listings (user_id, listing_id, sent_at)
            VALUES (?, ?, ?)
        ''', (user_id, listing_id, datetime.now()))
        self.conn.commit()