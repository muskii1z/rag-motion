"""Database connection helper."""

import psycopg
from pgvector.psycopg import register_vector

from ragmotion.config import settings
from ragmotion.errors import DatabaseUnavailable


def get_connection() -> psycopg.Connection:
    """Open a connection to Postgres and teach psycopg about the vector type.

    Use it as a context manager so the connection is committed and closed for you:

        with get_connection() as conn:
            conn.execute("SELECT 1")
    """
    try:
        conn = psycopg.connect(settings.database_url, connect_timeout=5)
    except psycopg.OperationalError as e:
        raise DatabaseUnavailable(
            "Can't reach the database. Is Docker running? Start it with: docker compose up -d --wait"
        ) from e
    register_vector(conn)
    return conn
