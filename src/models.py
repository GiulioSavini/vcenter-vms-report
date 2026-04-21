from dataclasses import dataclass, field
from typing import List


@dataclass
class VMRecord:
    vcenter: str
    esxi: str
    name: str
    ip: str
    state: str  # "ON" | "OFF"
    os: str = "N/A"
    cpu_count: int = 0
    memory_mb: int = 0
    disk_gb: float = 0.0
    is_template: bool = False
    snapshot_count: int = 0

    def to_row(self) -> list:
        return [
            self.vcenter, self.esxi, self.name, self.ip, self.state,
            self.os, self.cpu_count, self.memory_mb, self.disk_gb,
            self.is_template, self.snapshot_count,
        ]

    def sort_key(self) -> tuple:
        return (self.vcenter.lower(), self.esxi.lower(), self.name.lower())
