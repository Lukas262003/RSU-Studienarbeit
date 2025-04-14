import json
import asn1tools
import time
import os

# Basisverzeichnis ist der übergeordnete Ordner von `Conversion`
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# Data_files Pfad relativ zur Conversion-Datei setzen
OUTPUT_DIR = os.path.join(BASE_DIR, "Data_files")
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "dsrc_traffic_light_message.bin")

# Pfad zur JSON-Datei mit Ampelphasen
JSON_FILE = "Data_files/traffic_data.json"

# ASN.1 Definition für DSRC (SPATEM)
ASN1_SCHEMA = "Data_files/etsi_mapem_spatem.asn"

# Kompiliere die ASN.1-Spezifikation für DSRC (SPATEM) mit UPER-Codierung
dsrc_codec = asn1tools.compile_files(ASN1_SCHEMA, "uper")

# Mapping der Ampelphasen auf DSRC-konforme Werte
STATE_MAPPING = {
    "red": "stop-And-Remain",                # Rot: Haltephase
    "yellow": "permissive-clearance",       # Gelb: Übergangsphase
    "green": "permissive-Movement-Allowed", # Grün: Freigabephase
    "yellow-red": "pre-Movement"            # Gelb-Rot: Vorbereitungsphase
}

"""Lädt die aktuelle Ampelkonfiguration aus der JSON-Datei."""
def load_traffic_data():
    try:
        with open(JSON_FILE, "r") as file:
            return json.load(file)  # Lade und parse die JSON-Daten
    except FileNotFoundError:
        print("JSON-Datei nicht gefunden.")
        return None
    except json.JSONDecodeError:
        print("Fehler beim Dekodieren der JSON-Datei.")
        return None
    
"""Konvertiert JSON-Daten in eine SPATEM-DSRC-Nachricht."""
def convert_to_dsrc(json_data):
    print("Starte Konvertierung von JSON zu DSRC...")

    if not json_data:
        print("Fehler: JSON-Daten sind leer oder ungültig.")
        return None
    
    # Erstellen der DSRC-SPATEM-Nachricht basierend auf den JSON-Daten
    dsrc_message = {
        "header": {
            "protocolVersion": 2,  # Protokollversion
            "messageID": 4,        # Nachrichtentyp (SPATEM)
            "stationID": 12345      # ID der sendenden Station
        },
        "spat": {
            "intersections": [
                {
                    "id": {"region": 0, "id": 1},  # ID der Kreuzung
                    "revision": 1,  # Revisionsnummer der Nachricht
                    "status": (b'\x01', 1),  # Status der Kreuzung (binär kodiert)
                    "states": [
                        {
                            "signalGroup": 1,  # Ampelgruppe 1 (z.B. Nord-Süd)
                            "state-time-speed": [
                                {
                                    "eventState": STATE_MAPPING.get(json_data["north_south"], "stop-And-Remain"),
                                    "timing": {"minEndTime": json_data.get("remaining_time", 0)}
                                }
                            ]
                        },
                        {
                            "signalGroup": 2,  # Ampelgruppe 2 (z.B. Ost-West)
                            "state-time-speed": [
                                {
                                    "eventState": STATE_MAPPING.get(json_data["east_west"], "stop-And-Remain"),
                                    "timing": {"minEndTime": json_data.get("remaining_time", 0)}
                                }
                            ]
                        }
                    ],
                    "timestamp": int(time.time())  # Zeitstempel der Nachricht
                }
            ]
        }
    }

    try:
        encoded_message = dsrc_codec.encode("SPATEM", dsrc_message)  # Nachricht in DSRC-Format kodieren
        print(encoded_message)
        return encoded_message
    except Exception as e:
        print("Fehler beim Kodierungsversuch! Prüfe die ASN.1-Datenstruktur.")
        print("Fehlermeldung:", str(e))
        print("Dateninhalt:", json.dumps(dsrc_message, indent=4))
        return None

"""Speichert die kodierte DSRC-Nachricht in eine Datei in Data_files."""
def save_dsrc_message(encoded_message, output_file=OUTPUT_FILE):
    os.makedirs(OUTPUT_DIR, exist_ok=True)  # Falls Data_files nicht existiert, wird es erstellt

    with open(OUTPUT_FILE, "wb") as file:
        file.write(encoded_message)  # Schreibe die binär kodierte Nachricht in die Datei
    print(f"✅ DSRC-Nachricht gespeichert in {OUTPUT_FILE}")

"""Hauptfunktion zur Umwandlung und Speicherung der DSRC-Nachricht."""
def main():
    json_data = load_traffic_data()  # JSON-Daten laden
    dsrc_message = convert_to_dsrc(json_data)  # JSON-Daten in DSRC konvertieren
    
    if dsrc_message:
        save_dsrc_message(dsrc_message)  # DSRC-Nachricht speichern
        print("Nachricht erfolgreich konvertiert und gespeichert.")
    else:
        print("Fehler bei der DSRC-Umwandlung.")

if __name__ == "__main__":
    main()  # Skript ausführen
