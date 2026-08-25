-- Bootstrap role topology only. Credentials are injected later by the versioned migration runner.
-- Mirrors the pattern used by Assets-ERP (db/init/000_roles.sql), scaled down to a single
-- application role since CRM v2 has one schema so far.

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'crm_app_rw') THEN
        CREATE ROLE crm_app_rw NOLOGIN;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'crm_app') THEN
        CREATE ROLE crm_app NOLOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE INHERIT;
    END IF;
END $$;

GRANT crm_app_rw TO crm_app;
