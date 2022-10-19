#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import pathlib
import sys
import typing as t

import requests
import requests.adapters

PKG_PATH = pathlib.Path.cwd() / "src" / "pyschemata"
VENDOR_SCHEMASTORE_DIR = PKG_PATH / "schemastore"
VENDOR_SCHEMASTORE_JSON_DIR = VENDOR_SCHEMASTORE_DIR / "jsondata"
CATALOGFILE = VENDOR_SCHEMASTORE_DIR / "catalog.json"
INDEXFILE = VENDOR_SCHEMASTORE_DIR / "index.json"
VENDOR_LOCKFILE = VENDOR_SCHEMASTORE_DIR / "vendor_lock.json"


# TODO: also support `.versions` on the schema configs
INDEX: dict[str, dict[str, t.Any]] = {
    "by_name": {},
    "by_url": {},
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


def download_schema(sess: requests.Session, schema_id: str, schema_url: str) -> str:
    print(f"downloading schema: {schema_id} ({schema_url})")
    res = sess.get(schema_url)
    digest = hashlib.sha256(res.content).hexdigest()
    (VENDOR_SCHEMASTORE_JSON_DIR / f"{schema_id}.json").write_bytes(res.content)
    return digest


def download_catalog(sess: requests.Session) -> str:
    print("udpating catalog.json")
    res = sess.get("https://www.schemastore.org/api/json/catalog.json")
    digest = hashlib.sha256(res.content).hexdigest()
    CATALOGFILE.write_bytes(res.content)
    print(f"updated catalog.json: {digest}")
    return digest


def iter_catalog() -> t.Iterator[dict[str, t.Any]]:
    with CATALOGFILE.open() as fp:
        catalog = json.load(fp)

    yield from catalog["schemas"]


def handle_schema_info(sess: requests.Session, schema_info: dict[str, str]) -> None:
    schema_id = get_schema_id(schema_info)
    schema_url = schema_info["url"]
    try:
        digest = download_schema(sess, schema_id, schema_url)
    except requests.RequestException:
        print(f"\033[1;31mWARNING: failed to download {schema_id}\033[0m")
        return

    # add to the index
    assert schema_url not in INDEX["by_url"]
    INDEX["by_url"][schema_url] = schema_id
    if "name" in schema_info:
        assert schema_info["name"] not in INDEX["by_name"]
        INDEX["by_name"][schema_info["name"]] = schema_id

    # add to the lockfile data
    # FIXME: use a TypedDict instead of an ignore
    LOCKDATA["schemas"].append(  # type: ignore[union-attr]
        {"url": schema_url, "digest": digest}
    )


def update_catalog_schemas(sess: requests.Session) -> None:
    for info in iter_catalog():
        handle_schema_info(sess, info)

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
    adapter = requests.adapters.HTTPAdapter(
        max_retries=requests.adapters.Retry(total=5, backoff_factor=0.25)
    )
    sess = requests.Session()
    sess.mount("https://", adapter)

    catalog_digest = download_catalog(sess)
    LOCKDATA["catalog"] = catalog_digest
    update_catalog_schemas(sess)

    print("download and lockdata computation complete")
    print("update vendor lockfile")
    if update_vendor_lock():
        print("vendor lock updated (success)")
        return 0
    print("no vendor lock update needed (fail)")
    return 1


if __name__ == "__main__":
    sys.exit(main())
