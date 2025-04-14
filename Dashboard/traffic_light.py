import json
import datetime
from dash import dcc, html
from dash.dependencies import Input, Output, State
import dash_daq as daq

import sys
import os

# Dynamische Pfade zum Import von Modulen
sys.path.append(os.path.abspath("Conversion"))
sys.path.append(os.path.abspath("OBU_related"))

# Jetzt kann es importiert werden
from convert_traffic_light_to_DSRC import convert_to_dsrc, load_traffic_data, save_dsrc_message
from send_to_obu import send_file_to_obu # Importiere die Funktion zum Senden an OBU

# Datei zur Speicherung der Ampelphasen
DATA_FILE = "Data_files/traffic_data.json"

# Definiere die synchronisierten Ampelphasen mit Zeiten
TRAFFIC_CYCLE = [
    ("ns_red_yellow", 2),   # Nord-Süd Rot-Gelb, Ost-West bleibt Rot
    ("ns_green", 10),       # Nord-Süd Grün, Ost-West Rot
    ("ns_yellow", 3),       # Nord-Süd Gelb, Ost-West bleibt Rot
    ("all_red", 2),         # Alle Rot für sichere Umschaltung
    ("ew_red_yellow", 2),   # Ost-West Rot-Gelb, Nord-Süd bleibt Rot
    ("ew_green", 10),       # Ost-West Grün, Nord-Süd bleibt Rot
    ("ew_yellow", 3),       # Ost-West Gelb, Nord-Süd bleibt Rot
    ("all_red", 2)          # Alle Rot für sichere Umschaltung
]

# Initialisierungszeit
START_TIME = datetime.datetime.now()

# Speichert den letzten Zustand, um unnötige Schreibvorgänge zu vermeiden
last_saved_state = {"north_south": None, "east_west": None, "remaining_time": None}

layout = html.Div(style={"display": "flex", "flexDirection": "row", "justifyContent": "space-between"}, children=[

    # **LINKER BEREICH: Ampelsteuerung**
    html.Div(style={"flex": "1", "padding": "20px", "backgroundColor": "#f9f9f9"}, children=[
        html.H1("RSU Kreuzungssteuerung"),
        dcc.Interval(
            id="interval-component",
            interval=1000,  # Aktualisierung jede Sekunde
            n_intervals=0
        ),
        html.Div([
            html.Div([daq.Indicator(id="north-red", value=True, color="red"),
                      daq.Indicator(id="north-yellow", value=True, color="gray"),
                      daq.Indicator(id="north-green", value=True, color="gray")],
                     style={"display": "flex", "flexDirection": "column", "alignItems": "center"}),

        ], style={"display": "flex", "justifyContent": "flex-start", "marginBottom": "10px", "marginLeft": "125px"}),

        html.Div([
            html.Div([daq.Indicator(id="west-red", value=True, color="red"),
                      daq.Indicator(id="west-yellow", value=True, color="gray"),
                      daq.Indicator(id="west-green", value=True, color="gray")],
                     style={"display": "flex", "flexDirection": "row", "alignItems": "center", "marginRight": "10px"}),

            html.Div(style={"width": "150px", "height": "150px", "backgroundColor": "#ccc", "border": "3px solid black"}),

            html.Div([daq.Indicator(id="east-red", value=True, color="red"),
                      daq.Indicator(id="east-yellow", value=True, color="gray"),
                      daq.Indicator(id="east-green", value=True, color="gray")],
                     style={"display": "flex", "flexDirection": "row", "alignItems": "center", "marginLeft": "10px"})
        ], style={"display": "flex", "justifyContent": "flex-start", "alignItems": "center"}),

        html.Div([
            html.Div([daq.Indicator(id="south-red", value=True, color="red"),
                      daq.Indicator(id="south-yellow", value=True, color="gray"),
                      daq.Indicator(id="south-green", value=True, color="gray")],
                     style={"display": "flex", "flexDirection": "column", "alignItems": "center"}),

        ], style={"display": "flex", "justifyContent": "flex-start", "marginTop": "10px", "marginLeft": "125px"}),

        html.H1("RSU Kreuzungssteuerung - Manuelle Steuerung"),
        html.Button("Nächste Sekunde", id="next-second-button", n_clicks=0),

        html.H2("Aktueller Status"),
        html.Div(id="current-status-traffic-light"),
        html.H2("Verbleibende Zeit"),
        html.Div(id="remaining-time-traffic-light"),

        html.Button("⚡ Aktualisieren & DSRC senden", id="update-button-traffic-light", n_clicks=0),
        html.Div(id="status-message"),
    ]),

    # **RECHTER BEREICH: JSON**
    html.Div(style={"flex": "1", "padding": "20px", "borderLeft": "2px solid #ccc", "backgroundColor": "#f9f9f9"}, children=[
        html.H2("Aktualisierte JSON-Daten"),
        html.Pre(id="json-traffic-light-display", style={"border": "1px solid black", "padding": "10px", "whiteSpace": "pre-wrap",
                                           "backgroundColor": "white", "height": "100px", "overflowY": "scroll"})
    ])
])


def get_current_phase(n_clicks):
    """Berechnet die aktuelle Ampelphase basierend auf der Anzahl der Klicks."""
    elapsed_time = n_clicks
    cycle_time = sum(t[1] for t in TRAFFIC_CYCLE)
    elapsed_time = elapsed_time % cycle_time
    
    for phase, duration in TRAFFIC_CYCLE:
        if elapsed_time < duration:
            return phase, int(duration - elapsed_time)
        elapsed_time -= duration
    return "all_red", 0

def save_traffic_data(ns_phase, ew_phase, remaining_time):
    """Speichert die aktuellen Ampelphasen in JSON und gibt DSRC-Nachricht zurück."""
    data = {"north_south": ns_phase, "east_west": ew_phase, "remaining_time": remaining_time}

    # Speichert die Daten als JSON
    with open(DATA_FILE, "w") as file:
        json.dump(data, file, indent=4)

    print("✅ JSON aktualisiert:", data)

    # Automatische DSRC-Umwandlung
    json_data = load_traffic_data()  # Lade das gespeicherte JSON
    encoded_message = convert_to_dsrc(json_data)  # Wandle es in DSRC um

    if encoded_message:
        save_dsrc_message(encoded_message, "dsrc_traffic_light_message.bin")  # Speichern als Binärdatei
        print("✅ DSRC-Nachricht erfolgreich generiert & gespeichert!")

    send_file_to_obu("Data_files/dsrc_traffic_light_message.bin", "dsrc_traffic_light_message.bin")

# **Callback-Funktion wird über eine separate Funktion registriert**
def register_callbacks(app):
    # Callback A: Nächste Sekunde
    @app.callback(
        [Output("north-red", "color"), Output("north-yellow", "color"), Output("north-green", "color"),
         Output("south-red", "color"), Output("south-yellow", "color"), Output("south-green", "color"),
         Output("east-red", "color"), Output("east-yellow", "color"), Output("east-green", "color"),
         Output("west-red", "color"), Output("west-yellow", "color"), Output("west-green", "color"),
         Output("current-status-traffic-light", "children"), Output("remaining-time-traffic-light", "children")],
        Input("next-second-button", "n_clicks")
    )
    def update_traffic_light_phase(n_clicks):
        phase, remaining_time = get_current_phase(n_clicks)
        
        ns_phase = "red"
        ew_phase = "red"
        
        if phase == "ns_green":
            ns_phase = "green"
        elif phase == "ns_red_yellow":
            ns_phase = "yellow-red"
        elif phase == "ns_yellow":
            ns_phase = "yellow"
        elif phase == "ew_green":
            ew_phase = "green"
        elif phase == "ew_yellow":
            ew_phase = "yellow"
        elif phase == "ew_red_yellow":
            ew_phase = "yellow-red"
        elif phase == "all_red":
            ns_phase, ew_phase = "red", "red"

        def get_colors(phase):
            if phase == "green":
                return "gray", "gray", "green"
            elif phase == "yellow":
                return "gray", "yellow", "gray"
            elif phase == "yellow-red":
                return "red", "yellow", "gray"
            else:
                return "red", "gray", "gray"

        return (*get_colors(ns_phase),
                *get_colors(ns_phase),
                *get_colors(ew_phase),
                *get_colors(ew_phase),
                f"Aktuelle Phase: Nord/Süd - {ns_phase}, Ost/West - {ew_phase}",
                f"Verbleibende Zeit: {remaining_time} Sekunden")

    # Callback B: DSRC senden & JSON aktualisieren
    @app.callback(
        Output("json-traffic-light-display", "children"),
        Input("update-button-traffic-light", "n_clicks"),
        State("next-second-button", "n_clicks")
    )
    def send_traffic_data(n_clicks_send, n_clicks_phase):
        if not n_clicks_send:
            return "", ""

        phase, remaining_time = get_current_phase(n_clicks_phase)

        ns_phase = "red"
        ew_phase = "red"
        
        if phase == "ns_green":
            ns_phase = "green"
        elif phase == "ns_red_yellow":
            ns_phase = "yellow-red"
        elif phase == "ns_yellow":
            ns_phase = "yellow"
        elif phase == "ew_green":
            ew_phase = "green"
        elif phase == "ew_yellow":
            ew_phase = "yellow"
        elif phase == "ew_red_yellow":
            ew_phase = "yellow-red"
        elif phase == "all_red":
            ns_phase, ew_phase = "red", "red"

        save_traffic_data(ns_phase, ew_phase, remaining_time)

        with open(DATA_FILE, "r") as file:
            json_output = json.dumps(json.load(file), indent=4)

        return json_output, "✅ DSRC-Nachricht gesendet!"