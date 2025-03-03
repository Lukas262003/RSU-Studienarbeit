import json
import asn1tools
import time
import os

# Datei zur Speicherung der Wetterdaten
DATA_FILE = "Data_files/weather_data.json"

# Speicherort für die DSRC-Wetterdatei
OUTPUT_DIR = "Data_files"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "dsrc_weather_message.bin")

# ASN.1 Definition für DSRC
ASN1_SCHEMA = "Data_files/etsi_mapem_spatem.asn"

# ASN.1-Schema kompilieren
dsrc_codec = asn1tools.compile_files(ASN1_SCHEMA, "uper")

# Hauptkategorie für Wetterereignisse (CauseCode)
WEATHER_MAPPING = {
    "clear": 0,  # Kein besonderes Wetter
    "heavyRain": 19,  # AdverseWeatherCondition-Precipitation
    "fog": 18,  # AdverseWeatherCondition-Visibility
    "snow": 19,  # AdverseWeatherCondition-Precipitation
    "ice": 6  # AdverseWeatherCondition-Adhesion
}

# Detailinformationen (SubCauseCode)
SUBCAUSE_MAPPING = {
    "heavyRain": 1,  # Heavy rain
    "fog": 1,  # Fog
    "snow": 2,  # Heavy snowfall
    "ice": 5,  # Ice on road
    "clear": 0  # Kein Problem
}

def load_weather_data():
    """Lädt die gespeicherten Wetterdaten."""
    try:
        with open(DATA_FILE, "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"weatherCondition": "clear", "visibility": "good", "roadCondition": "normal"}

def convert_weather_to_dsrc():
    """Konvertiert aktuelle Wetterdaten in eine DSRC-Nachricht mit CauseCode."""
    weather_data = load_weather_data()

    dsrc_message = {
        "causeCode": WEATHER_MAPPING.get(weather_data["weatherCondition"], 0),
        "subCauseCode": SUBCAUSE_MAPPING.get(weather_data["weatherCondition"], 0)
    }

    try:
        encoded_message = dsrc_codec.encode("CauseCode", dsrc_message)
        return encoded_message
    except Exception as e:
        print("❌ Fehler bei DSRC-Kodierung:", str(e))
        return None
    
"""Speichert die kodierte DSRC-Nachricht in eine Datei in Data_files."""
def save_dsrc_message(encoded_message, output_file=OUTPUT_FILE):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(OUTPUT_FILE, "wb") as file:
        file.write(encoded_message)
    print(f"✅ DSRC-Wetterwarnung gespeichert in {OUTPUT_FILE}")

"""Hauptfunktion zur Umwandlung und Speicherung der DSRC-Nachricht."""
def main():
    json_data = load_weather_data()  # JSON-Daten laden
    dsrc_message = convert_weather_to_dsrc()  # JSON-Daten in DSRC konvertieren
    
    if dsrc_message:
        save_dsrc_message(dsrc_message)  # DSRC-Nachricht speichern
        print("Nachricht erfolgreich konvertiert und gespeichert.")
    else:
        print("Fehler bei der DSRC-Umwandlung.")

if __name__ == "__main__":
    main()  # Skript ausführen