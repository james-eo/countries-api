import httpx
import asyncio
from typing import Dict, Optional
from dotenv import load_dotenv
import os

load_dotenv()


class ExchangeRateService:
    """Service to fetch exchange rates from open.er-api.com"""
    
    def __init__(self):
        self.exchange_url = os.getenv("EXCHANGE_API_URL", "https://open.er-api.com/v6/latest/USD")
        self.timeout = 30.0  # 30 seconds timeout
        
    async def fetch_exchange_rates(self) -> Dict[str, float]:
        """
        Fetch exchange rates from the external API
        Returns: Dictionary mapping currency codes to exchange rates
        Raises: httpx.RequestError, httpx.TimeoutException
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(self.exchange_url)
                response.raise_for_status()
                data = response.json()
                
                # Return the rates dictionary
                return data.get("rates", {})
                
        except httpx.TimeoutException:
            raise Exception("Exchange rates API request timed out")
        except httpx.RequestError as e:
            raise Exception(f"Error fetching exchange rates: {str(e)}")
        except Exception as e:
            raise Exception(f"Unexpected error fetching exchange rates: {str(e)}")
    
    async def get_rate_for_currency(self, currency_code: str) -> Optional[float]:
        """
        Get exchange rate for a specific currency
        Returns: Exchange rate or None if not found
        """
        try:
            rates = await self.fetch_exchange_rates()
            return rates.get(currency_code.upper()) if currency_code else None
        except Exception:
            return None