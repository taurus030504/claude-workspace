"""Domain errors. The API layer maps them to HTTP responses with a stable ``code``."""

from __future__ import annotations


class AppError(Exception):
    status_code = 400
    code = "bad_request"

    def __init__(self, message: str, *, details: dict | None = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}


class NotFoundError(AppError):
    status_code = 404
    code = "not_found"


class ConflictError(AppError):
    status_code = 409
    code = "conflict"


class ValidationError(AppError):
    status_code = 422
    code = "validation_error"


class PayloadTooLargeError(AppError):
    status_code = 413
    code = "payload_too_large"


class UnsupportedFormatError(AppError):
    status_code = 415
    code = "unsupported_format"


class LLMUnavailableError(AppError):
    """Ollama is not running, or the configured model has not been pulled."""

    status_code = 503
    code = "llm_unavailable"
