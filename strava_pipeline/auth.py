import json
import logging
import pathlib
import time

import requests

log = logging.getLogger("strava_pipeline.auth")


class StravaAuth:
    """Access tokens last 6h, but we cap refreshes to once per day and
    persist state to disk so this works across separate script runs
    (e.g. an hourly cron job), not just within one process."""

    def __init__(self, client_id, client_secret, refresh_token,
                 state_path, min_refresh_interval):
        self.client_id = client_id
        self.client_secret = client_secret
        self.state_path = pathlib.Path(state_path)
        self.min_refresh_interval = min_refresh_interval

        if self.state_path.exists():
            state = json.loads(self.state_path.read_text())
            self.access_token = state.get("access_token")
            self.refresh_token = state.get("refresh_token", refresh_token)
            self.last_refresh = state.get("last_refresh", 0)
        else:
            self.access_token = None
            self.refresh_token = refresh_token
            self.last_refresh = 0  # forces a refresh on the very first call

    def _save_state(self):
        self.state_path.parent.mkdir(parents=True, exist_ok=True)
        self.state_path.write_text(json.dumps({
            "access_token": self.access_token,
            "refresh_token": self.refresh_token,
            "last_refresh": self.last_refresh,
        }))

    def get_token(self, force=False):
        due_for_refresh = time.time() - self.last_refresh >= self.min_refresh_interval
        if force or due_for_refresh or not self.access_token:
            log.info("Refreshing Strava access token...")
            resp = requests.post("https://www.strava.com/oauth/token", data={
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "grant_type": "refresh_token",
                "refresh_token": self.refresh_token,
            })
            resp.raise_for_status()
            data = resp.json()
            self.access_token = data["access_token"]
            self.last_refresh = time.time()
            # Strava rotates the refresh token on every use — must persist
            # the new one or the next scheduled refresh will fail.
            self.refresh_token = data["refresh_token"]
            self._save_state()
        return self.access_token