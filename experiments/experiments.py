from data_loader import DataLoader
from utils import *
from silkmoth.silkmoth_engine import SilkMothEngine
from silkmoth.utils import jaccard_similarity, contain, similar

import time
import os

def run_filter_experiment(related_thresholds, similarity_thresholds, labels, source_sets, reference_sets,
                          sim_metric, sim_func, is_search, file_name_prefix, folder_path):
    """
    Parameters
    ----------

    related_thresholds : list[float]
        Thresholds for determining relatedness between sets.
    similarity_thresholds : list[float]
        Thresholds for measuring similarity between sets.
    labels : list[str]
        Labels indicating the type of filtering applied (e.g., "NO FILTER", "CHECK FILTER", "NN FILTER").
    source_sets : list[]
        The sets to be compared against the reference sets or against itself.
    reference_sets : list[]
        The sets used as the reference for comparison.
    sim_metric : callable
        The metric function used to evaluate similarity between sets.
    sim_func : callable
        The function used to calculate similarity scores.
    is_search : bool
        Flag indicating whether to perform a search operation or discovery.
    file_name_prefix : str
        Prefix for naming output files generated during the experiment.
    folder_path: str
        Path to the folder where results will be saved.
    """

    # Calculate index time and RAM usage for the SilkMothEngine
    in_index_time_start = time.time()
    initial_ram = measure_ram_usage()

    # Initialize and run the SilkMothEngine
    silk_moth_engine = SilkMothEngine(
        related_thresh=0,
        source_sets=source_sets,
        sim_metric=sim_metric,
        sim_func=sim_func,
        sim_thresh=0,
        is_check_filter=False,
        is_nn_filter=False,
    )

    in_index_time_end = time.time()
    final_ram = measure_ram_usage()

    in_index_elapsed_time = in_index_time_end - in_index_time_start
    in_index_ram_usage = final_ram - initial_ram

    print(f"Inverted Index created in {in_index_elapsed_time:.2f} seconds.")

    results_overall = []
    results_related_sets = []
    for sim_thresh in similarity_thresholds:
        elapsed_times_final = []
        silk_moth_engine.set_alpha(sim_thresh)

        for label in labels:

            elapsed_times = []
            for idx, related_thresh in enumerate(related_thresholds):

                print(
                    f"\nRunning SilkMoth {file_name_prefix} with α = {sim_thresh}, θ = {related_thresh}, label = {label}")

                if label == "CHECK FILTER":
                    silk_moth_engine.is_check_filter = True
                    silk_moth_engine.is_nn_filter = False
                elif label == "NN FILTER":
                    silk_moth_engine.is_check_filter = False
                    silk_moth_engine.is_nn_filter = True
                else:  # NO FILTER
                    silk_moth_engine.is_check_filter = False
                    silk_moth_engine.is_nn_filter = False

                silk_moth_engine.set_related_threshold(related_thresh)
                # Measure the time taken to search for related sets
                time_start = time.time()

                # Used for search to see how many candidates were found and how many were removed
                candidates_amount = 0
                candidates_after = 0
                if is_search:
                    related_sets = defaultdict(set)
                    for ref_id, ref_set in enumerate(reference_sets):
                        related_sets_temp, candidates_amount_temp, candidates_removed_temp = silk_moth_engine.search_sets(
                            ref_set)
                        candidates_amount += candidates_amount_temp
                        candidates_after += candidates_removed_temp
                        if len(related_sets_temp) > 0:
                            related_sets[ref_id].update(related_sets_temp)
                else:
                    # If not searching, we are discovering sets
                    related_sets = silk_moth_engine.discover_sets(source_sets)



                time_end = time.time()
                elapsed_time = time_end - time_start

                elapsed_times.append(elapsed_time)

                # Create a new data dictionary for each iteration
                if is_search:
                    data_overall = {
                        "similarity_threshold": sim_thresh,
                        "related_threshold": related_thresh,
                        "reference_set_amount": len(reference_sets),
                        "source_set_amount": len(source_sets),
                        "label": label,
                        "elapsed_time": round(elapsed_time, 3),
                        "inverted_index_time": round(in_index_elapsed_time, 3),
                        "inverted_index_ram_usage": round(in_index_ram_usage, 3),
                        "candidates_amount": candidates_amount,
                        "candidates_amount_after_filtering": candidates_after,
                    }
                else:
                    data_overall = {
                        "similarity_threshold": sim_thresh,
                        "related_threshold": related_thresh,
                        "source_set_amount": len(source_sets),
                        "label": label,
                        "elapsed_time": round(elapsed_time, 3),
                        "inverted_index_time": round(in_index_elapsed_time, 3),
                        "inverted_index_ram_usage": round(in_index_ram_usage, 3),
                    }
                data_related_sets = {
                    "similarity_threshold": sim_thresh,
                    "related_threshold": related_thresh,
                    "label": label,
                    "source_set_amount": len(source_sets),
                    "related_sets": related_sets,
                }

                results_overall.append(data_overall)
                results_related_sets.append(data_related_sets)

            elapsed_times_final.append(elapsed_times)

        _ = plot_elapsed_times(
            related_thresholds=related_thresholds,
            elapsed_times_list=elapsed_times_final,
            fig_text=f"String Matching (α = {sim_thresh})",
            legend_labels=labels,
            file_name=f"{folder_path}{file_name_prefix}_filter_experiment_α={sim_thresh}.png"
        )

    # Save results to a CSV file
    save_experiment_results_to_csv(
        results=results_overall,
        file_name=f"{folder_path}{file_name_prefix}_filter_experiment_results.csv"
    )

    save_experiment_results_to_csv(
        results=results_related_sets,
        file_name=f"{folder_path}{file_name_prefix}_filter_experiment_related_sets.csv"
    )
