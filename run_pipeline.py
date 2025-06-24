import argparse
import os
import pandas as pd
from utils.rules_loader import load_rules
from utils.data_loader import load_eval_results, tag_rows
from utils.feedback_writer import load_feedback_logs

OUTPUT_DIR = "results/cli_output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def tag_and_save():
    rules = load_rules()
    raw_data = load_eval_results()
    tagged_df = tag_rows(raw_data, rules)
    out_path = os.path.join(OUTPUT_DIR, "eval-results-tagged.csv")
    tagged_df.to_csv(out_path, index=False)
    print(f"✅ Tagged output saved to {out_path}")

def export_false_negatives():
    df = load_feedback_logs("results/false_negatives.csv")
    out_path = os.path.join(OUTPUT_DIR, "false_negatives_export.csv")
    df.to_csv(out_path, index=False)
    print(f"📤 False negatives exported to {out_path}")

def export_false_positives():
    df = load_feedback_logs("results/false_positives.csv")
    out_path = os.path.join(OUTPUT_DIR, "false_positives_export.csv")
    df.to_csv(out_path, index=False)
    print(f"📤 False positives exported to {out_path}")

def show_stats():
    rules = load_rules()
    raw_data = load_eval_results()
    tagged_df = tag_rows(raw_data, rules)
    exploded = tagged_df.explode("Tags")

    print("\n📊 Top Tag Frequencies:")
    tag_counts = exploded["Tags"].value_counts().head(10)
    print(tag_counts.to_string())

    print("\n🌡️ Crosstab: Model vs. Tags")
    crosstab = pd.crosstab(exploded["Model"], exploded["Tags"])
    print(crosstab.to_string())

def main():
    parser = argparse.ArgumentParser(description="Adversarial Eval CLI")
    parser.add_argument("task", choices=["tag", "fn_export", "fp_export", "stats"], help="Task to perform")

    args = parser.parse_args()

    if args.task == "tag":
        tag_and_save()
    elif args.task == "fn_export":
        export_false_negatives()
    elif args.task == "fp_export":
        export_false_positives()
    elif args.task == "stats":
        show_stats()

if __name__ == "__main__":
    main()
