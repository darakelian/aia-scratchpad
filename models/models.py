from datetime import datetime
from typing import TypedDict, Optional, Union, List


class PageInfo(TypedDict):
    total_results: int
    results_per_page: int


class Product(TypedDict):
    publishdate: Optional[datetime]
    date: datetime
    width: Optional[int]
    height: Optional[int]
    aspect_ratio: Optional[str]
    title: str
    id: str
    type: Optional[str]
    keywords: Optional[str]
    credit: Optional[str]
    country: Optional[str]
    city: Optional[str]
    unit_name: Optional[str]
    branch: Optional[str]
    timestamp: datetime
    short_description: Optional[str]
    thumbnail: Optional[str]
    thumbnail_width: Optional[int]
    thumbnail_height: Optional[int]
    url: Optional[str]
    date_published: datetime


class ResolvedProduct(TypedDict):
    id: str
    title: str
    description: str
    keywords: Optional[str]
    date_published: datetime
    unit_name: Optional[str]


class SearchResponse(TypedDict):
    page_info: PageInfo
    results: List[Product]


class AssetResponse(TypedDict):
    results: ResolvedProduct


class Error(TypedDict):
    errors: List[str]
