import dash
import dash_leaflet as dl
from dash import dcc, html
from dash.dependencies import Input, Output, State
import json
import os
from dash.exceptions import PreventUpdate

# Datei zur Speicherung der MAPEM-Daten
MAPEM_FILE = "Data_files/road_infrastructure_data.json"

# Falls keine MAPEM-Daten vorhanden sind, erstelle eine Beispielstruktur
if not os.path.exists(MAPEM_FILE):
    example_data = {
        "restrictions": []  # Hier werden Baustellen, Spurverengungen, Tempolimits gespeichert
    }
    with open(MAPEM_FILE, "w") as file:
        json.dump(example_data, file, indent=4)

# MAPEM-Daten laden
def load_mapem_data():
    with open(MAPEM_FILE, "r") as file:
        return json.load(file)

layout = html.Div([
    html.H1("MAPEM - Kreuzungsverwaltung"),
    
    dl.Map(center=[47.662340, 9.454868], zoom=16, children=[
        dl.TileLayer(),
        dl.LayerGroup(id="map-layer"),
        dl.Marker(
            id="user-marker",
            position=[47.662340, 9.454868]
        )
    ], id="map", style={"width": "100%", "height": "500px"}),
    
    html.Div("Koordinaten eingeben (Format: Lat, Lon):", style={"margin-top": "10px", "font-weight": "bold"}),
    dcc.Input(id="coordinate-input", type="text", placeholder="47.658405, 9.456054", style={"width": "80%"}),
    html.Button("Position setzen", id="set-position-button", n_clicks=0),
    
    html.Div("Marker Position: ", style={"margin-top": "10px", "font-weight": "bold"}),
    html.Div(id="marker-position-output"),
    
    html.Button("Baustelle setzen", id="set-construction-button", n_clicks=0),
    html.Button("Spurverengung setzen", id="set-lane-reduction-button", n_clicks=0),
    html.Button("Straßensperrung setzen", id="set-road-closure-button", n_clicks=0),

    html.Div([
        html.Button("Tempolimit ändern", id="set-speed-limit-button", n_clicks=0, style={"margin-top": "10px"}),
        html.Button("Fahrzeugspezifisches Tempolimit", id="set-vehicle-speed-button", n_clicks=0, style={"margin-top": "10px"}),
        
        # Eingabefeld für das Tempolimit (wird für beide Buttons verwendet)
        html.Div([
            dcc.Input(id="speed-limit-input", type="number", placeholder="Tempolimit in km/h", 
                    min=5, max=130, step=5, style={"width": "80%"})
        ]),

        # Dropdown nur für fahrzeugspezifisches Tempolimit
        html.Div([
            dcc.Dropdown(
                id="vehicle-type-dropdown",
                options=[
                    {"label": "PKW", "value": "PKW"},
                    {"label": "LKW", "value": "LKW"},
                    {"label": "Motorrad", "value": "Motorrad"},
                    {"label": "Bus", "value": "Bus"}
                ],
                placeholder="Fahrzeugtyp wählen",
                style={"width": "80%"}
            )
        ], id="vehicle-dropdown-container")
    ]),

    html.Button("Alle Änderungen entfernen", id="clear-restrictions-button", n_clicks=0, style={"margin-top": "10px", "font-size": "16px", "font-weight": "bold"}),

    
    html.Div(id="status-message", style={"margin-top": "10px", "font-size": "20px"}),
    html.H2("MAPEM-Daten"),
    html.Pre(id="json-display", style={"border": "1px solid black", "padding": "10px", "whiteSpace": "pre-wrap"}),

    dcc.Store(id="click-store", data={
    "construction": 0,
    "lane_reduction": 0,
    "road_closure": 0,
    "speed_limit": 0,
    "vehicle_speed": 0,
    "reset": 0
    })

])

def parse_coordinates(coord_str):
    try:
        lat, lon = map(float, coord_str.split(","))
        return lat, lon
    except ValueError:
        return None

def register_callbacks(app):

    @app.callback(
        Output("user-marker", "position"),
        Output("marker-position-output", "children"),
        Input("set-position-button", "n_clicks"),
        State("coordinate-input", "value")
    )
    def update_position_from_input(n_clicks, coord_str):
        if n_clicks > 0 and coord_str:
            coords = parse_coordinates(coord_str)
            if coords:
                lat, lon = coords
                return [lat, lon], f"Lat: {lat:.6f}, Lon: {lon:.6f}"
        return dash.no_update, "Ungültige Eingabe oder keine Position gefunden!"
    
    @app.callback(
        [Output("map-layer", "children"),
        Output("json-display", "children"),
        Output("status-message", "children"),
        Output("click-store", "data")],  # Speichert die Klicks zurück
        [Input("set-construction-button", "n_clicks"),
        Input("set-lane-reduction-button", "n_clicks"),
        Input("set-road-closure-button", "n_clicks"),
        Input("set-speed-limit-button", "n_clicks"),
        Input("set-vehicle-speed-button", "n_clicks"),
        Input("clear-restrictions-button", "n_clicks")],
        [State("user-marker", "position"),
        State("click-store", "data")]  # Liest gespeicherte Klicks
    )
    def update_map(construction_n, lane_reduction_n, road_closure_n, speed_limit_n, vehicle_speed_n, clear_n, marker_position, click_data):
        ctx = dash.callback_context
        trigger_id = ctx.triggered_id if ctx.triggered_id else None

        data = load_mapem_data()
        status_msg = ""

        if trigger_id == "clear-restrictions-button":
            data["restrictions"] = []
            status_msg = "Alle Einschränkungen entfernt!"
            click_data = {k: 0 for k in click_data}  # Setzt alle Klicks zurück
        elif marker_position and isinstance(marker_position, list) and len(marker_position) == 2:
            lat, lon = marker_position
            if trigger_id == "set-construction-button" and construction_n > click_data["construction"]:
                data["restrictions"].append({"type": "Baustelle", "lat": lat, "lon": lon})
                status_msg = "Baustelle gesetzt!"
                click_data["construction"] = construction_n
            elif trigger_id == "set-lane-reduction-button" and lane_reduction_n > click_data["lane_reduction"]:
                data["restrictions"].append({"type": "Spurverengung", "lat": lat, "lon": lon})
                status_msg = "Spurverengung gesetzt!"
                click_data["lane_reduction"] = lane_reduction_n
            elif trigger_id == "set-road-closure-button" and road_closure_n > click_data["road_closure"]:
                data["restrictions"].append({"type": "Straßensperrung", "lat": lat, "lon": lon})
                status_msg = "Strassensperrung gesetzt!"
                click_data["road_closure"] = road_closure_n
            elif trigger_id == "set-speed-limit-button" and speed_limit_n > click_data["speed_limit"]:
                data["restrictions"].append({"type": "Tempolimit", "lat": lat, "lon": lon, "speed": 30})
                status_msg = "Tempolimit geändert auf 30 km/h!"
                click_data["speed_limit"] = speed_limit_n
            elif trigger_id == "set-vehicle-speed-button" and vehicle_speed_n > click_data["vehicle_speed"]:
                data["restrictions"].append({"type": "Fahrzeugspezifisches Tempolimit", "lat": lat, "lon": lon, "speed": 20, "vehicle": "LKW"})
                status_msg = "LKW-Tempolimit auf 20 km/h gesetzt!"
                click_data["vehicle_speed"] = vehicle_speed_n
        else:
            status_msg = "❌ Fehler: Bitte gültige Koordinaten eingeben!"
            raise PreventUpdate

        with open(MAPEM_FILE, "w") as file:
            json.dump(data, file, indent=4)

        markers = [dl.Marker(position=[r["lat"], r["lon"]], children=dl.Popup(f"{r['type']}")) for r in data["restrictions"]]

        return markers, json.dumps(data, indent=4), status_msg, click_data