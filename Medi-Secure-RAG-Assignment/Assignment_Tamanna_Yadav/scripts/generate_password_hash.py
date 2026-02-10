#!/usr/bin/env python3
"""Utility script to generate bcrypt password hashes for new users."""
import bcrypt
import sys


def generate_hash(password: str) -> str:
    """Generate a bcrypt hash for a password."""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def main():
    if len(sys.argv) > 1:
        password = sys.argv[1]
    else:
        password = input("Enter password to hash: ")
    
    hash_value = generate_hash(password)
    print(f"\nPassword hash:\n{hash_value}")
    print("\nAdd this to config/settings.py in DEMO_USERS dictionary.")


if __name__ == "__main__":
    main()
