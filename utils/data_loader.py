import json
import pandas as pd

def load_eval_results(json_path="results/raw/eval-results.json"):
    with open(json_path) as f:
        raw_data = json.load(f)["results"]["results"]
    return raw_data

def tag_rows(data, rules):
    rows = []
    for row in data:
        output = row.get("response", {}).get("output", "")
        prompt = row.get("prompt", {}).get("raw", "")
        provider = row.get("provider", {}).get("id", "")
        tags = [r_id for r_id, r_data in rules.items() if r_data["pattern"].search(output)]
        rows.append({
            "Prompt": prompt,
            "Output": output,
            "Model": provider,
            "Tags": tags
        })
    return pd.DataFrame(rows)
