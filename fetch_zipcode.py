from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

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

@app.route('/get_zip_code', methods=['GET','POST'])
def get_zip_code():
    lat = request.args.get('lat')
    lng = request.args.get('lng')
    
    # Validate and convert latitude and longitude to float
    try:
        lat = float(lat)
        lng = float(lng)
    except (ValueError, TypeError):
        return jsonify({'error': 'Invalid latitude or longitude'}), 400

    api_key = 'AIzaSyBnZeMv7ivrYEy4kMR7ewMoWcuabfr06Hs'  # Replace with your actual API key
    zip_code = get_zip_code_google(lat, lng, api_key)
    
    if zip_code:
        return jsonify({'zipCode': zip_code}), 200
    else:
        return jsonify({'error': 'Unable to fetch ZIP code'}), 400

if __name__ == '__main__':
    app.run('0.0.0.0', debug=True)
