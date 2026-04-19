from decimal import Decimal
from typing import Dict, Tuple
import aiohttp
import requests

from app.enum import CurrencyEnum

FALLBACK_RATES: Dict[Tuple[str, str], Decimal] = {
    (CurrencyEnum.USD, CurrencyEnum.RUB): Decimal(str(95.0)),
    (CurrencyEnum.USD, CurrencyEnum.EUR): Decimal(str(0.92)),
    (CurrencyEnum.EUR, CurrencyEnum.RUB): Decimal(str(103.26)),
    (CurrencyEnum.RUB, CurrencyEnum.USD): Decimal(str(0.0105)),
    (CurrencyEnum.EUR, CurrencyEnum.USD): Decimal(str(1.087)),
    (CurrencyEnum.RUB, CurrencyEnum.EUR): Decimal(str(0.0097)),
}



async def get_exchange_rate(base: CurrencyEnum, target: CurrencyEnum) -> Decimal:
    url = f"https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@latest/v1/currencies/{base}.json"

    timeout = aiohttp.ClientTimeout(total=5.0)
    try:
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url) as response:
                # raise_for_status() отбрасывает exception если код не 200
                response.raise_for_status()
                data = await response.json()
                base_map = data.get(base, {})
                rate = base_map.get(target)

        if rate is not None and isinstance(rate, (int, float)):
            return Decimal(rate)
        raise KeyError("Rate was not found")

    except Exception:
        # Если не найден курс валют, то возвращается 1
        return FALLBACK_RATES.get((base, target), Decimal(1))