import logging

import ray
from dotenv import load_dotenv

from strava_pipeline.pipeline import run_pipeline
import logging
# Load variables from a .env file (if present) into os.environ *before*
# config.get_settings() reads them.

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger("strava_pipeline.pipeline")


def main():
    ray.init()

    try:
        run_pipeline()
        
    finally:
        ray.shutdown()


if __name__ == "__main__":
    main()