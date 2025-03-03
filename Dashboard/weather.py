import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import json
import sys
import os

# Dynamischen Pfad zum Import des Moduls hinzufügen
sys.path.append(os.path.abspath("Conversion"))

from convert_weather_to_DSRC import convert_weather_to_dsrc, load_weather_data, save_dsrc_message

# Datei zur Speicherung der Wetterdaten
DATA_FILE = "Data_files/weather_data.json"

# Wetteroptionen
weather_conditions = ["clear", "heavyRain", "fog", "snow", "ice"]

def save_weather_data(condition):
    """Speichert die aktuellen Wetterbedingungen in einer JSON-Datei."""
    weather_data = {
        "weatherCondition": condition  # Nur noch "weatherCondition" speichern
    }
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, "w") as file:
        json.dump(weather_data, file, indent=4)
    print(f"✅ Wetterdaten aktualisiert: {weather_data}")

        # Automatische DSRC-Umwandlung
    json_data = load_weather_data()  # Lade das gespeicherte JSON
    dsrc_message = convert_weather_to_dsrc()  # Wandle es in DSRC um

    if dsrc_message:
        save_dsrc_message(dsrc_message, "dsrc_weather_message.bin")  # Speichern als Binärdatei
        print("✅ DSRC-Nachricht erfolgreich generiert & gespeichert!")

def load_weather_data():
    """Lädt die gespeicherten Wetterdaten."""
    try:
        with open(DATA_FILE, "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"weatherCondition": "clear"}

# Dashboard-Layout
layout = html.Div([
    html.H1("🌦 Wetterabhängige Straßenwarnungen"),
    
    html.Label("🌤 Wetterbedingung wählen:"),
    dcc.Dropdown(
        id="weather-condition",
        options=[{"label": w, "value": w} for w in weather_conditions],
        value=load_weather_data()["weatherCondition"]
    ),

    html.Button("⚡ Aktualisieren & DSRC senden", id="update_button_weather", n_clicks=0),
    html.Div(id="status-message"),
])

def register_callbacks(app):
    # Callback für Wetteraktualisierung & DSRC-Sendung
    @app.callback(
        Output("status-message", "children"),
        [Input("update_button_weather", "n_clicks")],
        [dash.State("weather-condition", "value")]
    )
    def update_weather(n_clicks, condition):
        if n_clicks > 0:
            save_weather_data(condition)
            dsrc_message = convert_weather_to_dsrc()
            if dsrc_message:
                return "✅ Wetteraktualisierung gespeichert & DSRC gesendet!"
            return "❌ Fehler bei der DSRC-Konvertierung!"
        return ""
