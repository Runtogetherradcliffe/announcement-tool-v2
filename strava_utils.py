
import requests
import gpxpy
import gpxpy.gpx
from io import BytesIO
from urllib.parse import urlparse

def refresh_strava_token(refresh_token, client_id, client_secret):
    response = requests.post(
        "https://www.strava.com/oauth/token",
        data={
            "client_id": client_id,
            "client_secret": client_secret,
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
        },
    )
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        raise Exception(f"Failed to refresh token: {response.text}")

def extract_route_id_from_url(url):
    parsed_url = urlparse(url)
    if "strava.com" in parsed_url.netloc and "/routes/" in parsed_url.path:
        return parsed_url.path.split("/routes/")[-1]
    return None

def download_gpx_from_strava_route(route_url, access_token):
    route_id = extract_route_id_from_url(route_url)
    if not route_id:
        raise ValueError("Invalid Strava route URL")
    gpx_url = f"https://www.strava.com/api/v3/routes/{route_id}/export_gpx"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(gpx_url, headers=headers)
    if response.status_code != 200:
        raise Exception(f"Failed to download GPX: {response.text}")
    return gpxpy.parse(BytesIO(response.content))

def extract_landmarks_from_gpx(gpx_data, access_token=None):
    points = []
    for track in gpx_data.tracks:
        for segment in track.segments:
            for point in segment.points:
                points.append((point.latitude, point.longitude))
    return points[:3]  # placeholder: ideally would return place names

def describe_gpx_route(gpx_data):
    try:
        landmarks = set()
        for track in gpx_data.tracks:
            for segment in track.segments:
                for point in segment.points:
                    if hasattr(point, 'address') and point.address:
                        landmarks.add(point.address)
        if not landmarks:
            return "No landmarks found along the route."
        sample = list(landmarks)[:3]
        return "This route passes through " + ", ".join(sample) + "..."
    except Exception as e:
        return f"Could not describe GPX route: {e}"
