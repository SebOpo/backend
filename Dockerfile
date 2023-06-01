# syntax=docker/dockerfile:1

FROM public.ecr.aws/docker/library/python:3.9 AS base
WORKDIR /src
COPY ./requirements.txt /src/requirements.txt
COPY ./populate_db.py /src/populate_db.py
COPY ./alembic.ini /src/alembic.ini
COPY ./alembic /src/alembic
COPY ./.env /src/.env
RUN pip install --no-cache-dir --upgrade -r /src/requirements.txt
COPY ./app /src/app
COPY ./startup.sh /src/startup.sh

FROM base AS test
SHELL ["/bin/bash", "-c"]
RUN cd /src
RUN python3 -m venv /src/venv
RUN source /src/venv/bin/activate
RUN alembic upgrade heads
RUN python populate_db.py
RUN echo "Running tests"
RUN sleep 5
RUN python -m pytest

FROM base AS production
EXPOSE 7000
CMD ["/bin/bash", "-c", "/src/startup.sh" ]
