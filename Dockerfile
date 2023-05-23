FROM public.ecr.aws/docker/library/python:3.9 as base
WORKDIR /src
COPY ./requirements.txt /src/requirements.txt
COPY ./populate_db.py /src/populate_db.py
COPY ./pre_start.sh /src/pre_start.sh
COPY ./alembic.ini /src/alembic.ini 
COPY ./alembic /src/alembic
COPY ./.env /src/.env
RUN pip install --no-cache-dir --upgrade -r /src/requirements.txt
COPY ./app /src/app
COPY ./startup.sh /src/startup.sh

FROM base as test
CMD ["/bin/sh", "-c", "pre_start.sh"]

FROM base as production
EXPOSE 7000
CMD ["/bin/sh", "-c", "/src/startup.sh" ]