import json
import pandas as pd


def load_watermark(watermark_path, default_ts=0):
    if watermark_path.exists():
        return json.loads(watermark_path.read_text()).get("since_ts", default_ts)
    return default_ts


def save_watermark(watermark_path, since_ts):
    watermark_path.parent.mkdir(parents=True, exist_ok=True)
    watermark_path.write_text(json.dumps({"since_ts": since_ts}))


def append_activities(activities_path, activities):
    # Append new activity summaries to the running Parquet file,
    # merging with whatever's already there.
    new_df = pd.DataFrame(activities)
    if activities_path.exists():
        existing_df = pd.read_parquet(activities_path)
        combined_df = pd.concat([existing_df, new_df], ignore_index=True)
    else:
        combined_df = new_df
    activities_path.parent.mkdir(parents=True, exist_ok=True)
    combined_df.to_parquet(activities_path)


def save_streams(streams_dir, results):
    # Save one file per activity
    streams_dir.mkdir(parents=True, exist_ok=True)
    for activity_id, streams in results:
        if not streams:
            continue
        data = {
            stream_type: stream_obj.get("data", [])
            for stream_type, stream_obj in streams.items()
        }
        df = pd.DataFrame(data)
        if df.empty:
            continue
        df.to_parquet(streams_dir / f"{activity_id}.parquet")