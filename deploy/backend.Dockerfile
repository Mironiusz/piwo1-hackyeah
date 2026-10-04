FROM ghcr.io/astral-sh/uv:0.11.0 AS uv
FROM routing
COPY --from=uv /uv /usr/local/bin/uv
ENV UV_PYTHON_INSTALL_DIR=/opt/python UV_LINK_MODE=copy UV_COMPILE_BYTECODE=1 VIRTUAL_ENV=/opt/venv PATH=/opt/venv/bin:$PATH
RUN uv python install 3.13 && uv venv --python 3.13 /opt/venv
WORKDIR /app
COPY db/pyproject.toml db/alembic.ini ./db/
COPY db/accessibility_db ./db/accessibility_db
RUN uv pip install ./db
COPY pyproject.toml ./
COPY .cache/.gitkeep ./.cache/.gitkeep
RUN uv pip install .
RUN valhalla_build_config > /opt/enableme/valhalla_config_template.json
COPY api ./api
COPY config ./config
COPY data ./data
COPY service ./service
COPY worker ./worker
COPY common_time.py common_sample_data.py ./
CMD ["python", "-m", "api"]
