CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE SCHEMA IF NOT EXISTS crm;

COMMENT ON SCHEMA crm IS 'Assets CRM v2 — commercial domain: organizations, contacts, and (later) leads/opportunities. Independent database from Assets ERP per docs/05-erp-module-boundary.md.';
