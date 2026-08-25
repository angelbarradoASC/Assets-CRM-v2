#!/usr/bin/env python3
"""Minimal versioned PostgreSQL migration runner for Assets CRM v2.

Same design as Assets-ERP/scripts/migrate.py: docker exec + psql, checksum-tracked
migrations in infra.schema_migrations, session advisory lock to serialize runners.
"""

from __future__ import annotations

import argparse
import contextlib
import hashlib
import os
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
MIGRATIONS_DIR = ROOT / "db" / "migrations"
MIGRATION_LOCK_KEY = 553017028


def load_env_file(path: pathlib.Path) -> None:
    if not path.exists():
        return
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())


def sql_literal(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


def db_connection_args() -> tuple[str, str, str, str]:
    container = os.environ.get("CRM_DB_CONTAINER", "assets-crm-db")
    db = os.environ.get("CRM_DB_NAME", "assets_crm")
    admin = os.environ.get("CRM_DB_ADMIN_USER", "crm_admin")
    admin_password = os.environ.get("CRM_DB_ADMIN_PASSWORD")
    if not admin_password:
        raise SystemExit("CRM_DB_ADMIN_PASSWORD is required")
    return container, db, admin, admin_password


def psql_command() -> list[str]:
    container, db, admin, admin_password = db_connection_args()
    return [
        "docker", "exec", "-i",
        "-e", f"PGPASSWORD={admin_password}",
        container,
        "psql", "-X", "-v", "ON_ERROR_STOP=1", "-At",
        "-U", admin, "-d", db,
    ]


def run_psql(sql: str, *, capture: bool = False) -> str:
    proc = subprocess.run(
        psql_command(),
        input=sql,
        encoding="utf-8",
        capture_output=capture,
        check=False,
    )
    if proc.returncode != 0:
        if proc.stderr:
            print(proc.stderr, file=sys.stderr)
        raise SystemExit(proc.returncode)
    return proc.stdout.strip() if capture else ""


@contextlib.contextmanager
def migration_lock():
    """Hold a PostgreSQL session advisory lock for the whole runner execution."""
    proc = subprocess.Popen(
        psql_command(),
        encoding="utf-8",
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        bufsize=1,
    )
    try:
        if proc.stdin is None or proc.stdout is None:
            raise SystemExit("Could not open persistent advisory-lock session")

        proc.stdin.write(
            f"SELECT pg_advisory_lock({MIGRATION_LOCK_KEY});\n"
            "SELECT 'LOCKED';\n"
        )
        proc.stdin.flush()

        for line in proc.stdout:
            if line.strip() == "LOCKED":
                break
        else:
            stderr = proc.stderr.read() if proc.stderr else ""
            raise SystemExit(
                "Migration advisory-lock session exited before acquiring lock. "
                + stderr
            )

        yield
    finally:
        if proc.poll() is None and proc.stdin is not None:
            try:
                proc.stdin.write(
                    f"SELECT pg_advisory_unlock({MIGRATION_LOCK_KEY});\n\\q\n"
                )
                proc.stdin.flush()
                proc.wait(timeout=5)
            except (BrokenPipeError, subprocess.TimeoutExpired):
                proc.terminate()
                try:
                    proc.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    proc.kill()
                    proc.wait(timeout=5)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--env-file", default=str(ROOT / ".env.infrastructure"))
    args = parser.parse_args()

    load_env_file(pathlib.Path(args.env_file))
    app_password = os.environ.get("CRM_DB_APP_PASSWORD")
    if not app_password:
        raise SystemExit("CRM_DB_APP_PASSWORD is required")

    with migration_lock():
        run_psql(
            "CREATE SCHEMA IF NOT EXISTS infra;\n"
            "CREATE TABLE IF NOT EXISTS infra.schema_migrations ("
            "version text PRIMARY KEY, filename text NOT NULL, checksum text NOT NULL, "
            "applied_at timestamptz NOT NULL DEFAULT now());\n"
        )

        migrations = sorted(MIGRATIONS_DIR.glob("[0-9][0-9][0-9]_*.sql"))
        for migration in migrations:
            version = migration.name.split("_", 1)[0]
            raw = migration.read_text(encoding="utf-8")
            checksum = hashlib.sha256(raw.encode("utf-8")).hexdigest()

            existing = run_psql(
                "SELECT checksum FROM infra.schema_migrations "
                f"WHERE version = {sql_literal(version)};\n",
                capture=True,
            )
            if existing:
                if existing != checksum:
                    raise SystemExit(
                        f"Migration {version} was modified after being applied. "
                        f"Expected checksum {existing}, current {checksum}."
                    )
                print(f"SKIP {migration.name}")
                continue

            rendered = raw.replace(
                "{{CRM_DB_APP_PASSWORD_LITERAL}}", sql_literal(app_password)
            )
            wrapped = (
                "BEGIN;\n"
                + rendered
                + "\nINSERT INTO infra.schema_migrations(version, filename, checksum) VALUES ("
                + ", ".join(
                    [sql_literal(version), sql_literal(migration.name), sql_literal(checksum)]
                )
                + ");\nCOMMIT;\n"
            )
            run_psql(wrapped)
            print(f"APPLIED {migration.name}")


if __name__ == "__main__":
    main()
