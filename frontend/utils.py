import matplotlib.pyplot as plt

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
    plt.savefig(file_name, bbox_inches='tight', dpi=300)

    return fig