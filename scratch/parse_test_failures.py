import re

log_path = "/home/ubuntu/.gemini/antigravity-cli/brain/e9bd1afd-538d-4f7e-83db-d1f289412b77/.system_generated/tasks/task-192.log"
with open(log_path) as f:
    content = f.read()

# Find all FAILURES sections
failures = re.split(r"_+ FAILURES _+", content)
if len(failures) > 1:
    failures_section = failures[1]
    # Split by individual test failures (usually start with ____ test_name ____)
    individual_failures = re.split(r"_+ (test_[a-zA-Z0-9_]+) _+", failures_section)
    print(f"Found {len(individual_failures) // 2} test failures in logs:")
    
    for i in range(1, len(individual_failures), 2):
        name = individual_failures[i]
        tb = individual_failures[i+1].strip()
        # print first 15 lines of traceback
        tb_lines = tb.split("\n")
        print(f"\n=== FAILURE: {name} ===")
        print("\n".join(tb_lines[:25]))
else:
    print("No FAILURES section found in log. First 50 lines:")
    print("\n".join(content.split("\n")[:50]))
