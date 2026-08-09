import requests, time, json, pathlib

class StravaAuth:
    """Handles OAuth2 token refresh for a one user.
    Access tokens last 6h, but we cap refreshes to once per day and
    persist state to disk so this works across separate script runs,
    not just within one process."""

    def __init__(self, client_id, client_secret, refresh_token,
                 state_path="strava_auth.json", min_refresh_interval=86400):
        self.client_id = client_id
        self.client_secret = client_secret
        self.state_path = pathlib.Path(state_path)
        self.min_refresh_interval = min_refresh_interval  # seconds; 86400 = 24h

        # Load any previously saved token/refresh_token/last_refresh from disk.
        # Falls back to the refresh_token passed in on first-ever run.
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
        # Persist so the next process invocation can reuse the token
        # instead of refreshing again.
        self.state_path.write_text(json.dumps({
            "access_token": self.access_token,
            "refresh_token": self.refresh_token,
            "last_refresh": self.last_refresh,
        }))

    def get_token(self):
        # Only hit the token endpoint if it's been >= min_refresh_interval
        # since the last refresh, regardless of how many times get_token()
        # is called in between (within a run, or across cron invocations).
        if time.time() - self.last_refresh >= self.min_refresh_interval:
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