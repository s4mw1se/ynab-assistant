import json

with open("ynab-api-spec.json") as f:
    spec = json.load(f)

schemas = spec.get("components", {}).get("schemas", {})

for name, val in schemas.items():
    t = val.get("type")
    if isinstance(t, list):
        print(f"Schema {name} has list type: {t}")
    if "additionalProperties" in val:
        print(f"Schema {name} has additionalProperties: {val['additionalProperties']}")
