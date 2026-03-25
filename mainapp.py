import numpy as np
import pandas as pd
import requests
import asyncio
import threading
import os
import time
from datetime import datetime
from skyfield.api import load, EarthSatellite, wgs84
from dash import Dash, dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objects as go

# --- THE TACTICAL ORBITAL ARCHITECTURE ---
LOG_DIR = "AETHER_STREAMS"
os.makedirs(LOG_DIR, exist_ok=True)
TLE_CACHE = "active_satellites.txt"

class GlobalAetherOrchestrator:
    def __init__(self):
        self.ts = load.timescale()
        self.sats = []
        self.active_data = []
        self.lock = threading.Lock()
        self.io_count = 0
        self.init_mass_signal_link()

    def init_mass_signal_link(self):
        """Ethical Mass Data Harvesting: The Single Payload Strike"""
        print("\n[AETHER-V2] Initiating bulk data tether to global constellation...")
        
        # Download data only if it's older than 12 hours to respect Celestrak limits
        download_needed = True
        if os.path.exists(TLE_CACHE):
            if (time.time() - os.path.getmtime(TLE_CACHE)) < 43200:
                print("[AETHER-V2] Utilizing cached orbital vectors (Low Resource Mode).")
                download_needed = False

        if download_needed:
            print("[AETHER-V2] Devouring live global TLE payload from Celestrak...")
            # Grabs ALL active satellites (Starlink, NASA, International)
            url = "https://celestrak.org/NORAD/elements/gp.php?GROUP=active&FORMAT=tle"
            try:
                response = requests.get(url, timeout=15)
                with open(TLE_CACHE, 'w') as f:
                    f.write(response.text)
            except Exception as e:
                print(f"[ERROR] Tether failed. {e}")
                return

        # Parse the localized payload into Skyfield Objects
        with open(TLE_CACHE, 'r') as f:
            lines = f.read().strip().split('\n')
            for i in range(0, len(lines), 3):
                if i + 2 < len(lines):
                    try:
                        name = lines[i].strip()
                        line1 = lines[i+1].strip()
                        line2 = lines[i+2].strip()
                        self.sats.append(EarthSatellite(line1, line2, name, self.ts))
                    except: continue
                    
        print(f"[AETHER-V2] Tactical Connection Locked: {len(self.sats)} Machines Orchestrated.")

    def calculate_swarm_vectors(self, t):
        """Vectorized computation for lightweight system consumption."""
        batch = []
        # Process in rapid sequence
        for sat in self.sats:
            try:
                geoc = sat.at(t)
                sub = wgs84.subpoint(geoc)
                
                # Keep calculations lightweight for mass rendering
                alt = sub.elevation.km
                if alt < 0: continue # Ignore anomalies
                
                batch.append({
                    'node_id': sat.name,
                    'lat': sub.latitude.degrees, 
                    'lon': sub.longitude.degrees,
                    'alt_km': alt,
                    'latency_ms': (alt / 299792.458) * 2 * 1000
                })
            except: continue
        return batch

    async def main_io_loop(self):
        """The 20-Second Rhythmic Output/Input Tether"""
        while True:
            t = self.ts.now()
            print(f"[AETHER-V2] Calculating pulse {self.io_count}...")
            
            # Compute new vectors
            batch = self.calculate_swarm_vectors(t)
            
            with self.lock:
                self.active_data = batch
            
            self.io_count += 1
            # 20 Second Refresh Cycle as requested
            await asyncio.sleep(20)

# --- THE FUTURISTIC REAL-TIME GUI ---
app = Dash(__name__)
orchestrator = GlobalAetherOrchestrator()

app.layout = html.Div(style={'backgroundColor': '#040d1a', 'color': '#00ffcc', 'padding': '10px', 'height': '100vh'}, children=[
    html.H2("AETHER-LINK V2: GLOBAL CONSTELLATION ORCHESTRATOR", style={'textAlign': 'center', 'fontFamily': 'Arial', 'letterSpacing': '2px'}),
    html.Div(id='terminal-output', style={'fontFamily': 'monospace', 'border': '1px solid #00ffcc', 'padding': '5px', 'marginBottom': '10px', 'textAlign': 'center', 'backgroundColor': '#02060d'}),
    
    # Mode Bar Buttons enabled for cropping, snapping images, zooming
    dcc.Graph(
        id='orbital-map', 
        style={'height': '80vh'},
        config={'displaylogo': False, 'scrollZoom': True, 'toImageButtonOptions': {'format': 'png', 'filename': 'aether_snap', 'scale': 2}}
    ),
    
    # 20,000 ms = 20 seconds
    dcc.Interval(id='refresh', interval=20000, n_intervals=0)
])

@app.callback(
    [Output('orbital-map', 'figure'), Output('terminal-output', 'children')],
    [Input('refresh', 'n_intervals')]
)
def update_view(n):
    with orchestrator.lock:
        current = orchestrator.active_data
    if not current: 
        return go.Figure(), "ESTABLISHING SIGNAL TETHER..."

    df = pd.DataFrame(current)
    
    # The Lightweight WebGL Plotly Engine for 10k+ points
    fig = go.Figure(data=go.Scattergeo(
        lat=df['lat'], lon=df['lon'],
        mode='markers',
        marker=dict(size=2, color='#00ffcc', opacity=0.7), # Tiny, lightweight markers
        text=df['node_id'] + '<br>Alt: ' + df['alt_km'].round(1).astype(str) + ' km<br>Latency: ' + df['latency_ms'].round(2).astype(str) + ' ms',
        hoverinfo='text'
    ))
    
    fig.update_geos(
        projection_type="orthographic", 
        showocean=True, oceancolor="rgb(2, 6, 13)",
        showland=True, landcolor="rgb(15, 20, 25)", 
        showcountries=True, countrycolor="rgb(40, 50, 60)",
        showframe=False,
        bgcolor="#040d1a"
    )
    
    fig.update_layout(
        template="plotly_dark", 
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor="#040d1a",
        uirevision='constant' # CRITICAL: Prevents camera reset on 20s data refresh
    )
    
    terminal_text = f"SYSTEM TETHER: ONLINE | ACTIVE NODES DISPLAYED: {len(df):,} | REFRESH CYCLE: 20s | GLOBAL LATENCY AVG: {df['latency_ms'].mean():.2f}ms"
    return fig, terminal_text

# --- SYSTEM INITIATION ---
def run_async_engine():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(orchestrator.main_io_loop())

if __name__ == "__main__":
    threading.Thread(target=run_async_engine, daemon=True).start()
    
    print("\n" + "="*60)
    print("AETHER-LINK V2: ORBITAL DISPLAY ENGAGED")
    print("Localhost Command Center: http://127.0.0.1:8050")
    print("="*60)
    
    app.run(debug=False, use_reloader=False)