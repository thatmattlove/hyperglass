"""Build docs tables from schema."""

HEADERS = ["Field", "Description", "Type", "Default"]


def build_table(data, level):
    table = [HEADERS]

    for prop, attrs in data.items():
        if attrs.get("level", 0) == 0:
            table.append(
                [
                    prop,
                    attrs.get("description", ""),
                    attrs.get("type", attrs.get("anyOf", "")),
                    attrs.get("default", ""),
                ]
            )
    return table


def process_object(obj):
    definitions = obj.pop("definitions", {})
    properties = obj.pop("properties")
    level = obj.pop("level", 0)

    top_properties = {}

    for key, value in properties.items():
        if value["title"] not in definitions:
            top_properties.update({key: value})

    data = build_table(data=top_properties, level=level)
    return data


def schema_top_level():
    from hyperglass.configuration.models.params import Params

    schema = Params.schema()
    definitions = schema.get("definitions")

    tables = {}
    top_level = process_object(schema)
    tables.update({schema["title"]: top_level})

    for k, v in definitions.items():
        if isinstance(v, dict) and "allOf" not in v:
            tables.update({k: process_object(v)})

    return tables
