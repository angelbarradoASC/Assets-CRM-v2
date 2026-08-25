from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from app.db import close_pool, get_pool, open_pool
from app.routers import contacts


@asynccontextmanager
async def lifespan(app: FastAPI):
    open_pool()
    yield
    close_pool()


app = FastAPI(title="Assets CRM v2 API", version="0.1.0", lifespan=lifespan, root_path="/crmv2")

app.include_router(contacts.router)


@app.get("/health")
def health():
    try:
        with get_pool().connection(timeout=3) as conn:
            conn.execute("SELECT 1")
        return {"status": "ok", "database": "reachable"}
    except Exception as exc:  # noqa: BLE001 — health check must report, not raise
        return JSONResponse(status_code=503, content={"status": "error", "detail": str(exc)})
