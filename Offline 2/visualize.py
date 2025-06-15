import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

# Read the CSV file
try:
    df = pd.read_csv('results.csv')
except FileNotFoundError:
    print("Error: results.csv not found. Make sure the file is in the same directory as the script.")
    exit()

# Ensure the 'Problem' column exists
if 'Problem' not in df.columns:
    print("Error: 'Problem' column not found in results.csv.")
    exit()

# Heuristic columns to plot and their desired labels for the legend
# Make sure these column names exactly match your CSV file
heuristic_map = {
    'Randomized': 'Randomized',
    'Greedy': 'Greedy',
    'SemiGreedy': 'SemiGreedy',
    'LocalSearch_Avg': 'Local Search', # Check column name in your CSV
    'GRASP_Best': 'GRASP'      # Check column name in your CSV
}
heuristic_cols_to_plot = list(heuristic_map.keys())
legend_labels = list(heuristic_map.values())

# Validate that all specified heuristic columns exist in the DataFrame
missing_cols = [col for col in heuristic_cols_to_plot if col not in df.columns]
if missing_cols:
    print(f"Error: The following heuristic columns are missing in results.csv: {', '.join(missing_cols)}")
    exit()

# Convert heuristic columns to numeric, coercing errors
for col in heuristic_cols_to_plot:
    df[col] = pd.to_numeric(df[col], errors='coerce')

# Drop rows where any of the heuristic values are NaN after conversion
df.dropna(subset=heuristic_cols_to_plot, inplace=True)

if df.empty:
    print("No data available to plot after cleaning. Please check your results.csv.")
    exit()

# Graph instances (Problem names)
graph_instances = df['Problem'].tolist()
n_graphs = len(graph_instances)
n_heuristics = len(heuristic_cols_to_plot)

# Create a directory to save plots if it doesn't exist
output_dir = "heuristic_plots"
os.makedirs(output_dir, exist_ok=True)

# --- Create Grouped Bar Chart ---
x = np.arange(n_graphs)  # the label locations
width = 0.15  # the width of the bars, adjust as needed
# Calculate total width for a group of bars to center them
total_group_width = n_heuristics * width
offset_start = -total_group_width / 2 + width / 2

fig, ax = plt.subplots(figsize=(max(18, n_graphs * 1.5), 8)) # Adjust figure size

fig, ax = plt.subplots(figsize=(max(18, n_graphs * 1.5), 8)) # Adjust figure size

for i, col_name in enumerate(heuristic_cols_to_plot):
    values = df[col_name].tolist()
    # bar_positions are the CENTERS of the bars
    bar_positions = x + offset_start + i * width
    rects = ax.bar(bar_positions, values, width, label=legend_labels[i])
    
    # Add text labels on top of each bar
    for rect in rects:
        height = rect.get_height()
        ax.annotate(f'{height:.0f}',
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3),  # 3 points vertical offset
                    textcoords="offset points",
                    ha='center', va='bottom', fontsize=7, rotation=90)

# Calculate the actual data extent (based on the edges of the bars)
# Leftmost edge of the first bar in the first group:
leftmost_bar_edge = (x[0] + offset_start) - (width / 2)

# Rightmost edge of the last bar in the last group:
center_of_last_bar_in_last_group = x[n_graphs - 1] + offset_start + (n_heuristics - 1) * width
rightmost_bar_edge = center_of_last_bar_in_last_group + (width / 2)

# Define the margin for the plot edges.
# This margin will be equal to the gap between two adjacent groups of bars.
# The distance between centers of groups is 1.
# The gap is 1 - total_group_width.
# Ensure total_group_width is less than 1 for a positive gap.
if total_group_width < 1:
    plot_edge_margin = 1 - total_group_width
else:
    # If bars are too wide and would overlap/touch, use a small default margin
    plot_edge_margin = width * 0.25 
    print(f"Warning: total_group_width ({total_group_width:.2f}) is not less than 1. Defaulting edge margin.")


ax.set_xlim(leftmost_bar_edge - plot_edge_margin, rightmost_bar_edge + plot_edge_margin)

# Add some text for labels, title and custom x-axis tick labels, etc.
ax.set_ylabel('Max Cut Value')
ax.set_xlabel('Graph Instance (Problem)')
ax.set_title('Comparison of Max Cut Values by Heuristic for Each Graph Instance')
ax.set_xticks(x)
ax.set_xticklabels(graph_instances, rotation=90) # Rotate X-axis labels
ax.legend(title="Heuristics")

ax.grid(axis='y', linestyle='--')
fig.tight_layout() # Adjust layout to prevent labels from overlapping

# Save the plot
plot_filename = os.path.join(output_dir, 'grouped_heuristic_comparison.png')
plt.savefig(plot_filename)
print(f"Saved grouped bar plot: {plot_filename}")
plt.show() # Display the plot
plt.close(fig) # Close the figure

print(f"\nGrouped plot saved in the '{output_dir}' directory.")
