.PHONY: vendor
vendor:
	hatch run vendor:schemastore

.PHONY: lint
lint:
	hatch run lint:check
