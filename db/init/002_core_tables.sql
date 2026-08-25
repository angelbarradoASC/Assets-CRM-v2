CREATE TABLE IF NOT EXISTS crm.organizations (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    legacy_company_id text,
    name text NOT NULL,
    tax_id text,
    domain text,
    organization_type text NOT NULL DEFAULT 'company',
    status text NOT NULL DEFAULT 'prospect' CONSTRAINT organizations_status_check CHECK (status IN ('prospect','customer','former_customer','partner','supplier','inactive')),
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS crm.contacts (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id uuid REFERENCES crm.organizations(id),
    first_name text,
    last_name text,
    email text,
    phone text,
    source text NOT NULL DEFAULT 'manual' CONSTRAINT contacts_source_check CHECK (source IN ('manual','erp_sale','import','other')),
    notes text,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now()
);

COMMENT ON TABLE crm.contacts IS 'Individual person. organization_id is nullable because most marketplace buyers (eBay/Wallapop) are consumers, not companies — see docs/03-crm-v2-target-design.md.';
COMMENT ON COLUMN crm.contacts.source IS 'erp_sale = auto-created/resolved by Assets ERP when a sale is recorded. Never a copy of ERP business data, only identity.';

CREATE UNIQUE INDEX IF NOT EXISTS idx_contacts_email_unique ON crm.contacts (lower(email)) WHERE email IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_contacts_organization ON crm.contacts(organization_id);
CREATE INDEX IF NOT EXISTS idx_organizations_status ON crm.organizations(status);
