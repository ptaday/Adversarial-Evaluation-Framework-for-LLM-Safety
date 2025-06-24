import streamlit as st
import pandas as pd
import datetime
import os
import matplotlib.pyplot as plt
import seaborn as sns

from utils.rules_loader import load_rules
from utils.data_loader import load_eval_results, tag_rows
from utils.feedback_writer import record_false_negative, record_false_positive

# --- Load Rules & Eval Data ---
rules = load_rules()
raw_data = load_eval_results()
df = tag_rows(raw_data, rules)

# --- App State ---
if "view" not in st.session_state:
    st.session_state.view = "main"  # or "stats"

st.title("🔍 Adversarial LLM Eval Viewer")

# --- Navigation Buttons ---
if st.session_state.view == "main":
    if st.button("📊 View Stats & Heatmap"):
        st.session_state.view = "stats"
        st.rerun()
elif st.session_state.view == "stats":
    if st.button("🔙 Back to Prompt Review"):
        st.session_state.view = "main"
        st.rerun()

# --- STATS VIEW ---
if st.session_state.view == "stats":
    st.markdown("## 📊 Evaluation Summary & Heatmap")
    exploded = df.explode("Tags")
    if exploded.empty:
        st.warning("No data available for stats.")
    else:
        st.markdown("### 🔁 Top Tags Frequency")
        tag_counts = exploded["Tags"].value_counts().reset_index()
        tag_counts.columns = ["Tag", "Count"]
        st.bar_chart(tag_counts.set_index("Tag"))

        st.markdown("### 🌡️ Heatmap: Model vs. Tag")
        heatmap_data = pd.crosstab(exploded["Model"], exploded["Tags"])
        if not heatmap_data.empty:
            st.dataframe(heatmap_data)
            fig, ax = plt.subplots(figsize=(10, 4))
            sns.heatmap(heatmap_data, annot=True, fmt="d", cmap="Oranges", linewidths=0.5, cbar=False, ax=ax)
            st.pyplot(fig)
        else:
            st.info("Not enough tagged data for heatmap.")
    st.stop()

# --- MAIN PROMPT REVIEW VIEW ---
# Filters
all_tags = sorted(set(df["Tags"].explode().dropna()))
selected_tags = st.multiselect("📛 Filter by Tags", options=["(No Tags)"] + all_tags)
selected_model = st.selectbox("🤖 Filter by Model", options=["All"] + sorted(df["Model"].unique()))

if not selected_tags and selected_model == "All":
    st.warning("Please select a tag or model to begin.")
    st.stop()

# Apply filters
filtered = df.copy()
if selected_model != "All":
    filtered = filtered[filtered["Model"] == selected_model]
if selected_tags:
    if "(No Tags)" in selected_tags:
        filtered = filtered[filtered["Tags"].apply(lambda tags: len(tags) == 0)]
    else:
        filtered = filtered[filtered["Tags"].apply(lambda tags: any(tag in tags for tag in selected_tags))]

# Prompt dropdown
prompt_options = {}
for i, (idx, row) in enumerate(filtered.iterrows()):
    tag_status = " [✅ Clean]" if not row["Tags"] else f" [❌ {len(row['Tags'])} Tags]"
    label = f"{i+1}. {row['Prompt'][:80]}{tag_status}"
    prompt_options[label] = idx

selected_label = st.selectbox("📝 Select a Prompt", options=list(prompt_options.keys()))

# --- Display & Interact ---
if selected_label:
    selected_row = filtered.loc[prompt_options[selected_label]]
    st.markdown(f"### 🧾 Prompt:\n{selected_row['Prompt']}")
    st.text_area("📤 Model Output", selected_row["Output"], height=150)
    st.caption(f"Model: {selected_row['Model']}")

    # CASE: No tags — False Negative
    if not selected_row["Tags"]:
        st.success("✅ No tags matched — clean response")
        is_fn = st.checkbox("⚠️ Mark this as a False Negative")
        if is_fn:
            new_tag = st.selectbox("➡️ Assign correct tag", options=sorted(rules.keys()))
            if st.button("📌 Submit False Negative Tag"):
                selected_row["Tags"].append(new_tag)
                record_false_negative(
                    selected_row["Prompt"],
                    selected_row["Output"],
                    selected_row["Model"],
                    new_tag
                )
                st.rerun()

    # CASE: Has tags — False Positive
    else:
        st.warning(f"⚠️ Matched Tags: {', '.join(selected_row['Tags'])}")
        st.markdown("### ❌ Tag Review")
        removed_tag = st.multiselect("🗑️ Remove incorrect tags", options=selected_row["Tags"])
        new_tag = st.selectbox("➕ Add missing tag (optional)", options=["None"] + sorted(set(rules.keys()) - set(selected_row["Tags"])))

        if st.button("✅ Submit Tag Update"):
            updated_tags = list(set([tag for tag in selected_row["Tags"] if tag not in removed_tag]))
            if new_tag != "None":
                updated_tags.append(new_tag)
            selected_row["Tags"] = updated_tags

            record_false_positive(
                selected_row["Prompt"],
                selected_row["Output"],
                selected_row["Model"],
                removed_tag,
                new_tag if new_tag != "None" else ""
            )
            st.rerun()

# --- Download filtered results
st.download_button(
    "📥 Download Filtered Results",
    filtered.to_csv(index=False),
    file_name="filtered_results.csv",
    mime="text/csv"
)
