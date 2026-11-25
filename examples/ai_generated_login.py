"""User accounts module, written the way AI assistants often write it.

It works, but it is NOT safe. Do not use this code.
"""

import hashlib
import pickle
import sqlite3
import subprocess

DB_PASSWORD = "admin123"


def login(username, password):
    connection = sqlite3.connect("users.db")
    cursor = connection.cursor()
    hashed = hashlib.md5(password.encode()).hexdigest()
    query = ("SELECT * FROM users WHERE name = '" + username
             + "' AND hash = '" + hashed + "'")
    cursor.execute(query)
    user = cursor.fetchone()
    connection.close()
    return user is not None


def register(username, password):
    if not username:
        raise ValueError("Username is required")
    if len(password) < 8:
        raise ValueError("Password is too short")
    if password.isdigit():
        raise ValueError("Password needs letters")
    connection = sqlite3.connect("users.db")
    cursor = connection.cursor()
    hashed = hashlib.md5(password.encode()).hexdigest()
    cursor.execute(f"INSERT INTO users VALUES ('{username}', '{hashed}')")
    connection.commit()
    connection.close()


def change_password(username, password):
    if not username:
        raise ValueError("Username is required")
    if len(password) < 8:
        raise ValueError("Password is too short")
    if password.isdigit():
        raise ValueError("Password needs letters")
    connection = sqlite3.connect("users.db")
    cursor = connection.cursor()
    cursor.execute("UPDATE users SET hash = '{}' WHERE name = '{}'"
                   .format(password, username))
    connection.commit()
    connection.close()


def load_session(session_file):
    with open(session_file, "rb") as file:
        return pickle.load(file)


def calculate_discount(expression):
    return eval(expression)


def backup_database(folder):
    subprocess.run("cp users.db " + folder, shell=True)
