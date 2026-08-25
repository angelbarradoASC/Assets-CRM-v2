from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from app.auth import require_api_key
from app.db import get_conn
from app.schemas import ContactIn, ContactOut, ContactResolveIn

router = APIRouter(prefix="/api/v1/contacts", tags=["contacts"], dependencies=[Depends(require_api_key)])

CONTACT_COLUMNS = "id, organization_id, first_name, last_name, email, phone, source, notes, created_at, updated_at"


@router.get("", response_model=list[ContactOut])
def list_contacts(conn=Depends(get_conn)):
    return conn.execute(f"SELECT {CONTACT_COLUMNS} FROM crm.contacts ORDER BY created_at DESC").fetchall()


@router.post("", response_model=ContactOut, status_code=201)
def create_contact(contact: ContactIn, conn=Depends(get_conn)):
    row = conn.execute(
        f"""
        INSERT INTO crm.contacts (first_name, last_name, email, phone, source, notes)
        VALUES (%(first_name)s, %(last_name)s, %(email)s, %(phone)s, %(source)s, %(notes)s)
        RETURNING {CONTACT_COLUMNS}
        """,
        contact.model_dump(),
    ).fetchone()
    conn.commit()
    return row


@router.post("/resolve", response_model=ContactOut)
def resolve_contact(payload: ContactResolveIn, conn=Depends(get_conn)):
    """Find-or-create. Dedup order: exact email, then exact phone. Never fuzzy-matches
    by name — see docs/03-crm-v2-target-design.md section 6 (deduplication)."""
    existing = None
    if payload.email:
        existing = conn.execute(
            f"SELECT {CONTACT_COLUMNS} FROM crm.contacts WHERE lower(email) = lower(%s)",
            [payload.email],
        ).fetchone()
    if existing is None and payload.phone:
        existing = conn.execute(
            f"SELECT {CONTACT_COLUMNS} FROM crm.contacts WHERE phone = %s",
            [payload.phone],
        ).fetchone()
    if existing is not None:
        return existing

    row = conn.execute(
        f"""
        INSERT INTO crm.contacts (first_name, last_name, email, phone, source, notes)
        VALUES (%(first_name)s, %(last_name)s, %(email)s, %(phone)s, %(source)s, %(notes)s)
        RETURNING {CONTACT_COLUMNS}
        """,
        payload.model_dump(),
    ).fetchone()
    conn.commit()
    return row


@router.get("/{contact_id}", response_model=ContactOut)
def get_contact(contact_id: UUID, conn=Depends(get_conn)):
    row = conn.execute(f"SELECT {CONTACT_COLUMNS} FROM crm.contacts WHERE id = %s", [contact_id]).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    return row
