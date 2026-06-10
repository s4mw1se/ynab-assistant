import json
import collections

with open("ynab-api-spec.json") as f:
    spec = json.load(f)

schemas = spec.get("components", {}).get("schemas", {})

def get_refs(schema_dict):
    refs = set()
    if isinstance(schema_dict, dict):
        if "$ref" in schema_dict:
            refs.add(schema_dict["$ref"].split("/")[-1])
        for k, v in schema_dict.items():
            refs.update(get_refs(v))
    elif isinstance(schema_dict, list):
        for item in schema_dict:
            refs.update(get_refs(item))
    return refs

deps = {}
for name, val in schemas.items():
    deps[name] = get_refs(val)

# Topological sort
visited = {}
order = []

def visit(node):
    if node in visited:
        if visited[node] == 1:
            # Cycle detected
            return
        return
    visited[node] = 1 # visiting
    for dep in deps.get(node, []):
        if dep in schemas:
            visit(dep)
    visited[node] = 2 # visited
    order.append(node)

for name in schemas:
    visit(name)

print("Total schemas in topological order:", len(order))
print("First 10:", order[:10])
print("Last 10:", order[-10:])
