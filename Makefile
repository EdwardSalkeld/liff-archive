.PHONY: dev build

dev:
	docker-compose up website

build:
	docker-compose run --rm hugo_build
