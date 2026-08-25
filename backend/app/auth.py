from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader

from app.config import settings

_api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def require_api_key(x_api_key: str | None = Security(_api_key_header)) -> None:
    """Static service key for the initial phase — same stopgap as Assets-ERP until
    service-to-service identity (Entra ID or similar) is decided."""
    if not x_api_key or x_api_key != settings.crm_api_key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or missing API key")
