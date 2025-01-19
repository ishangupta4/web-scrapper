import requests

from constants import DEFAulT_FALLBACK_URL, USER_AGENT, HTML_PRODUCT_TITLE_CLASS, HTML_PRICE_AMOUNT_CLASS, \
    HTML_PRODUCT_IMAGE
from model.scraper_config import ScraperConfig, ScrapedProduct

from bs4 import BeautifulSoup
from pathlib import Path
import time
from typing import Optional, List

from utility.cache_util import InMemoryDatabase
import configparser

config = configparser.ConfigParser()
config.read("config.properties")
BASE_URL = config.get("scraper", "base_url", fallback=DEFAulT_FALLBACK_URL)

CACHE = InMemoryDatabase()

class Scraper:
    def __init__(self, config: ScraperConfig):
        self.base_url = BASE_URL
        self.headers = {"User-Agent": USER_AGENT}
        self.proxies = {"http": config.proxy, "https": config.proxy} if config.proxy else None
        self.limit_pages = config.limit_pages
        self.retry_attempts = config.retry_attempts
        self.data_dir = Path("scraped_products")
        self.image_dir = self.data_dir / "images"
        self.image_dir.mkdir(parents=True, exist_ok=True)

    def fetch_page(self, url: str) -> Optional[str]:
        attempts = 0
        while attempts < self.retry_attempts:
            try:
                response = requests.get(url, headers=self.headers, proxies=self.proxies, timeout=10)
                response.raise_for_status()
                return response.text
            except requests.exceptions.RequestException as e:
                attempts += 1
                print(f"Attempt {attempts} failed for URL {url}: {e}")
                if attempts == self.retry_attempts:
                    print(f"Skipping URL {url} after {self.retry_attempts} failed attempts.")
                time.sleep(2)
        return None

    def parse_products(self, page_content: str) -> List[ScrapedProduct]:
        soup = BeautifulSoup(page_content, "html.parser")
        products = soup.select(".product")
        updated_scraped_products = []

        for product in products:
            try:
                title = product.select_one(HTML_PRODUCT_TITLE_CLASS).text.strip()
                price = product.select_one(HTML_PRICE_AMOUNT_CLASS).contents[0].contents[1].text.strip()
                image_url = product.select_one(HTML_PRODUCT_IMAGE)['data-lazy-src']

                # Save image locally
                image_response = requests.get(image_url, headers=self.headers, proxies=self.proxies, timeout=10)
                image_response.raise_for_status()

                image_name = image_url.split("/")[-1]
                image_path = self.image_dir / image_name
                with open(image_path, "wb") as f:
                    f.write(image_response.content)

                # Check cache for updates and add only updated scraped products
                cached_product = CACHE.get(title)
                if cached_product and cached_product["product_price"] == price:
                    continue

                CACHE.set(title, {
                    "product_price": price,
                    "path_to_image": str(image_path)
                })

                updated_scraped_products.append(ScrapedProduct(
                    product_title=title,
                    product_price=price,
                    path_to_image=str(image_path)
                ))
            except Exception as e:
                print(f"Failed to process product: {e}")

        return updated_scraped_products

    def scrape(self) -> List[ScrapedProduct]:
        scraped_products = []

        for page in range(1, self.limit_pages + 1):
            url = self.base_url.format(page)
            page_content = self.fetch_page(url)
            if not page_content:
                continue

            products = self.parse_products(page_content)
            scraped_products.extend(products)

        return scraped_products