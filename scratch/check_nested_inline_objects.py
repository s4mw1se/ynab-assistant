import json

with open("ynab-api-spec.json") as f:
    spec = json.load(f)

schemas = spec.get("components", {}).get("schemas", {})

def check_nested(schema, path=""):
    if not isinstance(schema, dict):
        return
    properties = schema.get("properties", {})
    for prop_name, prop_val in properties.items():
        if prop_val.get("type") == "object" and "properties" in prop_val:
            # Inline object!
            next_path = f"{path}.{prop_name}" if path else prop_name
            print(f"Nested inline object found at: {next_path}")
            check_nested(prop_val, next_path)
        elif prop_val.get("type") == "array":
            items = prop_val.get("items", {})
            if items.get("type") == "object" and "properties" in items:
                print(f"Array of inline object found at: {path}.{prop_name}[]")
                check_nested(items, f"{path}.{prop_name}[]")

for name, val in schemas.items():
    # If allOf, inspect each part
    if "allOf" in val:
        for sub in val["allOf"]:
            if "$ref" not in sub:
                check_nested(sub, name)
    else:
        check_nested(val, name)
