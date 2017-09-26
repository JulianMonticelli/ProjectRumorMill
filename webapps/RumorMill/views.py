# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render

import networkx as nx
import os.path
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
    for edge in graph.edges:
        e = {}
        e[0] = int(edge[0].lstrip("n"))
        e[1] = int(edge[1].lstrip("n"))
        edges.append(e)
    context["nodes"] = nodes
    context["edges"] = edges
    return render(request, 'index.html', context)
