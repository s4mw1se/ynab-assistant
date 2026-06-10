import json

with open("ynab-api-spec.json") as f:
    spec = json.load(f)

schemas = spec.get("components", {}).get("schemas", {})

for name, val in schemas.items():
    if "enum" in val:
        print(f"Enum schema: {name} -> {val['enum']}")
    properties = val.get("properties", {})
    for prop_name, prop_val in properties.items():
        if "enum" in prop_val:
            print(f"Inline enum in schema {name}, property {prop_name} -> {prop_val['enum']}")
