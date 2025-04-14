import dash
from dash import dcc, html
import traffic_light as traffic_light
import weather as weather
import road_infrastructure as road_infrastructure

# Erstelle die Dash-App
app = dash.Dash(__name__, suppress_callback_exceptions=True)

# Tabs für verschiedene Funktionen
app.layout = html.Div([
    dcc.Tabs(id="tabs", value="traffic", children=[
        dcc.Tab(label="Ampelsteuerung", value="traffic"),
        dcc.Tab(label="Wetter", value="weather"),
        dcc.Tab(label="Straßen Infrastruktur", value="road_infrastructure"),
        dcc.Tab(label="Koordination", value="coordination"),
        dcc.Tab(label="V2X-Kommunikation", value="v2x_communication"),
        dcc.Tab(label="Smart City-Integration", value="smart_city"),
        dcc.Tab(label="Gefahrenmanagement", value="hazard_management")
    ]),
    html.Div(id="tabs-content")
])

@app.callback(
    dash.dependencies.Output("tabs-content", "children"),
    [dash.dependencies.Input("tabs", "value")]
)
def update_tab_content(tab):
    """Aktualisiert den Inhalt des Tabs."""
    if tab == "traffic":
        return traffic_light.layout  # Importiere das Ampel-Layout
    elif tab == "weather":
        return weather.layout  # Importiere das Wetter-Layout
    elif tab == "road_infrastructure":
        return road_infrastructure.layout
    elif tab == "coordination":
        return html.Div([html.H3("Koordination zwischen RSUs")])
    elif tab == "v2x_communication":
        return html.Div([html.H3("V2X-Kommunikation mit Fahrzeugen")])
    elif tab == "smart_city":
        return html.Div([html.H3("Smart City-Integration")])
    elif tab == "hazard_management":
        return html.Div([html.H3("Gefahrenmanagement")])
    return html.Div()

# Registriere die Callbacks aus traffic_light.py
traffic_light.register_callbacks(app)
weather.register_callbacks(app)
road_infrastructure.register_callbacks(app)

# Ipv4: 192.168.147.1
# http://192.168.147.1:8050/
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8050)
