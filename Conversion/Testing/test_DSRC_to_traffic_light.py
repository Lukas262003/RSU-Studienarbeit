import json
import asn1tools

# ASN.1 Schema für DSRC
ASN1_SCHEMA = "Data_files/etsi_mapem_spatem.asn"

dsrc_codec = asn1tools.compile_files(ASN1_SCHEMA, "uper")

# Datei mit der kodierten DSRC-Nachricht
DSRC_FILE = "Data_files/dsrc_traffic_light_message.bin"

"""Lädt die kodierte DSRC-Nachricht aus einer Datei."""
def load_dsrc_message():
    try:
        with open(DSRC_FILE, "rb") as file:
            return file.read()
    except FileNotFoundError:
        print("Fehler: DSRC-Datei nicht gefunden.")
        return None

"""Dekodiert die DSRC-Nachricht zurück in JSON-Format."""
def decode_dsrc(encoded_message):
    try:
        decoded_message = dsrc_codec.decode("SPATEM", encoded_message)
        print("Dekodierte DSRC-Nachricht:")
        print(json.dumps(decoded_message, indent=4, default=str))
        return decoded_message
    except Exception as e:
        print("Fehler beim Dekodieren der DSRC-Nachricht:", str(e))
        return None

"""Hauptfunktion zur Dekodierung der DSRC-Nachricht."""
def main():
    encoded_message = load_dsrc_message()
    if encoded_message:
        decode_dsrc(encoded_message)
    else:
        print("Keine gültige DSRC-Nachricht zum Dekodieren gefunden.")

if __name__ == "__main__":
    main()
