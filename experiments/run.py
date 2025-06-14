import multiprocessing
from experiments import run_filter_experiment
import os
from data_loader import DataLoader
from utils import load_sets_from_files
from silkmoth.utils import jaccard_similarity, contain, similar


def run_experiment(experiment_method, *args):
    experiment_method(*args)


if __name__ == "__main__":
    data_loader = DataLoader(data_path=os.getenv("SILKMOTH_DATA_PATH"))

    # Labels for Filter Experiments
    labels = ["NO FILTER", "CHECK FILTER", "NN FILTER"]

    # Load the datasets for Filter Experiments
    data_path = os.path.join(os.path.dirname(__file__), "data", "dblp", "DBLP_100k.csv")
    source_string_matching = data_loader.load_dblp_titles(data_path)
    source_string_matching = [title.split() for title in source_string_matching]
    source_string_matching = source_string_matching[:3000]

    try:
        folder_path = os.path.join(os.path.dirname(__file__), "../experiments/data/webtables")
        folder_path = os.path.normpath(folder_path)

        reference_sets_in_dep, source_sets_in_dep = load_sets_from_files(
            folder_path=folder_path,
            reference_file="reference_sets_inclusion_dependency.json",
            source_file="source_sets_inclusion_dependency.json"
        )
        reference_sets_in_dep = reference_sets_in_dep[:10]
        source_sets_in_dep = source_sets_in_dep[:100_000]

        reference_sets_schema_matching, source_sets_schema_matching = load_sets_from_files(
            folder_path=folder_path,
            reference_file="webtable_schemas_sets_500k.json",
            source_file="webtable_schemas_sets_500k.json"
        )
        source_sets_schema_matching = source_sets_schema_matching[:2_000]
        del reference_sets_schema_matching
    except FileNotFoundError:
        print("Datasets not found. Skipping Experiments.")
        reference_sets_in_dep, source_sets_in_dep = [], []
        source_sets_schema_matching = []

    # Define experiments to run
    experiments = [
        # String Matching Experiment
        (run_filter_experiment, [0.7, 0.75, 0.8, 0.85], [0.7, 0.75, 0.8, 0.85],
         labels, source_string_matching, None, similar, jaccard_similarity, False,
         "dblp_string_matching", "results/string_matching/"),

        # Schema Matching Experiment
        (run_filter_experiment, [0.7, 0.75, 0.8, 0.85], [0.0, 0.25, 0.5, 0.75],
         labels, source_sets_schema_matching, None, similar, jaccard_similarity, False,
         "schema_matching", "results/schema_matching/"),

        # Inclusion Dependency Experiment
        (run_filter_experiment, [0.7, 0.75, 0.8, 0.85], [0.0, 0.25, 0.5, 0.75],
         labels, source_sets_in_dep, reference_sets_in_dep, contain, jaccard_similarity, True,
         "inclusion_dependency", "results/inclusion_dependency/"),
    ]

    # Create and start processes for each experiment
    processes = []
    for experiment in experiments:
        method, *args = experiment
        process = multiprocessing.Process(target=run_experiment, args=(method, *args))
        processes.append(process)
        process.start()

    # Wait for all processes to complete
    for process in processes:
        process.join()