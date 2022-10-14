.PHONY: vendor
vendor:
	hatch run vendor:schemastore

.PHONY: lint
lint:
	hatch run precommit:check
	hatch run mypy:src
	hatch run mypy:vendor

.PHONY: publish-from-pypirc
publish-from-pypirc:
	@echo "making some assumptions about your ~/.pypirc..."
	hatch publish -u '__token__' -a "$$(cat ~/.pypirc| grep '^password' | head -n1 | cut -d'=' -f2 | tr -d ' ')"
