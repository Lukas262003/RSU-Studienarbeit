import json
import asn1tools
import os
import glob

# Alle ASN.1-Dateien rekursiv sammeln
asn1_directory = "C:/Users/lukas/OneDrive/Desktop/Studienarbeit/ASN1_Git/ITS_ASN1"
asn1_mapem_files = sorted(glob.glob(os.path.join(asn1_directory, "**", "*.asn"), recursive=True))

print("Gefundene ASN.1-Dateien:")
for file in asn1_mapem_files:
    print(" -", file)

# Nur Dateien behalten, die mit einer gültigen Moduldefinition beginnen
valid_asn1_files = []
print("\nValidierungslog:")
for path in asn1_mapem_files:
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                stripped = line.strip()
                if not stripped or stripped.startswith("--"):
                    continue
                if "DEFINITIONS" in stripped:
                    valid_asn1_files.append(path)
                    print(f"✓ {os.path.basename(path)} enthält DEFINITIONS")
                else:
                    print(f"✗ {os.path.basename(path)} enthält KEINE DEFINITIONS-Zeile")
                break
    except Exception as e:
        print(f"Fehler beim Lesen von {path}: {e}")
        continue

print("\nVerwendete ASN.1-Dateien:")
for file in valid_asn1_files:
    print(" -", file)

# Kompilieren der ASN.1-Spezifikation für MAPEM
try:
    asn1_spec = asn1tools.compile_files(valid_asn1_files, codec="uper")
except Exception as e:
    print("Fehler beim Kompilieren der ASN.1-Dateien:", str(e))
    exit(1)

# JSON-Datei laden
with open("road_infrastructure_data.json", "r") as f:
    data = json.load(f)

# MAPEM-Nachricht zusammenbauen
mapem_msg = {
    "header": {
        "protocolVersion": 1,
        "messageID": 1,
        "stationID": 1234
    },
    "map": {
        "msgIssueRevision": 1,
        "intersections": [
            {
                "id": {"id": 1},
                "revision": 1,
                "refPoint": {
                    "lat": int(data['restrictions'][0]['lat'] * 1e7),
                    "long": int(data['restrictions'][0]['lon'] * 1e7)
                },
                "laneWidth": 300,
                "speedLimits": [],
                "approaches": [],
                "laneSet": [
                    {
                        "laneID": 1,
                        "laneAttributes": {
                            "directionalUse": (b'\x80', 1),
                            "sharedWith": (b'\x00', 1),
                            "laneType": ("vehicle", (b'\x00', 0))
                        },
                        "maneuvers": (b'\x00', 0),
                        "nodeList": ("nodes", [
                            {"delta": ("node-XY1", {"x": 0, "y": 0})}
                        ])
                    }
                ]
            }
        ]
    }
}

# Nachricht kodieren
try:
    mapem_encoded = asn1_spec.encode("MAPEM", mapem_msg)
except Exception as e:
    print("Fehler beim Kodieren der MAPEM-Nachricht:", str(e))
    mapem_encoded = None

# Datei speichern
if mapem_encoded:
    os.makedirs("output", exist_ok=True)
    with open("./output/mapem.bin", "wb") as f:
        f.write(mapem_encoded)
    print("MAPEM erfolgreich kodiert und gespeichert.")
else:
    print("MAPEM konnte nicht kodiert werden.")
