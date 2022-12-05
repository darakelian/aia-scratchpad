#!/usr/bin/env python3
import argparse
import logging
import math
import os
from typing import List
import requests
import sys

from datetime import datetime, timedelta
from models.models import Result, PageInfo, Product

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)


API_ROOT='https://api.dvidshub.net'
SECRET_KEY=os.environ.get('DVIDS_SECRET_KEY')


def make_query_string(**query_args) -> str:
    return '?' + '&'.join([f'{key}={value}' for key, value in query_args.items()])

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--date', type=str, help='Specific date to query (equivalent to --begin <date> and --end <date>)')
    parser.add_argument('--begin', type=str, help='Beginning date to query')
    parser.add_argument('--end', type=str, help='End date to query')
    args = parser.parse_args()
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
    products: List[Product] = []
    while begin_date <= end_date:
        query_string = make_query_string(date=begin_date.strftime('%Y-%m-%dT%H:%M:%SZ'), api_key=SECRET_KEY, short_description_length=300)
        url = f'{API_ROOT}/search{query_string}'
        print('Making request to ' + url)
        result: Result = requests.get(url).json()
        page_info: PageInfo = result['page_info']
        products.extend(result['results'])
        # Check if paged
        num_results = page_info['total_results']
        per_page = page_info['results_per_page']
        # 130 / 50 -> 2.6 (3) pages 1, 2, 3
        if num_results > per_page:
            for page in range(2, math.ceil(float(num_results) / per_page) + 1):
                query_string = make_query_string(date=begin_date.strftime('%Y-%m-%dT%H:%M:%SZ'), api_key=SECRET_KEY, page=page, short_description_length=300)
                url = f'{API_ROOT}/search{query_string}'
                result: Result = requests.get(url).json()
                products.extend(result['results'])
        begin_date += timedelta(days=1)
    print(len(products))


if __name__ == "__main__":
    sys.exit(main())