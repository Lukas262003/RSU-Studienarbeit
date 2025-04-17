import dash
from dash import dcc, html
import traffic_light as traffic_light
import weather as weather
import road_infrastructure as road_infrastructure
import automated_scenarios as automated_scenarios

# Erstelle die Dash-App
app = dash.Dash(__name__, suppress_callback_exceptions=True)

app.layout = html.Div([
    dcc.Tabs(
        id="tabs",
        value="traffic",
        colors={
            "border": "#ffffff",
            "primary": "#0d6efd",
            "background": "#f1f1f1"
        },
        children=[
            dcc.Tab(label="🚦 Ampelsteuerung", value="traffic"),
            dcc.Tab(label="🌤️ Wetter", value="weather"),
            dcc.Tab(label="🛣️ Straßen Infrastruktur", value="road_infrastructure"),
            dcc.Tab(label="🤖 Automatisierte Szenarien", value="automated_scenarios"),
            dcc.Tab(label="📡 V2X-Kommunikation", value="v2x_communication"),
            dcc.Tab(label="🏙️ Smart City-Integration", value="smart_city"),
            dcc.Tab(label="⚠️ Gefahrenmanagement", value="hazard_management")
        ]
    ),
    html.Div(id="tabs-content", className="tab-content")
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
        return road_infrastructure.layout # Importiere das Straßeninfrastruktur-Layout
    elif tab == "automated_scenarios":
        return automated_scenarios.layout  # Importiere das automatisierte Szenarien-Layout
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
#automated_scenarios.register_callbacks(app)

# Ipv4: 192.168.147.1
# http://192.168.147.1:8050/
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8050)
