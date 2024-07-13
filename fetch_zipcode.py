import requests

def get_zip_code_google(lat, lng, api_key):
    url = f"https://maps.googleapis.com/maps/api/geocode/json?latlng={lat},{lng}&key={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if 'results' in data and len(data['results']) > 0:
            for component in data['results'][0]['address_components']:
                if 'postal_code' in component['types']:
                    return component['long_name']
    return None

# Example usage
lat = 17.528241
lng = 78.387817
api_key = 'AIzaSyBnZeMv7ivrYEy4kMR7ewMoWcuabfr06Hs'
zip_code = get_zip_code_google(lat, lng, api_key)
print(f"ZIP Code: {zip_code}")
