import json
import asn1tools
import os

# Verwende bereinigte ETSI ASN.1 Datei
ivim_asn_path = "Test/IVIM-CLEAN.asn"

# Kompilieren der ASN.1-Spezifikation
asn1_spec = asn1tools.compile_files(ivim_asn_path, codec="uper")

# Einlesen der Infrastruktur-Daten aus der JSON-Datei
with open("Data_files/road_infrastructure_data.json", "r") as f:
    infra_data = json.load(f)

# Hilfsfunktion: GPS -> DSRC Koordinaten (WGS84 scaled integer)
def convert_gps(lat, lon):
    return int(lat * 1e7), int(lon * 1e7)

# Hilfsfunktion: Erzeuge IVIM-Nachricht aus Einschränkungen (minimal)
def build_ivim(restrictions):
    ivi_container_list = []
    container_id = 0

    for r in restrictions:
        if not r["type"].startswith("Tempo"):
            continue

        lat, lon = convert_gps(r["lat"], r["lon"])

        ivi = {
            "stationID": 1234,
            "messageID": 6,
            "iviIdentification": {
                "countryCode": 276,
                "providerIdentifier": 42,
                "messageID": container_id
            },
            "validityDuration": 300,
            "iviStatus": 0,
            "iviPurpose": 0,
            "applicablePosition": {
                "point": {
                    "latitude": lat,
                    "longitude": lon
                }
            },
            "signList": [{
                "iviType": 1,
                "trafficSigns": [{
                    "trafficSignPictogram": 274,
                    "trafficSignValue": r.get("speed", 30)
                }]
            }]
        }

        ivi_container_list.append(ivi)
        container_id += 1

    return {
        "ivimHeader": {
            "protocolVersion": 1,
            "messageID": 6,
            "generationDeltaTime": 0,
            "stationID": 1234
        },
        "iviContainerList": ivi_container_list
    }

# IVIM-Nachricht erzeugen
ivim_msg = build_ivim(infra_data["restrictions"])

# Kodieren
ivim_encoded = asn1_spec.encode("IVIM", ivim_msg)

# Speichern
output_dir = "./output"
os.makedirs(output_dir, exist_ok=True)
with open(os.path.join(output_dir, "ivim.bin"), "wb") as f:
    f.write(ivim_encoded)

print("IVIM wurde erfolgreich erzeugt.")