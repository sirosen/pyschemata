.PHONY: vendor
vendor:
	rm src/pyschemata/schemastore/jsondata/*.json
	hatch run vendor:schemastore

.PHONY: lint
lint:
	hatch run precommit:check
	hatch run mypy:src
	hatch run mypy:scripts

.PHONY: bumpversion
bumpversion:
	hatch run bumpv

.PHONY: build
build:
	hatch build

.PHONY: publish-from-pypirc
publish-from-pypirc: build
	@echo "making some assumptions about your ~/.pypirc..."
	hatch publish -u '__token__' -a "$$(awk '/^password/{print $$3; exit}' ~/.pypirc)"
