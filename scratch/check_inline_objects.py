import json

with open("ynab-api-spec.json") as f:
    spec = json.load(f)

schemas = spec.get("components", {}).get("schemas", {})

for name, val in schemas.items():
    if val.get("type") == "object":
        properties = val.get("properties", {})
        for prop_name, prop_val in properties.items():
            if prop_val.get("type") == "object" and "properties" in prop_val:
                print(f"Schema {name} has inline object property: {prop_name}")
