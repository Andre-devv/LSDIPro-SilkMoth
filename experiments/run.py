import multiprocessing
from experiments import run_experiment
import os
from data_loader import DataLoader
from utils import load_sets_from_files, experiment_set_ratio_calc
from silkmoth.utils import jaccard_similarity, contain, similar, SigType


def run_experiment_multi(experiment_method, *args):
    experiment_method(*args)


if __name__ == "__main__":
    data_loader = DataLoader("/")

    # Labels for Filter Experiments
    labels_filter = ["NO FILTER", "CHECK FILTER", "NN FILTER"]

    # Labels for Signature Scheme
    labels_sig_schemes = [SigType.WEIGHTED, SigType.SKYLINE, SigType.DICHOTOMY]

    # Load the datasets for Filter Experiments
    data_path = os.path.join(os.path.dirname(__file__), "data", "dblp", "DBLP_100k.csv")
    source_string_matching = data_loader.load_dblp_titles(data_path)
    source_string_matching = [title.split() for title in source_string_matching]

    try:
        folder_path = os.path.join(os.path.dirname(__file__), "../experiments/data/webtables")
        folder_path = os.path.normpath(folder_path)

        reference_sets_in_dep, source_sets_in_dep = load_sets_from_files(
            folder_path=folder_path,
            reference_file="reference_sets_inclusion_dependency.json",
            source_file="source_sets_inclusion_dependency.json"
        )

        reference_sets_schema_matching, source_sets_schema_matching = load_sets_from_files(
            folder_path=folder_path,
            reference_file="webtable_schemas_sets_500k.json",
            source_file="webtable_schemas_sets_500k.json"
        )
        del reference_sets_schema_matching
    except FileNotFoundError:
        print("Datasets not found. Skipping Experiments.")
        reference_sets_in_dep, source_sets_in_dep = [], []
        source_sets_schema_matching = []

    # Calculate ratios:
    """
    experiment_set_ratio_calc(source_string_matching, jaccard_similarity ,"results/string_matching/string_matching_ratio.csv", "String Matching")
    experiment_set_ratio_calc(source_sets_schema_matching, jaccard_similarity, "results/schema_matching/schema_matching_ratio.csv", "Schema Matching")
    experiment_set_ratio_calc(source_sets_in_dep, jaccard_similarity, "results/inclusion_dependency/inclusion_dependency_ratio.csv", "Inclusion Dependency")
    """
    # Define experiments to run
    experiments = [
        # Filter runs
        # String Matching Experiment
        #(run_experiment, [0.7, 0.75, 0.8, 0.85], [0.7, 0.75, 0.8, 0.85],
         #labels, source_string_matching, None, similar, jaccard_similarity, False,
         #"dblp_string_matching_filter", "results/string_matching/"),

        # Schema Matching Experiment
        #(run_experiment, [0.7, 0.75, 0.8, 0.85], [0.0, 0.25, 0.5, 0.75],
        #labels, source_sets_schema_matching[:60_000], None, similar, jaccard_similarity, False,
         #"schema_matching_filter", "results/schema_matching/", False),

         #Inclusion Dependency Experiment
        #(run_experiment, [0.7, 0.75, 0.8, 0.85], [0.0, 0.25, 0.5, 0.75],
         #labels, source_sets_in_dep, reference_sets_in_dep[:200], contain, jaccard_similarity, True,
         #"inclusion_dependency_filter", "results/inclusion_dependency/", False),



        # Signature Scheme Runs
        # Schema Matching Experiment
         (run_experiment, [0.7, 0.75, 0.8, 0.85], [0.0, 0.25, 0.5, 0.75],
         labels_sig_schemes, source_sets_schema_matching[:5_000], None, similar, jaccard_similarity, False,
         "schema_matching_sig", "results/schema_matching/", True),

        # Inclusion Dependency Experiment
        #(run_experiment, [0.7, 0.75, 0.8, 0.85], [0.0, 0.25, 0.5, 0.75],
        # labels_sig_schemes, source_sets_in_dep, reference_sets_in_dep[:10], contain, jaccard_similarity, True,
        #"inclusion_dependency_sig", "results/inclusion_dependency/", True),

    ]

    # Create and start processes for each experiment
    processes = []
    for experiment in experiments:
        method, *args = experiment
        process = multiprocessing.Process(target=run_experiment_multi, args=(method, *args))
        processes.append(process)
        process.start()

    # Wait for all processes to complete
    for process in processes:
        process.join()





