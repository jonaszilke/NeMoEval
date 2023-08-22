# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

import os
import pandas as pd
import json

df = pd.DataFrame()

# For each prompt, please specify the returned type you want.
prompts = [
    # 8 easy ones
    "How many nodes are in the graph? Return only the number.",
    "How many nodes and edges are in the graph? Return a list.",
    "Add a label app:prod to nodes with address prefix 15.76 and add the label app:test to nodes with address prefix 149.196. Return the networkx graph object.",
    "Show me the unique labels and the number of nodes per label. Return a table with header 'Label', 'Number of Nodes' on the first row.",
    "Remove the label 'type=VM' from all the nodes. Return the networkx graph object.",
    "What are max degree and min degree in the graph? Return a table with with header 'Max degree', 'Min degree' on the first row.",
    "Color all of the nodes with label 'app:prod' purple. Return the networkx graph object.",
    "Color the node with max degree red and min degree green. Return the networkx graph object.",

    # 8 medium ones
    "How many nodes are there that have an edge to nodes with labels app:prod or app:test and doesn't have either of those labels? Return only the number.",
    "Assign a unique color for each /16 IP address prefix and color the nodes accordingly. Return the networkx graph object.",
    "Color the size of the node with max degree green and double it's size. Return the networkx graph object.",
    "Find nodes with top 10 number of degrees, list nodes, labels and number of degrees. Return a table without headers.",
    "Color the nodes that can be connect to nodes with labels app:prod with green. Return the networkx graph object.",
    "Cut the graph into two parts such that the number of edges between the cuts is same. Color two parts with red and blue. Return the networkx graph object.",
    "Identify the unique labels in the graph. Create a new graph with a node for each unique label. For each edge in the old graph, identify the labels of the nodes on either side of the edge. Connect the nodes with those labels in the new graph if they are not already connected by an edge. Return the networkx graph object.",
    "Calculate the total byte weight of edges incident on each node, use kmeans clustering to cluster the total byte weights into 5 clusters, apply the cluster labels as strings to the nodes and pick and assign colors to the nodes based on their cluster labels. Shape the data correctly using numpy before passing it to kmeans. Return the networkx graph object.",

    # 8 hard ones
    "How many maximal cliques are in the graph? Return only the number.",
    "Color the nodes to reflect a heatmap based on the total byte weight of the edges. Return the networkx graph object.",
    "Bisect the network such that the number of nodes on either side of the cut is equal. Color the graph based on the bisection. Return the networkx graph object.",
    "Calculate the total byte weight of edges incident on each node, use kmeans clustering to cluster the total byte weights into 5 clusters. Return the networkx graph object.",
    "How many unique nodes have edges to nodes with label app:prod and doesn't contain the label app:prod? Return only the number.",
    "Show me the unique IP address prefix and the number of nodes per prefix. Return a table without headers.",
    "Delete all edges whose byte weight is less than the median byte weight in the whole graph without using the statistics library. Make sure to compute the median and not the mean. Return the networkx graph object.",
    "What is the average byte weight and connection weight of edges incident on nodes with labels app:prod? Return a table with header 'Average byte weight', 'Average connection weight' on the first row.",

]

answers=[
    # 8 easy ones
    "\ndef ground_truth_process_graph(graph_data):\n    return_object = {\n        'type': 'text',\n        'data': str(len(graph_data.nodes))\n    }\n    return return_object",
    "\ndef ground_truth_process_graph(graph_data):\n    num_nodes = len(graph_data.nodes())\n    num_edges = len(graph_data.edges())\n    return_object = {\n        'type': 'list',\n        'data': [num_nodes, num_edges]\n    }\n    return return_object",
    "\ndef ground_truth_process_graph(graph_data):\n    return_object = {'type': 'graph', 'data': {}}\n    for node in graph_data.nodes():\n        ip_address = graph_data.nodes[node]['ip_address']\n        if ip_address.startswith('15.76'):\n            graph_data.nodes[node]['labels'].append('app:prod')\n        elif ip_address.startswith('149.196'):\n            graph_data.nodes[node]['labels'].append('app:test')\n    return_object['data'] = graph_data\n    return return_object",
    "\ndef ground_truth_process_graph(graph_data):\n    labels = {}\n    for node in graph_data.nodes():\n        for label in graph_data.nodes[node]['labels']:\n            if label not in labels:\n                labels[label] = 1\n            else:\n                labels[label] += 1\n    return_object = {\n        'type': 'table',\n        'data': [['Label', 'Number of Nodes']]\n    }\n    for label, count in labels.items():\n        return_object['data'].append([label, count])\n    return return_object",
    "\ndef ground_truth_process_graph(graph_data):\n    for node in graph_data.nodes():\n        labels = graph_data.nodes[node]['labels']\n        if 'type:VM' in labels:\n            labels.remove('type:VM')\n            graph_data.nodes[node]['labels'] = labels\n    return_object = {\n        'type': 'graph',\n        'data': graph_data\n    }\n    return return_object",
    "\ndef ground_truth_process_graph(graph_data):\n    max_degree = 0\n    min_degree = float('inf')\n    for node in graph_data.nodes():\n        degree = graph_data.degree(node)\n        if degree > max_degree:\n            max_degree = degree\n        if degree < min_degree:\n            min_degree = degree\n    return_object = {\n        'type': 'table',\n        'data': [['Max degree', 'Min degree'], [max_degree, min_degree]]\n    }\n    return return_object",
    "\ndef ground_truth_process_graph(graph_data):\n    for node in graph_data.nodes():\n        if 'app:prod' in graph_data.nodes[node]['labels']:\n            graph_data.nodes[node]['color'] = 'purple'\n    return_object = {\n        'type': 'graph',\n        'data': graph_data\n    }\n    return return_object",
    "\ndef ground_truth_process_graph(graph_data):\n    max_degree = 0\n    min_degree = float('inf')\n    max_node = None\n    min_node = None\n    for node in graph_data.nodes():\n        degree = graph_data.degree(node)\n        if degree > max_degree:\n            max_degree = degree\n            max_node = node\n        if degree < min_degree:\n            min_degree = degree\n            min_node = node\n    graph_data.nodes[max_node]['color'] = 'red'\n    graph_data.nodes[min_node]['color'] = 'green'\n    return_object = {\n        'type': 'graph',\n        'data': graph_data\n    }\n    return return_object",

    # 8 medium ones
    "\ndef ground_truth_process_graph(graph_data):\n    count = 0\n    for node in graph_data.nodes():\n        if 'app:prod' not in graph_data.nodes[node]['labels'] and 'app:test' not in graph_data.nodes[node]['labels']:\n            for neighbor in graph_data.neighbors(node):\n                if 'app:prod' in graph_data.nodes[neighbor]['labels'] or 'app:test' in graph_data.nodes[neighbor]['labels']:\n                    count += 1\n                    break\n    return_object = {\n        'type': 'text',\n        'data': str(count)\n    }\n    return json.dumps(return_object)\n",
    "\ndef ground_truth_process_graph(graph_data):\n    # Create a dictionary to store the /16 IP prefixes and their corresponding colors\n    ip_prefix_colors = {}\n    # Iterate through the nodes in the graph\n    for node in graph_data.nodes():\n        # Get the IP address of the node\n        ip_address = graph_data.nodes[node]['ip_address']\n        # Get the /16 IP prefix of the node\n        ip_prefix = ip_address.split('.')[0] + '.' + ip_address.split('.')[1]\n        # Check if the /16 IP prefix is already in the dictionary\n        if ip_prefix not in ip_prefix_colors:\n            # Generate a random color for the /16 IP prefix\n            color = '#' + ''.join([random.choice('0123456789ABCDEF') for j in range(6)])\n            # Add the /16 IP prefix and its corresponding color to the dictionary\n            ip_prefix_colors[ip_prefix] = color\n        # Assign the color to the node\n        graph_data.nodes[node]['color'] = ip_prefix_colors[ip_prefix]\n    # Return the graph object\n    return_object = {\n        'type': 'graph',\n        'data': graph_data\n    }\n    return return_object",
    "\ndef ground_truth_process_graph(graph_data):\n    max_degree = 0\n    max_node = None\n    for node in graph_data.nodes():\n        if graph_data.degree(node) > max_degree:\n            max_degree = graph_data.degree(node)\n            max_node = node\n    graph_data.nodes[max_node]['color'] = 'green'\n    graph_data.nodes[max_node]['nodesize'] *= 2\n    return_object = {\n        'type': 'graph',\n        'data': graph_data\n    }\n    return return_object",
    "\ndef ground_truth_process_graph(graph_data):\n    degree_list = []\n    for node in graph_data.nodes():\n        degree_list.append((node, graph_data.degree(node)))\n    degree_list.sort(key=lambda x: x[1], reverse=True)\n    top_10_degree_list = degree_list[:10]\n    return_object = {\n        'type': 'table',\n        'data': [[node, graph_data.nodes[node]['labels'], degree] for node, degree in top_10_degree_list]\n    }\n    return return_object",
    "\ndef ground_truth_process_graph(graph_data):\n    for node in graph_data.nodes():\n        if any(label.startswith('app:prod') for label in graph_data.nodes[node]['labels']):\n            for neighbor in graph_data.neighbors(node):\n                graph_data.nodes[neighbor]['color'] = 'green'\n    return_object = {\n        'type': 'graph',\n        'data': graph_data\n    }\n    return return_object",
    "\ndef ground_truth_process_graph(graph_data):\n    # Get the IP prefixes of all nodes\n    ip_prefixes = set()\n    for node in graph_data.nodes():\n        ip_prefixes.add(graph_data.nodes[node]['ip_address'].split('.')[0])\n    \n    # Create two sets of nodes, one for each color\n    red_nodes = set()\n    blue_nodes = set()\n    for ip_prefix in ip_prefixes:\n        for node in graph_data.nodes():\n            if graph_data.nodes[node]['ip_address'].startswith(ip_prefix):\n                if len(red_nodes) <= len(blue_nodes):\n                    red_nodes.add(node)\n                else:\n                    blue_nodes.add(node)\n    \n    # Color the nodes\n    for node in red_nodes:\n        graph_data.nodes[node]['color'] = 'red'\n    for node in blue_nodes:\n        graph_data.nodes[node]['color'] = 'blue'\n    \n    # Return the graph\n    return_object = {\n        'type': 'graph',\n        'data': graph_data\n    }\n    return return_object",
    "\ndef ground_truth_process_graph(graph_data):\n    # Create a new graph\n    new_graph = nx.Graph()\n    \n    # Get the unique labels from the graph\n    labels = set()\n    for node in graph_data.nodes():\n        labels.update(graph_data.nodes[node]['labels'])\n    \n    # Create a node for each unique label\n    for label in labels:\n        new_graph.add_node(label)\n    \n    # Connect the nodes with those labels in the new graph if they are not already connected by an edge\n    for edge in graph_data.edges():\n        source_labels = graph_data.nodes[edge[0]]['labels']\n        target_labels = graph_data.nodes[edge[1]]['labels']\n        for source_label in source_labels:\n            for target_label in target_labels:\n                if not new_graph.has_edge(source_label, target_label):\n                    new_graph.add_edge(source_label, target_label)\n    \n    # Return the networkx graph object\n    return_object = {\n        'type': 'graph',\n        'data': new_graph\n    }\n    return return_object",
    "\ndef ground_truth_process_graph(graph_data):\n    # Calculate the total byte weight of edges incident on each node\n    node_byte_weights = {}\n    for node in graph_data.nodes():\n        node_byte_weights[node] = 0\n        for edge in graph_data.edges(node):\n            node_byte_weights[node] += graph_data.edges[edge]['byte_weight']\n    \n    # Use kmeans clustering to cluster the total byte weights into 5 clusters\n    byte_weights = np.array(list(node_byte_weights.values()))\n    byte_weights = byte_weights.reshape(-1, 1)\n    kmeans = KMeans(n_clusters=5, random_state=0).fit(byte_weights)\n    labels = kmeans.labels_\n    \n    # Apply the cluster labels as strings to the nodes\n    for i, node in enumerate(graph_data.nodes()):\n        graph_data.nodes[node]['labels'].append('cluster_label: ' + str(labels[i]))\n    \n    # Pick and assign colors to the nodes based on their cluster labels\n    colors = ['red', 'green', 'blue', 'yellow', 'orange']\n    for i, node in enumerate(graph_data.nodes()):\n        graph_data.nodes[node]['color'] = colors[labels[i]]\n    \n    # Return the networkx graph object\n    return_object = {\n        'type': 'graph',\n        'data': graph_data\n    }\n    return return_object",

    # 8 hard ones
    "\ndef ground_truth_process_graph(graph_data):\n    return_object = {\n        'type': 'text',\n        'data': len(list(nx.find_cliques(graph_data)))\n    }\n    return return_object",
    "\ndef ground_truth_process_graph(graph_data):\n    # Create a dictionary to store the total byte weight of each node\n    node_byte_weight = {}\n    # Iterate through the edges\n    for edge in graph_data.edges():\n        # Get the source and target IP addresses\n        source_ip = graph_data.edges[edge]['source_ip_address']\n        target_ip = graph_data.edges[edge]['target_ip_address']\n        # Get the byte weight of the edge\n        byte_weight = graph_data.edges[edge]['byte_weight']\n        # Add the byte weight to the total byte weight of the source node\n        if source_ip in node_byte_weight:\n            node_byte_weight[source_ip] += byte_weight\n        else:\n            node_byte_weight[source_ip] = byte_weight\n        # Add the byte weight to the total byte weight of the target node\n        if target_ip in node_byte_weight:\n            node_byte_weight[target_ip] += byte_weight\n        else:\n            node_byte_weight[target_ip] = byte_weight\n    # Iterate through the nodes\n    for node in graph_data.nodes():\n        # Get the IP address of the node\n        ip_address = graph_data.nodes[node]['ip_address']\n        # Get the total byte weight of the node\n        byte_weight = node_byte_weight[ip_address]\n        # Set the color of the node based on the total byte weight\n        if byte_weight < 10:\n            graph_data.nodes[node]['color'] = '#FF0000'\n        elif byte_weight < 20:\n            graph_data.nodes[node]['color'] = '#FF7F00'\n        elif byte_weight < 30:\n            graph_data.nodes[node]['color'] = '#FFFF00'\n        elif byte_weight < 40:\n            graph_data.nodes[node]['color'] = '#00FF00'\n        else:\n            graph_data.nodes[node]['color'] = '#0000FF'\n    # Return the graph object\n    return_object = {\n        'type': 'graph',\n        'data': graph_data\n    }\n    return return_object",
    "\ndef ground_truth_process_graph(graph_data):\n    # Get the IP prefixes of all nodes\n    ip_prefixes = set()\n    for node in graph_data.nodes():\n        ip_prefixes.add(graph_data.nodes[node]['ip_address'].split('.')[0])\n    \n    # Bisect the graph\n    left_nodes = set()\n    right_nodes = set()\n    for ip_prefix in ip_prefixes:\n        left_nodes_count = 0\n        right_nodes_count = 0\n        for node in graph_data.nodes():\n            if graph_data.nodes[node]['ip_address'].startswith(ip_prefix):\n                if left_nodes_count <= right_nodes_count:\n                    left_nodes.add(node)\n                    left_nodes_count += 1\n                else:\n                    right_nodes.add(node)\n                    right_nodes_count += 1\n    \n    # Color the graph\n    for node in graph_data.nodes():\n        if node in left_nodes:\n            graph_data.nodes[node]['color'] = 'blue'\n        else:\n            graph_data.nodes[node]['color'] = 'red'\n    \n    return_object = {\n        'type': 'graph',\n        'data': graph_data\n    }\n    return return_object",
    "\ndef ground_truth_process_graph(graph_data):\n    # Calculate the total byte weight of edges incident on each node\n    node_byte_weights = {}\n    for node in graph_data.nodes():\n        node_byte_weights[node] = 0\n        for edge in graph_data.edges(node):\n            node_byte_weights[node] += graph_data.edges[edge]['byte_weight']\n    \n    # Use kmeans clustering to cluster the total byte weights into 5 clusters\n    byte_weights = np.array(list(node_byte_weights.values()))\n    byte_weights = byte_weights.reshape(-1, 1)\n    kmeans = KMeans(n_clusters=5, random_state=0).fit(byte_weights)\n    labels = kmeans.labels_\n    \n    # Apply the cluster labels as strings to the nodes\n    for i, node in enumerate(graph_data.nodes()):\n        graph_data.nodes[node]['labels'].append('cluster_label: ' + str(labels[i]))\n    \n    # Pick and assign colors to the nodes based on their cluster labels\n    colors = ['red', 'green', 'blue', 'yellow', 'orange']\n    for i, node in enumerate(graph_data.nodes()):\n        graph_data.nodes[node]['color'] = colors[labels[i]]\n    \n    # Return the networkx graph object\n    return_object = {\n        'type': 'graph',\n        'data': graph_data\n    }\n    return return_object",
    "\ndef ground_truth_process_graph(graph_data):\n    prod_nodes = []\n    other_nodes = []\n    for node in graph_data.nodes():\n        labels = graph_data.nodes[node]['labels']\n        if 'app:prod' in labels:\n            prod_nodes.append(node)\n        else:\n            other_nodes.append(node)\n    \n    unique_nodes = []\n    for node in other_nodes:\n        is_connected = False\n        for prod_node in prod_nodes:\n            if graph_data.has_edge(node, prod_node):\n                is_connected = True\n                break\n        if is_connected:\n            unique_nodes.append(node)\n    \n    unique_nodes_count = len(unique_nodes)\n    return_object = {'type': 'text', 'data': str(unique_nodes_count)}\n    return return_object",
    "\ndef ground_truth_process_graph(graph_data):\n    # Initialize a dictionary to store the IP address prefix and the number of nodes per prefix\n    prefix_count = {}\n    \n    # Iterate through each node in the graph\n    for node in graph_data.nodes():\n        # Get the IP address of the node\n        ip_address = graph_data.nodes[node]['ip_address']\n        # Get the /8 IP prefix\n        prefix = ip_address.split('.')[0]\n        # Check if the prefix is already in the dictionary\n        if prefix in prefix_count:\n            # If it is, increment the count\n            prefix_count[prefix] += 1\n        else:\n            # If it isn't, add it to the dictionary and set the count to 1\n            prefix_count[prefix] = 1\n    \n    # Create a list of lists to store the data\n    table_data = []\n    # Iterate through the dictionary\n    for prefix, count in prefix_count.items():\n        # Append the prefix and count to the list\n        table_data.append([prefix, count])\n    \n    # Return the data in a JSON object\n    return_object = {\n        'type': 'table',\n        'data': table_data\n    }\n    return return_object",
    "\ndef ground_truth_process_graph(graph_data):\n    # Calculate the median byte weight\n    byte_weights = [graph_data[u][v]['byte_weight'] for u, v in graph_data.edges()]\n    byte_weights.sort()\n    median_byte_weight = byte_weights[len(byte_weights) // 2]\n\n    # Delete all edges whose byte weight is less than the median\n    edges_to_delete = []\n    for u, v in graph_data.edges():\n        if graph_data[u][v]['byte_weight'] < median_byte_weight:\n            edges_to_delete.append((u, v))\n    graph_data.remove_edges_from(edges_to_delete)\n\n    # Return the graph\n    return_object = {\n        'type': 'graph',\n        'data': graph_data\n    }\n    return return_object\n",
    "\ndef ground_truth_process_graph(graph_data):\n    total_byte_weight = 0\n    total_connection_weight = 0\n    count = 0\n    for edge in graph_data.edges(data=True):\n        source_node = graph_data.nodes[edge[0]]\n        target_node = graph_data.nodes[edge[1]]\n        if 'app:prod' in source_node['labels'] or 'app:prod' in target_node['labels']:\n            total_byte_weight += edge[2]['byte_weight']\n            total_connection_weight += edge[2]['connection_weight']\n            count += 1\n    if count > 0:\n        average_byte_weight = total_byte_weight / count\n        average_connection_weight = total_connection_weight / count\n    else:\n        average_byte_weight = 0\n        average_connection_weight = 0\n\n    return_object = {\n        'type': 'table',\n        'data': [\n            ['Average byte weight', 'Average connection weight'],\n            [average_byte_weight, average_connection_weight]\n        ]\n    }\n    return json.dumps(return_object)\n",
]

df['prompt'] = prompts
df['answer'] = answers

# Get the current working directory
root_path = os.getcwd()

# Create the file path
file_path = os.path.join('../data/prompt_golden_ans.json')

allData = df.set_index('prompt').T.to_dict('records')[0]
with open(file_path, "w") as f:
    json.dump(allData, f)
