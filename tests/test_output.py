import json
import tempfile
from src.models import VMRecord
from src.output.csv_writer import write_csv
from src.output.json_writer import write_json
from src.output.html_writer import write_html

SAMPLE = [
    VMRecord(vcenter="vc1", esxi="esxi1", name="vm1", ip="10.0.0.1", state="ON",
             os="Linux", cpu_count=2, memory_mb=4096, disk_gb=50.0, is_template=False, snapshot_count=1),
    VMRecord(vcenter="vc1", esxi="esxi1", name="vm2", ip="N/A", state="OFF",
             os="Windows", cpu_count=4, memory_mb=8192, disk_gb=100.0, is_template=False, snapshot_count=0),
]


def test_write_csv_creates_file():
    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as f:
        path = f.name
    write_csv(SAMPLE, path)
    with open(path, encoding="utf-8") as f:
        content = f.read()
    assert "vCenter" in content
    assert "vm1" in content
    assert ";" in content


def test_write_json_valid():
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
        path = f.name
    write_json(SAMPLE, path)
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    assert len(data) == 2
    assert data[0]["name"] == "vm1"
    assert data[0]["cpu_count"] == 2


def test_write_html_contains_table():
    with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as f:
        path = f.name
    write_html(SAMPLE, path)
    with open(path, encoding="utf-8") as f:
        content = f.read()
    assert "<table" in content
    assert "vm1" in content
    assert "vm2" in content
