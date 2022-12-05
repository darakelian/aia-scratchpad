from datetime import datetime
from typing import List, TypedDict


class PageInfo(TypedDict):
    total_results: int
    results_per_page: int


class Product(TypedDict):
    publishdate: datetime
    date: datetime
    width: int
    height: int
    aspect_ratio: str
    title: str
    id: str
    type: str
    keywords: str
    credit: str
    country: str
    city: str
    unit_name: str
    branch: str
    timestamp: datetime
    short_description: str
    thumbnail: str
    thumbnail_width: int
    thumbnail_height: int
    url: str
    date_published: datetime


class Result(TypedDict):
    page_info: PageInfo
    results: List[Product]
