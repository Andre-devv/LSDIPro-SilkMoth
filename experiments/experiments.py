from data_loader import DataLoader
from utils import *
from silkmoth.silkmoth_engine import SilkMothEngine
from silkmoth.utils import jaccard_similarity, contain, similar

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


    
    def run_dblp_approximate_string_matching_experiment(self):

        data_path = os.path.join(os.path.dirname(__file__), "data", "dblp", "DBLP_100k.csv")
        
        # Load titles
        titles = self.data_loader.load_dblp_titles(data_path)
        titles = [title.split() for title in titles]

        # Reduce/adjust dataset size for testing
        titles = titles[:4000]  

        #related_thresholds can be adjusted to [0.7, 0.75, 0.8, 0.85]
        related_thresholds = [0.7, 0.75, 0.8, 0.85] # larger data size returns better and more results for 0.7 to 0.85 

        elapsed_times = []

        for threshold in related_thresholds:
            print(f"\nRunning SilkMoth with δ = {threshold}")

            start_time = time.time()

            engine = SilkMothEngine(
                related_thresh=threshold,
                source_sets=titles,
                sim_metric=similar,
                sim_func=jaccard_similarity, # later with edit similarity 
                sim_thresh=0, 
                reduction=False
            )

            # Using discovery mode
            related_pairs = engine.discover_sets(titles)
            end_time = time.time()
            print(f"\nFound {len(related_pairs)} related pairs.")

            #for i, j, sim in related_pairs:
            #    print(f"[{sim:.3f}] {i}: {titles[i]}  ↔  {j}: {titles[j]}")

            elapsed = end_time - start_time
            elapsed_times.append(elapsed)
            print(f"δ = {threshold} → Elapsed time: {elapsed:.2f}s")

        plot_elapsed_times(
            related_thresholds=related_thresholds,
            elapsed_times=elapsed_times,
            fig_text="Approximate String Matching (α = 0.0)",
            legend_label="WEIGHTED",
            file_name="dblp_string_matching_experiment.png"
    )



