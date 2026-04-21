from src.models import VMRecord
from src.diff import compute_diff, DiffResult


def _vm(name, state="ON", ip="1.2.3.4", vcenter="vc1"):
    return VMRecord(vcenter=vcenter, esxi="esxi1", name=name, ip=ip, state=state)


def test_no_changes():
    old = [_vm("vm1"), _vm("vm2")]
    new = [_vm("vm1"), _vm("vm2")]
    result = compute_diff(old, new)
    assert result.added == []
    assert result.removed == []
    assert result.changed == []


def test_added_vm():
    old = [_vm("vm1")]
    new = [_vm("vm1"), _vm("vm2")]
    result = compute_diff(old, new)
    assert len(result.added) == 1
    assert result.added[0].name == "vm2"


def test_removed_vm():
    old = [_vm("vm1"), _vm("vm2")]
    new = [_vm("vm1")]
    result = compute_diff(old, new)
    assert len(result.removed) == 1
    assert result.removed[0].name == "vm2"


def test_changed_state():
    old = [_vm("vm1", state="ON")]
    new = [_vm("vm1", state="OFF")]
    result = compute_diff(old, new)
    assert len(result.changed) == 1
    assert result.changed[0][0].name == "vm1"
    assert result.changed[0][1].name == "vm1"


def test_diff_result_has_changes_property():
    result = compute_diff([_vm("vm1")], [_vm("vm2")])
    assert result.has_changes is True
