
import ray

# max_retries: retry up to 3 times on failure (e.g. transient network errors,
# rate-limit 429s) before giving up on this task.
# retry_exceptions=True: without this, Ray only retries on worker crashes,
# not on exceptions raised inside the function (like resp.raise_for_status()).
@ray.remote(max_retries=3, retry_exceptions=True)
def fetch_streams(access_token, activity_id):
    """Fetch time-series data (heart rate, power, GPS, etc.) for one activity.
    Runs as an independent Ray task so many activities can be fetched
    concurrently instead of sequentially."""
    resp = requests.get(
        f"https://www.strava.com/api/v3/activities/{activity_id}/streams",
        headers={"Authorization": f"Bearer {access_token}"},
        params={
            "keys": "time,heartrate,watts,cadence,altitude,latlng",
            "key_by_type": "true",  # returns a dict keyed by stream type instead of a list
        },
    )
    resp.raise_for_status()
    # Return the activity_id alongside the data so results can be matched
    # back up after ray.get() gathers them.
    return activity_id, resp.json()