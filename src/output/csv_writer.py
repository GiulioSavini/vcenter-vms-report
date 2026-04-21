import csv
from typing import List

from src.models import VMRecord

HEADER = ["vCenter", "ESXi", "Nome_VM", "IP_VM", "Stato", "OS", "CPU", "RAM_MB", "Disk_GB", "Is_Template", "Snapshots"]


def write_csv(records: List[VMRecord], path: str) -> None:
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, delimiter=";")
        writer.writerow(HEADER)
        for r in records:
            writer.writerow(r.to_row())
