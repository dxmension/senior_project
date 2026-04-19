import logging


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    _ensure_handler(logger)
    logger.setLevel(logging.INFO)
    return logger


def log_step(logger: logging.Logger, event: str, **context: object) -> None:
    details = _format_context(context)
    message = event if not details else f"{event} | {details}"
    logger.info(message)


def _format_context(context: dict[str, object]) -> str:
    pairs = []
    for key, value in sorted(context.items()):
        pairs.append(f"{key}={_safe_value(value)}")
    return ", ".join(pairs)


def _safe_value(value: object) -> str:
    if value is None:
        return "null"
    return str(value).replace("\n", "\\n")


def _ensure_handler(logger: logging.Logger) -> None:
    if logger.handlers:
        return
    handler = logging.StreamHandler()
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter(
        "%(asctime)s %(levelname)s [%(name)s] %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.propagate = False
