#!/usr/bin/env python3
"""
Estrae tutte le VM da una lista di vCenter letti da vcenters_list.txt
Output: vCenter, ESXi, Nome_VM, IP_VM, Stato (ON/OFF)
"""

import ssl
import csv
import sys
import re
from pyVim.connect import SmartConnect, Disconnect
from pyVmomi import vim


VCENTER_LIST_FILE = "vcenters_list.txt"
OUTPUT_FILE = "vm_report.csv"


def parse_vcenter_list(filepath):
    """
    Parsing del file vcenters_list.txt
    Formato: hostname_suffix  IP  username  password
    Es: vcenter1.example.com_suffix  192.168.1.10  <USERNAME>  <PASSWORD>
    """
    entries = []
    with open(filepath, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = re.split(r'\s+', line)
            if len(parts) < 4:
                print(f"  SKIP riga malformata: {line}")
                continue

            # Il nome host ha un suffisso tipo _suffix, usiamo l'IP per connetterci
            hostname_raw = parts[0]
            # Rimuovi suffisso _suffix (o simili) per avere il nome leggibile
            vcenter_name = re.sub(r'_[^.]+$', '', hostname_raw)
            ip = parts[1]
            username = parts[2]
            password = parts[3]

            entries.append({
                "name": vcenter_name,
                "ip": ip,
                "username": username,
                "password": password,
            })
    return entries


def get_all_vms(content):
    """Restituisce tutte le VM dal vCenter."""
    container = content.viewManager.CreateContainerView(
        content.rootFolder, [vim.VirtualMachine], True
    )
    vms = container.view
    container.Destroy()
    return vms


def get_vm_ip(vm):
    """Restituisce il primo IPv4 della VM o 'N/A'."""
    try:
        if vm.guest and vm.guest.ipAddress:
            return vm.guest.ipAddress
        if vm.guest and vm.guest.net:
            for nic in vm.guest.net:
                if nic.ipAddress:
                    for ip in nic.ipAddress:
                        if ":" not in ip:  # skip IPv6
                            return ip
    except Exception:
        pass
    return "N/A"


def get_esxi_host(vm):
    """Restituisce il nome dell'ESXi host."""
    try:
        if vm.runtime.host:
            return vm.runtime.host.name
    except Exception:
        pass
    return "N/A"


def collect_from_vcenter(entry):
    """Connette al vCenter e raccoglie i dati delle VM."""
    rows = []
    context = ssl._create_unverified_context()
    vcenter_name = entry["name"]

    try:
        si = SmartConnect(
            host=entry["ip"],
            user=entry["username"],
            pwd=entry["password"],
            sslContext=context,
        )
        print(f"  [OK] Connesso a {vcenter_name} ({entry['ip']})")
    except Exception as e:
        print(f"  [ERRORE] {vcenter_name} ({entry['ip']}): {e}")
        return rows

    try:
        content = si.RetrieveContent()
        vms = get_all_vms(content)
        print(f"       Trovate {len(vms)} VM")

        for vm in vms:
            if vm.config is None:
                continue

            stato = "ON" if vm.runtime.powerState == vim.VirtualMachinePowerState.poweredOn else "OFF"
            ip = get_vm_ip(vm) if stato == "ON" else "N/A"
            esxi = get_esxi_host(vm)
            nome = vm.name

            rows.append([vcenter_name, esxi, nome, ip, stato])
    except Exception as e:
        print(f"  [ERRORE] raccolta dati da {vcenter_name}: {e}")
    finally:
        Disconnect(si)

    return rows


def main():
    import warnings
    warnings.warn(
        "vcenter_vms.py is deprecated. Use `python main.py` instead.",
        DeprecationWarning, stacklevel=2,
    )
    listfile = VCENTER_LIST_FILE
    if len(sys.argv) > 1:
        listfile = sys.argv[1]

    print(f"Leggo lista vCenter da: {listfile}")
    entries = parse_vcenter_list(listfile)
    print(f"Trovati {len(entries)} vCenter\n")

    if not entries:
        print("Nessun vCenter trovato nel file.")
        sys.exit(1)

    all_rows = []
    for entry in entries:
        print(f"Processo: {entry['name']}")
        rows = collect_from_vcenter(entry)
        all_rows.extend(rows)
        print()

    # Ordina per vCenter, ESXi, nome VM
    all_rows.sort(key=lambda r: (r[0].lower(), r[1].lower(), r[2].lower()))

    # Scrivi CSV con separatore ;
    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, delimiter=";")
        writer.writerow(["vCenter", "ESXi", "Nome_VM", "IP_VM", "Stato"])
        writer.writerows(all_rows)

    print(f"--- Report salvato in {OUTPUT_FILE} ---")
    print(f"Totale VM: {len(all_rows)}")

    on_count = sum(1 for r in all_rows if r[4] == "ON")
    off_count = sum(1 for r in all_rows if r[4] == "OFF")
    print(f"  Accese: {on_count}  |  Spente: {off_count}")

    # Stampa anche a video
    print(f"\n{'vCenter':<45} {'ESXi':<35} {'Nome_VM':<35} {'IP_VM':<18} {'Stato'}")
    print("-" * 160)
    for r in all_rows:
        print(f"{r[0]:<45} {r[1]:<35} {r[2]:<35} {r[3]:<18} {r[4]}")


if __name__ == "__main__":
    main()
