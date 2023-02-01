#!/usr/bin/env python
import argparse
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional, Any

import ujson
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from dvids_apps.helpers import make_date_range, get_safe_datetime, path, iso_date, eprint
from dvids_apps.models.db_models import Base, Product, Credit, Location, File


def main() -> int:
    parser = argparse.ArgumentParser()
    data_source_group = parser.add_mutually_exclusive_group(required=True)
    data_source_group.add_argument("--data-dir", type=path,
                                   help="Path containing downloaded DVIDS data (expects folders in YYYYMMDD format)")
    data_source_group.add_argument("--data-zip", type=path,
                                   help="Path to a zip folder containing DVIDS data (expects folders in YYYYMMDD "
                                        "format)")
    parser.add_argument("--output-file", type=path, help="Path to create database at", required=True)
    parser.add_argument("--begin", type=iso_date, help="Begin date to convert (YYYYMMDD format)")
    parser.add_argument("--end", type=iso_date, help="End date to convert (YYYYMMDD format)")
    parser.add_argument("--date", type=iso_date, help="Single date to convert (YYYYMMDD format)")
    args = parser.parse_args()

    # Additional input validation
    if args.date and (args.begin or args.end):
        eprint("Error: cannot specify both --date and one of --begin or --end")
        return 1
    if args.begin and not args.end:
        eprint("Error: must specify --end if --begin is specified")
        return 1

    if args.date:
        begin = args.date
        end = args.date
    else:
        begin = args.begin
        end = args.end

    engine = create_engine(f"sqlite:///{args.output_file}")
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine)

    with session() as session:
        for date in make_date_range(begin, end):
            if args.data_dir:
                path_to_files: Path = args.data_dir.joinpath(date.strftime("%Y%m%d"))
                if not path_to_files.exists():
                    eprint(f"Warning: no path found at {path_to_files}")
                    continue
                for file in path_to_files.iterdir():
                    with open(file, "r", encoding="utf-8") as json_file:
                        try:
                            json_data: dict[str, Any] = ujson.load(json_file)
                        except ujson.JSONDecodeError as e:
                            eprint(f"Unable to load json from {file}")
                            raise e
                        # Construct our objects
                        product = Product(
                            id=json_data.get("id"),
                            branch=json_data.get("branch"),
                            description=json_data.get("description"),
                            keywords=json_data.get("keywords"),
                            date=get_safe_datetime(json_data, "date"),
                            date_published=get_safe_datetime(json_data, "date_published"),
                            image=json_data.get("image"),
                            timestamp=get_safe_datetime(json_data, "timestamp"),
                            title=json_data.get("title"),
                            unit_name=json_data.get("unit_name"),
                            url=json_data.get("url"),
                            virin=json_data.get("virin")
                        )
                        for credit_data in json_data.get("credits", []):
                            credit = Credit(
                                credit_id=credit_data.get("id"),
                                name=credit_data.get("name"),
                                rank=credit_data.get("rank"),
                                url=credit_data.get("url")
                            )
                            product.credits.append(credit)
                        for file_data in json_data.get("files", []):
                            file = File(
                                src=file_data.get("src"),
                                type=file_data.get("type"),
                                height=file_data.get("height"),
                                width=file_data.get("width"),
                                bitrate=file_data.get("bitrate")
                            )
                            product.files.append(file)

                        session.add(product)
                session.commit()


if __name__ == "__main__":
    sys.exit(main())
