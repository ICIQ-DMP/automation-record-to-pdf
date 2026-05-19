#!/usr/bin/env python3
"""
Convert automation records from MS List to PDF.

Data source (current): manually exported CSV from MS List.
Data source (future):  MS SharePoint / Graph API (see SharePointDataSource).

Usage examples:
    python main.py --id 1
    python main.py --id 2
    python main.py --row 0
    python main.py --all
    python main.py --all --output /tmp/pdfs
    python main.py --id 1 --file "input/Template Automatització.csv"
"""

import argparse
import sys
from pathlib import Path

from src.data_sources.csv_source import CSVDataSource
from src.transformers.ms_list_transformer import MSListTransformer
from src.renderers.pdf_renderer import PDFRenderer

DEFAULT_CSV = Path("input/Template Automatització.csv")
DEFAULT_OUTPUT = Path("output")


def _build_filename(record) -> str:
    """Derive an output filename from the record's ID and automation name."""
    name_slug = (
        record.automation_name
        .lower()
        .replace(" ", "_")
        .replace("/", "-")
    )
    try:
        id_num = int(record.internal_id)
        return f"fitxa_{id_num:02d}_{name_slug}.pdf"
    except ValueError:
        return f"fitxa_{name_slug}.pdf"


def _process(raw_records, transformer, renderer, output_dir):
    generated = []
    for raw in raw_records:
        record = transformer.transform(raw)
        filename = _build_filename(record)
        output_path = output_dir / filename
        result = renderer.render(record, output_path)
        print(f"  Generated: {result}")
        generated.append(result)
    return generated


def main():
    parser = argparse.ArgumentParser(
        description="Convert MS List automation records to PDF",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--source",
        choices=["csv"],
        default="csv",
        help="Data source type (default: csv; 'sharepoint' coming soon)",
    )
    parser.add_argument(
        "--file",
        type=Path,
        default=DEFAULT_CSV,
        metavar="PATH",
        help=f"CSV file path (default: {DEFAULT_CSV})",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        metavar="DIR",
        help=f"Output directory (default: {DEFAULT_OUTPUT})",
    )

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--id",
        metavar="ID",
        help="Select record by 'ID intern' value (e.g. --id 1)",
    )
    group.add_argument(
        "--row",
        type=int,
        metavar="N",
        help="Select record by 0-based row index (e.g. --row 0)",
    )
    group.add_argument(
        "--all",
        action="store_true",
        help="Convert every record in the source",
    )

    args = parser.parse_args()

    output_dir = args.output
    output_dir.mkdir(parents=True, exist_ok=True)

    source = CSVDataSource(args.file)
    transformer = MSListTransformer()
    renderer = PDFRenderer()

    try:
        if args.all:
            raw_records = source.fetch_all()
            print(f"Converting {len(raw_records)} record(s)…")
        elif args.id is not None:
            raw_records = [source.fetch_by_id(args.id)]
            print(f"Converting record with ID intern '{args.id}'…")
        else:
            raw_records = [source.fetch_by_index(args.row)]
            print(f"Converting row {args.row}…")
    except (ValueError, IndexError, FileNotFoundError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    _process(raw_records, transformer, renderer, output_dir)
    print("Done.")


if __name__ == "__main__":
    main()
