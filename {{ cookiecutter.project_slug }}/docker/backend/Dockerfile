FROM tiangolo/uvicorn-gunicorn-fastapi:python3.9

WORKDIR /src/

COPY ./src /src/
COPY ./alembic /alembic/

# Copy poetry.lock* in case it doesn't exist in the repo
COPY ./pyproject.toml ./poetry.lock /src/

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | POETRY_HOME=/opt/poetry python && \
    cd /usr/local/bin && \
    ln -s /opt/poetry/bin/poetry

# Allow installing dev dependencies to run tests
ARG INSTALL_DEV=false
RUN poetry config virtualenvs.create false
RUN bash -c "if [ $INSTALL_DEV == 'true' ] ; then poetry install --no-root ; else poetry install --no-root --only main ; fi"

COPY ./alembic.ini /alembic.ini
ENV PYTHONPATH=/src

COPY ./docker/celeryworker/worker-start.sh /start-celeryworker
RUN sed -i 's/\r$//g' /start-celeryworker
RUN chmod +x /start-celeryworker
