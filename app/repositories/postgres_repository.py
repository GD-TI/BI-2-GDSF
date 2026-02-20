from __future__ import annotations

from contextlib import contextmanager

from db import get_connection


@contextmanager
def get_cursor():
    conn = get_connection()
    try:
        cur = conn.cursor()
        yield cur
    finally:
        conn.close()
