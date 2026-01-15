import httpx
from datetime import datetime, timedelta
from typing import Optional
import os


class PriceService:
    """Service to fetch current spot prices for precious metals."""

    def __init__(self):
        self._cache: Optional[dict] = None
        self._cache_time: Optional[datetime] = None
        self._cache_duration = timedelta(minutes=30)  # Cache for 30 min to reduce API calls
        self._rate_limited_until: Optional[datetime] = None

    async def get_spot_prices(self) -> dict:
        """
        Get current spot prices for gold, silver, platinum, and palladium.
        Uses caching to avoid excessive API calls.
        """
        # Return cached prices if still valid
        if self._cache and self._cache_time:
            if datetime.now() - self._cache_time < self._cache_duration:
                return self._cache

        # Check if we're rate limited
        if self._rate_limited_until and datetime.now() < self._rate_limited_until:
            print(f"Rate limited until {self._rate_limited_until}, using cached/fallback prices")
            if self._cache:
                return self._cache
            return self._get_fallback_prices()

        # Try to fetch from API
        prices = await self._fetch_from_api()

        if prices:
            self._cache = prices
            self._cache_time = datetime.now()
            self._rate_limited_until = None  # Clear rate limit on success
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
        goldapi_key = os.getenv("GOLDAPI_KEY")
        if goldapi_key:
            prices = await self._fetch_from_goldapi(goldapi_key)
            if prices:
                return prices

        # Try Metals-API as fallback
        metals_api_key = os.getenv("METALS_API_KEY")
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
                    elif response.status_code == 429:
                        # Rate limited - back off for 1 hour
                        print(f"GoldAPI rate limited (429). Backing off for 1 hour.")
                        self._rate_limited_until = datetime.now() + timedelta(hours=1)
                        return None
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
                        "symbols": "XAU,XAG"
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
                            "updated_at": datetime.now()
                        }
        except Exception as e:
            print(f"Error fetching from Metals-API: {e}")

        return None

    def _get_fallback_prices(self) -> dict:
        """
        Fallback prices when API is unavailable or rate limited.
        These are approximate values - live prices will be used when available.
        """
        return {
            "gold": 2650.00,
            "silver": 30.00,
            "updated_at": datetime.now(),
            "is_fallback": True
        }


# Global instance
price_service = PriceService()
