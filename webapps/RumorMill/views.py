# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render

import networkx as nx
import os.path
import simrun
import simengine
import simhelper as helper
import disease_config as config

from django.http import HttpResponse
from django.core import serializers
import json
import random
# Create your views here.
def home(request):
    context = {}
    global graph
    global max_weight
    BASE = os.path.dirname(os.path.abspath(__file__))
    graph = nx.read_graphml(os.path.join(BASE, "static/simplemodel.graphml"))
    config.init(graph, 'n55', 'sim_name')
    max_weight = helper.max_weight(graph)
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

'''def runsim(request):
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
    return render(request, 'index.html', context)'''

def init(request):
    context = {}
    global graph
    global max_weight
    BASE = os.path.dirname(os.path.abspath(__file__))
    graph = nx.read_graphml(os.path.join(BASE, "static/simplemodel.graphml"))
    startnode = 'n'+str(random.randint(0,76))
    config.init(graph, startnode, 'sim_name')
    max_weight = helper.max_weight(graph)
    # Set an arbitrary node
    #startnode = 'n'+str(random.randint(0,76))
    #graph.node[startnode]['flagged'] = True
    #result = simrun.run(graph, 3, 3, True, True)[2]
    nodes = []
    for node in graph.node:
        n = {}
        n[0] = int(node.lstrip('n'))
        n[1] = node
        if graph.node[node]['infected']:
            n[2] = 1
        else:
            n[2] = 0#result.node[node]['flagged']
        if graph.node[node]['dead']:
            n[2] = 2
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
    #nodes = yaml.dump(nodes)
    nodes = json.dumps(nodes)
    nodes = nodes.encode('ascii', 'ignore')
    nodes = nodes.replace('u', '')
    #response_graph = yaml.load(nodes)
    response_graph = nodes#json.loads(nodes)
    #response_graph = json.loads(response_graph)
    return HttpResponse(response_graph, content_type="application/json")

graph = None
max_weight = 0

def get_graph(request):
    context = {}
    global graph
    global max_weight
    simengine.round(graph, max_weight, 'sim_name')
    #BASE = os.path.dirname(os.path.abspath(__file__))
    #graph = nx.read_graphml(os.path.join(BASE, "static/simplemodel.graphml"))
    #nx.set_node_attributes(graph, 'flagged', False)

    # Get graph-given weight attributes and save them
    #dict = nx.get_edge_attributes(graph, 'weight')

    # Write 1 weight to all edges
    #nx.set_edge_attributes(graph, 'weight', 1)

    #for n1,n2 in dict:
    #    graph.edge[n1][n2]['weight'] = dict[n1,n2]

    # Set an arbitrary node
    #startnode = 'n'+str(random.randint(0,76))
    #graph.node[startnode]['flagged'] = True
    #result = simrun.run(graph, 3, 3, True, True)[2]
    nodes = []
    for node in graph.node:
        n = {}
        n[0] = int(node.lstrip('n'))
        n[1] = node
        if graph.node[node]['infected']:
            n[2] = 1
        else:
            n[2] = 0#result.node[node]['flagged']
        if graph.node[node]['dead']:
            n[2] = 2
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
    #nodes = yaml.dump(nodes)
    nodes = json.dumps(nodes)
    nodes = nodes.encode('ascii', 'ignore')
    nodes = nodes.replace('u', '')
    #response_graph = yaml.load(nodes)
    response_graph = nodes#json.loads(nodes)
    #response_graph = json.loads(response_graph)
    return HttpResponse(response_graph, content_type="application/json")
