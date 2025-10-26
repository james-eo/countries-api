from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.schemas.country import (
    CountryResponse, CountryFilter, StatusResponse, 
    RefreshResponse, ErrorResponse
)
from app.services.country_service import CountryService
from app.services.image_service import ImageService
from app.utils.exceptions import (
    CountryNotFoundError, ExternalServiceError, 
    InternalServerError, ImageNotFoundError
)

router = APIRouter(prefix="/countries", tags=["countries"])


@router.post("/refresh", response_model=RefreshResponse)
async def refresh_countries(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Fetch all countries and exchange rates, then cache them in the database
    """
    try:
        country_service = CountryService(db)
        countries_updated, countries_added = await country_service.refresh_countries_data()
        
        # Generate summary image in background
        background_tasks.add_task(generate_summary_image_task, db)
        
        # Get updated stats
        stats = country_service.get_countries_stats()
        
        return RefreshResponse(
            message="Countries data refreshed successfully",
            countries_updated=countries_updated,
            countries_added=countries_added,
            last_refreshed_at=stats["last_refreshed_at"]
        )
        
    except Exception as e:
        if "Could not fetch data" in str(e) or "timeout" in str(e).lower():
            if "countries" in str(e).lower():
                raise ExternalServiceError("Countries API")
            else:
                raise ExternalServiceError("Exchange Rates API")
        raise InternalServerError(f"Failed to refresh countries: {str(e)}")


@router.get("", response_model=List[CountryResponse])
def get_countries(
    region: Optional[str] = Query(None, description="Filter by region (e.g., Africa)"),
    currency: Optional[str] = Query(None, description="Filter by currency code (e.g., NGN)"),
    sort: Optional[str] = Query(None, description="Sort by field (e.g., gdp_desc, population_asc, name_asc)"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    db: Session = Depends(get_db)
):
    """
    Get all countries from the database with optional filtering and sorting
    """
    try:
        country_service = CountryService(db)
        countries = country_service.get_countries(
            region=region, 
            currency=currency, 
            sort=sort, 
            skip=skip, 
            limit=limit
        )
        return countries
    except Exception as e:
        raise InternalServerError(f"Failed to fetch countries: {str(e)}")


@router.get("/{name}", response_model=CountryResponse)
def get_country_by_name(name: str, db: Session = Depends(get_db)):
    """
    Get one country by name
    """
    try:
        country_service = CountryService(db)
        country = country_service.get_country_by_name(name)
        
        if not country:
            raise CountryNotFoundError(name)
        
        return country
    except CountryNotFoundError:
        raise
    except Exception as e:
        raise InternalServerError(f"Failed to fetch country: {str(e)}")


@router.delete("/{name}")
def delete_country(name: str, db: Session = Depends(get_db)):
    """
    Delete a country record
    """
    try:
        country_service = CountryService(db)
        deleted = country_service.delete_country_by_name(name)
        
        if not deleted:
            raise CountryNotFoundError(name)
        
        return {"message": f"Country '{name}' deleted successfully"}
    except CountryNotFoundError:
        raise
    except Exception as e:
        raise InternalServerError(f"Failed to delete country: {str(e)}")


# Move image endpoint to avoid path conflicts with /{name}
image_router = APIRouter(prefix="/countries", tags=["countries"])

@image_router.get("/image", response_class=FileResponse)
def get_summary_image(db: Session = Depends(get_db)):
    """
    Serve the generated summary image
    """
    try:
        image_service = ImageService()
        
        if not image_service.image_exists():
            raise ImageNotFoundError()
        
        return FileResponse(
            path=image_service.get_image_path(),
            media_type="image/png",
            filename="summary.png"
        )
    except ImageNotFoundError:
        raise
    except Exception as e:
        raise InternalServerError(f"Failed to serve image: {str(e)}")


# Add status endpoint to main router
status_router = APIRouter(tags=["status"])

@status_router.get("/status", response_model=StatusResponse)
def get_status(db: Session = Depends(get_db)):
    """
    Show total countries and last refresh timestamp
    """
    try:
        country_service = CountryService(db)
        stats = country_service.get_countries_stats()
        
        return StatusResponse(
            total_countries=stats["total_countries"],
            last_refreshed_at=stats["last_refreshed_at"]
        )
    except Exception as e:
        raise InternalServerError(f"Failed to get status: {str(e)}")


async def generate_summary_image_task(db: Session):
    """Background task to generate summary image"""
    try:
        country_service = CountryService(db)
        image_service = ImageService()
        
        # Get data for image
        stats = country_service.get_countries_stats()
        top_countries = country_service.get_top_countries_by_gdp(5)
        
        # Generate image
        image_service.generate_summary_image(
            total_countries=stats["total_countries"],
            top_countries=top_countries,
            last_refreshed=stats["last_refreshed_at"]
        )
    except Exception as e:
        print(f"Failed to generate summary image: {str(e)}")