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

    html.Div(style={"flex": "1", "padding": "20px", "backgroundColor": "#f9f9f9"}, children=[
        html.H1("Automatisierte Ampelsteuerung"),

        html.Button("▶️ Start / ⏹️ Stopp", id="toggle-auto-mode", n_clicks=0),

        dcc.Interval(
            id="auto-interval",
            interval=1000,
            n_intervals=0,
            disabled=True
        ),

        html.Div([
            html.Div([daq.Indicator(id="north-red-auto", value=True, color="red"),
                      daq.Indicator(id="north-yellow-auto", value=True, color="gray"),
                      daq.Indicator(id="north-green-auto", value=True, color="gray")],
                     style={"display": "flex", "flexDirection": "column", "alignItems": "center"}),
        ], style={"display": "flex", "justifyContent": "flex-start", "marginBottom": "10px", "marginLeft": "125px"}),

        html.Div([
            html.Div([daq.Indicator(id="west-red-auto", value=True, color="red"),
                      daq.Indicator(id="west-yellow-auto", value=True, color="gray"),
                      daq.Indicator(id="west-green-auto", value=True, color="gray")],
                     style={"display": "flex", "flexDirection": "row", "alignItems": "center", "marginRight": "10px"}),

            html.Div(style={"width": "150px", "height": "150px", "backgroundColor": "#ccc", "border": "3px solid black"}),

            html.Div([daq.Indicator(id="east-red-auto", value=True, color="red"),
                      daq.Indicator(id="east-yellow-auto", value=True, color="gray"),
                      daq.Indicator(id="east-green-auto", value=True, color="gray")],
                     style={"display": "flex", "flexDirection": "row", "alignItems": "center", "marginLeft": "10px"})
        ], style={"display": "flex", "justifyContent": "flex-start", "alignItems": "center"}),

        html.Div([
            html.Div([daq.Indicator(id="south-red-auto", value=True, color="red"),
                      daq.Indicator(id="south-yellow-auto", value=True, color="gray"),
                      daq.Indicator(id="south-green-auto", value=True, color="gray")],
                     style={"display": "flex", "flexDirection": "column", "alignItems": "center"}),
        ], style={"display": "flex", "justifyContent": "flex-start", "marginTop": "10px", "marginLeft": "125px"}),

        html.H3("Letzte gesendete Phase"),
        html.Div(id="auto-traffic-phase")
    ]),

    html.Div(style={"flex": "1", "padding": "20px", "borderLeft": "2px solid #ccc", "backgroundColor": "#f9f9f9"}, children=[
        html.H3("Aktuelle JSON-Daten"),
        html.Pre(id="auto-json-display", style={"border": "1px solid black", "padding": "10px",
                                                 "backgroundColor": "white", "height": "150px",
                                                 "overflowY": "scroll"})
    ])
])

def get_current_phase(n_clicks):
    elapsed_time = n_clicks
    cycle_time = sum(t[1] for t in TRAFFIC_CYCLE)
    elapsed_time = elapsed_time % cycle_time

    for phase, duration in TRAFFIC_CYCLE:
        if elapsed_time < duration:
            return phase, int(duration - elapsed_time)
        elapsed_time -= duration
    return "all_red", 0

def save_traffic_data(ns_phase, ew_phase, remaining_time):
    data = {"north_south": ns_phase, "east_west": ew_phase, "remaining_time": remaining_time}

    with open(DATA_FILE, "w") as file:
        json.dump(data, file, indent=4)

    print("✅ JSON aktualisiert:", data)

    json_data = load_traffic_data()
    encoded_message = convert_to_dsrc(json_data)

    if encoded_message:
        save_dsrc_message(encoded_message, "dsrc_traffic_light_message.bin")
        print("✅ DSRC-Nachricht erfolgreich generiert & gespeichert!")

    send_file_to_obu("Data_files/dsrc_traffic_light_message.bin", "dsrc_traffic_light_message.bin")

def get_colors(phase):
    if phase == "green":
        return "gray", "gray", "green"
    elif phase == "yellow":
        return "gray", "yellow", "gray"
    elif phase == "yellow-red":
        return "red", "yellow", "gray"
    else:
        return "red", "gray", "gray"

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
         Output("north-red-auto", "color"), Output("north-yellow-auto", "color"), Output("north-green-auto", "color"),
         Output("south-red-auto", "color"), Output("south-yellow-auto", "color"), Output("south-green-auto", "color"),
         Output("east-red-auto", "color"), Output("east-yellow-auto", "color"), Output("east-green-auto", "color"),
         Output("west-red-auto", "color"), Output("west-yellow-auto", "color"), Output("west-green-auto", "color")],
        Input("auto-interval", "n_intervals"),
        prevent_initial_call=True
    )
    def update_automated_scenario(n_intervals):
        phase, remaining_time = get_current_phase(n_intervals)

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

        return (
            f"Phase: Nord/Süd - {ns_phase}, Ost/West - {ew_phase}, {remaining_time} Sek.",
            json_output,
            *get_colors(ns_phase),
            *get_colors(ns_phase),
            *get_colors(ew_phase),
            *get_colors(ew_phase)
        )
