from typing import List

from src.models import VMRecord

_TEMPLATE = """<!DOCTYPE html>
<html lang="it">
<head>
<meta charset="UTF-8">
<title>VM Report</title>
<style>
  body {{ font-family: sans-serif; margin: 2rem; }}
  h1 {{ color: #333; }}
  table {{ border-collapse: collapse; width: 100%; font-size: 0.9rem; }}
  th {{ background: #2c3e50; color: white; padding: 8px 12px; text-align: left; }}
  td {{ padding: 6px 12px; border-bottom: 1px solid #ddd; }}
  tr:nth-child(even) {{ background: #f5f5f5; }}
  .on {{ color: #27ae60; font-weight: bold; }}
  .off {{ color: #e74c3c; }}
  .summary {{ margin-bottom: 1rem; color: #555; }}
</style>
</head>
<body>
<h1>vCenter VM Report</h1>
<p class="summary">Totale: {total} VM &mdash; Accese: {on_count} &mdash; Spente: {off_count}</p>
<table>
<thead><tr>
  <th>vCenter</th><th>ESXi</th><th>Nome VM</th><th>IP</th><th>Stato</th>
  <th>OS</th><th>CPU</th><th>RAM (MB)</th><th>Disk (GB)</th><th>Template</th><th>Snapshot</th>
</tr></thead>
<tbody>
{rows}
</tbody>
</table>
</body>
</html>"""


def _row_html(r: VMRecord) -> str:
    state_cls = "on" if r.state == "ON" else "off"
    return (
        f"<tr>"
        f"<td>{r.vcenter}</td><td>{r.esxi}</td><td>{r.name}</td>"
        f"<td>{r.ip}</td><td class='{state_cls}'>{r.state}</td>"
        f"<td>{r.os}</td><td>{r.cpu_count}</td><td>{r.memory_mb}</td>"
        f"<td>{r.disk_gb}</td><td>{'Yes' if r.is_template else 'No'}</td>"
        f"<td>{r.snapshot_count}</td>"
        f"</tr>"
    )


def write_html(records: List[VMRecord], path: str) -> None:
    rows_html = "\n".join(_row_html(r) for r in records)
    on_count = sum(1 for r in records if r.state == "ON")
    html = _TEMPLATE.format(
        total=len(records),
        on_count=on_count,
        off_count=len(records) - on_count,
        rows=rows_html,
    )
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
