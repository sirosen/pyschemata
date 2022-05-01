# pyschemata

An experiment in bundling SchemaStore Schemas as a python package.

## Status of this Project

This project is very new and experimental. We'll see where it goes.

## Goals

- Provide all the schemas in [SchemaStore](https://github.com/SchemaStore/schemastore)
  as an installable python package, with the schemas as package data

- All schemas are vendored into this package at build time (no schemas are
  mirrored in this repo)

- Automatic updates and releases driven by a CI service, but only when there
  are schema updates

- Separation between build-time dependencies (e.g. `requests`) and runtime
  dependencies (e.g. `pkg_resources`)
