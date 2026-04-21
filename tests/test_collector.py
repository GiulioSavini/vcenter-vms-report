from unittest.mock import MagicMock, patch
from src.collector import get_vm_ip, get_esxi_host, get_vm_disk_gb, get_snapshot_count, collect_from_vcenter
from src.config import VCenterConfig
from src.models import VMRecord


def _make_vm(name="vm1", power_state="poweredOn", ip="1.2.3.4", host_name="esxi1",
             os="Linux", cpu=2, mem=4096, is_template=False):
    vm = MagicMock()
    vm.name = name
    vm.config.template = is_template
    vm.config.guestFullName = os
    vm.config.hardware.numCPU = cpu
    vm.config.hardware.memoryMB = mem
    vm.runtime.powerState = power_state
    vm.runtime.host.name = host_name
    vm.guest.ipAddress = ip
    vm.guest.net = []
    vm.snapshot = None
    vm.config.hardware.device = []
    return vm


def test_get_vm_ip_primary():
    vm = _make_vm(ip="10.0.0.1")
    assert get_vm_ip(vm) == "10.0.0.1"


def test_get_vm_ip_fallback_nic():
    vm = _make_vm(ip=None)
    vm.guest.ipAddress = None
    nic = MagicMock()
    nic.ipAddress = ["fe80::1", "10.0.0.2"]
    vm.guest.net = [nic]
    assert get_vm_ip(vm) == "10.0.0.2"


def test_get_esxi_host():
    vm = _make_vm(host_name="esxi01.example.com")
    assert get_esxi_host(vm) == "esxi01.example.com"


def test_get_vm_disk_gb_no_disks():
    vm = _make_vm()
    vm.config.hardware.device = []
    assert get_vm_disk_gb(vm) == 0.0


def test_get_snapshot_count_none():
    vm = _make_vm()
    vm.snapshot = None
    assert get_snapshot_count(vm) == 0


def test_collect_from_vcenter_returns_vmrecords():
    entry = VCenterConfig(name="vc1", ip="1.2.3.4", username="u", password="p")
    vm = _make_vm()
    with patch("src.collector.SmartConnect") as mock_connect, \
         patch("src.collector.Disconnect"), \
         patch("src.collector.ssl._create_unverified_context"):
        si = MagicMock()
        mock_connect.return_value = si
        content = MagicMock()
        si.RetrieveContent.return_value = content
        container = MagicMock()
        content.viewManager.CreateContainerView.return_value = container
        container.view = [vm]
        records = collect_from_vcenter(entry)
    assert len(records) == 1
    assert isinstance(records[0], VMRecord)
    assert records[0].vcenter == "vc1"
