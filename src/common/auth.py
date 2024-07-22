# src/common/auth.py
import bcrypt

def verify_password(stored_password_hash, provided_password):
    return bcrypt.checkpw(provided_password.encode(), stored_password_hash.encode())
