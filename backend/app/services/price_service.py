import httpx
from datetime import datetime, timedelta
from typing import Optional

from ..utils.secrets import get_secret


class PriceService:
    """Service to fetch current spot prices for precious metals."""

    def __init__(self):
        self._cache: Optional[dict] = None
        self._cache_time: Optional[datetime] = None
        self._cache_duration = timedelta(minutes=5)

    async def get_spot_prices(self) -> dict:
        """
        Get current spot prices for gold, silver, platinum, and palladium.
        Uses caching to avoid excessive API calls.
        """
        # Return cached prices if still valid
        if self._cache and self._cache_time:
            if datetime.now() - self._cache_time < self._cache_duration:
                return self._cache

        # Try to fetch from API
        prices = await self._fetch_from_api()

        if prices:
            self._cache = prices
            self._cache_time = datetime.now()
            return prices

        # Return fallback/cached prices if API fails
        if self._cache:
            return self._cache
        return self._get_fallback_prices()

    async def _fetch_from_api(self) -> Optional[dict]:
        """
        Fetch prices from a metals price API.
        Supports: GoldAPI.io (GOLDAPI_KEY) or Metals-API (METALS_API_KEY)
        """
        # Try GoldAPI.io first (recommended free option)
        goldapi_key = get_secret("GOLDAPI_KEY")
        if goldapi_key:
            prices = await self._fetch_from_goldapi(goldapi_key)
            if prices:
                return prices

        # Try Metals-API as fallback
        metals_api_key = get_secret("METALS_API_KEY")
        if metals_api_key:
            prices = await self._fetch_from_metals_api(metals_api_key)
            if prices:
                return prices

        return None

    async def _fetch_from_goldapi(self, api_key: str) -> Optional[dict]:
        """
        Fetch prices from GoldAPI.io
        Free tier: 300 requests/month
        Sign up at: https://www.goldapi.io/
        """
        metals = {
            "XAU": "gold",
            "XAG": "silver",
            "XPT": "platinum",
            "XPD": "palladium"
        }
        prices = {}

        try:
            async with httpx.AsyncClient() as client:
                for symbol, name in metals.items():
                    response = await client.get(
                        f"https://www.goldapi.io/api/{symbol}/USD",
                        headers={"x-access-token": api_key},
                        timeout=10.0
                    )

                    if response.status_code == 200:
                        data = response.json()
                        prices[name] = data.get("price", 0)
                    else:
                        print(f"GoldAPI error for {symbol}: {response.status_code}")
                        return None

                prices["updated_at"] = datetime.now()
                return prices

        except Exception as e:
            print(f"Error fetching from GoldAPI: {e}")
            return None

    async def _fetch_from_metals_api(self, api_key: str) -> Optional[dict]:
        """
        Fetch prices from Metals-API.com
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://metals-api.com/api/latest",
                    params={
                        "access_key": api_key,
                        "base": "USD",
                        "symbols": "XAU,XAG,XPT,XPD"
                    },
                    timeout=10.0
                )

                if response.status_code == 200:
                    data = response.json()
                    if data.get("success"):
                        rates = data.get("rates", {})
                        # API returns rates as 1/price, need to invert
                        return {
                            "gold": 1 / rates.get("XAU") if rates.get("XAU") else 0,
                            "silver": 1 / rates.get("XAG") if rates.get("XAG") else 0,
                            "platinum": 1 / rates.get("XPT") if rates.get("XPT") else 0,
                            "palladium": 1 / rates.get("XPD") if rates.get("XPD") else 0,
                            "updated_at": datetime.now()
                        }
        except Exception as e:
            print(f"Error fetching from Metals-API: {e}")

        return None

    def _get_fallback_prices(self) -> dict:
        """
        Fallback prices for development/testing when no API key is configured.
        """
        return {
            "gold": 2650.00,
            "silver": 31.50,
            "platinum": 1020.00,
            "palladium": 1050.00,
            "updated_at": datetime.now()
        }


# Global instance
price_service = PriceService()
