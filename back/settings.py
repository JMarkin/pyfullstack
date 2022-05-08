from functools import cached_property, lru_cache

from pydantic import BaseSettings


class Settings(BaseSettings):
    """Настройки проекта."""
    DATABASE_URL: str = "postgres://app:app@postgres:5432/app"
    LOG_LEVEL: str = "INFO"
    CONNECT_TIMEOUT: int = 1

    @cached_property
    def log_config(self):
        PRE_LOGGING: dict = {
            "version": 1,
            "disable_existing_loggers": False,
            "root": {
                "level": self.LOG_LEVEL,
                "handlers": ["stdout"],
            },
            "formatters": {
                "console": {
                    "format": "%(asctime)s | %(levelname)-8s | %(name)s - %(message)s"
                },
            },
            "handlers": {
                "stdout": {
                    "level": self.LOG_LEVEL,
                    "class": "logging.StreamHandler",
                    "formatter": "console",
                },
            },
            "loggers": {
                "uvicorn": {
                    "handlers": ["stdout"],
                    "level": self.LOG_LEVEL,
                    "propagate": False
                },
            },
        }

        try:
            import coloredlogs  # type: ignore

            coloredlogs.install()

            PRE_LOGGING["formatters"]["console"]["()"] = "coloredlogs.ColoredFormatter"

        except ImportError:
            pass
        return PRE_LOGGING

    class Config:
        allow_population_by_field_name = True

        anystr_strip_whitespace = True
        keep_untouched = (cached_property, property)


@lru_cache
def get_settings():
    return Settings()

settings = get_settings()
