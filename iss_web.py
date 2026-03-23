"""
ISS Tracker - Web Dashboard
Run with: python iss_web.py
Then open browser to: http://127.0.0.1:5000
"""

from flask import Flask, render_template_string, jsonify, send_file
import requests
from datetime import datetime
import pandas as pd
import os
import folium
from io import BytesIO

app = Flask(__name__)

# HTML Template
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>🚀 ISS Tracker Dashboard</title>
    <meta http-equiv="refresh" content="30">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
            color: white;
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        h1 {
            text-align: center;
            margin-bottom: 10px;
            font-size: 2.5em;
        }
        .subtitle {
            text-align: center;
            color: #bdc3c7;
            margin-bottom: 30px;
        }
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }
        .card {
            background: rgba(255,255,255,0.1);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .card h2 {
            margin-bottom: 15px;
            border-bottom: 2px solid #3498db;
            display: inline-block;
        }
        .coord {
            font-size: 2em;
            font-family: monospace;
            margin: 10px 0;
        }
        .timestamp {
            color: #bdc3c7;
            font-size: 0.9em;
        }
        .crew-list {
            list-style: none;
            padding: 0;
        }
        .crew-list li {
            padding: 8px;
            border-bottom: 1px solid rgba(255,255,255,0.2);
            font-size: 1.1em;
        }
        .stats-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
        }
        .stat {
            background: rgba(0,0,0,0.3);
            padding: 10px;
            border-radius: 8px;
            text-align: center;
        }
        .stat-value {
            font-size: 1.5em;
            font-weight: bold;
            color: #3498db;
        }
        .location-badge {
            display: inline-block;
            background: #27ae60;
            padding: 5px 10px;
            border-radius: 20px;
            margin-top: 10px;
            font-size: 0.9em;
        }
        .refresh {
            text-align: center;
            color: #95a5a6;
            font-size: 0.8em;
            margin-top: 20px;
        }
        .map-link {
            display: inline-block;
            margin-top: 15px;
            background: #3498db;
            color: white;
            padding: 8px 15px;
            text-decoration: none;
            border-radius: 8px;
        }
        .map-link:hover {
            background: #2980b9;
        }
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.5; }
            100% { opacity: 1; }
        }
        .live {
            animation: pulse 2s infinite;
            color: #e74c3c;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🛰️ International Space Station Tracker</h1>
        <div class="subtitle">Live Tracking Dashboard | Auto-refreshes every 30 seconds</div>
        
        <div class="grid">
            <!-- Position Card -->
            <div class="card">
                <h2>📍 Current Position</h2>
                <div class="coord">
                    <div>Latitude: <span id="lat">{{ location.latitude }}</span>°</div>
                    <div>Longitude: <span id="lon">{{ location.longitude }}</span>°</div>
                </div>
                <div class="timestamp">Time: {{ location.time }}</div>
                <div>
                    <span class="location-badge">{{ location.region }}</span>
                </div>
                <br>
                <a href="/map" target="_blank" class="map-link">🗺️ Open Interactive Map</a>
            </div>
            
            <!-- Crew Card -->
            <div class="card">
                <h2>👨‍🚀 ISS Crew <span class="live">● LIVE</span></h2>
                <ul class="crew-list">
                    {% for astronaut in crew.iss_crew %}
                    <li>🚀 {{ astronaut }}</li>
                    {% else %}
                    <li>No crew data available</li>
                    {% endfor %}
                </ul>
                {% if crew.others %}
                <hr style="margin: 15px 0; border-color: rgba(255,255,255,0.2);">
                <h3>🛰️ Other Humans in Space</h3>
                <ul class="crew-list">
                    {% for person in crew.others %}
                    <li>{{ person }}</li>
                    {% endfor %}
                </ul>
                {% endif %}
            </div>
            
            <!-- Statistics Card -->
            <div class="card">
                <h2>📊 Tracking Statistics</h2>
                <div class="stats-grid">
                    <div class="stat">
                        <div class="stat-value">{{ stats.total_records }}</div>
                        <div>Total Records</div>
                    </div>
                    <div class="stat">
                        <div class="stat-value">{{ stats.days_tracked }}</div>
                        <div>Days Tracked</div>
                    </div>
                    <div class="stat">
                        <div class="stat-value">{{ stats.lat_min }}°</div>
                        <div>Min Latitude</div>
                    </div>
                    <div class="stat">
                        <div class="stat-value">{{ stats.lat_max }}°</div>
                        <div>Max Latitude</div>
                    </div>
                    <div class="stat">
                        <div class="stat-value">{{ stats.lon_min }}°</div>
                        <div>Min Longitude</div>
                    </div>
                    <div class="stat">
                        <div class="stat-value">{{ stats.lon_max }}°</div>
                        <div>Max Longitude</div>
                    </div>
                </div>
                <div class="timestamp" style="margin-top: 15px;">
                    First track: {{ stats.first_track }}<br>
                    Last track: {{ stats.last_track }}
                </div>
            </div>
        </div>
        
        <div class="refresh">
            🔄 Page auto-refreshes every 30 seconds | Last update: {{ now }}
        </div>
    </div>
</body>
</html>
'''

def get_location():
    """Fetch current ISS location"""
    try:
        response = requests.get("http://api.open-notify.org/iss-now.json", timeout=10)
        data = response.json()
        
        lat = float(data['iss_position']['latitude'])
        lon = float(data['iss_position']['longitude'])
        
        # Simple region guess
        if -30 < lat < 30 and -20 < lon < 50:
            region = "🌍 Over Africa (probably)"
        elif lat > 45 and lon < -60:
            region = "🌎 Over North America (probably)"
        elif lat < -30 and lon > 100:
            region = "🌏 Over Australia/South Pacific (probably)"
        else:
            region = "🌊 Over open ocean"
        
        return {
            'latitude': lat,
            'longitude': lon,
            'time': datetime.fromtimestamp(data['timestamp']).strftime('%Y-%m-%d %H:%M:%S UTC'),
            'region': region
        }
    except Exception as e:
        return {'latitude': '--', 'longitude': '--', 'time': 'Error', 'region': 'Error fetching data'}

def get_crew():
    """Fetch crew data"""
    try:
        response = requests.get("http://api.open-notify.org/astros.json", timeout=10)
        data = response.json()
        
        iss_crew = [p['name'] for p in data['people'] if p['craft'] == 'ISS']
        others = [f"{p['name']} ({p['craft']})" for p in data['people'] if p['craft'] != 'ISS']
        
        return {
            'iss_crew': iss_crew,
            'others': others,
            'total': data['number']
        }
    except Exception as e:
        return {'iss_crew': [], 'others': [], 'total': 0}

def get_stats():
    """Get tracking statistics from CSV"""
    if not os.path.exists('iss_tracking.csv'):
        return {
            'total_records': 0,
            'days_tracked': 0,
            'lat_min': '--',
            'lat_max': '--',
            'lon_min': '--',
            'lon_max': '--',
            'first_track': 'No data',
            'last_track': 'No data'
        }
    
    try:
        df = pd.read_csv('iss_tracking.csv')
        
        return {
            'total_records': len(df),
            'days_tracked': pd.to_datetime(df['timestamp_readable']).dt.date.nunique(),
            'lat_min': round(df['latitude'].min(), 2),
            'lat_max': round(df['latitude'].max(), 2),
            'lon_min': round(df['longitude'].min(), 2),
            'lon_max': round(df['longitude'].max(), 2),
            'first_track': df['timestamp_readable'].iloc[0],
            'last_track': df['timestamp_readable'].iloc[-1]
        }
    except Exception:
        return {
            'total_records': 0,
            'days_tracked': 0,
            'lat_min': '--',
            'lat_max': '--',
            'lon_min': '--',
            'lon_max': '--',
            'first_track': 'Error',
            'last_track': 'Error'
        }

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template_string(
        HTML_TEMPLATE,
        location=get_location(),
        crew=get_crew(),
        stats=get_stats(),
        now=datetime.now().strftime('%H:%M:%S')
    )

@app.route('/map')
def show_map():
    """Generate and serve an interactive map directly"""
    try:
        location = get_location()
        lat = location['latitude']
        lon = location['longitude']
        
        # Check if we got valid coordinates
        if not isinstance(lat, float) or not isinstance(lon, float):
            return "<h3>Error: Could not fetch ISS coordinates</h3><p>Please check your internet connection and try again.</p>", 500
        
        # Create map
        m = folium.Map(
            location=[lat, lon],
            zoom_start=4,
            tiles='CartoDB positron'
        )
        
        # Add marker
        folium.Marker(
            [lat, lon],
            popup=f'ISS<br>Lat: {lat}°<br>Lon: {lon}°',
            icon=folium.Icon(color='red', icon='info-sign')
        ).add_to(m)
        
        # Add coverage circle
        folium.Circle(
            [lat, lon],
            radius=500000,
            color='red',
            fill=True,
            fill_opacity=0.2,
            popup='ISS Coverage Area (~500 km radius)'
        ).add_to(m)
        
        # Add timestamp to the map
        folium.Marker(
            [lat + 5, lon],  # Offset to avoid overlapping
            popup=f"Last updated: {location['time']}",
            icon=folium.Icon(color='gray', icon='info')
        ).add_to(m)
        
        # Return the map directly as HTML
        return m._repr_html_()
        
    except Exception as e:
        return f"<h3>Error creating map: {e}</h3><p>Please try again.</p>", 500

@app.route('/map-save')
def save_map():
    """Alternative: Save map as file and serve it"""
    try:
        location = get_location()
        lat = location['latitude']
        lon = location['longitude']
        
        if not isinstance(lat, float) or not isinstance(lon, float):
            return "Error fetching coordinates", 500
        
        m = folium.Map(
            location=[lat, lon],
            zoom_start=4,
            tiles='CartoDB positron'
        )
        
        folium.Marker(
            [lat, lon],
            popup=f'ISS<br>Lat: {lat}°<br>Lon: {lon}°',
            icon=folium.Icon(color='red', icon='info-sign')
        ).add_to(m)
        
        folium.Circle(
            [lat, lon],
            radius=500000,
            color='red',
            fill=True,
            fill_opacity=0.2,
            popup='ISS Coverage Area'
        ).add_to(m)
        
        # Save to a temporary file
        map_file = f"iss_map_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        m.save(map_file)
        
        # Serve the file
        return send_file(map_file, as_attachment=False)
        
    except Exception as e:
        return f"Error: {e}", 500

@app.route('/api/location')
def api_location():
    """JSON API endpoint for location"""
    return jsonify(get_location())

@app.route('/api/crew')
def api_crew():
    """JSON API endpoint for crew"""
    return jsonify(get_crew())

if __name__ == '__main__':
    print("="*50)
    print("🚀 ISS TRACKER WEB DASHBOARD")
    print("="*50)
    print("Open your browser to: http://127.0.0.1:5000")
    print("Click 'Open Interactive Map' to see the ISS location on a map")
    print("The page auto-refreshes every 30 seconds")
    print("Press Ctrl+C to stop the server")
    print("="*50)
    app.run(debug=True, host='127.0.0.1', port=5000)