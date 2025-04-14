import json
import asn1tools
import os

# Pfad zu deinem geklonten ETSI-Repo anpassen
etsi_repo_path = "C:/Users/lukas/OneDrive/Desktop/Studienarbeit/ETSI TS 130 301/is_ts103301"
etsi = "Data_files/etsi_mapem_spatem.asn"

# Alle ASN.1-Dateien im Repo automatisch einbinden
asn1_files = ([os.path.join(etsi_repo_path, f) for f in os.listdir(etsi_repo_path) if f.endswith(".asn")] +
              [etsi])

# Kompiliere alle gefundenen ASN.1-Dateien
asn1_compiled = asn1tools.compile_files(asn1_files, 'uper')

# Beispielhafte JSON-Daten (könnte aus einer Datei geladen werden)
json_data = {
    "restrictions": [
        {"type": "Baustelle", "lat": 47.657288, "lon": 9.474279},
        {"type": "Spurverengung", "lat": 47.657542, "lon": 9.473396},
        {"type": "Straßensperrung", "lat": 47.657376, "lon": 9.472856},
        {"type": "Tempolimit", "lat": 47.658864, "lon": 9.473592, "speed": 30},
        {"type": "Fahrzeugspezifisches Tempolimit", "lat": 47.657145, "lon": 9.472627, "speed": 20, "vehicle": "LKW"}
    ]
}

# Hilfsfunktion zum Umwandeln von GPS-Koordinaten in DSRC-Format
def convert_gps_to_dsrc(lat, lon):
    return {
        "lat": int(lat * 1e7),  # Umrechnung in Mikrodegrees
        "lon": int(lon * 1e7)
    }

# Erzeuge MAPEM und IVIM Daten
mapem_entries = []
ivim_entries = []

for restriction in json_data["restrictions"]:
    gps_data = convert_gps_to_dsrc(restriction["lat"], restriction["lon"])
    
    if restriction["type"] in ["Baustelle", "Spurverengung", "Straßensperrung"]:
        mapem_entries.append({
            "type": restriction["type"],
            "location": gps_data
        })
    elif restriction["type"] in ["Tempolimit", "Fahrzeugspezifisches Tempolimit"]:
        ivim_entries.append({
            "speedLimit": restriction["speed"],
            "location": gps_data,
            "vehicle": restriction.get("vehicle", "Alle")
        })

# MAPEM-Nachricht formatieren
mapem_message = {
    "header": {"protocolVersion": 2, "messageID": 5, "stationID": 1234},
    "map": {
        "msgIssueRevision": 1,  # Erforderliches Feld für die Revisionsnummer
        "elements": mapem_entries
    }
}

# IVIM-Nachricht formatieren (falls vorhanden)
if ivim_entries:
    ivim_message = {
        "header": {"protocolVersion": 2, "messageID": 6, "stationID": 1234},
        "ivi": {
            "elements": ivim_entries
        }
    }

# Kodieren in binäres Format
mapem_encoded = asn1_compiled.encode('MAPEM', mapem_message)
if ivim_entries:
    ivim_encoded = asn1_compiled.encode('IVIM', ivim_message)

# Speicherung als .bin
output_path = "C:/Users/lukas/OneDrive/Desktop/Studienarbeit/ETSI TS 130 301/output"
os.makedirs(output_path, exist_ok=True)

with open(os.path.join(output_path, "mapem.bin"), "wb") as f:
    f.write(mapem_encoded)
if ivim_entries:
    with open(os.path.join(output_path, "ivim.bin"), "wb") as f:
        f.write(ivim_encoded)

print("MAPEM und IVIM Nachrichten wurden erfolgreich in .bin gespeichert.")