import networkx as nx

import simhelper as helper
import iot_spy as config

'''
This is a file meant to serve as a volatile script
that will call functions in the IOT config with 
debug options. 

Essentially, when all tests work, and the IOT
simulation is done, this can be deleted without
worry.
'''


def test_graph_cross():
    g = nx.Graph()
    
    # Add five nodes
    g.add_node('1')
    g.add_node('2')
    g.add_node('3')
    g.add_node('4')
    g.add_node('5')
    
    # Add edges to make the graph a cross graph
    g.add_edge('1', '2')
    g.add_edge('1', '3')
    g.add_edge('1', '4')
    g.add_edge('1', '5')
    
    for node in g:
        g.node[node]['online'] = True # Each node should be online at first
        g.node[node]['broadcast_delay'] = 0
        for hasnode in g:
            g.node[node]['has_' + hasnode] = False # Every node should not have each other's information
    
    ug = helper.to_directed(g)
    
    for u in ug.edge:
        for v in ug.edge[u]:
            ug.edge[u][v]['broadcast_information'] = None
    
    return ug


g = test_graph_cross()
# 'has_1' is odd in this context, but whatever
g.node['2']['has_1'] = True
g.node['3']['has_1'] = True
g.node['4']['has_1'] = True
g.node['5']['has_1'] = True

config.before_round_start(g, 0, [], [], 'run_name')

gc = helper.copy_graph(g)

for node in g:
    config.on_node(g, gc, node, float('-inf'), 'run_name', debug=True)
    
for node in g:
    print str(g.node[node]['broadcast_delay'])