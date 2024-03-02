import os
import json

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

FILE_PATH = "logs/"
files_log = [f for f in os.listdir(FILE_PATH) if f.startswith('node10_log')]
files_exc = [f for f in os.listdir(FILE_PATH) if f.startswith('node10_exc')]

res_json = dict()

# handle log files
for file in files_log:
    with open(FILE_PATH+file, 'r') as f:
        lines = f.readlines()
        tmp_res = dict()
        tmp_prompt = None
        for i, line in enumerate(lines):
            if not line.startswith("{"):
                if len(tmp_res) > 0:
                    res_json[tmp_prompt].append(tmp_res)
                    tmp_res = dict()
                tmp_prompt = line[1:-2]
                if tmp_prompt not in res_json:
                    res_json[tmp_prompt] = []
            else:
                tmp_res.update(json.loads(line))

# handle exception log
for file in files_exc:
    with (open(FILE_PATH+file, 'r') as f):
        lines = f.readlines()
        tmp_res = dict()
        tmp_prompt = None
        for i, line in enumerate(lines):
            if not line.startswith("{"):
                if len(tmp_res) > 0:
                    res_json[tmp_prompt].append(tmp_res)
                    tmp_res = dict()
                tmp_prompt = line[1:-2]
                if tmp_prompt not in res_json:
                    res_json[tmp_prompt] = []
            else:
                line_json = json.loads(line)
                if "Exceptions" in line_json:
                    # filter exceptions
                    if "openai.error.RateLimitError: You exceeded your current quota" in line_json["Exceptions"] or "on tokens per min (TPM): Limit 80000" in line_json["Exceptions"]:
                        pass
                    else:
                        tmp_res.update({"Result": "Fail", "Info": "exception"})
        if len(tmp_res) > 0:
            res_json[tmp_prompt].append(tmp_res)

# calculate accuracy
sum_fails = 0
sum_exc = 0
eval_json = dict()
for key in res_json:
    cnt_runs = 0
    cnt_succ = 0
    for run in res_json[key]:
        cnt_runs += 1
        if run["Result"] == "Pass":
            cnt_succ += 1
        # calculate exception rate
        elif run["Result"] == "Fail":
            sum_fails += 1
            if "Info" in run:
                if run["Info"] == "exception":
                    sum_exc += 1
    if cnt_runs > 0:
        eval_json[key] = {"Index": prompts.index(key), "Runs": cnt_runs, "Passed": cnt_succ, "Acc": cnt_succ/cnt_runs}
    else:
        pass
        #eval_json[key] = {"Index": prompts.index(key), "Runs": cnt_runs, "Passed": cnt_succ, "Acc": 0}


print(json.dumps(res_json, indent=1))
#print(len(res_json))
#print(json.dumps(eval_json, indent=1))
overall_acc = 0
for i in eval_json:
    overall_acc += eval_json[i]["Acc"]
overall_acc /= len(eval_json)
summary = f"""
Accucary: {overall_acc}
Failures: {sum_fails}
Exceptions: {sum_exc}
Exception rate: {sum_exc/sum_fails}
"""
print(summary)
