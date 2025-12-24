"""PostgreSQL EXPLAIN executor."""

import json
from typing import Optional

try:
    import psycopg2
    PSYCOPG2_AVAILABLE = True
except ImportError:
    PSYCOPG2_AVAILABLE = False


def run_explain(
    query: str,
    dsn: Optional[str] = None,
    host: str = 'localhost',
    port: int = 5432,
    database: str = 'postgres',
    user: str = 'postgres',
    password: str = '',
) -> str:
    """Run EXPLAIN ANALYZE and return JSON result.

    Args:
        query: SQL query to analyze
        dsn: Full connection string (postgresql://...)
        host, port, database, user, password: Individual connection params

    Returns:
        JSON string of EXPLAIN output
    """
    if not PSYCOPG2_AVAILABLE:
        raise RuntimeError("psycopg2 not installed. Run: pip install psycopg2-binary")

    # Build connection
    if dsn:
        conn = psycopg2.connect(dsn)
    else:
        conn = psycopg2.connect(
            host=host,
            port=port,
            database=database,
            user=user,
            password=password,
        )

    try:
        with conn.cursor() as cur:
            explain_query = f"EXPLAIN (ANALYZE, FORMAT JSON) {query}"
            cur.execute(explain_query)
            result = cur.fetchone()[0]
            return json.dumps(result)
    finally:
        conn.close()


def parse_dsn(dsn: str) -> dict:
    """Parse PostgreSQL DSN into components."""
    # postgresql://user:pass@host:port/database
    from urllib.parse import urlparse

    parsed = urlparse(dsn)

    return {
        'host': parsed.hostname or 'localhost',
        'port': parsed.port or 5432,
        'database': parsed.path.lstrip('/') or 'postgres',
        'user': parsed.username or 'postgres',
        'password': parsed.password or '',
    }
