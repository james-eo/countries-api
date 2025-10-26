import random
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Dict, Optional, Tuple

from app.models.country import Country
from app.services.countries_service import CountriesAPIService
from app.services.exchange_service import ExchangeRateService


class CountryService:
    """Service for country data processing and database operations"""
    
    def __init__(self, db: Session):
        self.db = db
        self.countries_api = CountriesAPIService()
        self.exchange_api = ExchangeRateService()
    
    async def refresh_countries_data(self) -> Tuple[int, int]:
        """
        Refresh countries data from external APIs
        Returns: (countries_updated, countries_added)
        """
        try:
            # Fetch data from external APIs
            countries_data = await self.countries_api.fetch_countries()
            exchange_rates = await self.exchange_api.fetch_exchange_rates()
            
            countries_updated = 0
            countries_added = 0
            
            for country_data in countries_data:
                # Process the country data
                processed_country = self._process_country_for_db(country_data, exchange_rates)
                
                # Check if country exists (case-insensitive)
                existing_country = self.db.query(Country).filter(
                    func.lower(Country.name) == func.lower(processed_country["name"])
                ).first()
                
                if existing_country:
                    # Update existing country
                    self._update_country(existing_country, processed_country)
                    countries_updated += 1
                else:
                    # Create new country
                    new_country = Country(**processed_country)
                    self.db.add(new_country)
                    countries_added += 1
            
            # Commit all changes
            self.db.commit()
            
            return countries_updated, countries_added
            
        except Exception as e:
            self.db.rollback()
            raise Exception(f"Failed to refresh countries data: {str(e)}")
    
    def _process_country_for_db(self, country_data: Dict, exchange_rates: Dict[str, float]) -> Dict:
        """Process country data for database insertion"""
        currency_code = country_data.get("currency_code")
        exchange_rate = None
        estimated_gdp = 0
        
        # Get exchange rate if currency exists
        if currency_code and currency_code in exchange_rates:
            exchange_rate = exchange_rates[currency_code]
            
            # Calculate estimated GDP
            if exchange_rate and exchange_rate > 0:
                population = country_data.get("population", 0)
                random_multiplier = random.uniform(1000, 2000)
                estimated_gdp = (population * random_multiplier) / exchange_rate
        
        return {
            "name": country_data["name"],
            "capital": country_data.get("capital"),
            "region": country_data.get("region"),
            "population": country_data.get("population", 0),
            "currency_code": currency_code,
            "exchange_rate": exchange_rate,
            "estimated_gdp": estimated_gdp if estimated_gdp > 0 else None,
            "flag_url": country_data.get("flag_url"),
            "last_refreshed_at": datetime.utcnow()
        }
    
    def _update_country(self, existing_country: Country, new_data: Dict):
        """Update existing country with new data"""
        for key, value in new_data.items():
            if hasattr(existing_country, key):
                setattr(existing_country, key, value)
    
    def get_countries(self, region: Optional[str] = None, currency: Optional[str] = None, 
                     sort: Optional[str] = None, skip: int = 0, limit: int = 100) -> List[Country]:
        """Get countries with optional filtering and sorting"""
        query = self.db.query(Country)
        
        # Apply filters
        if region:
            query = query.filter(func.lower(Country.region) == func.lower(region))
        
        if currency:
            query = query.filter(func.lower(Country.currency_code) == func.lower(currency))
        
        # Apply sorting
        if sort:
            if sort.lower() == "gdp_desc":
                query = query.order_by(Country.estimated_gdp.desc())
            elif sort.lower() == "gdp_asc":
                query = query.order_by(Country.estimated_gdp.asc())
            elif sort.lower() == "population_desc":
                query = query.order_by(Country.population.desc())
            elif sort.lower() == "population_asc":
                query = query.order_by(Country.population.asc())
            elif sort.lower() == "name_asc":
                query = query.order_by(Country.name.asc())
            elif sort.lower() == "name_desc":
                query = query.order_by(Country.name.desc())
        
        return query.offset(skip).limit(limit).all()
    
    def get_country_by_name(self, name: str) -> Optional[Country]:
        """Get a country by name (case-insensitive)"""
        return self.db.query(Country).filter(
            func.lower(Country.name) == func.lower(name)
        ).first()
    
    def delete_country_by_name(self, name: str) -> bool:
        """Delete a country by name (case-insensitive)"""
        country = self.get_country_by_name(name)
        if country:
            self.db.delete(country)
            self.db.commit()
            return True
        return False
    
    def get_countries_stats(self) -> Dict:
        """Get countries statistics"""
        total_countries = self.db.query(Country).count()
        
        # Get the most recent refresh timestamp
        last_refresh = self.db.query(func.max(Country.last_refreshed_at)).scalar()
        
        return {
            "total_countries": total_countries,
            "last_refreshed_at": last_refresh
        }
    
    def get_top_countries_by_gdp(self, limit: int = 5) -> List[Country]:
        """Get top countries by estimated GDP"""
        return self.db.query(Country).filter(
            Country.estimated_gdp.isnot(None)
        ).order_by(Country.estimated_gdp.desc()).limit(limit).all()