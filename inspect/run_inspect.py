import re
import json
import yaml

# Load rules
with open("inspect/rules.yaml", "r") as f:
    rules_yaml = yaml.safe_load(f)

rules = rules_yaml["rules"]
regexes = [(r["id"], re.compile(r["pattern"], re.IGNORECASE)) for r in rules]

# Load Promptfoo results
with open("results/raw/eval-results.json", "r") as f:
    data = json.load(f)

# Go into the actual results array
results = data["results"]["results"]

# Loop through and tag
for row in results:
    output = row.get("response", {}).get("output", "")
    prompt = row.get("prompt", {}).get("raw", "")
    provider = row.get("provider", {}).get("id", "")

    tags = [rule_id for rule_id, regex in regexes if regex.search(output)]

    print(f"\n---\nModel: {provider}\nPrompt: {prompt}\nOutput:\n{output}\nTags: {tags}")
