# syntax=docker/dockerfile:1

# For M1/M2 chip set use docker build --platform linux/amd64 
# Or set env variable: export DOCKER_DEFAULT_PLATFORM=linux/amd64 

FROM public.ecr.aws/docker/library/python:3.9-slim AS python-base
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    POETRY_VERSION=1.5.1 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1 \
    # this is where our requirements + virtual environment will live
    PYSETUP_PATH="/opt/pysetup" \
    VENV_PATH="/opt/pysetup/.venv"

# prepend poetry and venv to path
ENV PATH="$POETRY_HOME/bin:$VENV_PATH/bin:$PATH"

FROM python-base as poetry-base
RUN apt-get update && apt-get install --no-install-recommends -y curl 
RUN curl -sSL https://install.python-poetry.org | python3 -


# ============ TARGET: poetry ============ 
# Add/remove/update packages
# run: docker build --target poetry -t poetry .
# docker run -it --rm -v ${PWD}:/src poetry
FROM poetry-base as poetry
VOLUME [ "/src" ]  # ? 
WORKDIR /src
ENTRYPOINT [ "bash" ]


# ============ TARGET: builder-base ============ 
# Instal packages without dev group
FROM poetry-base as builder-base
WORKDIR $PYSETUP_PATH
# copy project requirement files here to ensure they will be cached.
COPY poetry.lock pyproject.toml ./
RUN poetry install --without dev


# ============ TARGET: DEV-LOCAL ============ 
# docker build --target dev-local -t dim:dev-local .
# docker run --rm -v ${PWD}:/src dim:dev-local
# to run test:
# docker run --rm -v ${PWD}:/src dim:dev-local python3 -m pytest
FROM python-base as dev-local
ENV FASTAPI_ENV=development

# copy in our built poetry + venv
COPY --from=builder-base $POETRY_HOME $POETRY_HOME
COPY --from=builder-base $PYSETUP_PATH $PYSETUP_PATH

WORKDIR $PYSETUP_PATH
RUN poetry install

VOLUME [ "/src" ]
# will become mountpoint of our code
WORKDIR /src
EXPOSE 7000
CMD ["/bin/bash", "-c", "/src/startup.sh" ]



# ============ TARGET: PRODUCTION ============ 
# docker build -t app .
# docker run --rm --env-file .env app
FROM python-base as prod
ENV FASTAPI_ENV=production
COPY --from=builder-base $PYSETUP_PATH $PYSETUP_PATH
WORKDIR /src

COPY ./populate_db.py /src/populate_db.py
COPY ./alembic.ini /src/alembic.ini
COPY ./alembic /src/alembic
COPY ./app /src/app/
COPY ./.env /src/.env
COPY ./startup.sh /src/startup.sh

EXPOSE 7000
CMD ["/bin/bash", "-c", "/src/startup.sh" ]
