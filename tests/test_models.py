from src.models import VMRecord


def test_vmrecord_defaults():
    vm = VMRecord(vcenter="vc1", esxi="esxi1", name="vm1", ip="1.2.3.4", state="ON")
    assert vm.os == "N/A"
    assert vm.cpu_count == 0
    assert vm.memory_mb == 0
    assert vm.disk_gb == 0.0
    assert vm.is_template is False
    assert vm.snapshot_count == 0


def test_vmrecord_to_row():
    vm = VMRecord(
        vcenter="vc1", esxi="esxi1", name="vm1", ip="1.2.3.4", state="ON",
        os="Linux", cpu_count=4, memory_mb=8192, disk_gb=100.0,
        is_template=False, snapshot_count=2,
    )
    row = vm.to_row()
    assert row == ["vc1", "esxi1", "vm1", "1.2.3.4", "ON", "Linux", 4, 8192, 100.0, False, 2]


def test_vmrecord_sort_key():
    vm = VMRecord(vcenter="VC1", esxi="ESXI1", name="VM1", ip="N/A", state="OFF")
    assert vm.sort_key() == ("vc1", "esxi1", "vm1")
