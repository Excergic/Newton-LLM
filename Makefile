include .env

$(eval export $(shell sed -ne 's/ *#.*$$//; /./ s/=.*$$// p' .env))

PYTHONPATH := $(shell pwd)/src

install: # Create a local virtual environment and install all required Python dependencies.
	uv python install 3.11
	uv sync

help:
	@grep -E '^[a-zA-Z0-9 -]+:.*#'  Makefile | sort | while read -r l; do printf "\033[1;32m$$(echo $$l | cut -f 1 -d':')\033[00m:$$(echo $$l | cut -f 2- -d'#')\n"; done

# ======================================
# ------- Docker Infrastructure --------
# ======================================

local-start: # Build and start your local Docker infrastructure.
	docker compose -f docker-compose.yml up --build -d

local-stop: # Stop your local Docker infrastructure.
	docker compose -f docker-compose.yml down --remove-orphans

# ======================================
# ---------- Crawling Data -------------
# ======================================

local-test-wikipedia: # Make a call to your local AWS Lambda (hosted in Docker) to crawl a Wikipedia article.
	curl -X POST "http://localhost:9010/2015-03-31/functions/function/invocations" \
	  	-d '{"link": "https://en.wikipedia.org/wiki/Isaac_Newton"}'

local-ingest-data: # Ingest all Wikipedia links from data/links.txt by calling your local AWS Lambda hosted in Docker.
	while IFS= read -r link; do \
		echo "Processing: $$link"; \
		curl -X POST "http://localhost:9010/2015-03-31/functions/function/invocations" \
			-d "{\"link\": \"$$link\"}"; \
		echo "\n"; \
		sleep 2; \
	done < data/links.txt
