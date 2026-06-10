import json

with open("ynab-api-spec.json") as f:
    spec = json.load(f)

schemas = spec.get("components", {}).get("schemas", {})

for name, val in schemas.items():
    properties = val.get("properties", {})
    for prop_name, prop_val in properties.items():
        if prop_val.get("type") == "array":
            items = prop_val.get("items", {})
            if items.get("type") == "object" and "properties" in items:
                print(f"Schema {name}, property {prop_name} has array of inline objects")
