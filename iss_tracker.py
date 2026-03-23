import requests
import pandas as pd
from datetime import datetime
import os

# ================================================= MAIN FUNCTIONS ==============================================

def get_iss_crew():
    """Fetch and display the names of astronauts currently on the ISS."""
    
    url = "http://api.open-notify.org/astros.json"
    
    try:
        print("Contacting NASA API...")
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        # Check if the response has the expected structure
        if 'people' not in data or 'number' not in data:
            print("❌ Unexpected API response format")
            return
        
        total_people = data['number']
        print(f"Total people in space: {total_people}")
        
        all_people = data['people']
        
        # Verify that all_people is a list
        if not isinstance(all_people, list):
            print(f"❌ Expected 'people' to be a list, but got {type(all_people).__name__}")
            return
        
        iss_crew = []
        for person in all_people:
            if person['craft'] == 'ISS':
                iss_crew.append(person['name'])
        
        print("\n--- Current ISS Crew ---")
        if iss_crew:
            for astronaut in iss_crew:
                print(f"👨‍🚀 {astronaut}")
        else:
            print("🚨 No astronauts currently on ISS")
        print("------------------------")
        
        # Bonus: Show who's on other spacecraft
        other_craft = []
        for person in all_people:
            if person['craft'] != 'ISS':
                other_craft.append(f"{person['name']} ({person['craft']})")
        
        if other_craft:
            print("\n--- Other Humans in Space ---")
            for person in other_craft:
                print(f"🛰️ {person}")
    
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to the API. Check your internet connection.")
    except requests.exceptions.Timeout:
        print("❌ The request timed out. The API might be slow or unresponsive.")
    except requests.exceptions.HTTPError as e:
        print(f"❌ HTTP Error occurred: {e}")
    except Exception as e:
        print(f"❌ An unexpected error occurred: {e}")

# =====================================================================================================================

def create_iss_map(latitude, longitude, timestamp):
    """Create an HTML map showing the current ISS position."""
    
    try:
        import folium
        
        # Create a map centered at the ISS position
        iss_map = folium.Map(
            location=[float(latitude), float(longitude)],
            zoom_start=4,
            control_scale=True,
            tiles='CartoDB positron'
        )
        
        # Add a marker for the ISS
        folium.Marker(
            [float(latitude), float(longitude)],
            popup=f'ISS<br>Lat: {latitude}°<br>Lon: {longitude}°',
            icon=folium.Icon(color='red', icon='info-sign')
        ).add_to(iss_map)
        
        # Add a circle to highlight the area
        folium.Circle(
            [float(latitude), float(longitude)],
            radius=500000,  # 500 km radius
            color='red',
            fill=True,
            popup='ISS Coverage Area'
        ).add_to(iss_map)
        
        # Save the map with full path
        map_filename = f"iss_location_{timestamp}.html"
        iss_map.save(map_filename)
        
        full_path = os.path.abspath(map_filename)
        print(f"   🗺️  Map saved to: {full_path}")
        
    except ImportError:
        print("   ⚠️  Folium not installed. Run: pip install folium")
    except Exception as e:
        print(f"   ⚠️  Could not create map: {e}")

# =====================================================================================================================

def save_position_to_csv(latitude, longitude, timestamp):
    """Save ISS position data to a CSV file for tracking over time."""
    
    # Convert timestamp to readable format
    readable_time = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
    
    # Create a DataFrame with the new data
    new_data = pd.DataFrame([{
        'timestamp_unix': timestamp,
        'timestamp_readable': readable_time,
        'latitude': float(latitude),
        'longitude': float(longitude)
    }])
    
    # File name for our tracking data
    filename = 'iss_tracking.csv'
    
    # Check if file exists
    if os.path.exists(filename):
        # Append to existing file
        existing_data = pd.read_csv(filename)
        updated_data = pd.concat([existing_data, new_data], ignore_index=True)
        updated_data.to_csv(filename, index=False)
        print(f"   📊 Appended to {filename} (Total records: {len(updated_data)})")
    else:
        # Create new file
        new_data.to_csv(filename, index=False)
        print(f"   📊 Created new tracking file: {filename}")

# ===================================================================================================================

def get_iss_location():
    """Fetch and display the current latitude and longitude of the ISS."""
    
    url = "http://api.open-notify.org/iss-now.json"
    
    try:
        print("\n" + "="*40)
        print("📍 ISS LOCATION TRACKER")
        print("="*40)
        
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        # The location data is nested inside the 'iss_position' key
        iss_position = data['iss_position']
        
        # Extract latitude and longitude (they come as strings)
        latitude = iss_position['latitude']
        longitude = iss_position['longitude']
        
        # Get the timestamp and convert it to readable format
        timestamp = data['timestamp']
        readable_time = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S UTC')
        
        print(f"\n🛰️  Current ISS Position:")
        print(f"   Latitude:  {latitude}°")
        print(f"   Longitude: {longitude}°")
        print(f"   Time:      {readable_time}")
        
        # Create a map with this position
        create_iss_map(latitude, longitude, timestamp)
        
        # Save to CSV for tracking
        save_position_to_csv(latitude, longitude, timestamp)

        # Quick and dirty land/ocean check
        if -30 < float(latitude) < 30 and -20 < float(longitude) < 50:
            print("   Location:  🌍 Over Africa (probably)")
        elif float(latitude) > 45 and float(longitude) < -60:
            print("   Location:  🌎 Over North America (probably)")
        elif float(latitude) < -30 and float(longitude) > 100:
            print("   Location:  🌏 Over Australia/South Pacific (probably)")
        else:
            print("   Location:  🌊 Over open ocean (71% chance I'm right!)")
        
    except KeyError as e:
        print(f"❌ Unexpected data structure: Missing key {e}")
    except Exception as e:
        print(f"❌ Error fetching ISS location: {e}")

# ===================================================================================================================

def show_tracking_summary():
    """Display a summary of all tracked ISS positions."""
    
    filename = 'iss_tracking.csv'
    
    if not os.path.exists(filename):
        print("No tracking data yet. Run the tracker first!")
        return
    
    df = pd.read_csv(filename)
    
    print("\n" + "="*50)
    print("📈 ISS TRACKING SUMMARY")
    print("="*50)
    print(f"Total records: {len(df)}")
    print(f"First track: {df['timestamp_readable'].iloc[0]}")
    print(f"Last track:  {df['timestamp_readable'].iloc[-1]}")
    
    # Show latitude range
    lat_min = df['latitude'].min()
    lat_max = df['latitude'].max()
    print(f"Latitude range: {lat_min:.2f}° to {lat_max:.2f}°")
    
    # Show longitude range
    lon_min = df['longitude'].min()
    lon_max = df['longitude'].max()
    print(f"Longitude range: {lon_min:.2f}° to {lon_max:.2f}°")
    
    # Count unique dates tracked
    dates = pd.to_datetime(df['timestamp_readable']).dt.date
    unique_dates = dates.nunique()
    print(f"Days tracked: {unique_dates}")
    print("="*50)

# ===================================================================================================================

if __name__ == "__main__":
    get_iss_crew()
    get_iss_location()
    show_tracking_summary()