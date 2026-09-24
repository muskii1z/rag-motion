"""Database connection helper."""

import psycopg
from pgvector.psycopg import register_vector

from ragmotion.config import settings


def get_connection() -> psycopg.Connection:
    """Open a connection to Postgres and teach psycopg about the vector type.

    Use it as a context manager so the connection is committed and closed for you:

        with get_connection() as conn:
            conn.execute("SELECT 1")
    """
    conn = psycopg.connect(settings.database_url)
    register_vector(conn)
    return conn
