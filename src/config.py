import os
import re
from dataclasses import dataclass
from typing import List

from dotenv import load_dotenv

load_dotenv()


@dataclass
class VCenterConfig:
    name: str
    ip: str
    username: str
    password: str
    verify_ssl: bool = False


def _resolve_value(value: str, env_key: str) -> str:
    """If value is the sentinel __ENV__, read from environment."""
    if value == "__ENV__":
        return os.getenv(env_key, "")
    return value


def load_vcenter_list(filepath: str) -> List[VCenterConfig]:
    entries: List[VCenterConfig] = []
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = re.split(r"\s+", line)
            if len(parts) < 4:
                continue
            hostname_raw, ip, username, password = parts[0], parts[1], parts[2], parts[3]
            vcenter_name = re.sub(r"_[^.]+$", "", hostname_raw)
            username = _resolve_value(username, "VCENTER_DEFAULT_USER")
            password = _resolve_value(password, "VCENTER_DEFAULT_PASSWORD")
            entries.append(VCenterConfig(name=vcenter_name, ip=ip, username=username, password=password))
    return entries
