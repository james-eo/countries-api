import httpx
import asyncio
from typing import List, Dict, Optional
from dotenv import load_dotenv
import os

load_dotenv()


class CountriesAPIService:
    """Service to fetch countries data from restcountries.com"""
    
    def __init__(self):
        self.countries_url = os.getenv("COUNTRIES_API_URL", "https://restcountries.com/v2/all?fields=name,capital,region,population,flag,currencies")
        self.timeout = 30.0  # 30 seconds timeout
        
    async def fetch_countries(self) -> List[Dict]:
        """
        Fetch all countries data from the external API
        Returns: List of country dictionaries
        Raises: httpx.RequestError, httpx.TimeoutException
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(self.countries_url)
                response.raise_for_status()
                countries_data = response.json()
                
                # Process and normalize the data
                processed_countries = []
                for country_data in countries_data:
                    processed_country = self._process_country_data(country_data)
                    if processed_country:
                        processed_countries.append(processed_country)
                
                return processed_countries
                
        except httpx.TimeoutException:
            raise Exception("Countries API request timed out")
        except httpx.RequestError as e:
            raise Exception(f"Error fetching countries data: {str(e)}")
        except Exception as e:
            raise Exception(f"Unexpected error fetching countries: {str(e)}")
    
    def _process_country_data(self, country_data: Dict) -> Optional[Dict]:
        """
        Process and normalize country data from the API
        """
        try:
            # Extract currency code - take the first currency if multiple exist
            currency_code = None
            currencies = country_data.get("currencies", [])
            if currencies and len(currencies) > 0:
                # Currencies can be in different formats, handle both
                if isinstance(currencies[0], dict):
                    currency_code = currencies[0].get("code")
                elif isinstance(currencies[0], str):
                    currency_code = currencies[0]
            
            return {
                "name": country_data.get("name", ""),
                "capital": country_data.get("capital"),
                "region": country_data.get("region"),
                "population": country_data.get("population", 0),
                "currency_code": currency_code,
                "flag_url": country_data.get("flag")
            }
            
        except Exception as e:
            print(f"Error processing country {country_data.get('name', 'Unknown')}: {str(e)}")
            return None