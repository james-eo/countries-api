from fastapi import HTTPException
from typing import Dict, Any


class CountryNotFoundError(HTTPException):
    def __init__(self, country_name: str):
        super().__init__(status_code=404, detail={"error": "Country not found"})


class ValidationError(HTTPException):
    def __init__(self, details: Dict[str, Any]):
        super().__init__(
            status_code=400, 
            detail={"error": "Validation failed", "details": details}
        )


class ExternalServiceError(HTTPException):
    def __init__(self, service_name: str):
        super().__init__(
            status_code=503,
            detail={
                "error": "External data source unavailable",
                "details": f"Could not fetch data from {service_name}"
            }
        )


class InternalServerError(HTTPException):
    def __init__(self, message: str = "Internal server error"):
        super().__init__(
            status_code=500,
            detail={"error": message}
        )


class ImageNotFoundError(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=404,
            detail={"error": "Summary image not found"}
        )