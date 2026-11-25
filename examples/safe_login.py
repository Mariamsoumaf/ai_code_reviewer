"""User accounts module after fixing every problem the reviewer found."""

import hashlib
import json
import os
import shutil
import sqlite3

DATABASE_FILE = "users.db"
MIN_PASSWORD_LENGTH = 8
HASH_ITERATIONS = 200_000
SALT_SIZE = 16


def login(username, password):
    with sqlite3.connect(DATABASE_FILE) as connection:
        row = connection.execute(
            "SELECT salt, hash FROM users WHERE name = ?",
            (username,)).fetchone()
    if row is None:
        return False
    salt, stored_hash = row
    return hash_password(password, salt) == stored_hash


def register(username, password):
    validate_credentials(username, password)
    salt = os.urandom(SALT_SIZE)
    with sqlite3.connect(DATABASE_FILE) as connection:
        connection.execute(
            "INSERT INTO users (name, salt, hash) VALUES (?, ?, ?)",
            (username, salt, hash_password(password, salt)))


def change_password(username, password):
    validate_credentials(username, password)
    salt = os.urandom(SALT_SIZE)
    with sqlite3.connect(DATABASE_FILE) as connection:
        connection.execute(
            "UPDATE users SET salt = ?, hash = ? WHERE name = ?",
            (salt, hash_password(password, salt), username))


def validate_credentials(username, password):
    if not username:
        raise ValueError("Username is required")
    if len(password) < MIN_PASSWORD_LENGTH:
        raise ValueError("Password is too short")
    if password.isdigit():
        raise ValueError("Password needs letters")


def hash_password(password, salt):
    return hashlib.pbkdf2_hmac(
        "sha256", password.encode(), salt, HASH_ITERATIONS)


def load_session(session_file):
    with open(session_file, encoding="utf-8") as file:
        return json.load(file)


def calculate_discount(percentage_text):
    return float(percentage_text)


def backup_database(folder):
    shutil.copy(DATABASE_FILE, folder)


def database_password():
    return os.environ["DB_PASSWORD"]
