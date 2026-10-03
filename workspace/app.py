from database import connect_database


def start_app():
    db = connect_database()
    print("Application started")