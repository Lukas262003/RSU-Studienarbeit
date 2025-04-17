import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import json
import sys
import os

# Dynamischen Pfad zum Import des Moduls hinzufügen
sys.path.append(os.path.abspath("Conversion"))
sys.path.append(os.path.abspath("OBU_related"))

from convert_weather_to_DSRC import convert_weather_to_dsrc, load_weather_data, save_dsrc_message
from send_to_obu import send_file_to_obu # Importiere die Funktion zum Senden an OBU

# Datei zur Speicherung der Wetterdaten
DATA_FILE = "Data_files/weather_data.json"

LOG_FILE = "Data_files/process_weather.log"

# Wetteroptionen
weather_conditions = ["clear", "heavyRain", "fog", "snow", "ice"]

def save_weather_data(condition):
    """Speichert die aktuellen Wetterbedingungen in einer JSON-Datei."""
    weather_data = {
        "weatherCondition": condition  # Nur noch "weatherCondition" speichern
    }

    clear_log()
    write_log("JSON-Datei wird erstellt...")

    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, "w") as file:
        json.dump(weather_data, file, indent=4)

    write_log("JSON-Datei gespeichert.")
    print(f"✅ Wetterdaten aktualisiert: {weather_data}")

    # Automatische DSRC-Umwandlung
    json_data = load_weather_data()  # Lade das gespeicherte JSON
    dsrc_message = convert_weather_to_dsrc()  # Wandle es in DSRC um

    write_log("In DSRC-Nachrichtenformat umgewandelt.")

    if dsrc_message:
        save_dsrc_message(dsrc_message, "dsrc_weather_message.bin")  # Speichern als Binärdatei
        print("✅ DSRC-Nachricht erfolgreich generiert & gespeichert!")
        write_log("In Binärdatei gespeichert.")

    send_file_to_obu("Data_files/dsrc_weather_message.bin", "dsrc_weather_message.bin")

    write_log("Binärdatei per SSH an OBU gesendet.")
    write_log("Nachricht über OBU-Antenne gesendet (angenommen).")

def load_weather_data():
    """Lädt die gespeicherten Wetterdaten."""
    try:
        with open(DATA_FILE, "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"weatherCondition": "clear"}

# Dashboard-Layout
layout = html.Div(style={"display": "flex", "flexDirection": "row", "justifyContent": "space-between"}, children=[

    # **LINKER BEREICH: Wettersteuerung**
    html.Div(style={"flex": "1", "padding": "20px", "backgroundColor": "#f9f9f9"}, children=[
        html.H1("🌦 Wetterabhängige Straßenwarnungen"),
        
        html.Label("🌤 Wetterbedingung wählen:"),
        dcc.Dropdown(
            id="weather-condition",
            options=[{"label": w, "value": w} for w in weather_conditions],
            value=load_weather_data()["weatherCondition"]
        ),

        html.Button("⚡ Aktualisieren & DSRC senden", id="update_button_weather", n_clicks=0),
        html.Div(id="status-message-weather")

    ]),

    # **RECHTER BEREICH: JSON**
    html.Div(style={"flex": "1", "padding": "20px", "borderLeft": "2px solid #ccc", "backgroundColor": "#f9f9f9"}, children=[
        html.H2("Aktualisierte JSON-Daten"),
        html.Pre(id="json-weather-display", style={"border": "1px solid black", "padding": "10px", "whiteSpace": "pre-wrap",
                                           "backgroundColor": "white", "height": "100px", "overflowY": "scroll"}),
        
        dcc.Interval(id="json-update-interval-weather", interval=500, n_intervals=0),
        dcc.Interval(id="log-update-interval-weather", interval=200, n_intervals=0),

        html.H2("Live Ablaufprotokoll"),
        html.Pre(id="process-log-display-weather", style={
            "border": "1px solid black",
            "padding": "10px",
            "whiteSpace": "pre-wrap",
            "backgroundColor": "white",
            "height": "150px",
            "overflowY": "scroll"
        }),
    ])
    
])

def write_log(message):
    with open(LOG_FILE, "a") as f:
        f.write(f"{message}\n")

def clear_log():
    with open(LOG_FILE, "w") as f:
        f.write("")

def register_callbacks(app):
    # Callback für Wetteraktualisierung & DSRC-Sendung
    @app.callback(
        Output("status-message-weather", "children"),
        [Input("update_button_weather", "n_clicks")],
        [dash.State("weather-condition", "value")]
    )
    def update_weather(n_clicks, condition):
        
        clear_log()
        json_output = ""

        if n_clicks > 0:
            save_weather_data(condition)
            dsrc_message = convert_weather_to_dsrc()

            # Lade die JSON-Daten für die Anzeige
            with open(DATA_FILE, "r") as file:
                json_output = json.dumps(json.load(file), indent=4)

            if dsrc_message:
                return "✅ Wetteraktualisierung gespeichert & DSRC gesendet!"
            return "❌ Fehler bei der DSRC-Konvertierung!"
        return ""
    
    @app.callback(
        Output("process-log-display-weather", "children"),
        Input("log-update-interval-weather", "n_intervals")
    )
    def update_log_display(n):
        try:
            with open(LOG_FILE, "r") as f:
                return f.read()
        except FileNotFoundError:
            return "Noch keine Logs vorhanden."
        
    @app.callback(
    Output("json-weather-display", "children"),
    Input("json-update-interval-weather", "n_intervals"))
    def update_json_display(n):
        try:
            with open(DATA_FILE, "r") as f:
                return json.dumps(json.load(f), indent=4)
        except (FileNotFoundError, json.JSONDecodeError):
            return "Noch keine gültigen JSON-Daten vorhanden."
