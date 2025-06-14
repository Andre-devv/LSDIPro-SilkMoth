from experiments import Experiments

if __name__ == "__main__":
    # Run all experiments
    exp = Experiments()

    # Filter experiments
    #exp.run_webtable_approximate_inclusion_dependency_filter_experiment()
    exp.run_webtable_schema_matching_filter_experiment()
    #exp.run_dblp_approximate_string_matching_experiment()
