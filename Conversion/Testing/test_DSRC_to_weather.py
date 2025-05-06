import asn1tools
import os

# Speicherort der DSRC-Wetterdatei
OUTPUT_DIR = "Data_files"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "dsrc_weather_message.bin")

# ASN.1 Definition für DSRC
ASN1_SCHEMA = "Data_files/etsi_mapem_spatem.asn"

# ASN.1-Schema kompilieren
dsrc_codec = asn1tools.compile_files(ASN1_SCHEMA, "uper")

def test_dsrc_conversion():
    """Liest die DSRC-kodierte Datei und dekodiert sie zur Überprüfung."""
    if not os.path.exists(OUTPUT_FILE):
        print("❌ Keine DSRC-Datei gefunden. Bitte zuerst eine Konvertierung durchführen.")
        return

    try:
        with open(OUTPUT_FILE, "rb") as file:
            encoded_data = file.read()

        decoded_message = dsrc_codec.decode("CauseCode", encoded_data)
        print("✅ Erfolgreich dekodierte DSRC-Nachricht:")
        print(decoded_message)
    except Exception as e:
        print("❌ Fehler bei der DSRC-Dekodierung:", str(e))

if __name__ == "__main__":
    test_dsrc_conversion()
