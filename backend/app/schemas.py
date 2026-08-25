from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class ContactIn(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    email: str | None = None
    phone: str | None = None
    source: str = "manual"
    notes: str | None = None


class ContactOut(ContactIn):
    id: UUID
    organization_id: UUID | None = None
    created_at: datetime
    updated_at: datetime


class ContactResolveIn(BaseModel):
    """Find-or-create by email (primary key for dedup). Falls back to phone, then creates new."""
    first_name: str | None = None
    last_name: str | None = None
    email: str | None = None
    phone: str | None = None
    source: str = "erp_sale"
    notes: str | None = None
