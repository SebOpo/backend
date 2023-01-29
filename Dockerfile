FROM --platform=linux/amd64 python:3.8
WORKDIR /src

# Update and install dependencies
RUN apt-get update && pip install --upgrade pip
COPY ./requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy scripts and application code
COPY populate_db.py \
    alembic.ini \
    startup.sh \
    alembic \
    app \
    ./

EXPOSE 7000
CMD ["./startup.sh"]
