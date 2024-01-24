import aiohttp
import asyncio
import sys
from datetime import datetime, timedelta


class ExchangeRateFetcher:
    API_URL = "https://api.privatbank.ua/p24api/exchange_rates?json&date="

    async def fetch_rates(self, session, date):
        formatted_date = date.strftime("%d.%m.%Y")
        async with session.get(self.API_URL + formatted_date) as response:
            if response.status != 200:
                raise Exception(f"Error fetching data for {formatted_date}: {response.status}")
            data = await response.json()
            return self.extract_rates(data, formatted_date)

    def extract_rates(self, data, date):
        rates = {'EUR': {'sale': None, 'purchase': None}, 'USD': {'sale': None, 'purchase': None}}
        for rate in data.get('exchangeRate', []):
            if rate.get('currency') in rates:
                rates[rate['currency']]['sale'] = rate.get('saleRate')
                rates[rate['currency']]['purchase'] = rate.get('purchaseRate')
        return {date: rates}


async def main(days):
    if days < 1 or days > 10:
        raise ValueError("Number of days should be between 1 and 10")

    fetcher = ExchangeRateFetcher()
    tasks = []
    async with aiohttp.ClientSession() as session:
        for day_offset in range(days):
            date = datetime.now() - timedelta(days=day_offset)
            tasks.append(fetcher.fetch_rates(session, date))

        results = await asyncio.gather(*tasks)
        print(results)


if __name__ == "__main__":
    try:
        days = int(sys.argv[1])
        asyncio.run(main(days))
    except Exception as e:
        print(f"Error: {e}")
