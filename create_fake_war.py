#!/usr/bin/env python
import argparse
import sys
from collections import defaultdict

from jinja2 import Environment, PackageLoader
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from dvids_apps.helpers import path, iso_date, eprint
from dvids_apps.models.db_models import Product


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--database-path", type=path, required=True,
                        help="Path to SQLite database file to get DVIDS data from")
    parser.add_argument("--date", type=iso_date, required=True,
                        help="Date to select data from. Only one date at a time")
    parser.add_argument("--start", type=int, help="Start index of wars to use")
    parser.add_argument("--end", type=int, help="End index of wars to use")
    args = parser.parse_args()

    if not args.database_path.exists():
        eprint(f"Error: database {args.database_path} does not exist")
        return 1

    engine = create_engine(f"sqlite:///{args.database_path}")
    session = sessionmaker(bind=engine)
    with session() as session:
        descriptions_by_title: dict[str, set[str]] = defaultdict(set)
        instance: Product
        for instance in session.query(Product).filter(Product.date == args.date):
            descriptions_by_title[instance.title].add(instance.description)
        env = Environment(
            loader=PackageLoader("dvids_apps")
        )
        template = env.get_template("war_layout.jinja")
        start = 0
        end = len(descriptions_by_title.items())
        if args.start:
            start = args.start
        if args.end:
            end = args.end
        rendered_wars = [template.render(title=title, entries=items) for title, items
                         in descriptions_by_title.items()]
        for war in rendered_wars[start:end]:
            print(war)

    return 0


if __name__ == "__main__":
    sys.exit(main())
