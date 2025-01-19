from fastapi import FastAPI, Query, Header
from typing import Optional
import uvicorn

from auth_handler import authenticate
from constants import MIN_LIMIT, MAX_LIMIT, SCRAPED_DATA_FILE
from model.scraper_config import ScraperConfig
from utility.db_util import LocalStorage
from utility.scraper_util import Scraper


app = FastAPI()


@app.get("/scrape/")
def scrape(
    pages: int = Query(1, ge=MIN_LIMIT, le=MAX_LIMIT),
    proxy: Optional[str] = Query(None),
    retry: int = Query(3, ge=1),
    authorization: str = Header(...)
):
    authenticate(authorization)
    config = ScraperConfig(limit_pages=pages, proxy=proxy, retry_attempts=retry)
    scraper = Scraper(config)
    scraped_products = scraper.scrape()

    # Save data in the scraped_data.json file
    output_file = scraper.data_dir / SCRAPED_DATA_FILE
    local_storage = LocalStorage(output_file)
    local_storage.persist_data(scraped_products)

    print("finished scraping")
    # notify with API response
    return {"message": "Scraping complete", "updated_products_scraped": len(scraped_products)}


if __name__=="__main__":
    uvicorn.run(app)