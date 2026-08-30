from dataclasses import dataclass, field
from typing import List, Tuple

from src.models import VMRecord


@dataclass
class DiffResult:
    added: List[VMRecord] = field(default_factory=list)
    removed: List[VMRecord] = field(default_factory=list)
    changed: List[Tuple[VMRecord, VMRecord]] = field(default_factory=list)

    @property
    def has_changes(self) -> bool:
        return bool(self.added or self.removed or self.changed)

    def summary(self) -> str:
        lines = [f"Delta: +{len(self.added)} added, -{len(self.removed)} removed, ~{len(self.changed)} changed"]
        for vm in self.added:
            lines.append(f"  [+] {vm.vcenter} / {vm.name}")
        for vm in self.removed:
            lines.append(f"  [-] {vm.vcenter} / {vm.name}")
        for old, new in self.changed:
            changes = []
            # Every field compared by VMRecord equality must appear here.
            # A field that is compared but not listed produces a VM reported as
            # changed with nothing shown next to it.
            for attr in ("state", "ip", "esxi", "os", "cpu_count", "memory_mb",
                         "disk_gb", "is_template", "snapshot_count"):
                ov, nv = getattr(old, attr), getattr(new, attr)
                if ov != nv:
                    changes.append(f"{attr}: {ov!r} \u2192 {nv!r}")
            lines.append(f"  [~] {new.vcenter} / {new.name}: {', '.join(changes)}")
        return "\n".join(lines)


def compute_diff(old: List[VMRecord], new: List[VMRecord]) -> DiffResult:
    old_index = {(r.vcenter, r.name): r for r in old}
    new_index = {(r.vcenter, r.name): r for r in new}
    result = DiffResult()
    for key, vm in new_index.items():
        if key not in old_index:
            result.added.append(vm)
        else:
            old_vm = old_index[key]
            if old_vm != vm:
                result.changed.append((old_vm, vm))
    for key, vm in old_index.items():
        if key not in new_index:
            result.removed.append(vm)
    return result
