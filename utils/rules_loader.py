import yaml
import re

def load_rules(filepath="inspect/rules.yaml"):
    with open(filepath) as f:
        rules_yaml = yaml.safe_load(f)

    return {
        r["id"]: {
            "pattern": re.compile(r["pattern"], re.IGNORECASE),
            "description": r.get("description", ""),
            "severity": r.get("severity", "medium")
        }
        for r in rules_yaml["rules"]
    }
