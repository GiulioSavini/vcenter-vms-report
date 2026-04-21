# vcenter-vms-report

**Tool Python** per estrarre un inventario completo di **tutte le VM** da uno o più vCenter server. Produce report in CSV, JSON o HTML con dati estesi (CPU, RAM, disco, OS, snapshot) e supporta il confronto con report precedenti (diff/changelog).

---

## Funzionalità

- **Raccolta parallela** da più vCenter (`ThreadPoolExecutor`)
- **Dati estesi per VM**: nome, IP, ESXi host, stato, OS, CPU, RAM, disco, template, snapshot
- **Multi-formato**: CSV (Excel-friendly con `;`), JSON, HTML con tabella stilizzata
- **Diff/changelog**: confronta due report e mostra VM aggiunte/rimosse/modificate
- **Credenziali sicure**: `.env` o variabili d'ambiente — niente password hardcoded
- **Filtri CLI**: `--only-on`, `--only-off`, `--no-templates`
- **Docker**: container pronto all'uso con volume per input/output
- **GitHub Actions**: esecuzione notturna automatica con upload artifact e test su ogni push

---

## Quickstart

```bash
git clone https://github.com/GiulioSavini/vcenter-vms-report.git
cd vcenter-vms-report
pip install -r requirements.txt

cp .env.example .env                             # inserisci le credenziali default
cp vcenters_list.txt.example vcenters_list.txt   # inserisci i tuoi vCenter

python main.py --format html --output report.html
```

---

## Formato file di input

```
# vcenters_list.txt
# hostname_suffix  IP  username  password
# Usa __ENV__ come sentinel per leggere VCENTER_DEFAULT_PASSWORD da .env

vcenter-prod.example.com_dc1    192.168.1.10    readonly@vsphere.local    __ENV__
vcenter-dr.example.com_dc2      192.168.2.10    readonly@vsphere.local    __ENV__
```

---

## CLI

```
python main.py [opzioni]

--list FILE         File vcenters (default: vcenters_list.txt)
--format FORMAT     csv | json | html (default: csv)
--output FILE       File di output (default: vm_report.<format>)
--workers N         Worker paralleli (default: 4)
--only-on           Solo VM accese
--only-off          Solo VM spente
--no-templates      Escludi i template
--diff PREV.json    Confronta con un report JSON precedente
--verbose, -v       Logging debug
```

### Esempi

```bash
# Report HTML con tutte le VM
python main.py --format html --output report.html

# Solo VM accese, JSON
python main.py --format json --only-on --output on_vms.json

# Changelog rispetto al report precedente
python main.py --format json --output today.json
python main.py --diff yesterday.json --format json --output today.json

# 8 worker paralleli
python main.py --workers 8
```

---

## Docker

```bash
# Metti vcenters_list.txt in ./data/
mkdir data
cp vcenters_list.txt.example data/vcenters_list.txt
# modifica data/vcenters_list.txt con le tue credenziali

docker compose up
# Il report viene scritto in ./data/vm_report.html
```

---

## GitHub Actions

Il workflow `.github/workflows/report.yml`:
- Esegue i **test** ad ogni push e pull request
- Genera il **report** ogni notte alle 02:00 UTC (schedule)
- Permette **esecuzione manuale** con scelta del formato (csv/json/html)
- Carica il report come **artifact** (retention 30 giorni)

**Secrets da configurare nel repo:**

| Secret | Descrizione |
|---|---|
| `VCENTER_LIST` | Contenuto intero del file `vcenters_list.txt` |
| `VCENTER_DEFAULT_USER` | Username vCenter (se usi `__ENV__` nel file) |
| `VCENTER_DEFAULT_PASSWORD` | Password vCenter |

---

## Output

### CSV (`vm_report.csv`)
```
vCenter;ESXi;Nome_VM;IP_VM;Stato;OS;CPU;RAM_MB;Disk_GB;Is_Template;Snapshots
vcenter-prod.example.com;esxi01;webserver01;192.168.1.100;ON;Red Hat Enterprise Linux;4;8192;100.0;False;0
```

### HTML (`vm_report.html`)
Tabella stilizzata con evidenziazione stato ON/OFF e statistiche riassuntive.

### JSON (`vm_report.json`)
Array di oggetti con tutti i campi — ideale per pipeline e diff automatizzati.

---

## Diff / Changelog

```bash
python main.py --format json --output yesterday.json
python main.py --format json --output today.json --diff yesterday.json
```

Output esempio:
```
Delta: +2 added, -1 removed, ~1 changed
  [+] vcenter-prod / newserver01
  [+] vcenter-dr / backupvm02
  [-] vcenter-prod / oldserver99
  [~] vcenter-prod / webserver01: state: 'ON' -> 'OFF'
```

---

## Struttura progetto

```
vcenter-vms-report/
├── main.py                  # Entry point CLI (usa questo)
├── vcenter_vms.py           # Script originale (deprecato)
├── src/
│   ├── config.py            # Parsing vcenters_list.txt + dotenv
│   ├── collector.py         # Raccolta parallela da vCenter (pyVmomi)
│   ├── models.py            # VMRecord dataclass
│   ├── diff.py              # Engine diff tra report
│   └── output/
│       ├── csv_writer.py    # Export CSV
│       ├── json_writer.py   # Export JSON
│       └── html_writer.py   # Export HTML
├── tests/                   # pytest
├── data/                    # Volume Docker (escluso da git)
├── Dockerfile
├── docker-compose.yml
├── .github/workflows/report.yml
├── requirements.txt
└── .env.example
```

---

## Requisiti

- Python 3.9+
- `pyVmomi`, `python-dotenv`
- Accesso read-only al vCenter (`System.View`, `System.Read`)
- Porta **443/tcp** verso i vCenter

---

## Licenza

MIT License
