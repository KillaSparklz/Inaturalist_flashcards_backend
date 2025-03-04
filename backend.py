from flask import Flask, jsonify, request
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

def get_bounded_observations(nelat=None, nelng=None, swlat=None, swlng=None, iconic_taxa=[], quality_grade=None, per_page=100, max_results=100):
    base_url = "https://api.inaturalist.org/v1/observations"
    observations = []
    page = 1

    while len(observations) < max_results:
        params = {
            "nelat": nelat,
            "nelng": nelng,
            "swlat": swlat,
            "swlng": swlng,
            "quality_grade": quality_grade,
            "iconic_taxa[]": iconic_taxa, 
            "has[]": "photos",
            "page": page,
            "per_page": per_page
        }

        #print(params)
        response = requests.get(base_url, params=params)

        if response.status_code != 200:
            print(f"Error: {response.status_code} - {response.text}")
            break
        
        data = response.json()
        results = data.get("results", [])

        if not results:
            break

        observations.extend(results)

        if len(results) < per_page:
            break

        page += 1

    return observations

@app.route('/api/observations', methods=['GET'])
def get_observations():
    print(request.args)
    try:
        nelat = request.args.get('nelat', type=float)
        nelng = request.args.get('nelng', type=float)
        swlat = request.args.get('swlat', type=float)
        swlng = request.args.get('swlng', type=float)
        quality_grade = request.args.get('qualityGrade', type=str)
        iconic_taxa = request.args.getlist('iconic_taxa[]')
    except TypeError:
        return jsonify({"error": "Invalid bounding box coordinates"}), 400


    if not all([nelat, nelng, swlat, swlng]):
        return jsonify({"error": "Missing bounding box coordinates"}), 400

    observations = get_bounded_observations(nelat=nelat, nelng=nelng, swlat=swlat, swlng=swlng, quality_grade=quality_grade, iconic_taxa=iconic_taxa, max_results=100)

    flashcards = []
    for obs in observations:
        if obs.get("taxon", {}):
            species_name = obs.get("taxon", {}).get("name")
            images = []
            for photo in obs.get("photos", [{}]):
                images.append(photo.get("url").replace("square", "original"))
            flashcards.append({
                "name": species_name,
                "images": images
            })
    return jsonify(flashcards)

if __name__ == '__main__':
    app.run(debug=True)