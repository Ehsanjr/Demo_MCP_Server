import sqlite3

DATABASE_NAME = "app.db"


def connect_database():
    return sqlite3.connect(DATABASE_NAME)