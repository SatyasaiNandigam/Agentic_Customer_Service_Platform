"""One-shot dev script: set every user's password_hash to bcrypt("password").

Run against the Docker Postgres (port 5432 must be exposed to host):

    uv run python scripts/rehash_passwords.py

Override the DB URL if needed:

    DATABASE_URL=postgresql://dev_user:root123@localhost:5432/ecommerce \
        uv run python scripts/rehash_passwords.py
"""

import os

import bcrypt
import psycopg

_DB_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://dev_user:root123@localhost:5432/ecommerce",
)

# Strip the async driver prefix if someone passes the app's DSN directly
_DB_URL = _DB_URL.replace("postgresql+psycopg://", "postgresql://")

_NEW_HASH = bcrypt.hashpw(b"password", bcrypt.gensalt(rounds=12)).decode()


def main() -> None:
    print(f"Connecting to: {_DB_URL}")
    with psycopg.connect(_DB_URL) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM users")
            (total,) = cur.fetchone()

            cur.execute("UPDATE users SET password_hash = %s", (_NEW_HASH,))
            updated = cur.rowcount

        conn.commit()

    print(f"Done. Updated {updated}/{total} users -> password = 'password'")
    print(f"Hash written: {_NEW_HASH}")


if __name__ == "__main__":
    main()
