import asn1tools
import os
import json

# Pfad zur ETSI MAPEM ASN.1 Datei
mapem_asn_path = "Data_files/etsi_mapem_spatem.asn"

# Pfad zur codierten Datei
encoded_file = "./output/mapem.bin"

# Kompilieren
asn1_spec = asn1tools.compile_files(mapem_asn_path, codec="uper")

# Einlesen
with open(encoded_file, "rb") as f:
    mapem_encoded = f.read()

# Dekodieren
mapem_decoded = asn1_spec.decode("MAPEM", mapem_encoded)

# Anzeigen
print(json.dumps(mapem_decoded, indent=2))
