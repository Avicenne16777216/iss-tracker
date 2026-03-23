"""
ISS Tracker - Desktop GUI Application
Run with: python iss_gui.py
"""

import requests
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import threading
import webbrowser

class ISSTrackerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🚀 ISS Tracker")
        self.root.geometry("600x500")
        self.root.resizable(True, True)
        
        # Set style
        self.root.configure(bg='#2c3e50')
        
        self.setup_ui()
        self.update_data()
    
    def setup_ui(self):
        """Create all the GUI elements"""
        
        # Title Frame
        title_frame = tk.Frame(self.root, bg='#2c3e50')
        title_frame.pack(pady=10)
        
        title = tk.Label(title_frame, text="International Space Station Tracker", 
                         font=('Arial', 18, 'bold'), 
                         fg='#ecf0f1', bg='#2c3e50')
        title.pack()
        
        subtitle = tk.Label(title_frame, text="Live Position & Crew", 
                            font=('Arial', 10), 
                            fg='#bdc3c7', bg='#2c3e50')
        subtitle.pack()
        
        # Notebook (tabs)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Tab 1: Position
        self.position_frame = tk.Frame(self.notebook, bg='#ecf0f1')
        self.notebook.add(self.position_frame, text="📍 Position")
        self.setup_position_tab()
        
        # Tab 2: Crew
        self.crew_frame = tk.Frame(self.notebook, bg='#ecf0f1')
        self.notebook.add(self.crew_frame, text="👨‍🚀 Crew")
        self.setup_crew_tab()
        
        # Tab 3: Stats
        self.stats_frame = tk.Frame(self.notebook, bg='#ecf0f1')
        self.notebook.add(self.stats_frame, text="📊 Stats")
        self.setup_stats_tab()
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready - Last update: Never")
        status_bar = tk.Label(self.root, textvariable=self.status_var, 
                              bd=1, relief=tk.SUNKEN, anchor=tk.W,
                              bg='#34495e', fg='#ecf0f1')
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Refresh button
        refresh_btn = tk.Button(self.root, text="🔄 Refresh Data", 
                                command=self.update_data,
                                bg='#3498db', fg='white',
                                font=('Arial', 10, 'bold'),
                                padx=20, pady=5)
        refresh_btn.pack(pady=10)
    
    def setup_position_tab(self):
        """Setup the position tab"""
        
        # Position info
        self.pos_label = tk.Label(self.position_frame, 
                                   text="Fetching location...",
                                   font=('Arial', 14),
                                   bg='#ecf0f1', fg='#2c3e50')
        self.pos_label.pack(pady=20)
        
        # Coordinates
        self.coord_frame = tk.Frame(self.position_frame, bg='#ecf0f1')
        self.coord_frame.pack(pady=10)
        
        self.lat_label = tk.Label(self.coord_frame, text="Latitude: --", 
                                   font=('Arial', 12), bg='#ecf0f1')
        self.lat_label.pack()
        
        self.lon_label = tk.Label(self.coord_frame, text="Longitude: --", 
                                   font=('Arial', 12), bg='#ecf0f1')
        self.lon_label.pack()
        
        self.time_label = tk.Label(self.coord_frame, text="Time: --", 
                                    font=('Arial', 10), bg='#ecf0f1')
        self.time_label.pack(pady=5)
        
        self.location_label = tk.Label(self.coord_frame, text="Location: --", 
                                        font=('Arial', 10), bg='#ecf0f1')
        self.location_label.pack(pady=5)
        
        # Map button
        self.map_btn = tk.Button(self.position_frame, 
                                  text="🗺️ Open Map in Browser",
                                  command=self.open_map,
                                  bg='#27ae60', fg='white',
                                  font=('Arial', 10, 'bold'),
                                  padx=15, pady=5,
                                  state=tk.DISABLED)
        self.map_btn.pack(pady=20)
        
        # Distance info (optional - you can add your location)
        self.distance_label = tk.Label(self.position_frame, 
                                        text="",
                                        font=('Arial', 10),
                                        bg='#ecf0f1', fg='#7f8c8d')
        self.distance_label.pack(pady=10)
    
    def setup_crew_tab(self):
        """Setup the crew tab"""
        
        # Scrollable list for crew
        crew_frame = tk.Frame(self.crew_frame, bg='#ecf0f1')
        crew_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        scrollbar = tk.Scrollbar(crew_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.crew_listbox = tk.Listbox(crew_frame, yscrollcommand=scrollbar.set,
                                        font=('Arial', 11), height=12)
        self.crew_listbox.pack(side=tk.LEFT, fill='both', expand=True)
        scrollbar.config(command=self.crew_listbox.yview)
        
        # Other humans in space
        self.other_label = tk.Label(self.crew_frame, text="", 
                                     bg='#ecf0f1', fg='#7f8c8d',
                                     font=('Arial', 9))
        self.other_label.pack(pady=5)
    
    def setup_stats_tab(self):
        """Setup the stats tab"""
        
        self.stats_text = tk.Text(self.stats_frame, wrap=tk.WORD,
                                   font=('Arial', 10),
                                   bg='#ecf0f1', fg='#2c3e50')
        self.stats_text.pack(fill='both', expand=True, padx=10, pady=10)
        
    def update_data(self):
        """Fetch and update all data"""
        
        # Run in thread to avoid freezing GUI
        thread = threading.Thread(target=self._fetch_data)
        thread.daemon = True
        thread.start()
        
        self.status_var.set("Updating...")
        
    def _fetch_data(self):
        """Actually fetch data from APIs"""
        
        try:
            # Fetch location
            loc_data = self.fetch_location()
            
            # Fetch crew
            crew_data = self.fetch_crew()
            
            # Update GUI (need to use after() for thread safety)
            self.root.after(0, self.update_position_display, loc_data)
            self.root.after(0, self.update_crew_display, crew_data)
            self.root.after(0, self.update_stats_display)
            self.root.after(0, self.update_status, "Ready - Updated: " + datetime.now().strftime('%H:%M:%S'))
            
        except Exception as e:
            self.root.after(0, self.show_error, str(e))
    
    def fetch_location(self):
        """Get ISS location"""
        response = requests.get("http://api.open-notify.org/iss-now.json", timeout=10)
        response.raise_for_status()
        data = response.json()
        
        return {
            'latitude': data['iss_position']['latitude'],
            'longitude': data['iss_position']['longitude'],
            'timestamp': data['timestamp']
        }
    
    def fetch_crew(self):
        """Get crew data"""
        response = requests.get("http://api.open-notify.org/astros.json", timeout=10)
        response.raise_for_status()
        data = response.json()
        
        iss_crew = [p['name'] for p in data['people'] if p['craft'] == 'ISS']
        others = [f"{p['name']} ({p['craft']})" for p in data['people'] if p['craft'] != 'ISS']
        
        return {
            'iss_crew': iss_crew,
            'others': others,
            'total': data['number']
        }
    
    def update_position_display(self, data):
        """Update position tab with new data"""
        lat = data['latitude']
        lon = data['longitude']
        timestamp = data['timestamp']
        
        readable_time = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S UTC')
        
        self.lat_label.config(text=f"Latitude: {lat}°")
        self.lon_label.config(text=f"Longitude: {lon}°")
        self.time_label.config(text=f"Time: {readable_time}")
        
        # Simple location guess
        lat_f = float(lat)
        lon_f = float(lon)
        
        if -30 < lat_f < 30 and -20 < lon_f < 50:
            location = "🌍 Over Africa (probably)"
        elif lat_f > 45 and lon_f < -60:
            location = "🌎 Over North America (probably)"
        elif lat_f < -30 and lon_f > 100:
            location = "🌏 Over Australia/South Pacific (probably)"
        else:
            location = "🌊 Over open ocean"
        
        self.location_label.config(text=f"Location: {location}")
        
        # Store for map button
        self.current_lat = lat
        self.current_lon = lon
        self.map_btn.config(state=tk.NORMAL)
        
    def update_crew_display(self, data):
        """Update crew tab with new data"""
        self.crew_listbox.delete(0, tk.END)
        
        for astronaut in data['iss_crew']:
            self.crew_listbox.insert(tk.END, f"👨‍🚀 {astronaut}")
        
        if data['others']:
            self.other_label.config(text=f"Other humans in space: {len(data['others'])}")
        else:
            self.other_label.config(text="No other humans in space")
    
    def update_stats_display(self):
        """Update stats tab"""
        import os
        import pandas as pd
        
        self.stats_text.delete(1.0, tk.END)
        
        if os.path.exists('iss_tracking.csv'):
            df = pd.read_csv('iss_tracking.csv')
            
            stats = f"""
=== ISS TRACKING STATISTICS ===

Total records: {len(df)}
First track: {df['timestamp_readable'].iloc[0]}
Last track:  {df['timestamp_readable'].iloc[-1]}

Latitude range: {df['latitude'].min():.2f}° to {df['latitude'].max():.2f}°
Longitude range: {df['longitude'].min():.2f}° to {df['longitude'].max():.2f}°

Days tracked: {pd.to_datetime(df['timestamp_readable']).dt.date.nunique()}
"""
            self.stats_text.insert(1.0, stats)
        else:
            self.stats_text.insert(1.0, "No tracking data yet. Run the tracker and save some positions!")
    
    def open_map(self):
        """Open folium map in browser"""
        try:
            import folium
            
            # Create temporary map
            m = folium.Map(
                location=[float(self.current_lat), float(self.current_lon)],
                zoom_start=4,
                tiles='CartoDB positron'
            )
            
            folium.Marker(
                [float(self.current_lat), float(self.current_lon)],
                popup=f'ISS<br>Lat: {self.current_lat}°<br>Lon: {self.current_lon}°',
                icon=folium.Icon(color='red', icon='info-sign')
            ).add_to(m)
            
            folium.Circle(
                [float(self.current_lat), float(self.current_lon)],
                radius=500000,
                color='red',
                fill=True,
                popup='ISS Coverage Area'
            ).add_to(m)
            
            map_file = "iss_temp_map.html"
            m.save(map_file)
            
            webbrowser.open(map_file)
            
        except Exception as e:
            messagebox.showerror("Error", f"Could not create map: {e}")
    
    def update_status(self, message):
        self.status_var.set(message)
    
    def show_error(self, error):
        messagebox.showerror("Error", f"Failed to fetch data: {error}")
        self.status_var.set("Error - Check connection")


if __name__ == "__main__":
    root = tk.Tk()
    app = ISSTrackerGUI(root)
    root.mainloop()