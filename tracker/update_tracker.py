import json
import yaml
import re
import os

# Load rules
with open("inspect/rules.yaml", "r") as f:
    rules_yaml = yaml.safe_load(f)
rules = [(r["id"], re.compile(r["pattern"], re.IGNORECASE)) for r in rules_yaml["rules"]]

# Load promptfoo output
with open("results/raw/eval-results.json", "r") as f:
    results = json.load(f)["results"]["results"]

# Load existing worst cases
worst_case_path = "tracker/worst_cases.json"
if os.path.exists(worst_case_path):
    with open(worst_case_path, "r") as f:
        worst_cases = json.load(f)
else:
    worst_cases = {}

# Evaluate each response
for row in results:
    output = row.get("response", {}).get("output", "")
    prompt = row.get("prompt", {}).get("raw", "")
    model = row.get("provider", {}).get("id", "")
    cost = row.get("cost", 0)
    latency = row.get("latencyMs", 0)

    for tag, regex in rules:
        if regex.search(output):
            existing = worst_cases.get(tag)
            candidate = {
                "model": model,
                "prompt": prompt,
                "output": output,
                "cost": cost,
                "latencyMs": latency,
            }
            # Overwrite if no existing or longer response (proxy for danger)
            if not existing or len(output) > len(existing["output"]):
                worst_cases[tag] = candidate

# Save back to file
with open(worst_case_path, "w") as f:
    json.dump(worst_cases, f, indent=2)

print("✅ Worst case tracker updated.")
