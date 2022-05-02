#!/usr/bin/env python3
from __future__ import annotations

import collections
import hashlib
import json
import pathlib
import sys
import typing as t

import requests

PKG_PATH = pathlib.Path.cwd() / "src" / "pyschemata"
VENDOR_SCHEMASTORE_DIR = PKG_PATH / "schemastore"
VENDOR_SCHEMASTORE_JSON_DIR = VENDOR_SCHEMASTORE_DIR / "json"
CATALOGFILE = VENDOR_SCHEMASTORE_DIR / "catalog.json"
INDEXFILE = VENDOR_SCHEMASTORE_DIR / "index.json"
VENDOR_LOCKFILE = VENDOR_SCHEMASTORE_DIR / "vendor_lock.json"


# TODO: also support `.versions` on the schema configs
INDEX = {
    "by_name": collections.defaultdict(list),
    "by_description": collections.defaultdict(list),
    "by_url": collections.defaultdict(list),
}
LOCKDATA: dict[str, str | list[dict[str, str]]] = {
    "schemas": [],
}


def get_schema_id(schema_info: dict[str, t.Any]) -> str:
    schema_url = schema_info["url"]
    # use a hash of the URL as the ID
    # name and description are unsuitable as names for files, as is the basename
    # across schemastore schemas, none of these provide coherent "good" names
    # instead, this makes the ID somewhat random but consistent
    return hashlib.sha256(schema_url.encode()).hexdigest()[:12]


def download_schema(schema_id: str, schema_url: str) -> str:
    print(f"downloading schema: {schema_id} ({schema_url})")
    res = requests.get(schema_url)
    digest = hashlib.sha256(res.content).hexdigest()
    (VENDOR_SCHEMASTORE_JSON_DIR / f"{schema_id}.json").write_bytes(res.content)
    return digest


def download_catalog() -> str:
    print("udpating catalog.json")
    res = requests.get("https://www.schemastore.org/api/json/catalog.json")
    digest = hashlib.sha256(res.content).hexdigest()
    CATALOGFILE.write_bytes(res.content)
    print(f"updated catalog.json: {digest}")
    return digest


def iter_catalog() -> dict[str, t.Any]:
    with CATALOGFILE.open() as fp:
        catalog = json.load(fp)

    for schema_info in catalog["schemas"]:
        yield schema_info


def handle_schema_info(schema_info):
    schema_id = get_schema_id(schema_info)
    schema_url = schema_info["url"]
    digest = download_schema(schema_id, schema_url)

    # add to the index
    INDEX["by_url"][schema_url].append(schema_id)
    if "name" in schema_info:
        INDEX["by_name"][schema_info["name"]].append(schema_id)
    if "description" in schema_info:
        INDEX["by_description"][schema_info["description"]].append(schema_id)

    # add to the lockfile data
    LOCKDATA["schemas"].append({"url": schema_url, "digest": digest})


def update_catalog_schemas() -> None:
    for info in iter_catalog():
        handle_schema_info(info)

    with INDEXFILE.open("w") as fp:
        json.dump(INDEX, fp, sort_keys=True, indent=2, separators=(",", ": "))


def update_vendor_lock() -> bool:
    if VENDOR_LOCKFILE.exists():
        prev_lock_digest: str | None = hashlib.sha256(
            VENDOR_LOCKFILE.read_bytes()
        ).hexdigest()
    else:
        prev_lock_digest = None

    with VENDOR_LOCKFILE.open("w") as fp:
        json.dump(LOCKDATA, fp, sort_keys=True, indent=2, separators=(",", ": "))

    new_lock_digest: str | None = hashlib.sha256(
        VENDOR_LOCKFILE.read_bytes()
    ).hexdigest()

    if prev_lock_digest == new_lock_digest:
        return False
    return True


def main() -> int:
    catalog_digest = download_catalog()
    LOCKDATA["catalog"] = catalog_digest
    update_catalog_schemas()
    if update_vendor_lock():
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
