# database/dependencies.py
from database.manager import DBManager

def get_db():
    return DBManager()
