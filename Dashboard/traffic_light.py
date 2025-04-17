import json
import datetime
from dash import dcc, html
from dash.dependencies import Input, Output, State
import sys
import os

sys.path.append(os.path.abspath("Conversion"))
sys.path.append(os.path.abspath("OBU_related"))

from convert_traffic_light_to_DSRC import convert_to_dsrc, load_traffic_data, save_dsrc_message
from send_to_obu import send_file_to_obu

DATA_FILE = "Data_files/traffic_data.json"
LOG_FILE = "Data_files/process_traffic_light.log"

TRAFFIC_CYCLE = [
    ("ns_red_yellow", 2),
    ("ns_green", 10),
    ("ns_yellow", 3),
    ("all_red", 2),
    ("ew_red_yellow", 2),
    ("ew_green", 10),
    ("ew_yellow", 3),
    ("all_red", 2)
]
layout = html.Div(style={"display": "flex", "flexDirection": "row", "justifyContent": "space-between"}, children=[

    html.Div(style={"flex": "1", "padding": "20px", "backgroundColor": "#f9f9f9"}, children=[
        html.H1("RSU Kreuzungssteuerung"),
        dcc.Interval(id="interval-component", interval=1000, n_intervals=0),

        # Obere Ampel
        html.Div(className="traffic-light", children=[
            html.Div(id="north-red", className="traffic-light-dot dot-off"),
            html.Div(id="north-yellow", className="traffic-light-dot dot-off"),
            html.Div(id="north-green", className="traffic-light-dot dot-off")
        ], style={"margin": "0 auto 20px auto"}),

        # Mittelteil: Ost-/West-Ampeln + Kreuzung
        html.Div(style={
            "display": "flex",
            "justifyContent": "center",
            "alignItems": "center",
            "gap": "40px",
            "marginLeft": "-40px",
            "marginRight": "-40px"
        }, children=[
            html.Div(className="traffic-light", style={"marginRight": "-20px"}, children=[
                html.Div(id="west-red", className="traffic-light-dot dot-off"),
                html.Div(id="west-yellow", className="traffic-light-dot dot-off"),
                html.Div(id="west-green", className="traffic-light-dot dot-off")
            ]),
            html.Div(style={
                "width": "150px",
                "height": "150px",
                "backgroundColor": "#ccc",
                "border": "3px solid black"
            }),
            html.Div(className="traffic-light", style={"marginLeft": "-20px"}, children=[
                html.Div(id="east-red", className="traffic-light-dot dot-off"),
                html.Div(id="east-yellow", className="traffic-light-dot dot-off"),
                html.Div(id="east-green", className="traffic-light-dot dot-off")
            ])
        ]),

        # Untere Ampel
        html.Div(className="traffic-light", children=[
            html.Div(id="south-red", className="traffic-light-dot dot-off"),
            html.Div(id="south-yellow", className="traffic-light-dot dot-off"),
            html.Div(id="south-green", className="traffic-light-dot dot-off")
        ], style={"margin": "20px auto 0 auto"}),

        html.H2(""),
        html.Button("Nächste Sekunde", id="next-second-button", n_clicks=0),

        html.H2("Aktueller Status"),
        html.Div(id="current-status-traffic-light"),

        html.H2("Verbleibende Zeit"),
        html.Div(id="remaining-time-traffic-light"),

        html.Button("⚡ Aktualisieren & DSRC senden", id="update-button-traffic-light", n_clicks=0),
        html.Div(id="status-message-traffic-light"),
    ]),

    # Rechte Spalte: JSON & Ablaufprotokoll
    html.Div(style={"flex": "1", "padding": "20px", "borderLeft": "2px solid #ccc", "backgroundColor": "#f9f9f9"}, children=[
        html.H2("Aktualisierte JSON-Daten"),
        html.Pre(id="json-traffic-light-display", className="json-box"),

        dcc.Interval(id="json-update-interval-traffic-light", interval=500, n_intervals=0),
        dcc.Interval(id="log-update-interval-traffic-light", interval=200, n_intervals=0),

        html.H2("Live Ablaufprotokoll"),
        html.Pre(id="process-log-display-traffic-light", className="log-box"),
    ])
])


def get_current_phase(n_clicks):
    elapsed_time = n_clicks % sum(t[1] for t in TRAFFIC_CYCLE)
    for phase, duration in TRAFFIC_CYCLE:
        if elapsed_time < duration:
            return phase, int(duration - elapsed_time)
        elapsed_time -= duration
    return "all_red", 0

def save_traffic_data(ns_phase, ew_phase, remaining_time):
    data = {"north_south": ns_phase, "east_west": ew_phase, "remaining_time": remaining_time}
    with open(DATA_FILE, "w") as file:
        json.dump(data, file, indent=4)
    write_log("JSON-Datei gespeichert.")
    json_data = load_traffic_data()
    encoded_message = convert_to_dsrc(json_data)
    write_log("In DSRC-Nachrichtenformat umgewandelt.")
    if encoded_message:
        save_dsrc_message(encoded_message, "dsrc_traffic_light_message.bin")
        write_log("In Bin\u00e4rdatei gespeichert.")
    send_file_to_obu("Data_files/dsrc_traffic_light_message.bin", "dsrc_traffic_light_message.bin")
    write_log("Bin\u00e4rdatei per SSH an OBU gesendet.")
    write_log("Nachricht \u00fcber OBU-Antenne gesendet (angenommen).")

def write_log(message):
    with open(LOG_FILE, "a") as f:
        f.write(f"{message}\n")

def clear_log():
    with open(LOG_FILE, "w") as f:
        f.write("")

def register_callbacks(app):
    @app.callback(
        [Output(f"{d}-{c}", "className") for d in ["north", "south", "east", "west"] for c in ["red", "yellow", "green"]] +
        [Output("current-status-traffic-light", "children"), Output("remaining-time-traffic-light", "children")],
        Input("next-second-button", "n_clicks")
    )
    def update_traffic_light_phase(n_clicks):
        phase, remaining_time = get_current_phase(n_clicks)
        clear_log()

        ns_phase = ew_phase = "red"
        if phase == "ns_green": ns_phase = "green"
        elif phase == "ns_red_yellow": ns_phase = "yellow-red"
        elif phase == "ns_yellow": ns_phase = "yellow"
        elif phase == "ew_green": ew_phase = "green"
        elif phase == "ew_yellow": ew_phase = "yellow"
        elif phase == "ew_red_yellow": ew_phase = "yellow-red"

        def get_class(phase):
            if phase == "green":
                return ["traffic-light-dot dot-off", "traffic-light-dot dot-off", "traffic-light-dot dot-green"]
            elif phase == "yellow":
                return ["traffic-light-dot dot-off", "traffic-light-dot dot-yellow", "traffic-light-dot dot-off"]
            elif phase == "yellow-red":
                return ["traffic-light-dot dot-red", "traffic-light-dot dot-yellow", "traffic-light-dot dot-off"]
            else:
                return ["traffic-light-dot dot-red", "traffic-light-dot dot-off", "traffic-light-dot dot-off"]

        return (
            *get_class(ns_phase),
            *get_class(ns_phase),
            *get_class(ew_phase),
            *get_class(ew_phase),
            f"Aktuelle Phase: Nord/S\u00fcd - {ns_phase}, Ost/West - {ew_phase}",
            f"Verbleibende Zeit: {remaining_time} Sekunden"
        )

    @app.callback(
        Output("status-message-traffic-light", "children"),
        Input("update-button-traffic-light", "n_clicks"),
        State("next-second-button", "n_clicks")
    )
    def send_traffic_data(n_clicks_send, n_clicks_phase):
        if not n_clicks_send:
            return ""
        clear_log()
        write_log("JSON-Datei wird erstellt...")
        phase, remaining_time = get_current_phase(n_clicks_phase)
        ns_phase = ew_phase = "red"
        if phase == "ns_green": ns_phase = "green"
        elif phase == "ns_red_yellow": ns_phase = "yellow-red"
        elif phase == "ns_yellow": ns_phase = "yellow"
        elif phase == "ew_green": ew_phase = "green"
        elif phase == "ew_yellow": ew_phase = "yellow"
        elif phase == "ew_red_yellow": ew_phase = "yellow-red"
        save_traffic_data(ns_phase, ew_phase, remaining_time)
        return "\u2705 Ampelaktualisierung gespeichert & DSRC gesendet!"

    @app.callback(
        Output("process-log-display-traffic-light", "children"),
        Input("log-update-interval-traffic-light", "n_intervals")
    )
    def update_log_display(n):
        try:
            with open(LOG_FILE, "r") as f:
                return f.read()
        except FileNotFoundError:
            return "Noch keine Logs vorhanden."

    @app.callback(
        Output("json-traffic-light-display", "children"),
        Input("json-update-interval-traffic-light", "n_intervals")
    )
    def update_json_display(n):
        try:
            with open(DATA_FILE, "r") as f:
                return json.dumps(json.load(f), indent=4)
        except (FileNotFoundError, json.JSONDecodeError):
            return "Noch keine g\u00fcltigen JSON-Daten vorhanden."
