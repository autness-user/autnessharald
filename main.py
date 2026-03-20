import uvicorn

from app.utils.logger import get_logger
from config.settings import settings

logger = get_logger(__name__)


def main() -> None:
    logger.info(f"Iniciando {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Servidor em http://{settings.HOST}:{settings.PORT}")
    logger.info(f"Documentação em http://{settings.HOST}:{settings.PORT}/docs")

    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    )


if __name__ == "__main__":
    main()
