default: down up

up:
	docker-compose up -d

down:
	docker-compose down --remove-orphans

build:
	docker-compose build


# convenience targets
b: build
u: up
d: down