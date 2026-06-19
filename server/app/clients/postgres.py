from __future__ import annotations

import psycopg
from psycopg import Connection

from app.settings import Settings


def connect_postgres(settings: Settings) -> Connection:
    database_url = settings.secret_value(settings.supabase_database_url)
    if database_url:
        return psycopg.connect(database_url, connect_timeout=20)

    password = settings.secret_value(settings.supabase_db_password)
    missing = [
        name
        for name, value in (
            ("SUPABASE_DB_HOST", settings.supabase_db_host),
            ("SUPABASE_DB_USER", settings.supabase_db_user),
            ("SUPABASE_DB_PASSWORD", password),
        )
        if not value
    ]
    if missing:
        raise RuntimeError(f"Missing Postgres connection settings: {', '.join(missing)}")

    return psycopg.connect(
        host=settings.supabase_db_host,
        port=settings.supabase_db_port,
        dbname=settings.supabase_db_name,
        user=settings.supabase_db_user,
        password=password,
        sslmode=settings.supabase_db_sslmode,
        connect_timeout=20,
    )
