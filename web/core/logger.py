LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "console_formatter": {"format": "{message}", "style": "{"},
        "file_formatter": {
            "format": "{levelname} {asctime} \n\tModule: {module} \n\tFilePath: {pathname} \n\tFunction Name: {funcName} \n\tLine No: {lineno} \n\tMessage: {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "INFO",
            "formatter": "console_formatter",
        },
        "core": {
            "class": "logging.handlers.TimedRotatingFileHandler",
            "level": "INFO",
            "filename": "logs/core/core.log",
            "formatter": "file_formatter",
            "when": "midnight",
            "interval": 1,
            "backupCount": 7,
            "encoding": "utf-8",
            "delay": True,
        },
        "request_file": {
            "class": "logging.handlers.TimedRotatingFileHandler",
            "level": "DEBUG",
            "filename": "logs/requests/requests.log",
            "formatter": "file_formatter",
            "when": "midnight",
            "interval": 1,
            "backupCount": 7,
            "encoding": "utf-8",
            "delay": True,
        },
    },
    "loggers": {
        "": {
            "handlers": ["core", "console"],
            "level": "DEBUG",
            "propagate": False,
        },
        "django": {
            "handlers": ["request_file", "console"],
            "level": "INFO",
            "propagate": False,
        },
    },
}
