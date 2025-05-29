from data_loader import DataLoader
from utils import *
from silkmoth.silkmoth_engine import SilkMothEngine
from silkmoth.utils import jaccard_similarity, contain

import time
import os

class Experiments:
    def __init__(self, data_path=os.getenv("SILKMOTH_DATA_PATH", None)):
        self.data_loader = DataLoader(data_path)


    def run_webtable_approximate_inclusion_dependency_experiment(self):
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

        # Collect results
        elapsed_times = []

        for related_threshold in related_thresholds:
            # Measure the time taken to search for related sets
            time_start = time.time()

            silk_moth_engine = SilkMothEngine(
                related_thresh= related_threshold,
                source_sets= source_sets,
                sim_metric= contain,
                sim_func= jaccard_similarity,
                sim_thresh= 0,
                reduction=False
            )
            related_sets = silk_moth_engine.search_sets(reference_sets[500])
            time_end = time.time()

            # Release previous instance to free memory
            del silk_moth_engine
            del related_sets


            elapsed_time = time_end - time_start
            elapsed_times.append(elapsed_time)
            print(f"Related threshold: {related_threshold}, Elapsed time: {elapsed_time:.2f} seconds")


        plot_elapsed_times(
            related_thresholds=related_thresholds,
            elapsed_times=elapsed_times,
            fig_text="Inclusion Dependency (α = 0.0)",
            legend_label="WEIGHTED",
            file_name="webtable_inclusion_dependency_experiment.png"
        )


