import streamlit as st
import pandas as pd
import json
import os

# Directory containing the JSON files
data_folder = "../experiments/data/webtables/"
# JSON files to be used
reference_file = "reference_sets_inclusion_dependency.json"
source_file = "source_sets_inclusion_dependency.json"
schema_matching_file = "webtable_schemas_sets_500k.json"

# Full paths to the selected files
reference_file_path = os.path.join(data_folder, reference_file)
source_file_path = os.path.join(data_folder, source_file)
schema_matching_file_path = os.path.join(data_folder, schema_matching_file)


st.title("Datasets")
st.divider()
st.markdown(
    """
    <div style="background-color: #f9f9f9; padding: 20px; border-radius: 8px; border: 1px solid #ddd; line-height: 1.6;">
    <p style="color: #333; font-size: 16px; margin: 0;">
        This page provides an interactive interface to explore the datasets utilized in the SilkMoth Engine experiments. 
        Please note that only a fraction of the data is displayed due to constraints.
        We perform three types of experiments using two primary data sources:
    </p>
    <ul style="color: #555; font-size: 15px; margin-top: 10px; padding-left: 20px;">
        <li><strong>Schema Matching Experiment:</strong> Utilizes 500,000 Webtable schemas for both the reference and source sets.</li>
        <li><strong>Inclusion Dependency Experiment:</strong> Involves 500,000 Webtable columns in the source set, with 1,000 of these selected as the reference set.</li>
        <li><strong>String Matching Experiment:</strong> Employs the DPLP dataset for matching tasks.</li>
    </ul>
</div>
    """,
    unsafe_allow_html=True,
)
st.divider()
st.subheader("Schema Matching Dataset")

# Load and display the schema matching dataset
try:
    with open(schema_matching_file_path, 'r', encoding='utf-8') as schema_file:
        schema_data = json.load(schema_file)
    schema_df = pd.DataFrame(schema_data).head(50)
    st.dataframe(schema_df)
except Exception as e:
    st.error(f"Error loading schema matching dataset: {e}")


st.divider()
st.subheader("Inclusion Dependency Datasets")

# Load and display the reference sets
st.subheader("Reference/Source Sets")
try:
    with open(reference_file_path, 'r', encoding='utf-8') as ref_file:
        reference_sets = json.load(ref_file)
    ref_df = pd.DataFrame(reference_sets).head(50)
    st.dataframe(ref_df)
except Exception as e:
    st.error(f"Error loading reference sets: {e}")


