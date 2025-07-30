from experiments.utils import plot_elapsed_times
import csv

import csv

labels = []
elapsed_times = []

def read_csv_add_data(filename, labels, elapsed_times):
    with open(filename, newline='') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # skip header
        times = []
        current_label = None
        for row in reader:
            sim_thresh = float(row[0])
            label = row[4]
            elapsed = float(row[5])

            if sim_thresh == 0.5:
                if current_label != label:
                    # New label group started
                    if times:
                        # Save times of previous label if not empty
                        elapsed_times.append(times)
                    times = [elapsed]
                    current_label = label
                else:
                    times.append(elapsed)

                # When 4 times collected, append and reset
                if len(times) == 4:
                    elapsed_times.append(times)
                    times = []
                    current_label = None

            if label not in labels:
                labels.append(label)

        # In case last label times were not appended
        if times:
            elapsed_times.append(times)

# Read first CSV
read_csv_add_data('inclusion_dependency/raw_matching_experiment_results.csv', labels, elapsed_times)

# Read second CSV
read_csv_add_data('inclusion_dependency/inclusion_dependency_filter_experiment_results.csv', labels, elapsed_times)

print("Labels:", labels)
print("Elapsed Times:", elapsed_times)

# Then plot
file_name_prefix = "inclusion_dependency_filter_combined_raw"
folder_path = ""

_ = plot_elapsed_times(
    related_thresholds=[0.7, 0.75, 0.8, 0.85],
    elapsed_times_list=elapsed_times,
    fig_text=f"{file_name_prefix} (α = 0.5)",
    legend_labels=labels,
    file_name=f"{folder_path}{file_name_prefix}_experiment_α=0.5.png"
)

