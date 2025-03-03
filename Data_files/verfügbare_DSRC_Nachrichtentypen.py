import json
import asn1tools
import time
import os

# ASN.1 Definition für DSRC
ASN1_SCHEMA = "Data_files/etsi_mapem_spatem.asn"

# ASN.1-Schema kompilieren
dsrc_codec = asn1tools.compile_files(ASN1_SCHEMA, "uper")

print("✅ Verfügbare DSRC-Nachrichtentypen:", list(dsrc_codec.types.keys()))
