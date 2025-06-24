import pandas as pd
import os
import datetime

def record_false_negative(prompt, output, model, assigned_tag, path="results/false_negatives.csv"):
    feedback = {
        "Timestamp": datetime.datetime.now().isoformat(),
        "Prompt": prompt,
        "Output": output,
        "Model": model,
        "AssignedTag": assigned_tag
    }
    _write_feedback(feedback, path)

def record_false_positive(prompt, output, model, removed_tags, added_tag, path="results/false_positives.csv"):
    feedback = {
        "Timestamp": datetime.datetime.now().isoformat(),
        "Prompt": prompt,
        "Output": output,
        "Model": model,
        "RemovedTags": removed_tags,
        "AddedTag": added_tag
    }
    _write_feedback(feedback, path)

def _write_feedback(feedback, path):
    df = pd.DataFrame([feedback])
    if os.path.exists(path):
        df.to_csv(path, mode="a", header=False, index=False)
    else:
        df.to_csv(path, index=False)
              
       
def load_feedback_logs(path: str) -> pd.DataFrame:
    if os.path.exists(path):
        return pd.read_csv(path, on_bad_lines='skip')  # Skip malformed rows
    else:
        return pd.DataFrame()
