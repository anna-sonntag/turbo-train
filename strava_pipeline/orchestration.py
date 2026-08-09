import ray
from strava_auth import StravaAuth 
from strava_pipeline.list_new_activities import list_new_activities 
from ray_activity_detail import fetch_streams

ray.init()  # starts a local Ray cluster

def run_pipeline(auth: StravaAuth, since_ts: int):
    # One full pipeline run: fetch new activities, pull detailed streams
    # for each in parallel, store everything, and return a new watermark
    # for the next run."""
    token = auth.get_token()
    activities = list_new_activities(token, since_ts)

    futures = [fetch_streams.remote(token, a["id"]) for a in activities]

    # ray.get() blocks until all futures resolve, collecting results
    # in the same order the futures list was built.
    results = ray.get(futures)

    import pandas as pd
    pd.DataFrame(activities).to_parquet("activities.parquet")

    for activity_id, streams in results:
        pd.DataFrame(streams).to_parquet(f"streams/{activity_id}.parquet")

    return activities[-1]["start_date"] if activities else since_ts