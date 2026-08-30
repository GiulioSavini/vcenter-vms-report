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


# --- identity -----------------------------------------------------------------

def test_a_vm_is_identified_by_vcenter_and_name_together():
    # The same VM name in two vCenters is two different machines. Keying on
    # name alone would report a move between vCenters as "no change".
    old = [_vm("vm1", vcenter="vc1")]
    new = [_vm("vm1", vcenter="vc2")]
    result = compute_diff(old, new)
    assert [vm.vcenter for vm in result.added] == ["vc2"]
    assert [vm.vcenter for vm in result.removed] == ["vc1"]
    assert result.changed == []


def test_an_empty_previous_run_reports_everything_as_added():
    result = compute_diff([], [_vm("vm1"), _vm("vm2")])
    assert len(result.added) == 2
    assert result.removed == []


def test_an_empty_new_run_reports_everything_as_removed():
    # A collector failure that returns nothing must not read as "all fine".
    result = compute_diff([_vm("vm1"), _vm("vm2")], [])
    assert len(result.removed) == 2
    assert result.added == []


# --- summary ------------------------------------------------------------------

def test_summary_counts_each_category():
    old = [_vm("gone"), _vm("stays", state="ON")]
    new = [_vm("stays", state="OFF"), _vm("fresh")]
    summary = compute_diff(old, new).summary()
    assert summary.splitlines()[0] == "Delta: +1 added, -1 removed, ~1 changed"


def test_summary_marks_each_line_by_kind():
    old = [_vm("gone")]
    new = [_vm("fresh")]
    lines = compute_diff(old, new).summary().splitlines()
    assert "  [+] vc1 / fresh" in lines
    assert "  [-] vc1 / gone" in lines


def test_summary_names_every_field_that_changed():
    old = [_vm("vm1", state="ON", ip="10.0.0.1")]
    new = [_vm("vm1", state="OFF", ip="10.0.0.2")]
    line = compute_diff(old, new).summary().splitlines()[-1]
    assert line.startswith("  [~] vc1 / vm1: ")
    assert "state: 'ON' → 'OFF'" in line
    assert "ip: '10.0.0.1' → '10.0.0.2'" in line


def test_summary_reports_numeric_fields_too():
    old = [_vm("vm1")]
    new = [_vm("vm1")]
    new[0].cpu_count = 4
    new[0].memory_mb = 8192
    line = compute_diff(old, new).summary().splitlines()[-1]
    assert "cpu_count: 0 → 4" in line
    assert "memory_mb: 0 → 8192" in line


def test_summary_of_no_changes_is_just_the_header():
    summary = compute_diff([_vm("vm1")], [_vm("vm1")]).summary()
    assert summary == "Delta: +0 added, -0 removed, ~0 changed"


def test_every_compared_field_is_also_reported():
    # A field compared by VMRecord equality but missing from summary's field
    # loop produces a VM reported as changed with nothing shown beside it.
    # This asserts the two lists stay in step.
    for attr, value in [
        ("state", "OFF"), ("ip", "10.9.9.9"), ("esxi", "esxi2"), ("os", "Debian"),
        ("cpu_count", 8), ("memory_mb", 4096), ("disk_gb", 120.5),
        ("is_template", True), ("snapshot_count", 3),
    ]:
        old = [_vm("vm1")]
        new = [_vm("vm1")]
        setattr(new[0], attr, value)
        result = compute_diff(old, new)
        assert len(result.changed) == 1, f"{attr} was not detected as a change"
        line = result.summary().splitlines()[-1]
        assert attr in line, f"{attr} changed but summary did not mention it: {line!r}"
