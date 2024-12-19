from dotenv import load_dotenv
import os
import googlemaps
import datetime
import folium

# Load environment variables
load_dotenv()

# Get the environment variables
API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

# Initialize the Google Maps client
gmaps = googlemaps.Client(key=API_KEY)

def get_route_info(source, source_county, destination, destination_county, mode):
    """Fetch and print route information including traffic conditions."""
    
    valid_modes = ["walking", "driving", "bicycling", "transit"]
    if mode not in valid_modes:
        print(f"Invalid mode. Please choose from: {', '.join(valid_modes)}")
        return

    base_params = {
        "origin": f"{source}, {source_county}",
        "destination": f"{destination}, {destination_county}",
        "mode": mode,
        "departure_time": datetime.datetime.now()
    }

    try:
        if mode == "driving":
            traffic_models = ["best_guess", "optimistic", "pessimistic"]
            for model in traffic_models:
                params = base_params.copy()
                params["traffic_model"] = model
                directions_result = gmaps.directions(**params)

                if not directions_result:
                    print(f"No route found for traffic model: {model}.")
                    continue

                # Extract and print route and traffic details
                for leg in directions_result[0]['legs']:
                    start_address = leg['start_address']
                    end_address = leg['end_address']
                    duration = leg['duration']['text']
                    duration_in_traffic = leg.get('duration_in_traffic', {}).get('text', "Not available")
                    
                    print(f"Traffic model: {model}")
                    print(f"Route: {start_address} to {end_address}")
                    print(f"Normal Duration: {duration}")
                    print(f"Duration in Traffic ({model}): {duration_in_traffic}")
                    print("-" * 30)

                # Visualize route with traffic information
                visualize_route(directions_result[0], traffic_model=model)
        else:
            directions_result = gmaps.directions(**base_params)
            if not directions_result:
                print("No route found. Please check the locations and try again.")
                return

            for leg in directions_result[0]['legs']:
                start_address = leg['start_address']
                end_address = leg['end_address']
                duration = leg['duration']['text']

                print(f"Route: {start_address} to {end_address}")
                print(f"Duration: {duration}")
                print("-" * 30)

            visualize_route(directions_result[0])

    except googlemaps.exceptions.ApiError as api_err:
        print(f"Google Maps API error: {api_err}")
    except googlemaps.exceptions.TransportError as transport_err:
        print(f"Transport error: {transport_err}")
    except googlemaps.exceptions.Timeout as timeout_err:
        print(f"Request timed out: {timeout_err}")
    except googlemaps.exceptions.HTTPError as http_err:
        print(f"HTTP error: {http_err}")
    except KeyError as key_err:
        print(f"Unexpected response structure: Missing key {key_err}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        
def visualize_route(route, traffic_model=None):
    """Visualize the best route on a map using Folium, including traffic details."""
    try:
        steps = route['overview_polyline']['points']
        decoded_points = googlemaps.convert.decode_polyline(steps)
        start_location = route['legs'][0]['start_location']
        end_location = route['legs'][0]['end_location']

        # Create a Folium map centered at the starting location
        map_route = folium.Map(location=[start_location['lat'], start_location['lng']], zoom_start=13)

        # Add the route to the map
        folium.PolyLine([(point['lat'], point['lng']) for point in decoded_points], color="blue", weight=5).add_to(map_route)

        # Add markers for start and end points
        folium.Marker([start_location['lat'], start_location['lng']], popup="Start", icon=folium.Icon(color="green")).add_to(map_route)
        folium.Marker([end_location['lat'], end_location['lng']], popup="End", icon=folium.Icon(color="red")).add_to(map_route)

        # Add traffic information if available
        if traffic_model:
            folium.Marker(
                [start_location['lat'], start_location['lng']],
                popup=f"Traffic Model: {traffic_model}",
                icon=folium.Icon(color="orange")
            ).add_to(map_route)

        # Save map to file
        map_file = f"route_map_{traffic_model or 'default'}.html"
        map_route.save(map_file)
        print(f"Route visualization saved as '{map_file}'. Open it in a browser to view.")

    except Exception as e:
        print(f"An error occurred while visualizing the route: {e}")

# Get user input
try:
    source = input("Enter the starting location: ")
    source_county = "Nairobi"  # Assume the source is in Nairobi County
    destination = input("Enter the destination: ")
    destination_county = "Nairobi"  # Assume the source is in Nairobi County
    mode = input("Enter the mode of transportation (walking, driving, bicycling, transit): ").lower()

    # Call the function
    get_route_info(source, source_county, destination, destination_county, mode)

except Exception as e:
    print(f"An error occurred during user input: {e}")