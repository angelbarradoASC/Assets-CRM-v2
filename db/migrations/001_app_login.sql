-- Migration 001: activate the application login. Password injected by scripts/migrate.py, never committed.
ALTER ROLE crm_app WITH LOGIN PASSWORD {{CRM_DB_APP_PASSWORD_LITERAL}};
