
import requests
import gpxpy
import gpxpy.gpx

def refresh_strava_token(client_id, client_secret, refresh_token):
    response = requests.post(
        "https://www.strava.com/api/v3/oauth/token",
        data={
            "client_id": client_id,
            "client_secret": client_secret,
            "grant_type": "refresh_token",
            "refresh_token": refresh_token
        },
    )
    return response.json()

def download_gpx_from_strava_route(route_url, access_token):
    try:
        route_id = route_url.strip("/").split("/")[-1]
        gpx_url = f"https://www.strava.com/api/v3/routes/{route_id}/export_gpx"

        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.get(gpx_url, headers=headers)
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(f"Error downloading GPX: {e}")
        return None

def extract_landmarks_from_gpx(gpx_data, access_token=None):
    try:
        gpx = gpxpy.parse(gpx_data)
        points = gpx.tracks[0].segments[0].points if gpx.tracks else []
        latlon_pairs = [(p.latitude, p.longitude) for p in points[::len(points)//10 or 1]]

        landmarks = []
        for lat, lon in latlon_pairs:
            res = requests.get(
                "https://nominatim.openstreetmap.org/reverse",
                params={"format": "json", "lat": lat, "lon": lon, "zoom": 14, "addressdetails": 1},
                headers={"User-Agent": "RunTogetherApp"}
            )
            if res.status_code == 200:
                data = res.json()
                name = data.get("name") or data.get("display_name")
                if name and name not in landmarks:
                    landmarks.append(name.split(",")[0])

        return " 🌍 Route highlights: " + ", ".join(landmarks[:5]) if landmarks else ""
    except Exception as e:
        print(f"Error extracting landmarks: {e}")
        return ""
