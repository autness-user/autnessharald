from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.sheets import router as sheets_router
from app.api.performance import router as performance_router
from app.api.public_sheets import router as public_sheets_router
from config.settings import settings


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
)

allow_credentials = settings.CORS_CREDENTIALS
if "*" in settings.CORS_ORIGINS and allow_credentials:
    allow_credentials = False

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=allow_credentials,
    allow_methods=settings.CORS_METHODS,
    allow_headers=settings.CORS_HEADERS,
)


@app.get("/")
def health() -> dict:
    return {"status": "ok", "service": settings.APP_NAME, "version": settings.APP_VERSION}


app.include_router(sheets_router, prefix="/sheets", tags=["Sheets"])
app.include_router(performance_router, prefix="/performance", tags=["Performance"])
app.include_router(public_sheets_router, prefix="/public-sheets", tags=["Public Sheets"])
