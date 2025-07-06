# RSU-Studienarbeit

Dieses Repository dient dem Versenden von V2X-Nachrichten (z. B. SPATEM, MAPEM) über DSRC (IEEE 802.11p) mit einer MK5-OBU von Cohda Wireless. Die Nachrichten werden über ein Dashboard konfiguriert, in ein Binärformat konvertiert und anschließend per WLAN-Broadcast ausgesendet.

📁 Projektstruktur

conversion/
Enthält alle Skripte zur Umwandlung von JSON-basierten Szenarien in DSRC-konforme Binärnachrichten (z. B. SPATEM, MAPEM, IVIM).
Beispiel: convert_to_spatem.py, convert_to_mapem.py

dashboard/
Webinterface zur Erstellung, Anzeige und Bearbeitung von Verkehrsszenarien (z. B. Ampelphasen, Straßenverläufe).
Die Dateien dort umfassen HTML-Templates, Flask-Backend und CSS.

data_files/
Sammlung von Beispieldateien im JSON-Format, die typische Szenarien oder Nachrichtenstrukturen abbilden.
Dient der schnellen Erprobung und Konvertierung.

obu_related/
Skripte zur Übertragung und zum Senden der Binärnachrichten an die OBU, z. B. per SSH oder SCP.

Beispiel:

send_to_obu.py – schickt die Nachricht und führt test-tx auf der OBU aus

watch_and_send_polling.py – überwacht Änderungen im Szenario und triggert automatisch das Senden

output/
Enthält die generierten Binärnachrichten (z. B. mapem.bin, ivim.bin), die an die OBU übertragen werden.

## 🖥️ Voraussetzungen

### Hardware

- NUC
- Cohda MK5 OBU
- passende Antenne zum Senden

### Software / Tools

- Linux (empfohlen) oder Windows mit WSL
- Python 3.x
- `scp`, `ssh`, ggf. `sshpass` (bei Linux)
- `Wireshark` zur Paketverifizierung

---

## 🚀 Komplette Einrichtung Schritt für Schritt (Erst-Setup)

### 📡 1. Netzwerkverbindung einrichten

Die Kommunikation zwischen RSU (z. B. Raspberry Pi) und OBU (z. B. Cohda MK5) erfolgt direkt über ein Ethernet-Kabel (kein DHCP). Dafür müssen statische IP-Adressen vergeben werden:

#### Auf dem RSU-Gerät (z. B. Raspberry Pi)

```bash
sudo ip addr add 192.168.101.236/24 dev eth0
```

#### Auf der OBU

```bash
ip addr add 192.168.101.121/24 dev eth0
```

> ⚠️ Je nach Setup kann das Interface auch `enp0s31f6`, `eth1`, etc. heißen – prüfbar mit `ip a`.

---

### 🗃️ 2. OBU vorbereiten – Skripte und Tools übertragen

Folgende Dateien müssen auf die OBU kopiert werden (z. B. ins Verzeichnis `/root/send_dsrc/`):

- `test-tx` → ausführbares Binary zum Senden der Nachricht
- `message.bin` → erzeugte V2X-Nachricht im Binärformat
- `watch_and_send_polling.sh` → optionales Skript zum automatisierten Versand

```bash
scp ./test-tx root@192.168.101.121:/root/send_dsrc/
scp ./out/message.bin root@192.168.101.121:/root/send_dsrc/
```

Anschließend auf der OBU:

```bash
chmod +x /root/send_dsrc/test-tx
```

---

### 📤 3. Nachricht per OBU senden

SSH-Verbindung aufbauen:

```bash
ssh root@192.168.101.121
```

Dann Nachricht senden:

```bash
/root/send_dsrc/test-tx /root/send_dsrc/message.bin
```

> Alternativ kannst du das automatisch über `send_to_obu.py` vom PC aus erledigen.

---

### 📁 Empfohlene Ordnerstruktur auf der OBU

```
/root/send_dsrc/
├── test-tx
├── message.bin
└── watch_and_send.sh
```

---

## ⚠️ Besonderheiten unter Windows

Falls du unter **Windows** arbeitest:

- In `send_to_obu.py` muss `sshpass` auskommentiert werden (ca. Zeile 18), da nicht Windows-kompatibel.
- Nutze alternativ `watch_and_send_polling.py`, das lokal die Dateiänderungen überwacht.
- Stelle sicher, dass dein Windows-System Zugriff auf das Netzwerk-Interface zur OBU hat.

---

## 🧪 Testing & Debugging

- Nutze `Wireshark`, um SPATEM/MAPEM-Nachrichten live auf der RSU oder der OBU mitzuschneiden und zu analysieren.

---


