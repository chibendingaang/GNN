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
f = open("./mylocalrepo/data/internal-references-v0.2.0-2019-03-01.json")
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
print(GG)

# Selection of the largest Weakly Connected Components in Citation Network
GG_cc = max(nx.weakly_connected_components(GG), key=len)
GG = GG.subgraph(GG_cc)
print(GG)

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



# In-degree distribution and fitting by a power-law distribution
# Calculating the in-degree

GGs = [d for d in list(set(list(GG.nodes)))]
GGs_in_degrees = [GG.in_degree[d] for d in GGs]

GGs_in_order = [x for y, x in sorted(zip(GGs_in_degrees, GGs), reverse=True)]
GGs_in_degrees_order = sorted((GG.in_degree[d] for d in GGs), reverse=True)

# Plotting the in-degree distribution
degree_count = collections.Counter(GGs_in_degrees_order)
deg, cnt = zip(*degree_count.items())

plt.figure(figsize=(20, 10))

plt.bar(deg, cnt, width=1, color='b')
plt.xlabel("Node degree size", fontsize=20)
plt.ylabel("Frequency", fontsize=20)
plt.xticks(fontsize=20)
plt.yticks(fontsize=20)
plt.title("Entire graph - Node in degree distribution", fontsize=20)
plt.grid(color='gray', linestyle='--', linewidth=1)
plt.rc('axes', axisbelow=True)

# Save the plot locally
plt.savefig("in_degree_distribution.png", bbox_inches='tight')
plt.close()


"""
Obtain dataframes and implement Field Categories Network
"""

# Filtering only fields

df_filt = df

df_filt = df_filt[df_filt["top"].apply(lambda x: True if (x.find('/')!=-1) else False)]
df_filt = df_filt[df_filt["sub"].apply(lambda x: True if (x.find('/')!=-1) else False)]
df_filt = df_filt[df_filt["top"].apply(lambda x: True if (x[0].isnumeric()!=True) else False)]
df_filt = df_filt[df_filt["sub"].apply(lambda x: True if (x[0].isnumeric()!=True) else False)]

print(df_filt.shape)
df_filt.head()
fields_main = df_filt["top"].apply(lambda x: x[0:x.find('/')])
fields_refs = df_filt["sub"].apply(lambda x: x[0:x.find('/')])

df_fields = pd.DataFrame({'top':fields_main, 'sub':fields_refs})
df_fields = df_fields.reset_index(drop=True)

print(df_fields.shape)
df_fields.head()

# Completing the number of citations between fields

df_fields = df_fields.groupby(df_fields.columns.tolist()).size().reset_index().rename(columns={0:'count'})

print(df_fields.shape)
df_fields.head()


# Filter count >= 3
df_fields = df_fields[df_fields["count"]>=3]

print(df_fields.shape)
df_fields.head()

# Filter fields that reference themselves
df_fields = df_fields[df_fields["top"]!=df_fields["sub"]]

print(df_fields.shape)
df_fields.head()

# Saving for use in Cytoscape
df_fields.to_csv("cytoscape/fields_network.csv", sep='\t', encoding='utf-8', index=False)

# prepare dataset for the graph
GG_fields = nx.from_pandas_edgelist(df_fields, source="top",
                                    target="sub", edge_attr="count",
                                    create_using=nx.DiGraph())
print(GG_fields)

"""
Visualizing the network connectivity between different fields
"""

spring_pos = nx.spring_layout(GG_fields) 
# might take a while
fig = plt.figure(figsize = (40, 30))
ax = fig.add_subplot(111)
ax.axis('off')

nx.draw_networkx(GG_fields,
                 spring_pos,
                 ax = ax,
                 node_color='orange',
                 node_size=[v*1200 for v in dict(GG_fields.in_degree()).values()],
                 font_size=35,
                 with_labels=True,
                 arrowsize=60,
                 width=list(1+df_fields["count"].values/2),
                 connectionstyle="arc3,rad=0.2",
                 edge_color='steelblue')
plt.title("Entire graph - Default node size")
plt.savefig(f'./network_spring_layout.png')
plt.close();
