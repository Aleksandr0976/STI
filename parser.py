import aiohttp
import asyncio
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import re
from urllib.parse import quote

from config import CITIES

class AvitoParser:
    def __init__(self):
        self.ua = UserAgent()
        self.session = None
    
    async def get_session(self):
        if not self.session:
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def close(self):
        if self.session:
            await self.session.close()
    
    def generate_url(self, model_config, city):
        base_url = "https://www.avito.ru/tatarstan/avtomobili"
        params = {
            'make': model_config['make'],
            'model': model_config['model'],
            'pmax': model_config['max_price'],
            's': 104,
            'user': 1,
            'radius': 0,
            'q': quote(f"{city}")
        }
        if model_config['max_mileage']:
            params['max_mileage'] = model_config['max_mileage']
        
        query = '&'.join([f"{k}={v}" for k, v in params.items() if v])
        return f"{base_url}?{query}"
    
    async def parse_listing(self, url):
        session = await self.get_session()
        headers = {'User-Agent': self.ua.random}
        
        try:
            async with session.get(url, headers=headers) as response:
                if response.status != 200:
                    return []
                
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                listings = []
                items = soup.find_all('div', {'data-marker': 'item'})
                
                for item in items:
                    try:
                        listing = await self.parse_item(item)
                        if listing:
                            listings.append(listing)
                    except:
                        continue
                
                return listings
        except:
            return []
    
    async def parse_item(self, item):
        item_id = item.get('data-item-id')
        if not item_id:
            return None
        
        title_elem = item.find('h3', {'itemprop': 'name'})
        title = title_elem.text.strip() if title_elem else 'Нет названия'
        
        price_elem = item.find('span', {'itemprop': 'price'})
        price = 0
        if price_elem:
            price_text = price_elem.get('content', '0')
            price = int(float(price_text))
        
        link_elem = item.find('a', {'data-marker': 'item-title'})
        url = f"https://www.avito.ru{link_elem.get('href')}" if link_elem else ''
        
        mileage = 0
        year = 0
        
        desc_elems = item.find_all('p', {'class': 'styles-MuiBox-root'})
        for elem in desc_elems:
            text = elem.text.strip()
            if 'км' in text:
                numbers = re.findall(r'(\d+)\s*км', text)
                if numbers:
                    mileage = int(numbers[0])
            if 'г.' in text:
                numbers = re.findall(r'(\d{4})\s*г', text)
                if numbers:
                    year = int(numbers[0])
        
        city_elem = item.find('div', {'class': re.compile('.*address.*')})
        city = city_elem.text.strip() if city_elem else 'Татарстан'
        
        return {
            'id': item_id,
            'title': title,
            'price': price,
            'mileage': mileage,
            'year': year,
            'city': city,
            'url': url
        }
    
    async def check_new_listings(self, model_name, model_config):
        all_listings = []
        for city in CITIES:
            url = self.generate_url(model_config, city)
            listings = await self.parse_listing(url)
            for listing in listings:
                listing['model'] = model_name
            all_listings.extend(listings)
            await asyncio.sleep(1)
        return all_listings