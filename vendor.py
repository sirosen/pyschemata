#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import pathlib
import sys

import requests

PKG_PATH = pathlib.Path.cwd() / "src" / "pyschemata"
VENDOR_SCHEMASTORE_DIR = PKG_PATH / "schemastore"
VENDOR_SCHEMASTORE_JSON_DIR = VENDOR_SCHEMASTORE_DIR / "json"


def download_schema(schema_name: str, schema_url: str) -> bool:
    print(f"downloading {schema_name} schema to check ({schema_url})")
    res = requests.get(schema_url)
    sha = hashlib.sha256()
    sha.update(res.content)
    new_digest = sha.hexdigest()

    schemafile = VENDOR_SCHEMASTORE_JSON_DIR / f"{schema_name}.json"
    hashfile = VENDOR_SCHEMASTORE_JSON_DIR / f"{schema_name}.sha256"
    if hashfile.exists():
        prev_digest: str | None = hashfile.read_text().strip()
    else:
        prev_digest = None

    if new_digest == prev_digest:
        return False

    schemafile.write_bytes(res.content)
    hashfile.write_text(new_digest)

    return True


def download_catalog() -> bool:
    res = requests.get("https://www.schemastore.org/api/json/catalog.json")
    sha = hashlib.sha256()
    sha.update(res.content)
    new_digest = sha.hexdigest()

    catalogfile = VENDOR_SCHEMASTORE_DIR / "catalog.json"
    hashfile = VENDOR_SCHEMASTORE_DIR / "catalog.sha256"

    # FIXME FIXME FIXME
    # check is comparing against the hash on disk
    # somehow, check against the last published version
    if catalogfile.exists():
        prev_digest: str | None = catalogfile.read_text().strip()
    else:
        prev_digest = None

    if new_digest == prev_digest:
        return False

    catalogfile.write_bytes(res.content)
    hashfile.write_text(new_digest)

    return True


def main() -> int:
    made_changes = download_catalog()

    # for name, schema_url in iter-on-catalog()
    #     made_changes = download_schema(name, schema_url) or made_changes

    if made_changes:
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
