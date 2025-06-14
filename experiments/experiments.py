from data_loader import DataLoader
from utils import *
from silkmoth.silkmoth_engine import SilkMothEngine
from silkmoth.utils import jaccard_similarity, contain, similar

import time
import os


class Experiments:
    def __init__(self, data_path=os.getenv("SILKMOTH_DATA_PATH", None)):
        self.data_loader = DataLoader(data_path)

    def run_webtable_approximate_inclusion_dependency_filter_experiment(self):
        # Prepare data and configuration for the experiment
        try:
            folder_path = os.path.join(os.path.dirname(__file__), "../experiments/data/webtables")
            folder_path = os.path.normpath(folder_path)
            reference_sets, source_sets = load_sets_from_files(
                folder_path=folder_path,
                reference_file="reference_sets_inclusion_dependency.json",
                source_file="source_sets_inclusion_dependency.json"
            )
        except FileNotFoundError:
            reference_sets, source_sets = self.data_loader.load_webtable_columns_randomized(1000, 500_000)

        related_thresholds = [0.7, 0.75, 0.8, 0.85]
        similarity_thresholds = [0.0, 0.25, 0.5, 0.75]
        # Filter experiment setup
        labels = ["NO FILTER", "CHECK FILTER", "NN FILTER"]

        # Reduce the size of the datasets for testing purposes if needed
        # reference_sets = reference_sets[:10]
        # source_sets = source_sets[:100_000]

        # Calculate index time and RAM usage for the SilkMothEngine
        in_index_time_start = time.time()
        initial_ram = measure_ram_usage()

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
        final_ram = measure_ram_usage()

        in_index_elapsed_time = in_index_time_end - in_index_time_start
        in_index_ram_usage = final_ram - initial_ram

        print(f"Inverted Index created in {in_index_elapsed_time:.2f} seconds.")

        results = []
        for sim_thresh in similarity_thresholds:
            elapsed_times_final = []
            silk_moth_engine.set_alpha(sim_thresh)

            for label in labels:

                elapsed_times = []
                for idx, related_thresh in enumerate(related_thresholds):

                    print(
                        f"\nRunning SilkMoth inclusion dependency with α = {sim_thresh}, θ = {related_thresh}, label = {label}")

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

                    related_sets = defaultdict(set)
                    candidates_amount = 0
                    candidates_after = 0

                    for ref_id, ref_set in enumerate(reference_sets):
                        related_sets_temp, candidates_amount_temp, candidates_removed_temp = silk_moth_engine.search_sets(
                            ref_set)
                        candidates_amount += candidates_amount_temp
                        candidates_after += candidates_removed_temp
                        if len(related_sets_temp) > 0:
                            related_sets[ref_id].update(related_sets_temp)



                    time_end = time.time()
                    elapsed_time = time_end - time_start

                    elapsed_times.append(elapsed_time)

                    # Create a new data dictionary for each iteration
                    data = {
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
                        "related_sets": related_sets,
                    }

                    results.append(data)

                elapsed_times_final.append(elapsed_times)

            _ = plot_elapsed_times(
                related_thresholds=related_thresholds,
                elapsed_times_list=elapsed_times_final,
                fig_text=f"Inclusion Dependency (α = {sim_thresh})",
                legend_labels=labels,
                file_name=f"webtable_inclusion_dependency_filter_experiment_α={sim_thresh}.png"
            )

        # Save results to a CSV file
        save_experiment_results_to_csv(
            results=results,
            file_name="webtable_inclusion_dependency_filter_experiment_results.csv"
        )

    def run_webtable_schema_matching_filter_experiment(self):
        # Prepare data and configuration for the experiment
        try:
            folder_path = os.path.join(os.path.dirname(__file__), "../experiments/data/webtables")
            folder_path = os.path.normpath(folder_path)
            _, source_sets = load_sets_from_files(
                folder_path=folder_path,
                reference_file="webtable_schemas_sets_500k.json",
                source_file="webtable_schemas_sets_500k.json"
            )
        except FileNotFoundError:
            source_sets = self.data_loader.load_webtable_schemas_randomized(500_000)

        related_thresholds = [0.7, 0.75, 0.8, 0.85]
        similarity_thresholds = [0.0, 0.25, 0.5, 0.75]
        # Filter experiment setup
        labels = ["NO FILTER", "CHECK FILTER", "NN FILTER"]

        # Reduce the size of the datasets for testing purposes if needed
        source_sets = source_sets[:2_000]

        # Calculate index time and RAM usage for the SilkMothEngine
        in_index_time_start = time.time()
        initial_ram = measure_ram_usage()

        # Initialize and run the SilkMothEngine
        silk_moth_engine = SilkMothEngine(
            related_thresh=0,
            source_sets=source_sets,
            sim_metric=similar,
            sim_func=jaccard_similarity,
            sim_thresh=0,
            is_check_filter=False,
            is_nn_filter=False,
        )

        in_index_time_end = time.time()
        final_ram = measure_ram_usage()

        in_index_elapsed_time = in_index_time_end - in_index_time_start
        in_index_ram_usage = final_ram - initial_ram

        print(f"Inverted Index created in {in_index_elapsed_time:.2f} seconds.")

        results = []
        for sim_thresh in similarity_thresholds:
            elapsed_times_final = []
            silk_moth_engine.set_alpha(sim_thresh)

            for label in labels:

                elapsed_times = []
                for idx, related_thresh in enumerate(related_thresholds):

                    print(
                        f"\nRunning SilkMoth schema matching with α = {sim_thresh}, θ = {related_thresh}, label = {label}")

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

                    related_sets = silk_moth_engine.discover_sets(source_sets)

                    time_end = time.time()
                    elapsed_time = time_end - time_start

                    elapsed_times.append(elapsed_time)

                    # Create a new data dictionary for each iteration
                    data = {
                        "similarity_threshold": sim_thresh,
                        "related_threshold": related_thresh,
                        "source_set_amount": len(source_sets),
                        "label": label,
                        "elapsed_time": round(elapsed_time, 3),
                        "inverted_index_time": round(in_index_elapsed_time, 3),
                        "inverted_index_ram_usage": round(in_index_ram_usage, 3),
                        "related_sets": related_sets,
                    }

                    results.append(data)

                elapsed_times_final.append(elapsed_times)

            _ = plot_elapsed_times(
                related_thresholds=related_thresholds,
                elapsed_times_list=elapsed_times_final,
                fig_text=f"Schema Matching (α = {sim_thresh})",
                legend_labels=labels,
                file_name=f"webtable_schema_matching_filter_experiment_α={sim_thresh}.png"
            )

        # Save results to a CSV file
        save_experiment_results_to_csv(
            results=results,
            file_name="webtable_schema_matching_filter_experiment_results.csv"
        )


    def run_dblp_approximate_string_matching_experiment(self):

        data_path = os.path.join(os.path.dirname(__file__), "data", "dblp", "DBLP_100k.csv")

        # Load titles
        titles = self.data_loader.load_dblp_titles(data_path)
        titles = [title.split() for title in titles]

        # Reduce/adjust dataset size for testing
        titles = titles[:3000]

        # related_thresholds can be adjusted to [0.7, 0.75, 0.8, 0.85]
        related_thresholds = [0.7, 0.75, 0.8, 0.85]  # larger data size returns better and more results for 0.7 to 0.85
        similarity_thresholds = [0.7, 0.75, 0.8, 0.85]
        # Filter experiment setup
        labels = ["NO FILTER", "CHECK FILTER", "NN FILTER"]

        # Calculate index time and RAM usage for the SilkMothEngine
        in_index_time_start = time.time()
        initial_ram = measure_ram_usage()

        # Initialize and run the SilkMothEngine
        silk_moth_engine = SilkMothEngine(
            related_thresh=0,
            source_sets=titles,
            sim_metric=similar,
            sim_func=jaccard_similarity,
            sim_thresh=0,
            is_check_filter=False,
            is_nn_filter=False,
        )

        in_index_time_end = time.time()
        final_ram = measure_ram_usage()

        in_index_elapsed_time = in_index_time_end - in_index_time_start
        in_index_ram_usage = final_ram - initial_ram

        print(f"Inverted Index created in {in_index_elapsed_time:.2f} seconds.")

        results = []
        for sim_thresh in similarity_thresholds:
            elapsed_times_final = []
            silk_moth_engine.set_alpha(sim_thresh)

            for label in labels:

                elapsed_times = []
                for idx, related_thresh in enumerate(related_thresholds):

                    print(
                        f"\nRunning SilkMoth String matching with α = {sim_thresh}, θ = {related_thresh}, label = {label}")

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

                    related_sets = silk_moth_engine.discover_sets(titles)

                    time_end = time.time()
                    elapsed_time = time_end - time_start

                    elapsed_times.append(elapsed_time)

                    # Create a new data dictionary for each iteration
                    data = {
                        "similarity_threshold": sim_thresh,
                        "related_threshold": related_thresh,
                        "source_set_amount": len(titles),
                        "label": label,
                        "elapsed_time": round(elapsed_time, 3),
                        "inverted_index_time": round(in_index_elapsed_time, 3),
                        "inverted_index_ram_usage": round(in_index_ram_usage, 3),
                        "related_sets": related_sets,
                    }

                    results.append(data)

                elapsed_times_final.append(elapsed_times)

            _ = plot_elapsed_times(
                related_thresholds=related_thresholds,
                elapsed_times_list=elapsed_times_final,
                fig_text=f"String Matching (α = {sim_thresh})",
                legend_labels=labels,
                file_name=f"dblp_string_matching_filter_experiment_α={sim_thresh}.png"
            )

        # Save results to a CSV file
        save_experiment_results_to_csv(
            results=results,
            file_name="dblp_string_matching_filter_experiment_results.csv"
        )
