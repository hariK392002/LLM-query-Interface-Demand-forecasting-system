import sqlite3
from flask import g
from config import Config

def get_db_connection():
    '''
    Get database connection from Flask's g object or create new one
    '''
    if 'db' not in g:
        g.db = sqlite3.connect(Config.DATABASE_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db_connection(e=None):
    '''
    Close database connection
    '''
    db = g.pop('db', None)
    if db is not None:
        db.close()