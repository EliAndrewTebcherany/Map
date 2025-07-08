from flask import Flask, render_template, request
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import folium

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def map_viewer():
    if request.method == 'POST':
        location_name1 = request.form.get('location1')
        location_name2 = request.form.get('location2')
        show_line = 'show_line' in request.form  # Check if the button was clicked
        
        # Initialize map with default view
        m = folium.Map(location=[0, 0], zoom_start=2, tiles='cartodbpositron')
        locations_found = False
        distance_km = None
        location1_coords = None
        location2_coords = None
        
        if location_name1:
            geolocator = Nominatim(user_agent="my_map_app")
            location1 = geolocator.geocode(location_name1)
            
            if location1:
                location1_coords = (location1.latitude, location1.longitude)
                folium.Marker(
                    location1_coords,
                    popup=f"Location 1: {location_name1}",
                    icon=folium.Icon(color='blue')
                ).add_to(m)
                locations_found = True
                # Center the map on the first location if only one is provided
                if not location_name2:
                    m.location = [location1.latitude, location1.longitude]
                    m.zoom_start = 15
        
        if location_name2:
            geolocator = Nominatim(user_agent="my_map_app")
            location2 = geolocator.geocode(location_name2)
            
            if location2:
                location2_coords = (location2.latitude, location2.longitude)
                folium.Marker(
                    location2_coords,
                    popup=f"Location 2: {location_name2}",
                    icon=folium.Icon(color='red')
                ).add_to(m)
                locations_found = True
                # If both locations are found, adjust the view to show both
                if location_name1 and location1:
                    bounds = [
                        [location1.latitude, location1.longitude],
                        [location2.latitude, location2.longitude]
                    ]
                    m.fit_bounds(bounds)
                else:
                    # Center on the second location if only it is provided
                    m.location = [location2.latitude, location2.longitude]
                    m.zoom_start = 15
        
        # Add line and distance calculation if both locations exist and button was clicked
        if show_line and location1_coords and location2_coords:
            # Draw line between points
            folium.PolyLine(
                locations=[location1_coords, location2_coords],
                color='green',
                weight=2,
                dash_array='5, 5'
            ).add_to(m)
            
            # Calculate distance
            distance_km = round(geodesic(location1_coords, location2_coords).km, 2)
            
            # Add midpoint marker with distance info
            midpoint = [
                (location1_coords[0] + location2_coords[0]) / 2,
                (location1_coords[1] + location2_coords[1]) / 2
            ]
            folium.Marker(
                midpoint,
                popup=f"Distance: {distance_km} km",
                icon=folium.DivIcon(html=f"""<div style="font-size: 12pt; color: black">{distance_km} km</div>""")
            ).add_to(m)
        
        if locations_found:
            map_html = m._repr_html_()
            return render_template('map.html', 
                                map_html=map_html,
                                location1=location_name1,
                                location2=location_name2,
                                distance=distance_km,
                                show_line=show_line)
        
        return render_template('map.html', error="No locations found")
    
    return render_template('map.html')

if __name__ == '__main__':
    # Run the app on all available network interfaces
    app.run(host='0.0.0.0', port=5000, debug=True)