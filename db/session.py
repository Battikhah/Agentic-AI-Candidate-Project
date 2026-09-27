"""Shared PostgreSQL persistence for AgentOS sessions and traces."""

from functools import cache

from agno.db.postgres import PostgresDb

from db.url import db_url


@cache
def get_postgres_db() -> PostgresDb:
    """Reuse one database handle for advisor sessions and platform traces."""
    return PostgresDb(id="agentos-db", db_url=db_url)
