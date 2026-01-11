# SafeChord Docs - Makefile
IMAGE_NAME := squidfunk/mkdocs-material
PORT := 8000

.PHONY: dev build clean

# run dev server
dev:
	docker run --rm -it -p $(PORT):$(PORT) -v $(shell pwd):/docs $(IMAGE_NAME)

# build the static site (at ./site/)
build:
	docker run --rm -v $(shell pwd):/docs -u $(shell id -u):$(shell id -g) $(IMAGE_NAME) build

# clean compiled files (using docker to handle root-owned files from previous builds)
clean:
	rm -rf site/
