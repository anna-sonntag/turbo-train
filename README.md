# Strava Pipeline

A personal pipeline that regularly downloads Strava training data and stores it locally as Parquet files. Uses [Ray](https://www.ray.io/) to fetch activity data in parallel.

Built for **personal use only**, to analyze the Strava data of one user.

---

## How it works

1) Checks/refreshes the OAuth token (strava_data/auth_state.json).
2) Pulls new activity summaries since the last run timestamp (strava_data/watermark.json).
3) Fetches per-activity streams in parallel using Ray tasks with exponential backoff.
4) Appends summaries to activities.parquet and writes stream files to streams/<id>.parquet.
5) Advances the watermark timestamp.

## Structure
strava_pipeline/
├── .env.example
├── pyproject.toml
├── main.py
└── strava_pipeline/
    ├── config.py          # Env loading & settings
    ├── auth.py            # OAuth refresh & storage
    ├── strava_client.py   # Main Strava API client
    ├── tasks.py           # Parallel Ray tasks
    ├── storage.py         # Watermark and Parquet read/write
    ├── pipeline.py        # Core execution flow
    └── main.py            # Entrypoint

## Quickstart
1. Installation
<git clone <repo-url> && cd strava-pipeline
pip install -e . 
>


2. Strava API Credentials

    1) Create an application at strava.com/settings/api (set callback domain to localhost).
    2) Get an authorization code with activity:read_all permissions by opening this URL in your browser (replace <CLIENT_ID>):
    3) https://www.strava.com/oauth/authorize?client_id=<CLIENT_ID>&response_type=code&redirect_uri=http://localhost&approval_prompt=force&scope=activity:read_all

    4) Copy the code query parameter from the redirected URL, then exchange it for a refresh token:

        curl -X POST https://www.strava.com/oauth/token \
          -F client_id=<CLIENT_ID> \
          -F client_secret=<CLIENT_SECRET> \
          -F code=<AUTH_CODE> \
          -F grant_type=authorization_code

3. Environment Config
  cp .env.example .env

  STRAVA_CLIENT_ID=<your_client_id>
  STRAVA_CLIENT_SECRET=<your_client_secret>
  STRAVA_REFRESH_TOKEN=<refresh_token_from_curl_response>

4. Data Schema & Output

Files are stored in ./strava_data/ (configurable via STRAVA_DATA_DIR):

    activities.parquet – Summary metadata (distance, moving time, elevation gain, type).

    streams/<activity_id>.parquet – High-resolution telemetry (time, heart rate, power, cadence, altitude, lat/lng). Skipped for manual entries without sensor streams.

    watermark.json – Unix timestamp of the most recent synced activity.

    auth_state.json – Cached access token and latest rotated refresh token.

Token Rotation: Strava issues a new refresh token on every refresh. auth.py automatically updates strava_data/auth_state.json on each run.

Rate Limits: By default, auth refreshes are throttled to once per 24 hours. If running jobs more frequently than every 6 hours, adjust min_refresh_interval in config.py to prevent token expiry.

