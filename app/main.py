from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.routers.countries import router as countries_router, status_router, image_router
from app.database import engine, Base
from app.models.country import Country


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Skip database setup for now to ensure app starts
    print("🚀 Starting Country API...")
    print("⏭️ Skipping database setup during startup to avoid connection issues")
    yield
    # Shutdown: Clean up resources if needed
    print("🛑 Shutting down Country API...")


# Create FastAPI application
app = FastAPI(
    title="Country Currency & Exchange API",
    description="A RESTful API that fetches country data and exchange rates, with CRUD operations",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(image_router)  # Include image router first to avoid conflicts
app.include_router(countries_router)
app.include_router(status_router)


# Global exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.detail
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error"}
    )


# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Welcome to Country Currency & Exchange API",
        "version": "1.0.0",
        "endpoints": {
            "refresh": "POST /countries/refresh",
            "countries": "GET /countries",
            "country_by_name": "GET /countries/{name}",
            "delete_country": "DELETE /countries/{name}",
            "status": "GET /status",
            "summary_image": "GET /countries/image"
        }
    }


# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "API is running"}


# Debug endpoint to check environment (remove after debugging)
@app.get("/debug/env")
async def debug_env():
    import os
    env_vars = {
        "PORT": os.getenv("PORT"),
        "DEBUG": os.getenv("DEBUG"), 
        # Standard variables
        "DB_HOST": os.getenv("DB_HOST"),
        "DB_NAME": os.getenv("DB_NAME"),
        # Railway-specific variables
        "MYSQLHOST": os.getenv("MYSQLHOST"),
        "MYSQLPORT": os.getenv("MYSQLPORT"),
        "MYSQLUSER": os.getenv("MYSQLUSER"),
        "MYSQLDATABASE": os.getenv("MYSQLDATABASE"),
        "MYSQL_DATABASE": os.getenv("MYSQL_DATABASE"),
        # Connection strings (masked for security)
        "MYSQL_URL": "***" if os.getenv("MYSQL_URL") else None,
        "DATABASE_URL": "***" if os.getenv("DATABASE_URL") else None
    }
    return {"environment_variables": env_vars}


if __name__ == "__main__":
    import uvicorn
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    uvicorn.run(
        "app.main:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", 8000)),
        reload=os.getenv("DEBUG", "False").lower() == "true"
    )