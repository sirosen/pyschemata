.PHONY: vendor
vendor:
	hatch run vendor:schemastore

.PHONY: lint
lint:
	hatch run precommit:check
	hatch run mypy:src
	hatch run mypy:vendor
