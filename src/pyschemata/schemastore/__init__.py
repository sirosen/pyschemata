# TODO: implement caching for all functions
from __future__ import annotations

import json
import typing as t

import importlib_resources

_THIS = importlib_resources.files("pyschemata.schemastore")
_DATA = importlib_resources.files("pyschemata.schemastore.jsondata")


def _get_index() -> dict[str, t.Any]:
    with _THIS.joinpath("index.json").open() as fp:
        return t.cast("dict[str, t.Any]", json.load(fp))


def get_catalog() -> dict[str, t.Any]:
    with _THIS.joinpath("catalog.json").open() as fp:
        return t.cast("dict[str, t.Any]", json.load(fp))


def name2schema(schema_name: str) -> dict[str, t.Any]:
    index = _get_index()
    by_name = index["by_name"]
    try:
        sha = by_name[schema_name]
    except KeyError as e:
        raise LookupError(f"'{schema_name}' is not a recognized schema name") from e

    with _DATA.joinpath(f"{sha}.json").open() as fp:
        return t.cast("dict[str, t.Any]", json.load(fp))


def url2schema(schema_url: str) -> dict[str, t.Any]:
    index = _get_index()
    by_url = index["by_url"]
    try:
        sha = by_url[schema_url]
    except KeyError as e:
        raise LookupError(f"'{schema_url}' is not a recognized schema URL") from e

    with _DATA.joinpath(f"{sha}.json").open() as fp:
        return t.cast("dict[str, t.Any]", json.load(fp))
