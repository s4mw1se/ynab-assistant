import json

with open("ynab-api-spec.json") as f:
    spec = json.load(f)

schemas = spec.get("components", {}).get("schemas", {})

for name, val in schemas.items():
    properties = val.get("properties", {})
    for prop_name, prop_val in properties.items():
        for kw in ["allOf", "anyOf", "oneOf"]:
            if kw in prop_val:
                print(f"Schema {name}, property {prop_name} has {kw}: {prop_val[kw]}")
        # also check items of array
        if prop_val.get("type") == "array":
            items = prop_val.get("items", {})
            for kw in ["allOf", "anyOf", "oneOf"]:
                if kw in items:
                    print(f"Schema {name}, property {prop_name} (array items) has {kw}: {items[kw]}")
