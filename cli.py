from __future__ import annotations

import argparse

import pandas as pd

from src.database import bootstrap_demo, connect, initialize, load_frame
from src.importers import read_csv
from src.scraping.jsonld import JsonLdJobScraper
from src.settings import DEMO_DATA_PATH


def main() -> None:
    parser = argparse.ArgumentParser(description="Tunisia Job-Market data operations")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("init", help="Create the DuckDB database and load demo data")
    importer = commands.add_parser("import", help="Import a permitted/manual CSV")
    importer.add_argument("path")
    scrape = commands.add_parser("scrape-url", help="Collect JobPosting JSON-LD from one permitted URL")
    scrape.add_argument("url")
    args = parser.parse_args()

    con = connect()
    initialize(con)
    if args.command == "init":
        count = bootstrap_demo(con, DEMO_DATA_PATH)
        print(f"Database ready; {count} demo rows loaded.")
    elif args.command == "import":
        print(f"Loaded {load_frame(con, read_csv(args.path))} rows.")
    elif args.command == "scrape-url":
        records = JsonLdJobScraper(args.url).collect(args.url)
        frame = pd.DataFrame([record.to_dict() for record in records])
        count = load_frame(con, frame) if not frame.empty else 0
        print(f"Loaded {count} rows.")


if __name__ == "__main__":
    main()
