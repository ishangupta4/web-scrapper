from typing import Optional

from pydantic import BaseModel, Field

from constants import MIN_LIMIT, MAX_LIMIT


class ScrapedProduct(BaseModel):
    product_title: str = Field(...)
    product_price: str = Field(...)
    path_to_image: str = Field(...)

class ScraperConfig(BaseModel):
    limit_pages: int = Field(5, ge=MIN_LIMIT, le=MAX_LIMIT)
    proxy: Optional[str] = Field(None)
    retry_attempts: int = Field(3, ge=MIN_LIMIT)
