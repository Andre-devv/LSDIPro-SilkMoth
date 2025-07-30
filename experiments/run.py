# Python
import multiprocessing
from experiments import run_experiment_filter_schemes, run_reduction_experiment, run_scalability_experiment, run_matching_without_silkmoth_inc_dep
import os
from data_loader import DataLoader
from utils import load_sets_from_files, experiment_set_ratio_calc, save_sets_to_files
from silkmoth.utils import jaccard_similarity, contain, similar, SigType, edit_similarity


def run_experiment_multi(experiment_method, *args):
    experiment_method(*args)


if __name__ == "__main__":
    data_loader = DataLoader("/")

    # Labels for Filter Experiments
    labels_filter = ["NO FILTER", "CHECK FILTER", "NN FILTER"]

    # Labels for Signature Scheme
    labels_sig_schemes = [SigType.WEIGHTED, SigType.SKYLINE, SigType.DICHOTOMY]

    # Labels for Reduction
    labels_reduction = ["REDUCTION", "NO REDUCTION"]

    # Load the datasets for Experiments
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

        _, github_source_sets_schema_matching = load_sets_from_files(
            folder_path=folder_path,
            reference_file="github_webtable_schemas_sets_500k.json",
            source_file="github_webtable_schemas_sets_500k.json"
        )

    except FileNotFoundError:
        print("Datasets not found. Skipping Experiments.")
        reference_sets_in_dep, source_sets_in_dep, reference_sets_in_dep_reduction = [], [], []
        source_sets_schema_matching = []
        github_source_sets_schema_matching = []

    # Experiment configuration
    experiment_config = {
        "filter_runs": False,
        "signature_scheme_runs": False,
        "reduction_runs": False,
        "scalability_runs": False,
        "schema_github_webtable_runs": False,
        "inc_dep_without_silkmoth": True
    }

    # Define experiments to run
    experiments = []

    if experiment_config["filter_runs"]:
        # Filter runs
        # String Matching Experiment
        experiments.append((
            run_experiment_filter_schemes, [0.7, 0.75, 0.8, 0.85], [0.7, 0.75, 0.8, 0.85],
            labels_filter, source_string_matching[:60_000], None, similar, edit_similarity , False,
            "string_matching_filter", "results/string_matching/"
        ))

        # Schema Matching Experiment
        experiments.append((
            run_experiment_filter_schemes(), [0.7, 0.75, 0.8, 0.85], [0.0, 0.25, 0.5, 0.75],
            labels_filter, source_sets_schema_matching[:60_000], None, similar, jaccard_similarity, False,
            "schema_matching_filter", "results/schema_matching/"
        ))

        # Inclusion Dependency Experiment
        experiments.append((
            run_experiment_filter_schemes(), [0.7, 0.75, 0.8, 0.85], [0.0, 0.25, 0.5, 0.75],
            labels_filter, source_sets_in_dep, reference_sets_in_dep[:200], contain, jaccard_similarity, True,
            "inclusion_dependency_filter", "results/inclusion_dependency/"
        ))


    if experiment_config["signature_scheme_runs"]:
        # Signature Scheme Runs
        #String Matching Experiment
        experiments.append((
            run_experiment_filter_schemes, [0.7, 0.75, 0.8, 0.85], [0.7, 0.75, 0.8, 0.85],
            labels_sig_schemes, source_string_matching[:60_000], None, similar, edit_similarity , False,
            "string_matching_sig", "results/string_matching/"
        ))

        # Schema Matching Experiment
        experiments.append((
            run_experiment_filter_schemes, [0.7, 0.75, 0.8, 0.85], [0.0, 0.25, 0.5, 0.75],
            labels_sig_schemes, source_sets_schema_matching[:60_000], None, similar, jaccard_similarity, False,
            "schema_matching_sig", "results/schema_matching/"
        ))

        # Inclusion Dependency Experiment
        experiments.append((
            run_experiment_filter_schemes, [0.7, 0.75, 0.8, 0.85], [0.0, 0.25, 0.5, 0.75],
            labels_sig_schemes, source_sets_in_dep, reference_sets_in_dep[:200], contain, jaccard_similarity, True,
            "inclusion_dependency_sig", "results/inclusion_dependency/"
        ))

    if experiment_config["reduction_runs"]:
        # Reduction Runs
        experiments.append((
            run_reduction_experiment, [0.7, 0.75, 0.8, 0.85], 0.0,
            labels_reduction, source_sets_in_dep, reference_sets_in_dep[:200], contain, jaccard_similarity, True,
            "inclusion_dependency_reduction", "results/inclusion_dependency/"
        ))

    if experiment_config["scalability_runs"]:
        # Scalability Runs
        # String Matching
        experiments.append((
            run_scalability_experiment, [0.7, 0.75, 0.8, 0.85], 0.7, [12_000, 24_000, 36_000, 48_000, 60_000],
            source_string_matching[:500_000], None, similar, edit_similarity, False,
            "string_matching_scalability", "results/string_matching/"
        ))

        # Inclusion Dependency
        experiments.append((
            run_scalability_experiment, [0.7, 0.75, 0.8, 0.85], 0.5, [100_000, 200_000, 300_000, 400_000, 500_000],
            source_sets_in_dep, reference_sets_in_dep[:200], contain, jaccard_similarity, True,
            "inclusion_dependency_scalability", "results/inclusion_dependency/"
        ))

        # Schema Matching
        experiments.append((
            run_scalability_experiment, [0.7, 0.75, 0.8, 0.85], 0.0, [12_000, 24_000, 36_000, 48_000, 60_000],
            source_sets_schema_matching[:60_000], None, similar, jaccard_similarity, False,
            "schema_matching_scalability", "results/schema_matching/"
        ))

    if experiment_config["schema_github_webtable_runs"]:
        # Schema Matching with GitHub Webtable Schemas
        experiments.append((
            run_experiment_filter_schemes, [0.7, 0.75, 0.8, 0.85], [0.0, 0.25, 0.5, 0.75],
            labels_filter, source_sets_schema_matching[:10000], github_source_sets_schema_matching[:10000], similar, jaccard_similarity, True,
            "github_webtable_schema_matching", "results/schema_matching/"
        ))

    if experiment_config["inc_dep_without_silkmoth"]:
        experiments.append((
            run_matching_without_silkmoth_inc_dep, source_sets_in_dep[:500_000], reference_sets_in_dep[:200], [0.7, 0.75, 0.8, 0.85], 0.5, contain, jaccard_similarity,
            "raw_matching", "results/inclusion_dependency/"
        ))

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