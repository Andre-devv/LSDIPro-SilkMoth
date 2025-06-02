import matplotlib.pyplot as plt

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
    fig = plt.figure(figsize=(8, 6))

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

    return fig