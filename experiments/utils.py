import matplotlib.pyplot as plt
import json
import os

def is_convertible_to_number(value):
    try:
        float(value)
        return True
    except ValueError:
        return False

def save_sets_to_files(reference_sets, source_sets, reference_file="reference_sets.json", source_file="source_sets.json"):
    """
    Saves reference sets and source sets to their respective JSON files.

    Args:
        reference_sets (list): The reference sets to save.
        source_sets (list): The source sets to save.
        reference_file (str): The file name for saving reference sets.
        source_file (str): The file name for saving source sets.
    """
    with open(reference_file, 'w', encoding='utf-8') as ref_file:
        json.dump(reference_sets, ref_file, ensure_ascii=False, indent=4)

    with open(source_file, 'w', encoding='utf-8') as src_file:
        json.dump(source_sets, src_file, ensure_ascii=False, indent=4)

def load_sets_from_files(folder_path: str, reference_file: str = "reference_sets.json", source_file: str = "source_sets.json") -> tuple[list, list]:
    source_path = os.path.join(folder_path, source_file)
    reference_path = os.path.join(folder_path, reference_file)

    # Check if the files exist
    if not os.path.exists(source_path) or not os.path.exists(reference_path):
        raise FileNotFoundError("One or both of the required files do not exist in the specified folder.")

    # Load the reference sets
    with open(reference_path, 'r', encoding='utf-8') as ref_file:
        reference_sets = json.load(ref_file)
    # Load the source sets
    with open(source_path, 'r', encoding='utf-8') as src_file:
        source_sets = json.load(src_file)

    return reference_sets, source_sets


def plot_elapsed_times(related_thresholds, elapsed_times, fig_text, file_name, xlabel=r'$\theta$', ylabel='Time (s)', title=None, legend_label="Method"):
    """
    Utility function to plot elapsed times against related thresholds.

    Args:
        file_name: (str): Name of the file to save the plot.
        fig_text: (str): Text to display on the figure.
        related_thresholds (list): List of related thresholds (x-axis values).
        elapsed_times (list): List of elapsed times (y-axis values).
        xlabel (str): Label for the x-axis.
        ylabel (str): Label for the y-axis.
        title (str): Title of the plot (optional).
        legend_label (str): Label for the legend.
    """
    plt.figure(figsize=(8, 6))

    plt.plot(related_thresholds, elapsed_times, marker='o', label=legend_label)

    plt.xlabel(xlabel, fontsize=14)
    plt.ylabel(ylabel, fontsize=14)
    plt.xticks(related_thresholds)

    if elapsed_times:
        min_time = int(min(elapsed_times))
        max_time = int(max(elapsed_times))
        step = max(1, int((max_time - min_time) / 10))  # Dynamically calculate step size
        plt.ylim(max(0, min_time - step), max_time + step)
        plt.yticks(range(max(0, min_time - step), max_time + step + 1, step))
    else:
        plt.ylim(0, 1000)
        plt.yticks(range(0, 1001, 100))

    plt.grid(True)
    plt.legend(fontsize=12)
    plt.tight_layout()
    plt.figtext(0.1, 0.01, fig_text, ha='left', fontsize=16)

    # Ensure the 'results' directory exists
    results_dir = os.path.join(os.path.dirname(__file__), "./results")
    os.makedirs(results_dir, exist_ok=True)

    plot_path = os.path.join(results_dir, file_name)
    plt.savefig(plot_path, dpi=300, bbox_inches='tight')