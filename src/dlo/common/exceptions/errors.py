"""
DLO error definitions aligned with JSON-RPC 2.0 error codes
"""

from typing import Any, Dict, Optional


# ============================================================
# Base Error
# ============================================================

class DloError(Exception):
    """
    Base class for all DLO errors.
    Produces a protocol-compatible error object.
    """

    CODE: int = -32000
    MESSAGE: str = "Server error"
    ERROR_TYPE: str = "Server"

    def __init__(self, message: Optional[str] = None, data: Any = None):
        super().__init__(message or self.MESSAGE)
        self.data = data

    @property
    def type(self) -> str:
        return self.ERROR_TYPE

    def to_dict(self) -> Dict[str, Any]:
        err = {
            "code": self.CODE,
            "message": str(self),
            "type": self.type,
        }
        if self.data is not None:
            err["data"] = self.data
        return err


# ============================================================
# Protocol-Level Errors (JSON-RPC Spec Codes)
# ============================================================

class ParseError(DloError):
    CODE = -32700
    MESSAGE = "Parse error"
    ERROR_TYPE = "Parse"


class InvalidRequestError(DloError):
    CODE = -32600
    MESSAGE = "Invalid Request"
    ERROR_TYPE = "Request"


class MethodNotFoundError(DloError):
    CODE = -32601
    MESSAGE = "Method not found"
    ERROR_TYPE = "Method"


class InvalidParamsError(DloError):
    CODE = -32602
    MESSAGE = "Invalid params"
    ERROR_TYPE = "Params"


class InternalError(DloError):
    CODE = -32603
    MESSAGE = "Internal error"
    ERROR_TYPE = "Internal"


# ============================================================
# DLO Server Errors (Reserved Range: -32000 to -32099)
# ============================================================

class DloServerError(DloError):
    CODE = -32000
    MESSAGE = "Server error"
    ERROR_TYPE = "Server"

# ---------------- Parse / Validation ----------------


class DloParseError(ParseError):
    CODE = -32001
    MESSAGE = "Parse error"
    ERROR_TYPE = "Parse"


# ---------------- Runtime / Execution ----------------

class DloRuntimeError(DloServerError):
    CODE = -32001
    MESSAGE = "Runtime error"
    ERROR_TYPE = "Runtime"


class DloCompilationError(DloRuntimeError):
    CODE = -32002
    MESSAGE = "Compilation error"
    ERROR_TYPE = "Compilation"


class DloRecursionLimitError(DloRuntimeError):
    CODE = -32003
    MESSAGE = "Recursion limit exceeded"
    ERROR_TYPE = "Runtime"


# ---------------- Configuration / Features ----------------

class DloConfigError(DloServerError):
    CODE = -32010
    MESSAGE = "Configuration error"
    ERROR_TYPE = "Config"


class DloFeatureNotImplementedError(DloServerError):
    CODE = -32011
    MESSAGE = "Feature not implemented"
    ERROR_TYPE = "NotImplemented"


# ============================================================
# Helper
# ============================================================

def to_error_dict(exc: Exception) -> Dict[str, Any]:
    """
    Convert any exception into a protocol-compatible error dict.
    """
    if isinstance(exc, DloError):
        return exc.to_dict()

    # Never leak raw exceptions
    return InternalError().to_dict()


# ============================================================
# Example (safe to delete)
# ============================================================

if __name__ == "__main__":
    try:
        raise DloCompilationError(
            "Failed to compile query",
            data={"line": 12, "column": 8},
        )
    except Exception as e:
        response = {
            "id": 1,
            "error": to_error_dict(e),
        }
        print(response)
