import time
from math import floor

from silkmoth.silkmoth_engine import SilkMothEngine
from silkmoth.utils import SigType, edit_similarity
from utils import *
import multiprocessing
from multiprocessing import Manager


def run_experiment_filter_schemes(related_thresholds, similarity_thresholds, labels, source_sets, reference_sets,
                          sim_metric, sim_func, is_search, file_name_prefix, folder_path):
    """
    Parameters
    ----------
    related_thresholds : list[float]
        Thresholds for determining relatedness between sets.
    similarity_thresholds : list[float]
        Thresholds for measuring similarity between sets.
    labels : list[str]
        Labels indicating the type of setting applied (e.g., "NO FILTER", "CHECK FILTER", "WEIGHTED").
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

    for sim_thresh in similarity_thresholds:

        # Check if the similarity function is edit similarity
        if sim_func == edit_similarity:
            # calc the maximum possible q-gram size based on sim_thresh
            upper_bound_q = sim_thresh/(1 - sim_thresh)
            q = floor(upper_bound_q)

            print(f"Using q = {q} for edit similarity with sim_thresh = {sim_thresh}")
            print(f"Rebuilding Inverted Index with q = {q}...")
            silk_moth_engine.set_q(q)



        elapsed_times_final = []
        silk_moth_engine.set_alpha(sim_thresh)
        for label in labels:

            elapsed_times = []
            for idx, related_thresh in enumerate(related_thresholds):

                print(
                    f"\nRunning SilkMoth {file_name_prefix} with α = {sim_thresh}, θ = {related_thresh}, label = {label}")

                # checks for filter runs
                if label == "CHECK FILTER":
                    silk_moth_engine.is_check_filter = True
                    silk_moth_engine.is_nn_filter = False
                elif label == "NN FILTER":
                    silk_moth_engine.is_check_filter = False
                    silk_moth_engine.is_nn_filter = True
                else:  # NO FILTER
                    silk_moth_engine.is_check_filter = False
                    silk_moth_engine.is_nn_filter = False

                # checks for signature scheme runs
                if label == SigType.WEIGHTED:
                    silk_moth_engine.set_signature_type(SigType.WEIGHTED)
                elif label == SigType.SKYLINE:
                    silk_moth_engine.set_signature_type(SigType.SKYLINE)
                elif label == SigType.DICHOTOMY:
                    silk_moth_engine.set_signature_type(SigType.DICHOTOMY)

                silk_moth_engine.set_related_threshold(related_thresh)
                # Measure the time taken to search for related sets
                time_start = time.time()

                # Used for search to see how many candidates were found and how many were removed
                candidates_amount = 0
                candidates_after = 0
                related_sets_found = 0
                if is_search:
                    for ref_id, ref_set in enumerate(reference_sets):
                        related_sets_temp, candidates_amount_temp, candidates_removed_temp = silk_moth_engine.search_sets(
                            ref_set)
                        candidates_amount += candidates_amount_temp
                        candidates_after += candidates_removed_temp
                        related_sets_found += len(related_sets_temp)
                else:
                    # If not searching, we are discovering sets
                    silk_moth_engine.discover_sets(source_sets)

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
                        "related_sets_found": related_sets_found,
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
                # Save results to a CSV file
                save_experiment_results_to_csv(
                    results=data_overall,
                    file_name=f"{folder_path}{file_name_prefix}_experiment_results.csv"
                )

            elapsed_times_final.append(elapsed_times)
        _ = plot_elapsed_times(
            related_thresholds=related_thresholds,
            elapsed_times_list=elapsed_times_final,
            fig_text=f"{file_name_prefix} (α = {sim_thresh})",
            legend_labels=labels,
            file_name=f"{folder_path}{file_name_prefix}_experiment_α={sim_thresh}.png"
        )


def run_reduction_experiment(related_thresholds, similarity_threshold, labels, source_sets, reference_sets,
                          sim_metric, sim_func, is_search, file_name_prefix, folder_path):
    """
    Parameters
    ----------
    related_thresholds : list[float]
        Thresholds for determining relatedness between sets.
    similarity_threshold : float
        Thresholds for measuring similarity between sets.
    labels : list[str]
        Labels indicating the type of setting applied (e.g., "NO FILTER", "CHECK FILTER", "WEIGHTED").
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
    in_index_time_start = time.time()
    initial_ram = measure_ram_usage()

    # Initialize and run the SilkMothEngine
    silk_moth_engine = SilkMothEngine(
        related_thresh=0,
        source_sets=source_sets,
        sim_metric=sim_metric,
        sim_func=sim_func,
        sim_thresh=similarity_threshold,
        is_check_filter=False,
        is_nn_filter=False,
    )
    # use dichotomy signature scheme for this experiment
    silk_moth_engine.set_signature_type(SigType.DICHOTOMY)

    in_index_time_end = time.time()
    final_ram = measure_ram_usage()

    in_index_elapsed_time = in_index_time_end - in_index_time_start
    in_index_ram_usage = final_ram - initial_ram

    print(f"Inverted Index created in {in_index_elapsed_time:.2f} seconds.")

    elapsed_times_final = []
    for label in labels:

        if label == "REDUCTION":
            silk_moth_engine.set_reduction(True)
        elif label == "NO REDUCTION":
            silk_moth_engine.set_reduction(False)

        elapsed_times = []
        for idx, related_thresh in enumerate(related_thresholds):

            print(
                f"\nRunning SilkMoth {file_name_prefix} with α = {similarity_threshold}, θ = {related_thresh}, label = {label}")

            silk_moth_engine.set_related_threshold(related_thresh)
            # Measure the time taken to search for related sets
            time_start = time.time()

            # Used for search to see how many candidates were found and how many were removed
            candidates_amount = 0
            candidates_after = 0
            if is_search:
                for ref_id, ref_set in enumerate(reference_sets):
                    related_sets_temp, candidates_amount_temp, candidates_removed_temp = silk_moth_engine.search_sets(
                        ref_set)
                    candidates_amount += candidates_amount_temp
                    candidates_after += candidates_removed_temp
            else:
                # If not searching, we are discovering sets
                silk_moth_engine.discover_sets(source_sets)

            time_end = time.time()
            elapsed_time = time_end - time_start

            elapsed_times.append(elapsed_time)

            # Create a new data dictionary for each iteration
            if is_search:
                data_overall = {
                    "similarity_threshold": similarity_threshold,
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
                    "similarity_threshold": similarity_threshold,
                    "related_threshold": related_thresh,
                    "source_set_amount": len(source_sets),
                    "label": label,
                    "elapsed_time": round(elapsed_time, 3),
                    "inverted_index_time": round(in_index_elapsed_time, 3),
                    "inverted_index_ram_usage": round(in_index_ram_usage, 3),
                }

            # Save results to a CSV file
            save_experiment_results_to_csv(
                results=data_overall,
                file_name=f"{folder_path}{file_name_prefix}_experiment_results.csv"
            )


        elapsed_times_final.append(elapsed_times)
    _ = plot_elapsed_times(
        related_thresholds=related_thresholds,
        elapsed_times_list=elapsed_times_final,
        fig_text=f"{file_name_prefix} (α = {similarity_threshold})",
        legend_labels=labels,
        file_name=f"{folder_path}{file_name_prefix}_experiment_α={similarity_threshold}.png"
    )


def run_scalability_experiment(related_thresholds, similarity_threshold, set_sizes, source_sets, reference_sets,
                          sim_metric, sim_func, is_search, file_name_prefix, folder_path):
    """
    Parameters
    ----------
    related_thresholds : list[float]
        Thresholds for determining relatedness between sets.
    similarity_threshold : float
        Thresholds for measuring similarity between sets.
    set_sizes : list[int]
        Sizes of the sets to be used in the experiment.
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
    elapsed_times_final = []
    for idx, related_thresh in enumerate(related_thresholds):
        elapsed_times = []
        for size in set_sizes:
            in_index_time_start = time.time()
            initial_ram = measure_ram_usage()

            # Initialize and run the SilkMothEngine
            silk_moth_engine = SilkMothEngine(
                related_thresh=0,
                source_sets=source_sets[:size],
                sim_metric=sim_metric,
                sim_func=sim_func,
                sim_thresh=similarity_threshold,
                is_check_filter=True,
                is_nn_filter=True,
            )
            in_index_time_end = time.time()
            final_ram = measure_ram_usage()

            in_index_elapsed_time = in_index_time_end - in_index_time_start
            in_index_ram_usage = final_ram - initial_ram

            print(f"Inverted Index created in {in_index_elapsed_time:.2f} seconds.")


            print(
                f"\nRunning SilkMoth {file_name_prefix} with α = {similarity_threshold}, θ = {related_thresh}, set_size = {size}")

            silk_moth_engine.set_related_threshold(related_thresh)
            # Measure the time taken to search for related sets
            time_start = time.time()

            if sim_func == edit_similarity:
                # calc the maximum possible q-gram size based on sim_thresh
                upper_bound_q = similarity_threshold / (1 - similarity_threshold)
                q = floor(upper_bound_q)

                print(f"Using q = {q} for edit similarity with sim_thresh = {similarity_threshold}")
                print(f"Rebuilding Inverted Index with q = {q}...")
                silk_moth_engine.set_q(q)

            # Used for search to see how many candidates were found and how many were removed
            candidates_amount = 0
            candidates_after = 0
            if is_search:
                for ref_id, ref_set in enumerate(reference_sets):
                    related_sets_temp, candidates_amount_temp, candidates_removed_temp = silk_moth_engine.search_sets(
                        ref_set)
                    candidates_amount += candidates_amount_temp
                    candidates_after += candidates_removed_temp
            else:
                # If not searching, we are discovering sets
                silk_moth_engine.discover_sets(source_sets[:size])

            time_end = time.time()
            elapsed_time = time_end - time_start

            elapsed_times.append(elapsed_time)

            # Create a new data dictionary for each iteration
            if is_search:
                data_overall = {
                    "similarity_threshold": similarity_threshold,
                    "related_threshold": related_thresh,
                    "reference_set_amount": len(reference_sets),
                    "source_set_amount": len(source_sets[:size]),
                    "set_size": size,
                    "elapsed_time": round(elapsed_time, 3),
                    "inverted_index_time": round(in_index_elapsed_time, 3),
                    "inverted_index_ram_usage": round(in_index_ram_usage, 3),
                    "candidates_amount": candidates_amount,
                    "candidates_amount_after_filtering": candidates_after,
                }
            else:
                data_overall = {
                    "similarity_threshold": similarity_threshold,
                    "related_threshold": related_thresh,
                    "source_set_amount": len(source_sets[:size]),
                    "set_size": size,
                    "elapsed_time": round(elapsed_time, 3),
                    "inverted_index_time": round(in_index_elapsed_time, 3),
                    "inverted_index_ram_usage": round(in_index_ram_usage, 3),
                }

            # Save results to a CSV file
            save_experiment_results_to_csv(
                results=data_overall,
                file_name=f"{folder_path}{file_name_prefix}_experiment_results.csv"
            )
        del silk_moth_engine

        elapsed_times_final.append(elapsed_times)

    # create legend labels based on set sizes
    adjusted_legend_labels = [f"θ = {rt}" for rt in related_thresholds]
    adjusted_set_sizes = [size / 100_000 for size in set_sizes]
    _ = plot_elapsed_times(
        related_thresholds=adjusted_set_sizes,
        elapsed_times_list=elapsed_times_final,
        fig_text=f"{file_name_prefix} (α = {similarity_threshold})",
        legend_labels=adjusted_legend_labels,
        file_name=f"{folder_path}{file_name_prefix}_experiment_α={similarity_threshold}.png",
        xlabel="Number of Sets (in 100ks)",
    )