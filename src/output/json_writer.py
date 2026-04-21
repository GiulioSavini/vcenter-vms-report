import json
from typing import List

from src.models import VMRecord


def write_json(records: List[VMRecord], path: str) -> None:
    data = [
        {
            "vcenter": r.vcenter,
            "esxi": r.esxi,
            "name": r.name,
            "ip": r.ip,
            "state": r.state,
            "os": r.os,
            "cpu_count": r.cpu_count,
            "memory_mb": r.memory_mb,
            "disk_gb": r.disk_gb,
            "is_template": r.is_template,
            "snapshot_count": r.snapshot_count,
        }
        for r in records
    ]
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
