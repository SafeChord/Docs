# SafeChord Docs - Makefile
IMAGE_NAME := safechord-docs
PORT := 8000

.PHONY: dev build clean image

# build custom image with plugins
image:
	docker build -t $(IMAGE_NAME) .

# run dev server
dev: image
	docker run --rm -it -p $(PORT):$(PORT) -v $(shell pwd):/docs $(IMAGE_NAME)

# build the static site (at ./site/)
build: image
	docker run --rm -v $(shell pwd):/docs -u $(shell id -u):$(shell id -g) $(IMAGE_NAME) build

# clean compiled files
clean:
	rm -rf site/
