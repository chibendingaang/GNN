# Load libraries
# Installing additional libraries

# !pip install networkx
# !pip install powerlaw

# Importing libraries
import pandas as pd
import networkx as nx
import collections
import statistics as stats
import time
import seaborn as sns
import json
import numpy as np
import random
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import powerlaw
import warnings

warnings.filterwarnings('ignore')

# Loading Data
# Reading the json file
f = open("data/internal-references-pdftotext.json")
data = json.load(f)

# Show how the data is presented
# Suppressing the output, convert to print statement
print(list(data.items())[50:60])

# Length of the data
orig_len = len(data)
print(orig_len)

# Get N elements in the dictionary, because of limited computational resources
n_sample = 50000
random.seed(12)
data = dict(random.sample(data.items(), n_sample))

print("Working with the " + str(round(100 * len(data) / orig_len, 2)) + "% of the original data")

# Some Pre-Processing
# Consider only papers with more than 4 citations
keys = []
for key, value in data.items():
    if len(value) >= 4:
        keys.append(key)

data = {your_key: data[your_key] for your_key in keys}

# Show how the data is presented
print(list(data.items())[0:4])

# Construct the dataframe
papers_main = []
papers_refs = []

for key in data:
    if len(data[key]) != 0:
        for _ in range(len(data[key])):
            papers_main.append(key)
            papers_refs.append(data[key][_])

# Sanity check
print(len(papers_main))
print(len(papers_refs))

# The TOP papers are the cited and the SUB, the ones that cited
df = pd.DataFrame({'top': papers_refs, 'sub': papers_main})

# Sanity check
print(len(df))
print(df.shape)
print(df.head())

# Remove duplicates rows
df = df.drop_duplicates(keep=False, inplace=False)
print(df.shape)
print(df.head())

# Consider only the TOP papers that cite other papers, not those that do not cite any other paper
intersection = list(set(list(df["top"])).intersection(list(df["sub"])))

papers_top = []
papers_sub = []
for idx in range(0, len(df)):
    if (df["top"].iloc[idx] in intersection):
        papers_top.append(df["top"].iloc[idx])
        papers_sub.append(df["sub"].iloc[idx])

df = pd.DataFrame({'top': papers_top, 'sub': papers_sub})
print(df.shape)
print(df.head())

# Saving for later use in Cytoscape
df.to_csv("cytoscape/citations_network.csv", sep='\t', encoding='utf-8', index=False)

# Creation of the Citation Network
GG = nx.from_pandas_edgelist(df, source="top", target="sub", edge_attr=None, create_using=nx.DiGraph())
print(nx.info(GG))

# Selection of the largest Weakly Connected Components in Citation Network
GG_cc = max(nx.weakly_connected_components(GG), key=len)
GG = GG.subgraph(GG_cc)
print(nx.info(GG))

# Visualization of the Citation Network using NetworkX
# Warning: This step takes a long time

# The direction of the arrow indicates the flow of information from the cited paper to the citing paper
spring_pos = nx.spring_layout(GG)  # might take a little while
fig = plt.figure(figsize=(40, 30))
ax = fig.add_subplot(111)
ax.axis('off')

nx.draw_networkx(GG, spring_pos, ax=ax, node_size=10, width=1, with_labels=False)
plt.title("Entire graph - Default node size")
plt.close()
