import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Load data
df = pd.read_csv('results.csv')

# Filter rows with non-zero KnownBest
df = df[df['KnownBest'] > 0]

# Algorithms to plot
algos = ['Randomized', 'Greedy', 'SemiGreedy', 'LocalSearch_Avg', 'GRASP_Best']

# Plotting
x = np.arange(len(df['Problem']))  # label locations
width = 0.15  # width of each bar

fig, ax = plt.subplots(figsize=(15, 6))

# Plot bars for each algorithm
for i, algo in enumerate(algos):
    ax.bar(x + i * width, df[algo], width, label=algo)

# Axis formatting
ax.set_ylabel('Cut Value')
ax.set_title('Algorithm Performance on MAX-CUT Benchmark Graphs')
ax.set_xticks(x + width * 2)
ax.set_xticklabels(df['Problem'], rotation=45)
ax.legend()
ax.grid(axis='y', linestyle='--', alpha=0.7)

plt.tight_layout()
plt.savefig('maxcut_algorithm_comparison_original_values.png')
plt.show()