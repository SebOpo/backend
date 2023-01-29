default: down up

up:
	docker-compose up -d

down:
	docker-compose down --remove-orphans

build:
	docker-compose build

test:
	docker-compose run fastapi  python -m pytest

exec:
	docker-compose exec fastapi bash

pre-start: up test down

# convenience targets
b: build
u: up
d: down
e: exec