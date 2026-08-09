"""
Combining config, auth, strava_client, tasks, and storage into
one pipeline.
"""

import logging

import pandas as pd
import ray

from strava_pipeline.auth import StravaAuth
from strava_pipeline.config import load_settings
from strava_pipeline.strava_client import list_new_activities
from strava_pipeline.tasks import fetch_streams
from strava_pipeline import storage

log = logging.getLogger("strava_pipeline.pipeline")


def run_pipeline():
    """One full pipeline run: fetch new activities, pull detailed streams
    for each in parallel, save everything, and update the watermark."""
    settings = load_settings()

    auth = StravaAuth(
        client_id=settings.client_id,
        client_secret=settings.client_secret,
        refresh_token=settings.refresh_token,
        state_path=settings.auth_state_path,
        min_refresh_interval=settings.min_refresh_interval_seconds,
    )

    since_ts = storage.load_watermark(settings.watermark_path)
    token = auth.get_token()

    log.info(f"Fetching activities since {since_ts}...")
    activities = list_new_activities(token, since_ts)
    log.info(f"Found {len(activities)} new activities.")


    if not activities:
        log.info("Nothing new — exiting.")
        return

    futures = [fetch_streams.remote(token, a["id"]) for a in activities]

    # Fetch results from Ray
    #raw_results = ray.get(futures)

    # Keep only tuples with valid stream data (filters out 404s)
    #results = [(act_id, streams) for act_id, streams in raw_results if streams is not None]
    results = ray.get(futures)
    results = [res for res in results if res != None]

    storage.append_activities(settings.activities_path, activities)
    storage.save_streams(settings.streams_dir, results)

    # Advance the watermark so the next run only fetches what's new.
    newest_ts = max(
        pd.Timestamp(a["start_date"]).timestamp() for a in activities
    )
    storage.save_watermark(settings.watermark_path, int(newest_ts) + 1)  # +1 avoids refetching the last one

    log.info(f"Watermark advanced to {int(newest_ts) + 1}.")
    log.info(f"Wrote {len(activities)} activities and {len(results)} stream sets.")