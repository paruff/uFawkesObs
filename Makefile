.PHONY: check-env up

check-env:
	./scripts/check-env.sh

up: check-env
	docker compose --profile core up -d
