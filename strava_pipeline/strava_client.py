import requests

def list_new_activities(access_token, after_ts):
    # Fetch all activities created after `after_ts`.
    activities = []
    page = 1
    while True:
        resp = requests.get(
            "https://www.strava.com/api/v3/athlete/activities",
            headers={"Authorization": f"Bearer {access_token}"},
            params={"after": after_ts, "per_page": 200, "page": page},
        )
        resp.raise_for_status()
        batch = resp.json()
        if not batch:
            break  # empty page means we've reached the end
        activities.extend(batch)
        page += 1
    return activities