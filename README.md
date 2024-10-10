# Graph Connectivity 

![network_spring_layout](https://github.com/user-attachments/assets/d5d670d9-a2e8-4d9e-a24b-25ae65b031a0)


This project involves constructing a citation network from a JSON dataset, processing and filtering data, visualizing the network's connectivity, and analyzing the in-degree distribution. The steps are outlined below:

Loading and Preprocessing the Data:

The dataset is loaded from a JSON file, and we select a subset (50,000 entries) from it.
We filter the papers that have more than four citations, creating a directed network where the nodes are papers, and the edges represent citations.

1. Creating the Dataframe:

Two lists, papers_main and papers_refs, are constructed. The former contains papers that cite other papers (called "SUB"), while the latter holds the cited papers ("TOP").
The dataframe is constructed with two columns: "top" for the cited papers and "sub" for the citing papers. Duplicate entries are removed for accuracy.

2. Building the Citation Network:

A citation network is built using the NetworkX library, where nodes represent papers, and directed edges represent citation relationships.
We focus on the largest weakly connected component of the graph to visualize the core network structure.

3. Visualizing the Citation Network:

The citation network is visualized using NetworkX with a spring layout algorithm, where nodes represent papers and edges represent citations. The visualization is saved as an image file.

4. In-Degree Distribution Analysis:

The in-degree distribution of the nodes (i.e., the number of incoming citations each paper receives) is analyzed. The results are plotted and saved as an image, helping us understand how citations are distributed across papers.

Field Categories Network:

After constructing the citation network, we filter only the fields of study by removing entries with numerical values and selecting those with field-based categorizations.
The filtered dataframe is then used to create a network of citation flows between fields of study, representing how different fields cite each other.
A visualization of this network is generated, where node size and edge width represent the number of citations between fields.


