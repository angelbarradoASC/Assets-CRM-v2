from collections.abc import Iterator

from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool

from app.config import settings

pool: ConnectionPool | None = None


def open_pool() -> None:
    global pool
    pool = ConnectionPool(conninfo=settings.db_dsn, min_size=1, max_size=10, open=True)


def close_pool() -> None:
    if pool is not None:
        pool.close()


def get_pool() -> ConnectionPool:
    assert pool is not None, "DB pool not initialised"
    return pool


def get_conn() -> Iterator:
    assert pool is not None, "DB pool not initialised"
    with pool.connection() as conn:
        conn.row_factory = dict_row
        yield conn
