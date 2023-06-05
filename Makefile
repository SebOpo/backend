default: down up

up:
	docker compose up -d

down:
	docker compose down --remove-orphans

build:
	docker compose build

test:
	docker compose run --rm fastapi python3 -m pytest

exec:
	docker compose exec fastapi bash

poetry:
	docker build --target poetry -t dim/api:poetry .
	docker run -it --rm -v ${PWD}:/src dim/api:poetry

lint:
	@echo "🧹 Run Bllack with pyfound/black:latest_release"
	docker run --rm --volume $(shell pwd):/src --workdir /src pyfound/black:latest_release black .

pre-start: up test down

# convenience targets
b: build
u: up
d: down
e: exec
