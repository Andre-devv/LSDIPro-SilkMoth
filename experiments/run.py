import multiprocessing
from experiments import Experiments

def run_experiment(experiment_method):
    experiment_method()

if __name__ == "__main__":
    exp = Experiments()

    # Define experiments to run
    experiments = [
        exp.run_webtable_approximate_inclusion_dependency_filter_experiment(),
        exp.run_webtable_schema_matching_filter_experiment,
        exp.run_dblp_approximate_string_matching_experiment
    ]

    # Create and start processes for each experiment
    processes = []
    for experiment in experiments:
        process = multiprocessing.Process(target=run_experiment, args=(experiment,))
        processes.append(process)
        process.start()

    # Wait for all processes to complete
    for process in processes:
        process.join()