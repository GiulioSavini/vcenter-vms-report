#!/usr/bin/env python3
"""
vcenter-vms-report — CLI entry point.

Usage:
  python main.py [options]

Examples:
  python main.py --format html --output report.html
  python main.py --format json --only-on
  python main.py --diff previous_report.json
  python main.py --list vcenters_list.txt --workers 8
"""

import argparse
import json
import logging
import sys

from src.config import load_vcenter_list
from src.collector import collect_all
from src.diff import compute_diff
from src.models import VMRecord
from src.output.csv_writer import write_csv
from src.output.json_writer import write_json
from src.output.html_writer import write_html


def setup_logging(verbose: bool) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%H:%M:%S",
        level=level,
    )


def load_previous(path: str):
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    return [VMRecord(**item) for item in data]


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Extract a full VM inventory from one or more vCenter servers.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("--list", default="vcenters_list.txt",
                   help="Path to vcenters list file (default: vcenters_list.txt)")
    p.add_argument("--format", choices=["csv", "json", "html"], default="csv",
                   help="Output format (default: csv)")
    p.add_argument("--output", default=None,
                   help="Output file path (default: vm_report.<format>)")
    p.add_argument("--workers", type=int, default=4,
                   help="Number of parallel workers (default: 4)")
    p.add_argument("--only-on", action="store_true",
                   help="Only include powered-on VMs")
    p.add_argument("--only-off", action="store_true",
                   help="Only include powered-off VMs")
    p.add_argument("--no-templates", action="store_true",
                   help="Exclude VM templates from output")
    p.add_argument("--diff", metavar="PREV_JSON",
                   help="Compare with a previous JSON report and print changelog")
    p.add_argument("--verbose", "-v", action="store_true",
                   help="Enable debug logging")
    return p


def apply_filters(records, args) -> list:
    if args.only_on:
        records = [r for r in records if r.state == "ON"]
    if args.only_off:
        records = [r for r in records if r.state == "OFF"]
    if args.no_templates:
        records = [r for r in records if not r.is_template]
    return records


def write_output(records, fmt: str, path: str) -> None:
    writers = {"csv": write_csv, "json": write_json, "html": write_html}
    writers[fmt](records, path)


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    setup_logging(args.verbose)
    log = logging.getLogger(__name__)

    try:
        entries = load_vcenter_list(args.list)
    except FileNotFoundError:
        log.error("File not found: %s", args.list)
        return 1

    if not entries:
        log.error("No vCenter entries found in %s", args.list)
        return 1

    log.info("Connecting to %d vCenter(s) with %d workers...", len(entries), args.workers)
    records = collect_all(entries, workers=args.workers)
    records = apply_filters(records, args)

    fmt = args.format
    output_path = args.output or f"vm_report.{fmt}"
    write_output(records, fmt, output_path)

    on_count = sum(1 for r in records if r.state == "ON")
    off_count = len(records) - on_count
    log.info("Report saved to %s — Total: %d (ON: %d, OFF: %d)",
             output_path, len(records), on_count, off_count)

    if args.diff:
        try:
            previous = load_previous(args.diff)
            diff = compute_diff(previous, records)
            print("\n" + diff.summary())
        except FileNotFoundError:
            log.error("Previous report not found: %s", args.diff)

    return 0


if __name__ == "__main__":
    sys.exit(main())
