import networkx as nx

import pytest

import iot_spy as config
import simhelper as helper


'''
Read in the text.csv graph, where range is given.
'''
@pytest.fixture(scope='function')
def setup_test_graph():
    g = config.iot_graph('iot/test.csv')
    return g

'''
Read in the test_xyz.csv graph with a given radius.
'''
@pytest.fixture(scope='function')
def setup_test_graph_from_test_xyz_csv(radius):
    g = config.iot_graph_xyz('iot/test_xyz.csv', radius)
    return g

'''
Construct a cross graph, with node 1 in the middle.
'''
@pytest.fixture(scope='function')
def test_cross_graph():
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

    
'''

'''
def a():
    assert True
    
    
'''
Checks that the import IOT graph as x,y, range works as intended.
Important: I drew out nodes on a grid with ranges, and x and y coordinates.
This test may not work if you alter test.csv.
'''
def test_iot_graph_correct_digraph():
    g = setup_test_graph()
    
    # A list for all of the nodes that exist (1-7)
    all_nodes_list = [node for node in g.node]
    
    # Create a dictionary for which paths to each node should have.
    node_neighbor_dict = {}
    node_neighbor_dict['1'] = ['2']
    node_neighbor_dict['2'] = ['1', '3', '4']
    node_neighbor_dict['3'] = []
    node_neighbor_dict['4'] = ['1', '2', '3', '5', '6']
    node_neighbor_dict['5'] = ['6']
    node_neighbor_dict['6'] = ['5', '7']
    node_neighbor_dict['7'] = []
    
    for node in node_neighbor_dict:
        for n in node_neighbor_dict[node]:
            assert(n in g.edge[node])
        temp_list = [e for e in all_nodes_list if e not in node_neighbor_dict[node]]
        for n in temp_list:
            assert(n not in g.edge[node])

    
    
'''
Test that a complete graph finishes upon calling the
finished hook.
'''
def test_graph_finished():
    g = test_cross_graph()
    for node in g.node:
        for node2 in g.node:
            g.node[node]['has_' + node2] = True
            
    assert config.finished_hook(g, 0, 'run_name') == 1
    
    
'''
Tests whether or not a graph will appropriately set broadcast_information
on all relevant nodes using the cross graph.
'''
def test_cross_graph_center_edge_spread():
    g = test_cross_graph()
    g.node['1']['has_1'] = True
    
    config.before_round_start(g, [], [], [], [], 0, 'run_name')
    
    assert(len(g.edge['1']) == 4)
    
    for edge_to in g.edge['1']:
        assert(g.edge['1'][edge_to]['broadcast_information'] == '1')

        
'''
Tests whether or not a graph will appropriately set broadcast_information
on all relevant nodes using the cross graph and makes sure that the center
node does not recieve the broadcast.
'''
def test_cross_graph_center_edge_receives_four_transmissions():
    g = test_cross_graph()
    set_config_variable_dicts(g)
    # 'has_1' is odd in this context, but whatever
    g.node['2']['has_1'] = True
    g.node['3']['has_1'] = True
    g.node['4']['has_1'] = True
    g.node['5']['has_1'] = True
    
    config.before_round_start(g, [], [], [], [], 0, 'run_name')

    gc = helper.copy_graph(g)
    
    for node in g:
        config.on_node(g, gc, node, 0, 'run_name')
        
    assert(len(g.edge['1']) == 4)
    
    # Test that the information DID NOT get spread to the center node
    assert not g.node['1']['has_1']
    
    # Test that there is a broadcast_delay on each node that is not 0
    assert g.node['2']['broadcast_delay'] > 0
    assert g.node['3']['broadcast_delay'] > 0
    assert g.node['4']['broadcast_delay'] > 0
    assert g.node['5']['broadcast_delay'] > 0
    
@pytest.fixture(scope='function')
def set_config_variable_dicts(g):
    for node in g.node:
        # Total dictionaries
        config.total_broadcasts_sent[node] = 0
        config.total_broadcasts_received_successfully[node] = 0
        config.total_broadcasts_received_overall[node] = 0
        config.total_interference_failures[node] = 0
        # Current dictionaries
        config.current_broadcasts_sent[node] = 0
        config.current_broadcasts_received_successfully[node] = 0
        config.current_broadcasts_received_overall[node] = 0
        config.current_interference_failures[node] = 0
    
'''
Tests whether or not a graph will appropriately reset broadcast_information
at the end of a round.
'''
def test_cross_graph_center_edge_spread():
    g = test_cross_graph()
    set_config_variable_dicts(g)
    
    g.node['1']['has_1'] = True
    
    config.before_round_start(g, [], [], [], [], 0, 'run_name')
    
    assert(len(g.edge['1']) == 4)
    
    config.after_round_end(g, [], [], [], [], 0, 'run_name')
    
    for edge_to in g.edge['1']:
        assert(g.edge['1'][edge_to]['broadcast_information'] is None)
        
 
'''
Tests whether or not a graph will spread transmission to other nodes as
would happen in a simulation, given there are no conflicts.
'''
def test_cross_graph_center_information_spread():
    g = test_cross_graph()
    set_config_variable_dicts(g)
    
    g.node['1']['has_1'] = True
    
    config.before_round_start(g, [], [], [], [], 0, 'run_name')
    
    gc = helper.copy_graph(g)
    
    for node in g:
        config.on_node(g, gc, node, 0, 'run_name')
        
    for node in g:
        assert(g.node[node]['has_1'])
    
    

    
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
    g = setup_test_graph_from_test_xyz_csv(10)
    
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
    g = setup_test_graph_from_test_xyz_csv(100)
    
    all_nodes_list = [str(x) for x in range (1,11)]
    
    for node in all_nodes_list:
        for n in all_nodes_list:
            if not node == n:
                assert(n in g.edge[node])