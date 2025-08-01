from collections import defaultdict

import matplotlib.pyplot as plt
import json
import os
import pandas as pd
import psutil
from src.silkmoth.utils import jaccard_similarity
from src.silkmoth.tokenizer import Tokenizer

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

def measure_ram_usage():
    process = psutil.Process()
    return process.memory_info().rss / (1024 ** 2)


def plot_elapsed_times(related_thresholds, elapsed_times_list, fig_text, file_name, xlabel=r'$\theta$', ylabel='Time (s)', title=None, legend_labels=None):
    """
    Utility function to plot elapsed times against related thresholds for multiple settings.

    Args:
        related_thresholds (list): Related thresholds (x-axis values).
        elapsed_times_list (list of lists): List of elapsed times (y-axis values) for different settings.
        fig_text (str): Text to display on the figure.
        file_name (str): Name of the file to save the plot.
        xlabel (str): Label for the x-axis.
        ylabel (str): Label for the y-axis.
        title (str): Title of the plot (optional).
        legend_labels (list): List of labels for the legend (optional).
    """
    fig = plt.figure(figsize=(8, 6))

    # Plot each elapsed_times list with a different color and label
    for i, elapsed_times in enumerate(elapsed_times_list):
        label = legend_labels[i] if legend_labels and i < len(legend_labels) else f"Setting {i + 1}"
        plt.plot(related_thresholds, elapsed_times, marker='o', label=label)

    plt.xlabel(xlabel, fontsize=14)
    plt.ylabel(ylabel, fontsize=14)

    plt.xticks(related_thresholds)

    if title:
        plt.title(title, fontsize=16)

    plt.grid(True)
    if legend_labels:
        plt.legend(fontsize=12)
    plt.tight_layout()

    # Add figure text
    plt.figtext(0.1, 0.01, fig_text, ha='left', fontsize=10)

    # Save the figure
    plt.savefig(f"{file_name}", bbox_inches='tight', dpi=300)

def save_experiment_results_to_csv(results, file_name):
    """
    Appends experiment results to a CSV file.

    Args:
        results (dict):
        file_name (str): Name of the CSV file to save the results.
    """
    df = pd.DataFrame([results])

    # Append to the file if it exists, otherwise create a new file
    df.to_csv(f"{file_name}", mode='a', header=not os.path.exists(file_name), index=False)

def calculate_set_ratios(source_set, sim_func):
    tokenizer = Tokenizer(sim_func)

    total_elements = 0
    total_tokens = 0

    for s in source_set:
        total_elements += len(s)
        for element in s:
            total_tokens += len(tokenizer.tokenize(element))

    return total_elements/len(source_set), total_tokens/total_elements

def experiment_set_ratio_calc(source_set, sim_func , folder, experiment_name):
    elem_set, tokens_elem = calculate_set_ratios(source_set, sim_func)
    data = {
        "experiment name": experiment_name,
        "elem/set": elem_set,
        "tokens/elem": tokens_elem,
    }
    save_experiment_results_to_csv(data, folder)



