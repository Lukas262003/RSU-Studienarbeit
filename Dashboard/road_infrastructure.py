import dash
import dash_leaflet as dl
from dash import dcc, html
from dash.dependencies import Input, Output, State
import json
import os
import re

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
    html.Button("Tempolimit ändern", id="set-speed-limit-button", n_clicks=0),
    html.Button("Fahrzeugspezifisches Tempolimit", id="set-vehicle-speed-button", n_clicks=0),
    html.Button("Alle Änderungen entfernen", id="clear-restrictions-button", n_clicks=0),
    
    html.Div(id="status-message"),
    html.H2("MAPEM-Daten"),
    html.Pre(id="json-display", style={"border": "1px solid black", "padding": "10px", "whiteSpace": "pre-wrap"})
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
         Output("status-message", "children")],
        [Input("set-construction-button", "n_clicks"),
         Input("set-lane-reduction-button", "n_clicks"),
         Input("set-road-closure-button", "n_clicks"),
         Input("set-speed-limit-button", "n_clicks"),
         Input("set-vehicle-speed-button", "n_clicks"),
         Input("clear-restrictions-button", "n_clicks")],
        [State("user-marker", "position")]
    )
    def update_map(construction_n, lane_reduction_n, road_closure_n, speed_limit_n, vehicle_speed_n, clear_n, marker_position):
        data = load_mapem_data()
        status_msg = ""
        
        if clear_n > 0:
            data["restrictions"] = []
            status_msg = "Alle Einschränkungen entfernt!"
        elif marker_position and isinstance(marker_position, list) and len(marker_position) == 2:
            lat, lon = marker_position
            if construction_n > 0:
                data["restrictions"].append({"type": "Baustelle", "lat": lat, "lon": lon})
                status_msg = "Baustelle gesetzt!"
            elif lane_reduction_n > 0:
                data["restrictions"].append({"type": "Spurverengung", "lat": lat, "lon": lon})
                status_msg = "Spurverengung gesetzt!"
            elif road_closure_n > 0:
                data["restrictions"].append({"type": "Straßensperrung", "lat": lat, "lon": lon})
                status_msg = "Straßensperrung gesetzt!"
            elif speed_limit_n > 0:
                data["restrictions"].append({"type": "Tempolimit", "lat": lat, "lon": lon, "speed": 30})
                status_msg = "Tempolimit geändert auf 30 km/h!"
            elif vehicle_speed_n > 0:
                data["restrictions"].append({"type": "Fahrzeugspezifisches Tempolimit", "lat": lat, "lon": lon, "speed": 20, "vehicle": "LKW"})
                status_msg = "LKW-Tempolimit auf 20 km/h gesetzt!"
        else:
            status_msg = "❌ Fehler: Bitte gültige Koordinaten eingeben!"
        
        with open(MAPEM_FILE, "w") as file:
            json.dump(data, file, indent=4)
        
        markers = [dl.Marker(position=[r["lat"], r["lon"]], children=dl.Popup(f"{r['type']}")) for r in data["restrictions"]]
        
        return markers, json.dumps(data, indent=4), status_msg