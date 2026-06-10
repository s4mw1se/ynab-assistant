import json

with open("ynab-api-spec.json") as f:
    spec = json.load(f)

schemas = spec.get("components", {}).get("schemas", {})

for name, val in schemas.items():
    for kw in ["allOf", "anyOf", "oneOf"]:
        if kw in val:
            print(f"Schema {name} is defined using {kw}")
