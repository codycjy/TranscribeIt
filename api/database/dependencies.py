# database/dependencies.py
from fastapi import Depends
from .manager import DBManager

def get_db():
    return DBManager()
