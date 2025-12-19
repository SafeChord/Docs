# SafeChord Docs - Makefile
# 使用 Docker 封裝 MkDocs 操作

IMAGE_NAME := squidfunk/mkdocs-material
PORT := 8000

.PHONY: dev build clean

# 本機開發預覽
dev:
	docker run --rm -it -p $(PORT):$(PORT) -v $(shell pwd):/docs $(IMAGE_NAME)

# 靜態網站建置 (產出至 site/)
build:
	docker run --rm -v $(shell pwd):/docs $(IMAGE_NAME) build

# 清理編譯檔案
clean:
	rm -rf site/
