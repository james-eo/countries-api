from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class CountryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="Country name")
    capital: Optional[str] = Field(None, max_length=255, description="Capital city")
    region: Optional[str] = Field(None, max_length=255, description="Geographic region")
    population: int = Field(..., ge=0, description="Population count")
    currency_code: Optional[str] = Field(None, max_length=10, description="Currency code (e.g., USD, NGN)")
    exchange_rate: Optional[float] = Field(None, gt=0, description="Exchange rate to USD")
    estimated_gdp: Optional[float] = Field(None, gt=0, description="Estimated GDP")
    flag_url: Optional[str] = Field(None, description="URL to country flag image")


class CountryCreate(CountryBase):
    pass


class CountryUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    capital: Optional[str] = Field(None, max_length=255)
    region: Optional[str] = Field(None, max_length=255)
    population: Optional[int] = Field(None, ge=0)
    currency_code: Optional[str] = Field(None, max_length=10)
    exchange_rate: Optional[float] = Field(None, gt=0)
    estimated_gdp: Optional[float] = Field(None, gt=0)
    flag_url: Optional[str] = None


class CountryResponse(CountryBase):
    id: int
    last_refreshed_at: datetime

    class Config:
        from_attributes = True


class CountryFilter(BaseModel):
    region: Optional[str] = Field(None, description="Filter by region")
    currency: Optional[str] = Field(None, description="Filter by currency code")
    sort: Optional[str] = Field(None, description="Sort by field (e.g., gdp_desc, population_asc)")


class StatusResponse(BaseModel):
    total_countries: int
    last_refreshed_at: Optional[datetime]


class ErrorResponse(BaseModel):
    error: str
    details: Optional[dict] = None


class RefreshResponse(BaseModel):
    message: str
    countries_updated: int
    countries_added: int
    last_refreshed_at: datetime