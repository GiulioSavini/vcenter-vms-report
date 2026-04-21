import tempfile
from src.config import VCenterConfig, load_vcenter_list


def test_load_vcenter_list_parses_entries():
    content = "vcenter1.example.com_dc1  192.168.1.10  user@vsphere.local  pass123\n"
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write(content)
        path = f.name
    entries = load_vcenter_list(path)
    assert len(entries) == 1
    assert entries[0].name == "vcenter1.example.com"
    assert entries[0].ip == "192.168.1.10"
    assert entries[0].username == "user@vsphere.local"
    assert entries[0].password == "pass123"


def test_load_vcenter_list_skips_comments():
    content = "# comment\n\nvcenter1.example.com_dc1  192.168.1.10  user  pass\n"
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write(content)
        path = f.name
    entries = load_vcenter_list(path)
    assert len(entries) == 1


def test_load_vcenter_list_env_password_override(monkeypatch):
    monkeypatch.setenv("VCENTER_DEFAULT_PASSWORD", "envpass")
    content = "vcenter1.example.com_dc1  192.168.1.10  user  __ENV__\n"
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write(content)
        path = f.name
    entries = load_vcenter_list(path)
    assert entries[0].password == "envpass"


def test_vcenterconfig_dataclass():
    cfg = VCenterConfig(name="vc1", ip="1.2.3.4", username="u", password="p")
    assert cfg.verify_ssl is False
