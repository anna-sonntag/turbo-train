import ray
import requests
from requests.exceptions import HTTPError

@ray.remote(max_retries=3, retry_exceptions=True)

def fetch_streams(access_token, activity_id):
    # Fetch time-series data (heart rate, power, GPS, etc.) for one activity.
    # Runs as an independent Ray task so many activities can be fetched
    # concurrently instead of sequentially."""

    resp = requests.get(
    f"https://www.strava.com/api/v3/activities/{activity_id}/streams",
    headers={"Authorization": f"Bearer {access_token}"},
    params={
        "keys": "time,heartrate,watts,cadence,altitude,latlng,velocity_smooth,grade_smooth,distance,temp,moving",
        "key_by_type": "true",
    },
)
    if 'errors' in resp.json():
        print(activity_id, "No Data")
        pass 
    else: 
        return activity_id, resp.json()       

    

    