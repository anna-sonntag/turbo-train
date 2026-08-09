FROM python:3.13-slim-trixie

WORKDIR /turbo-train

COPY uv.lock .
COPY pyproject.toml .
COPY .python-version .
RUN pip install --upgrade pip
RUN pip install uv
RUN uv sync --no-install-project

COPY . .

CMD ["uv", "run", "strava_pipeline/main.py"]