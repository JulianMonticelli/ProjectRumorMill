# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render

import networkx as nx
import os.path
import simrun
# Create your views here.
def home(request):
    context = {}
    BASE = os.path.dirname(os.path.abspath(__file__))
    graph = nx.read_graphml(os.path.join(BASE, "static/simplemodel.graphml"))
    nodes = []
    for node in graph.node:
        n = {}
        n[0] = int(node.lstrip('n'))
        n[1] = node
        nodes.append(n)
    edges = []
    for node1 in graph.edge:
        for node2 in graph.edge[node1]:
	    e = {}
            e[0] = int(node1.lstrip("n"))
            e[1] = int(node2.lstrip("n"))
            ex = {}
            ex[1] = int(node1.lstrip("n"))
            ex[0] = int(node2.lstrip("n"))
            if ex not in edges:
                edges.append(e)
    context["nodes"] = nodes
    context["edges"] = edges
    return render(request, 'index.html', context)

def runsim(request):
    context = {}
    BASE = os.path.dirname(os.path.abspath(__file__))
    graph = nx.read_graphml(os.path.join(BASE, "static/simplemodel.graphml"))
    nx.set_node_attributes(graph, 'flagged', False)

    # Get graph-given weight attributes and save them
    dict = nx.get_edge_attributes(graph, 'weight')

    # Write 1 weight to all edges
    #nx.set_edge_attributes(graph, 'weight', 1)

    #for n1,n2 in dict:
    #    graph.edge[n1][n2]['weight'] = dict[n1,n2]

    # Set an arbitrary node
    graph.node['n9']['flagged'] = True
    result = simrun.run(graph, 3, 3, True, False)[2]
    nodes = []
    for node in result.node:
        n = {}
        n[0] = int(node.lstrip('n'))
        n[1] = node
        if result.node[node]['flagged']:
            n[2] = 1
        else:
            n[2] = 0#result.node[node]['flagged']
        nodes.append(n)
    edges = []
    for node1 in result.edge:
        for node2 in result.edge[node1]:
	    e = {}
            e[0] = int(node1.lstrip("n"))
            e[1] = int(node2.lstrip("n"))
            ex = {}
            ex[1] = int(node1.lstrip("n"))
            ex[0] = int(node2.lstrip("n"))
            if ex not in edges:
                edges.append(e)
    context["nodes"] = nodes
    context["edges"] = edges
    return render(request, 'index.html', context)


def cs1571vis(request):
    context = {}
    BASE = os.path.dirname(os.path.abspath(__file__))
    ###########
    f = open(os.path.join(BASE, "static/test_aggregation2.config"), 'rb')#graph = nx.read_graphml(os.path.join(BASE, "static/simplemodel.graphml"))
    problem = {}
    problem["type"] = f.readline().rstrip("\n")
    problem["nodes"] = {}
    problem["connections"] = {}
    nodes = f.readline().split(",")
    for i in range(0, len(nodes), 3):
        if i == 0:
            node = nodes[i].lstrip("[(\"").rstrip("\"")
            problem["nodes"][node] = {}
            problem["nodes"][node][0] = nodes[i+1]
            problem["nodes"][node][1] = nodes[i+2].rstrip(")")
        elif i == len(nodes)-3:
            node = nodes[i].lstrip("(\"").rstrip("\"")
            problem["nodes"][node] = {}
            problem["nodes"][node][0] = nodes[i+1]
            problem["nodes"][node][1] = nodes[i+2].rstrip(")]\n")
        else:
            node = nodes[i].lstrip("(\"").rstrip("\"")
            problem["nodes"][node] = {}
            problem["nodes"][node][0] = nodes[i+1]
            problem["nodes"][node][1] = nodes[i+2].rstrip(")")
    k = 0
    for line in f:
        if line == " \n":
            break
        weight = line.rstrip("\n").split(",")
        problem["connections"][k] = {}
        problem["connections"][k][0] = weight[0].lstrip("(\"").rstrip("\"")
        problem["connections"][k][1] = weight[1].lstrip(" \"").rstrip("\"")
        problem["connections"][k][2] = int(weight[2].lstrip(" ").rstrip(")"))
        k = k+1
    ###########
    nodes = []
    for node in problem["nodes"]:#graph.node:
        n = {}
        n[0] = int(node.lstrip('N_'))#n'))
        n[1] = int(node.lstrip('N_'))#node
        nodes.append(n)
    edges = []
    for edge in range(len(problem["connections"])):#graph.edges:
        e = {}
        e[0] = int(problem["connections"][edge][0].lstrip('N_'))#"n"))
        e[1] = int(problem["connections"][edge][1].lstrip('N_'))#"n"))
        edges.append(e)
    context["nodes"] = nodes
    context["edges"] = edges
    return render(request, 'index.html', context)
