import db.session as db

def get_connection():
    return db.get_connection()

