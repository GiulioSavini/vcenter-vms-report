# vcenter_vms.py

**Tool Python** per estrarre un report completo di **tutte le VM** da una lista di vCenter server. Produce un file CSV con vCenter, host ESXi, nome VM, IP e stato (ON/OFF).

---

## Panoramica

Lo script:

1. Legge una lista di vCenter da un file di testo
2. Si connette a ciascun vCenter tramite pyVmomi
3. Raccoglie tutte le VM con: nome, IP, host ESXi, stato di accensione
4. Produce un file CSV ordinato e una tabella a video

---

## Output

### File CSV (`vm_report.csv`)

```
vCenter;ESXi;Nome_VM;IP_VM;Stato
vcenter1.example.com;esxi01.example.com;webserver01;192.168.1.100;ON
vcenter1.example.com;esxi01.example.com;dbserver01;192.168.1.101;ON
vcenter2.example.com;esxi03.example.com;testvm01;N/A;OFF
```

### Output a video

```
vCenter                                       ESXi                                Nome_VM                             IP_VM              Stato
----------------------------------------------------------------------------------------------------------------------------------------------------------------
vcenter1.example.com                          esxi01.example.com                  webserver01                         192.168.1.100      ON
```

---

## Requisiti

- **Python 3.6+**
- **pyVmomi** (VMware vSphere API Python Bindings)

```bash
pip3 install pyvmomi
```

### Permessi richiesti

| Componente | Permesso |
|---|---|
| vCenter | Utente read-only con accesso all'inventario (`System.View`, `System.Read`) |

---

## Porte di rete richieste

| Sorgente | Destinazione | Porta | Protocollo | Descrizione |
|---|---|---|---|---|
| Script host | vCenter Server(s) | **443/tcp** | HTTPS | vSphere API (pyVmomi / SOAP) |

---

## Installazione

```bash
# Clona il repository
git clone https://github.com/GiulioSavini/vcenter-vms-report.git
cd vcenter-vms-report

# Installa le dipendenze
pip3 install pyvmomi

# Rendi eseguibile
chmod +x vcenter_vms.py
```

---

## Formato file di input

Il file `vcenters_list.txt` contiene una riga per ogni vCenter:

```
# Formato: hostname_suffix  IP  username  password
# Le righe che iniziano con # sono commenti
# Il suffisso dopo _ nel nome host viene rimosso per il report

vcenter1.example.com_tag    192.168.1.10    <USERNAME>    <PASSWORD>
vcenter2.example.com_tag    192.168.2.10    <USERNAME>    <PASSWORD>
```

| Campo | Descrizione |
|---|---|
| `hostname_suffix` | Nome del vCenter con un suffisso opzionale dopo `_` (viene rimosso nel report) |
| `IP` | Indirizzo IP del vCenter (usato per la connessione) |
| `username` | Username per l'autenticazione (es: `user@vsphere.local`) |
| `password` | Password |

> **ATTENZIONE:** Il file contiene credenziali in chiaro. Proteggerlo con permessi restrittivi (`chmod 600 vcenters_list.txt`).

---

## Sintassi

```bash
./vcenter_vms.py [percorso_file_vcenter_list]
```

| Parametro | Default | Descrizione |
|---|---|---|
| `percorso_file` | `vcenters_list.txt` | Percorso al file con la lista dei vCenter |

---

## Esempi di utilizzo

### Uso con file default

```bash
./vcenter_vms.py
```

### Uso con file personalizzato

```bash
./vcenter_vms.py /path/to/my_vcenters.txt
```

### Output tipico

```
Leggo lista vCenter da: vcenters_list.txt
Trovati 3 vCenter

Processo: vcenter1.example.com
  [OK] Connesso a vcenter1.example.com (192.168.1.10)
       Trovate 45 VM

Processo: vcenter2.example.com
  [OK] Connesso a vcenter2.example.com (192.168.2.10)
       Trovate 30 VM

--- Report salvato in vm_report.csv ---
Totale VM: 75
  Accese: 60  |  Spente: 15
```

---

## Dettagli tecnici

### Architettura dello script

```
vcenter_vms.py
├── parse_vcenter_list()     # Parsing file di input (hostname, IP, credenziali)
├── get_all_vms()            # ContainerView su VirtualMachine
├── get_vm_ip()              # Primo IPv4 da guest.ipAddress o guest.net
├── get_esxi_host()          # runtime.host.name
├── collect_from_vcenter()   # Connessione + raccolta dati per un singolo vCenter
└── main()
    ├── Parsing file input
    ├── Loop su ogni vCenter
    ├── Ordinamento per vCenter > ESXi > VM name
    ├── Scrittura CSV (separatore ;)
    └── Stampa tabella a video
```

### Gestione IP della VM

Lo script prova a ottenere l'IP della VM in quest'ordine:
1. `vm.guest.ipAddress` (IP primario riportato dal VMware Tools)
2. `vm.guest.net[].ipAddress` (scansione di tutte le NIC, primo IPv4 trovato)
3. Se la VM e' spenta → `N/A`

> **Nota:** L'IP viene riportato solo se VMware Tools e' installato e in esecuzione sulla VM.

### Formato CSV

- Separatore: `;` (punto e virgola) - compatibile con Excel in localizzazioni europee
- Encoding: UTF-8
- Header: `vCenter;ESXi;Nome_VM;IP_VM;Stato`

---

## File di esempio

### vcenters_list.txt

```
# Lista vCenter per il report VM
# Formato: hostname_suffix  IP  username  password

vcenter-prod.example.com_dc1    192.168.1.10    <USERNAME>    <PASSWORD>
vcenter-dr.example.com_dc2      192.168.2.10    <USERNAME>    <PASSWORD>
```

---

## Licenza

MIT License
