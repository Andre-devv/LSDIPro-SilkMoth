import random
import time

import streamlit as st

from silkmoth.silkmoth_engine import SilkMothEngine
from silkmoth.utils import jaccard_similarity, contain
import os
import json
from utils import *


# Streamlit app
st.title("SilkMoth Engine Input Interface")
st.divider()
st.subheader("Inclusion Dependency Experiment")


# Input fields for SilkMothEngine parameters
# Allow the user to select the number of thresholds (up to 4)
num_thresholds = st.number_input("Number of Thresholds", min_value=1, max_value=4, value=1, step=1)

# Dynamically create sliders for the selected number of thresholds
thresholds = []
for i in range(num_thresholds):
    threshold = st.slider(f"Threshold {i + 1}", 0.0, 1.0, 0.5, 0.05)
    thresholds.append(threshold)


# sim_thresh = st.slider("Similarity Threshold", 0.0, 1.0, 0.0, 0.05)
check_filter = st.checkbox("Enable Check Filter", value=False)
nn_filter = st.checkbox("Enable Nearest Neighbor Filter", value=False)

# Directory containing the JSON files
data_folder = "../experiments/data/webtables/"

# JSON files to be used
reference_file = "reference_sets_inclusion_dependency.json"
source_file = "source_sets_inclusion_dependency.json"

# Full paths to the selected files
reference_file_path = os.path.join(data_folder, reference_file)
source_file_path = os.path.join(data_folder, source_file)

# Run the SilkMothEngine with progress animation and loading mask
if st.button("Run SilkMoth Engine"):
    if reference_file and source_file:
        try:
            # Create a placeholder for the loading animation
            loading_placeholder = st.empty()
            loading_placeholder.markdown("<div style='text-align: center; font-size: 20px;'>SilkMothEngine is running...</div>", unsafe_allow_html=True)

            # Open and load reference and source sets from selected files
            with open(reference_file_path, 'r', encoding='utf-8') as ref_file:
                reference_sets = json.load(ref_file)[:50]
            with open(source_file_path, 'r', encoding='utf-8') as src_file:
                source_sets = json.load(src_file)[:50_000]



            st.write(f"Create Inverted Index ...")
            in_index_time_start = time.time()
            # Initialize and run the SilkMothEngine
            silk_moth_engine = SilkMothEngine(
                related_thresh=0,
                source_sets=source_sets,
                sim_metric=contain,
                sim_func=jaccard_similarity,
                sim_thresh=0,
                is_check_filter=False,
                is_nn_filter=False,
            )
            in_index_time_end = time.time()
            in_index_elapsed_time = in_index_time_end - in_index_time_start
            st.write(f"Inverted Index created in {in_index_elapsed_time:.2f} seconds.")


            elapsed_times_final = []
            labels = ["NO FILTER"]
            if check_filter:
                labels.append("CHECK FILTER")

            if nn_filter:
                labels.append("NN FILTER")

            if nn_filter and check_filter:
                labels.append("CHECK + NN FILTER")


            for label in labels:
                elapsed_times = []
                for idx, related_thresh in enumerate(thresholds):

                    if label == "CHECK FILTER":
                        silk_moth_engine.is_check_filter = True
                        silk_moth_engine.is_nn_filter = False
                    elif label == "NN FILTER":
                        silk_moth_engine.is_check_filter = False
                        silk_moth_engine.is_nn_filter = True
                    elif label == "CHECK + NN FILTER":
                        silk_moth_engine.is_check_filter = True
                        silk_moth_engine.is_nn_filter = True


                    st.write(f"Processing Threshold {idx + 1}: {related_thresh} with {label} ...")
                    silk_moth_engine.set_related_threshold(related_thresh)
                    # Measure the time taken to search for related sets
                    time_start = time.time()


                    for ref_set in reference_sets:
                        related_sets = silk_moth_engine.search_sets(ref_set)
                        del related_sets

                    time_end = time.time()


                    elapsed_time = time_end - time_start
                    elapsed_times.append(elapsed_time)

                elapsed_times_final.append(elapsed_times)

            # Remove the loading animation
            loading_placeholder.empty()

            # Display results
            st.success("SilkMoth Engine ran successfully!")
            fig = plot_elapsed_times(
                related_thresholds=thresholds,
                elapsed_times_list=elapsed_times_final,
                fig_text="Inclusion Dependency (α = 0.0)",
                legend_labels=labels,
                file_name="webtable_inclusion_dependency_experiment_demo.png"
            )
            st.pyplot(fig)

        except Exception as e:
            st.error(f"An error occurred: {e}")
    else:
        st.warning("Please upload both reference and source set files.")