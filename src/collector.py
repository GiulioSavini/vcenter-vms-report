import ssl
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List

from pyVim.connect import SmartConnect, Disconnect
from pyVmomi import vim

from src.config import VCenterConfig
from src.models import VMRecord

logger = logging.getLogger(__name__)


def get_vm_ip(vm) -> str:
    try:
        if vm.guest and vm.guest.ipAddress:
            return vm.guest.ipAddress
        if vm.guest and vm.guest.net:
            for nic in vm.guest.net:
                for ip in (nic.ipAddress or []):
                    if ":" not in ip:
                        return ip
    except Exception:
        pass
    return "N/A"


def get_esxi_host(vm) -> str:
    try:
        if vm.runtime.host:
            return vm.runtime.host.name
    except Exception:
        pass
    return "N/A"


def get_vm_disk_gb(vm) -> float:
    total = 0.0
    try:
        for device in vm.config.hardware.device:
            if isinstance(device, vim.vm.device.VirtualDisk):
                total += device.capacityInKB / (1024 * 1024)
    except Exception:
        pass
    return round(total, 2)


def _count_snapshots(snapshot_tree) -> int:
    count = 0
    for snap in snapshot_tree:
        count += 1
        if snap.childSnapshotList:
            count += _count_snapshots(snap.childSnapshotList)
    return count


def get_snapshot_count(vm) -> int:
    try:
        if vm.snapshot and vm.snapshot.rootSnapshotList:
            return _count_snapshots(vm.snapshot.rootSnapshotList)
    except Exception:
        pass
    return 0


def _get_all_vms(content):
    container = content.viewManager.CreateContainerView(
        content.rootFolder, [vim.VirtualMachine], True
    )
    vms = list(container.view)
    container.Destroy()
    return vms


def collect_from_vcenter(entry: VCenterConfig) -> List[VMRecord]:
    records: List[VMRecord] = []
    context = ssl._create_unverified_context()
    try:
        si = SmartConnect(
            host=entry.ip,
            user=entry.username,
            pwd=entry.password,
            sslContext=context,
        )
        logger.info("Connected to %s (%s)", entry.name, entry.ip)
    except Exception as exc:
        logger.error("Failed to connect to %s (%s): %s", entry.name, entry.ip, exc)
        return records

    try:
        content = si.RetrieveContent()
        vms = _get_all_vms(content)
        logger.info("Found %d VMs on %s", len(vms), entry.name)
        for vm in vms:
            if vm.config is None:
                continue
            is_on = vm.runtime.powerState == vim.VirtualMachinePowerState.poweredOn
            state = "ON" if is_on else "OFF"
            ip = get_vm_ip(vm) if is_on else "N/A"
            records.append(VMRecord(
                vcenter=entry.name,
                esxi=get_esxi_host(vm),
                name=vm.name,
                ip=ip,
                state=state,
                os=getattr(vm.config, "guestFullName", "N/A") or "N/A",
                cpu_count=getattr(vm.config.hardware, "numCPU", 0) or 0,
                memory_mb=getattr(vm.config.hardware, "memoryMB", 0) or 0,
                disk_gb=get_vm_disk_gb(vm),
                is_template=bool(getattr(vm.config, "template", False)),
                snapshot_count=get_snapshot_count(vm),
            ))
    except Exception as exc:
        logger.error("Error collecting from %s: %s", entry.name, exc)
    finally:
        Disconnect(si)
    return records


def collect_all(entries: List[VCenterConfig], workers: int = 4) -> List[VMRecord]:
    all_records: List[VMRecord] = []
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {pool.submit(collect_from_vcenter, e): e for e in entries}
        for future in as_completed(futures):
            entry = futures[future]
            try:
                all_records.extend(future.result())
            except Exception as exc:
                logger.error("Unhandled error for %s: %s", entry.name, exc)
    all_records.sort(key=lambda r: r.sort_key())
    return all_records
