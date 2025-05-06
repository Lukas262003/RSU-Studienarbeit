import asn1tools
import os

# Pfad zur bereinigten ASN.1-Datei
ivim_asn_path = "Test/IVIM-CLEAN.asn"

# Pfad zur .bin-Datei
encoded_file = "./output/ivim.bin"

# Kompilieren der ASN.1-Spezifikation
asn1_spec = asn1tools.compile_files(ivim_asn_path, codec="uper")

# Einlesen der binären IVIM-Datei
with open(encoded_file, "rb") as f:
    ivim_encoded = f.read()

# Dekodieren
ivim_decoded = asn1_spec.decode("IVIM", ivim_encoded)

# Ausgeben
import json
print(json.dumps(ivim_decoded, indent=2))