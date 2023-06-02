# syntax=docker/dockerfile:1

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


# run: docker build --target poetry -t poetry .
# docker run -it --rm -v ${PWD}:/src poetry
FROM poetry-base as poetry
VOLUME [ "/src" ]  # ? 
WORKDIR /src
ENTRYPOINT [ "bash" ]


FROM poetry-base as builder-base
# copy project requirement files here to ensure they will be cached.
WORKDIR $PYSETUP_PATH
COPY poetry.lock pyproject.toml ./
# install runtime deps - uses $POETRY_VIRTUALENVS_IN_PROJECT internally
RUN poetry install --without dev

# ============ DEV TARGET ============ 
# docker build --target dev -t app:dev .
# docker run --rm -v ${PWD}:/src app:dev
FROM python-base as dev
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

CMD ["uvicorn", "--reload", "app.main:app", "--host", "0.0.0.0", "--port", "7000"]


# ============ TEST TARGET ============ 

FROM dev as test
VOLUME [ "/src" ]
WORKDIR /src
ENTRYPOINT [ "python3", "-m", "pytest" ]


# ============ PRODUCTION TARGET ============ 
# docker build -t app .
# docker build --platform linux/amd64 -t app .
# docker run --rm app
FROM python-base as prod
ENV FASTAPI_ENV=production
COPY --from=builder-base $PYSETUP_PATH $PYSETUP_PATH
WORKDIR /src
COPY ./app /src/app/
COPY ./.env /src/.env
EXPOSE 7000
CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "app.main:app", "-b", "0.0.0.0:7000", "-w", "2"]


