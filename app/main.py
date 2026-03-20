from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.sheets import router as sheets_router
from app.api.performance import router as performance_router
from config.settings import settings


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_CREDENTIALS,
    allow_methods=settings.CORS_METHODS,
    allow_headers=settings.CORS_HEADERS,
)


@app.get("/")
def health() -> dict:
    return {"status": "ok", "service": settings.APP_NAME, "version": settings.APP_VERSION}


app.include_router(sheets_router, prefix="/sheets", tags=["Sheets"])
app.include_router(performance_router, prefix="/performance", tags=["Performance"])
