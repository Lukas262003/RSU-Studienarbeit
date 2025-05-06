import json
import asn1tools
import os
import glob

# Pfad zum geklonten is_ts103301-Repo
asn1_directory = "C:/Users/lukas/OneDrive/Desktop/Studienarbeit/asn1/is_ts103301"
asn1_ivim_files = sorted(glob.glob(os.path.join(asn1_directory, "**", "*.asn"), recursive=True))

print("Gefundene ASN.1-Dateien:")
for file in asn1_ivim_files:
    print(" -", file)

# Nur Dateien behalten, die mit einer gültigen Moduldefinition beginnen
valid_asn1_files = []
print("\nValidierungslog:")
for path in asn1_ivim_files:
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

# Kompilieren der ASN.1-Spezifikation für IVIM
try:
    asn1_spec = asn1tools.compile_files(valid_asn1_files, codec="uper")
except Exception as e:
    print("Fehler beim Kompilieren der ASN.1-Dateien:", str(e))
    exit(1)

# JSON-Datei laden
with open("road_infrastructure_data.json", "r") as f:
    data = json.load(f)

# Beispiel-IVIM-Nachricht aus JSON aufbauen
ivim_msg = {
    "ivimHeader": {
        "protocolVersion": 1,
        "messageID": 6,
        "generationDeltaTime": 0,
        "stationID": 1234
    },
    "iviContainerList": []
}

for entry in data.get("restrictions", []):
    container = {
        "stationID": 617,
        "messageID": 3,
        "iviIdentification": {
            "countryCode": 138,
            "providerIdentifier": 21,
            "messageID": 0
        },
        "validityDuration": 150,
        "iviStatus": 0,
        "iviPurpose": 0,
        "applicablePosition": {
            "point": {
                "latitude": int(entry["lat"] * 1e7),
                "longitude": int(entry["lon"] * 1e7)
            }
        },
        "signList": [
            {
                "iviType": 123,
                "trafficSigns": [],
                "trafficRule": {
                    "regulatory": {
                        "type": 1,
                        "value": 50
                    }
                }
            }
        ]
    }
    ivim_msg["iviContainerList"].append(container)

# Nachricht kodieren
try:
    ivim_encoded = asn1_spec.encode("IVIM", ivim_msg)
except Exception as e:
    print("Fehler beim Kodieren der IVIM-Nachricht:", str(e))
    ivim_encoded = None

# Datei speichern
if ivim_encoded:
    os.makedirs("output", exist_ok=True)
    with open("./output/ivim.bin", "wb") as f:
        f.write(ivim_encoded)
    print("IVIM erfolgreich kodiert und gespeichert.")
else:
    print("IVIM konnte nicht kodiert werden.")
