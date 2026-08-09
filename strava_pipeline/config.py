"""
Loads and validates pipeline configuration from environment variables.
"""

import os
from pathlib import Path
from dataclasses import dataclass
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseModel):

    client_id: str
    client_secret: str
    refresh_token: str

    data_dir: Path
    auth_state_path: Path
    watermark_path: Path
    activities_path: Path
    streams_dir: Path

    min_refresh_interval_seconds: int


def load_settings() -> Settings:
    client_id = os.environ.get("STRAVA_CLIENT_ID", "")
    client_secret = os.environ.get("STRAVA_CLIENT_SECRET", "")
    refresh_token = os.environ.get("STRAVA_REFRESH_TOKEN", "")

    if not (client_id and client_secret and refresh_token):
        print(
            "Missing Strava credentials. Set STRAVA_CLIENT_ID, "
            "STRAVA_CLIENT_SECRET, and STRAVA_REFRESH_TOKEN as environment "
            "variables before running."
        )
        pass 

    data_dir = Path(os.environ.get("STRAVA_DATA_DIR", "./strava_data"))

    return Settings(
        client_id=client_id,
        client_secret=client_secret,
        refresh_token=refresh_token,
        data_dir=data_dir,
        auth_state_path=data_dir / "auth_state.json",
        watermark_path=data_dir / "watermark.json",
        activities_path=data_dir / "activities.parquet",
        streams_dir=data_dir / "streams",
        min_refresh_interval_seconds=24 * 60 * 60,  # refresh access token at most once/day
    )

_settings = None