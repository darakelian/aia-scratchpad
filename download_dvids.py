#!/usr/bin/env python
import argparse
import asyncio
import json.decoder
import logging
import math
import os
from pathlib import Path
from typing import cast, Iterator, Union
import httpx
import sys

from datetime import datetime, timedelta

import ujson

from dvids_apps.helpers import make_date_range
from dvids_apps.models.api_models import SearchResponse, PageInfo, Product, ResolvedProduct, Error, AssetResponse

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)


API_ROOT = 'https://api.dvidshub.net'
SECRET_KEY = os.environ.get('DVIDS_SECRET_KEY')


def make_query_string(**query_args) -> str:
    return '?' + '&'.join([f'{key}={value}' for key, value in query_args.items()])


def make_page_range(total_results: int, per_page: int) -> Iterator[int]:
    for page in range(2, math.ceil(float(total_results) / per_page) + 1):
        yield page


async def get_response(client: httpx.AsyncClient, url_to_query: str, retry_attempt: int = 0) -> httpx.Response:
    logger.debug('Making request to %s', url_to_query)
    try:
        response = await client.get(url_to_query)
        return response
    except httpx.HTTPError:
        retry_time = 1 + retry_attempt
        logger.warning('Exception thrown for url %s, retrying in %d seconds', url_to_query, retry_time)
        await asyncio.sleep(retry_time)
        return await get_response(client, url_to_query, retry_attempt + 1)


async def get_product_data(client: httpx.AsyncClient, product_id: str) -> Union[ResolvedProduct, Error]:
    query_string = make_query_string(api_key=SECRET_KEY, id=product_id)
    url_to_query = f'{API_ROOT}/asset{query_string}'
    response = await get_response(client, url_to_query)
    if response.status_code >= 400:
        logger.warning('Error with ID %s', product_id)
        try:
            return cast(Error, response.json())
        except json.decoder.JSONDecodeError:
            return {'errors': [f'Error with ID {product_id}']}
    result: AssetResponse = cast(AssetResponse, response.json())
    return result['results']


async def get_page_date(client: httpx.AsyncClient, date: datetime, page: int) -> Union[Error, tuple[PageInfo, list[Product]]]:
    end_date = date + timedelta(hours=23, minutes=59, seconds=59)
    query_string = make_query_string(from_publishdate=date.isoformat(),
                                     to_publishdate=end_date.isoformat(),
                                     api_key=SECRET_KEY, short_description_length=300, page=page)
    url_to_query = f'{API_ROOT}/search{query_string}'
    response = await get_response(client, url_to_query)
    if response.status_code >= 400:
        logger.warning('Error getting page data for date %s, page %d', date, page)
        return cast(Error, response.json())
    result: SearchResponse = cast(SearchResponse, response.json())
    results: list[Product] = result['results']
    return result['page_info'], results


def valid_product(product: Product) -> bool:
    return 'graphics' not in product['id'] and 'publication_issue' not in product['id']


async def get_date_data(date: datetime) -> list[ResolvedProduct]:
    logger.info('Getting data for date %s', date)
    products_to_query: list[Product] = []
    client: httpx.AsyncClient
    async with httpx.AsyncClient() as client:
        # Need to make one request first serially and then can get the rest parallel
        initial_page_info, initial_results = await get_page_date(client, date, 1)
        total_results = initial_page_info['total_results']
        per_page = initial_page_info['results_per_page']
        products_to_query.extend(initial_results)
        if total_results > per_page:
            # Need to paginate
            page_results = await asyncio.gather(
                *[get_page_date(client, date, page) for page in make_page_range(total_results, per_page)]
            )
            for _, results in page_results:
                products_to_query.extend(results)
        resolved_products = await asyncio.gather(
            *[get_product_data(client, product['id']) for product in products_to_query if valid_product(product)]
        )
        valid_products = [product for product in resolved_products if 'id' in product]
        return cast(list[ResolvedProduct], valid_products)


def save_data(output_dir: str, date_saving: datetime, products_to_save: list[ResolvedProduct]) -> None:
    date_folder = datetime.strftime(date_saving, '%Y%m%d')
    parent_folder = Path(output_dir).joinpath(date_folder)
    if not parent_folder.exists() and len(products_to_save) > 0:
        parent_folder.mkdir(parents=True)
    for product in products_to_save:
        output_path = parent_folder.joinpath(f"{product['id'].replace(':', '_')}.json")
        with open(output_path, 'w+', encoding='utf-8') \
                as output_file:
            output_file.write(ujson.dumps(product))


async def async_main(args) -> int:
    begin_date_str = args.begin
    end_date_str = args.end
    date_str = args.date
    if date_str and (begin_date_str or end_date_str):
        logger.error('Cannot specify --date AND --begin or --end')
        return 1
    if date_str:
        begin_date_str = date_str
        end_date_str = date_str
    begin_date = datetime.strptime(begin_date_str, '%Y%m%d')
    end_date = datetime.strptime(end_date_str, '%Y%m%d')
    for date_to_query in make_date_range(begin_date, end_date):
        products_for_date = await get_date_data(date_to_query)
        save_data(args.output_dir, date_to_query, products_for_date)
        await asyncio.sleep(5)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--date', type=str, help='Specific date to query (equivalent to --begin <date> and --end '
                                                 '<date>)')
    parser.add_argument('--begin', type=str, help='Beginning date to query')
    parser.add_argument('--end', type=str, help='End date to query')
    parser.add_argument('--output-dir', type=str, help='Path to save output data to')
    args = parser.parse_args()

    sys.exit(asyncio.run(async_main(args)))


if __name__ == "__main__":
    main()
