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

DATA_FILE = "Data_files/automated_scenario_data.json"

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

    html.Div(style={"flex": "1", "padding": "20px"}, children=[
        html.H1("Automatisierte Ampelsteuerung"),

        html.Button("▶️ Start / ⏹️ Stopp", id="toggle-auto-mode", n_clicks=0),

        dcc.Interval(
            id="auto-interval",
            interval=1000,
            n_intervals=0,
            disabled=True
        ),

        # Obere Ampel
        html.Div([
            html.Div([
                html.Div(id="north-red-auto", className="traffic-light-dot dot-off"),
                html.Div(id="north-yellow-auto", className="traffic-light-dot dot-off"),
                html.Div(id="north-green-auto", className="traffic-light-dot dot-off")
            ], className="traffic-light")
        ], style={"display": "flex", "justifyContent": "center", "marginBottom": "10px"}),

        # Mittelteil – angepasst!
        html.Div(style={
            "display": "flex",
            "justifyContent": "center",
            "alignItems": "center",
            "gap": "40px",
            "marginLeft": "-40px",
            "marginRight": "-40px"
        }, children=[
            html.Div([
                html.Div(id="west-red-auto", className="traffic-light-dot dot-off"),
                html.Div(id="west-yellow-auto", className="traffic-light-dot dot-off"),
                html.Div(id="west-green-auto", className="traffic-light-dot dot-off")
            ], className="traffic-light", style={"marginRight": "-20px"}),

            html.Div(style={
                "width": "150px",
                "height": "150px",
                "backgroundColor": "#ccc",
                "border": "3px solid black"
            }),

            html.Div([
                html.Div(id="east-red-auto", className="traffic-light-dot dot-off"),
                html.Div(id="east-yellow-auto", className="traffic-light-dot dot-off"),
                html.Div(id="east-green-auto", className="traffic-light-dot dot-off")
            ], className="traffic-light", style={"marginLeft": "-20px"})
        ]),

        # Untere Ampel
        html.Div([
            html.Div([
                html.Div(id="south-red-auto", className="traffic-light-dot dot-off"),
                html.Div(id="south-yellow-auto", className="traffic-light-dot dot-off"),
                html.Div(id="south-green-auto", className="traffic-light-dot dot-off")
            ], className="traffic-light")
        ], style={"display": "flex", "justifyContent": "center", "marginTop": "10px"}),

        html.H3("Letzte gesendete Phase"),
        html.Div(id="auto-traffic-phase")
    ]),

    html.Div(style={"flex": "1", "padding": "20px", "borderLeft": "2px solid #ccc"}, children=[
        html.H3("Aktuelle JSON-Daten"),
        html.Pre(id="auto-json-display", className="json-box")
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
    json_data = load_traffic_data()
    encoded_message = convert_to_dsrc(json_data)
    if encoded_message:
        save_dsrc_message(encoded_message, "dsrc_traffic_light_message.bin")
    send_file_to_obu("Data_files/dsrc_traffic_light_message.bin", "dsrc_traffic_light_message.bin")

def get_dot_classes(phase):
    if phase == "green":
        return ["traffic-light-dot dot-off", "traffic-light-dot dot-off", "traffic-light-dot dot-green"]
    elif phase == "yellow":
        return ["traffic-light-dot dot-off", "traffic-light-dot dot-yellow", "traffic-light-dot dot-off"]
    elif phase == "yellow-red":
        return ["traffic-light-dot dot-red", "traffic-light-dot dot-yellow", "traffic-light-dot dot-off"]
    else:
        return ["traffic-light-dot dot-red", "traffic-light-dot dot-off", "traffic-light-dot dot-off"]

def register_callbacks(app):
    @app.callback(
        Output("auto-interval", "disabled"),
        Input("toggle-auto-mode", "n_clicks"),
        State("auto-interval", "disabled"),
        prevent_initial_call=True
    )
    def toggle_auto_mode(n_clicks, current_disabled):
        return not current_disabled

    @app.callback(
        [Output("auto-traffic-phase", "children"),
         Output("auto-json-display", "children"),
         Output("north-red-auto", "className"), Output("north-yellow-auto", "className"), Output("north-green-auto", "className"),
         Output("south-red-auto", "className"), Output("south-yellow-auto", "className"), Output("south-green-auto", "className"),
         Output("east-red-auto", "className"), Output("east-yellow-auto", "className"), Output("east-green-auto", "className"),
         Output("west-red-auto", "className"), Output("west-yellow-auto", "className"), Output("west-green-auto", "className")],
        Input("auto-interval", "n_intervals"),
        prevent_initial_call=True
    )
    def update_automated_scenario(n_intervals):
        phase, remaining_time = get_current_phase(n_intervals)
        ns_phase = ew_phase = "red"
        if phase == "ns_green": ns_phase = "green"
        elif phase == "ns_red_yellow": ns_phase = "yellow-red"
        elif phase == "ns_yellow": ns_phase = "yellow"
        elif phase == "ew_green": ew_phase = "green"
        elif phase == "ew_yellow": ew_phase = "yellow"
        elif phase == "ew_red_yellow": ew_phase = "yellow-red"

        save_traffic_data(ns_phase, ew_phase, remaining_time)

        with open(DATA_FILE, "r") as file:
            json_output = json.dumps(json.load(file), indent=4)

        return (
            f"Phase: Nord/Süd - {ns_phase}, Ost/West - {ew_phase}, {remaining_time} Sek.",
            json_output,
            *get_dot_classes(ns_phase),
            *get_dot_classes(ns_phase),
            *get_dot_classes(ew_phase),
            *get_dot_classes(ew_phase)
        )
