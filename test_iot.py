import networkx as nx

import pytest

import iot_spy as config

'''
Read in the test.csv graph with a given radius.
'''
@pytest.fixture(scope='function')
def setup_test_graph_from_test_csv(radius):
    g = config.iot_graph('iot/test.csv', radius)
    return g

    
@pytest.fixture(scope='function')
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
    
    g = helper.to_directed(g)
    
    return g
    
def test_cross_graph_center_information_spread():
    g = test_graph_cross()
    # Stopped here

    
'''
These CSV Graph tests will test that our CSV graph readin works with a given 
input, given that the test.csv is (with commas, of course):
    1	0	0	0
    2	10	0	0
    3	0	10	0
    4	0	0	10
    5	0	0	20
    6	20	20	0
    7	-5	-5	-5
    8	-10	-10	-10
    9	18	1	1
    10	0	11	0

'''
def test_csv_graph_distance_10():
    g = setup_test_graph_from_test_csv(10)
    
    # A list for all of the nodes that exist
    all_nodes_list = [str(x) for x in range(1,11)]
    
    # Create a dictionary for which neighbors each node should have.
    node_neighbor_dict = {}
    node_neighbor_dict['1'] = ['2', '3', '4', '7']
    node_neighbor_dict['2'] = ['1', '9']
    node_neighbor_dict['3'] = ['1', '10']
    node_neighbor_dict['4'] = ['1', '5']
    node_neighbor_dict['5'] = ['4']
    node_neighbor_dict['6'] = []
    node_neighbor_dict['7'] = ['1', '8']
    node_neighbor_dict['8'] = ['7']
    node_neighbor_dict['9'] = ['2']
    node_neighbor_dict['10'] = ['3']
    
    for node in node_neighbor_dict:
        for n in node_neighbor_dict[node]:
            assert(n in g.edge[node])
        temp_list = [e for e in all_nodes_list if e not in node_neighbor_dict[node]]
        for n in temp_list:
            assert(n not in g.edge[node])
    
    

def test_csv_graph_distance_100():
    g = setup_test_graph_from_test_csv(100)
    
    all_nodes_list = [str(x) for x in range (1,11)]
    
    for node in all_nodes_list:
        for n in all_nodes_list:
            if not node == n:
                assert(n in g.edge[node])