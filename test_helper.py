import networkx as nx

import pytest

import simhelper as helper

# Run in command line as 'pytest simtest.py' if you are not familiar with pytest
# You will need to pip install pytest if you don't have it installed.

@pytest.fixture(scope='function')
def setup_many_node_graph():
    g = nx.Graph()
    for i in range (0, 20000):
        g.add_node('n' + str(i), test=False)
    return g
    
def setup_very_long_chain_graph():
    g = nx.Graph()
    g.add_node('n0')
    for i in range (1, 20000):
        g.add_node('n' + str(i))
        g.add_edge('n' + str(i-1), 'n' + str(i), weight=-1, test=False)
    return g

@pytest.fixture(scope='function')
def setup_graph_positive():
    g = nx.Graph()
    g.add_node(1)
    g.add_node(2)
    g.add_node(3)
    g.add_node(4)
    g.add_node(5)
    g.add_edge(1, 3, weight=4)
    g.add_edge(2, 3, weight=9)
    g.add_edge(4, 5, weight=3)
    g.add_edge(1, 5, weight=7)
    g.add_edge(2, 4, weight=4)
    return g

@pytest.fixture(scope='function')
def setup_graph_negative():
    g = nx.Graph()
    g.add_node(1)
    g.add_node(2)
    g.add_node(3)
    g.add_node(4)
    g.add_node(5)
    g.add_edge(1, 3, weight=-4)
    g.add_edge(2, 3, weight=-9)
    g.add_edge(4, 5, weight=-3)
    g.add_edge(1, 5, weight=-7)
    g.add_edge(2, 4, weight=-4)
    return g
    
# Tests percentage function
def test_percent():
    assert helper.percent(3, 4) == 75.0
    assert helper.percent(3, 5) == 60.0
    

# Tests max_weight against a newly constructed graph
def test_max_weight_normal():
    g = setup_graph_positive()
    assert helper.max_weight(g) == 9

def test_max_weight_negative():
    g = setup_graph_negative()
    assert helper.max_weight(g) == -3


    
def test_chance_zero():
    for i in range (0, 1000):
        assert helper.chance(0) != True
	  
def test_chance_negative():
    for i in range (0, 1000):
        assert helper.chance(-i) != True
	  
def test_chance_absolute():
    for i in range (0, 1000):
        assert helper.chance(1.0) == True


#
# WARNING: There is a chance this will fail - but it will in most instances pass	  
def test_chance_50():
    num = 100000
    trues = 0
    for i in range (0, num):
        if helper.chance(0.5) == True:
	     trues += 1
    percent_pass = trues / float(num)
    assert (percent_pass > .49 and percent_pass < .51)
    
def test_create_node_attribute():
    g = setup_graph_positive()
    helper.create_node_attribute(g, 'test', True)
    for node in g.node:
        assert g.node[node]['test']


def test_randomize_node_attribute():
    g = setup_graph_positive()
    helper.create_node_attribute(g, 'test', -1)
    helper.randomize_node_attribute(g, 'test', 0, 10)
    for node in g.node:
        val = g.node[node]['test']
        assert val >= 0 and val <= 10


def test_randomize_node_attribute_boolean():
    g = setup_many_node_graph()
    helper.randomize_node_attribute_boolean(g, 'test', .50)
    true_nodes = 0
    total_nodes = len(g.node)
    for node in g.node:
        if g.node[node]['test']:
            true_nodes += 1
    perc_nodes = true_nodes / float(total_nodes)
    assert perc_nodes >= .49 and perc_nodes <= .51
    
def test_create_edge_attribute():
    g = setup_graph_positive()
    helper.create_edge_attribute(g, 'test', True)
    for source in g.edge:
        for dest in g.edge[source]:
            assert g.edge[source][dest]['test']


def test_randomize_edge_attribute():
    g = setup_graph_positive()
    helper.create_edge_attribute(g, 'test', -1)
    helper.randomize_edge_attribute(g, 'test', 0, 10)
    for source in g.edge:
        for dest in g.edge[source]:
            val = g.edge[source][dest]['test']
            assert val >= 0 and val <= 10


def test_randomize_edge_attribute_boolean():
    g = setup_very_long_chain_graph()
    helper.create_edge_attribute(g, 'test', False)
    helper.randomize_edge_attribute_boolean(g, 'test', .50)
    true_edges = 0
    total_edges = g.number_of_edges()
    for source in g.edge:
        for dest in g.edge[source]:
            if g.edge[source][dest]['test'] and (source < dest or nx.is_directed(g)):
                true_edges += 1
    perc_edges = true_edges / float(total_edges)
    assert perc_edges >= .49 and perc_edges <= .51

@pytest.fixture(scope='function')
def setup_graph():
    g = nx.Graph()    
    g.add_node(1, flagged=True)
    g.add_node(2, flagged=True)
    g.add_node(3, flagged=True)
    g.add_node(4, flagged=True)
    g.add_node(5, flagged=True)
    return g

@pytest.fixture(scope='function')
def setup_disjoint_subgraphs():
    g = setup_graph()
    # Note we keep node 6 in the subgraph, unflagged
    g.add_node(6, flagged=False)
    g.add_edge(1, 2, weight=1)
    g.add_edge(2, 3, weight=1)
    g.add_edge(3, 4, weight=1)
    g.add_edge(4, 5, weight=1)
    g.add_edge(5, 6, weight=1)
    g.add_node(7, flagged=True)
    g.add_node(8, flagged=True)
    g.add_node(9, flagged=False)
    g.add_edge(7, 8, weight=1)
    g.add_edge(8, 9, weight=1)
    return g
    
@pytest.fixture(scope='function')
def setup_long_chain_graph(start_flag, init_flag, w):
    g = nx.Graph()
    g.add_node('n0', flagged=start_flag)
    for i in range (1, 100):
        g.add_node('n' + str(i), flagged=init_flag)
        g.add_edge('n' + str(i-1), 'n' + str(i), weight=w)
    return g
    
@pytest.fixture(scope='function')
def setup_short_chain_graph(start_flag, init_flag, w):
    g = nx.Graph()
    g.add_node('n0', flagged=start_flag)
    for i in range (1, 10):
        g.add_node('n' + str(i), flagged=init_flag)
        g.add_edge('n' + str(i-1), 'n' + str(i), weight=w)
    return g  
  
def test_num_flagged_5():
    g = setup_graph()
    assert helper.num_flagged(g, 'flagged') == 5
    
def test_num_flagged_6_flagged_3_unflagged():
    g = setup_graph()
    g.add_node(6, flagged=False)
    g.add_node(7, flagged=False)
    g.add_node(8, flagged=False)
    g.add_node(9, flagged=True)
    assert helper.num_flagged(g, 'flagged') == 6


def test_roll_weight():
    num = 1000000
    num_passed = 0
    for i in range (0, num):
        if helper.roll_weight(3, 5):
            num_passed += 1
    perc_passed = num_passed / float(num)
    assert perc_passed >= .59 and perc_passed <= .61

def test_roll_weight_zero():
    num = 1000000
    num_passed = 0
    for i in range (0, num):
        if helper.roll_weight(0, 5):
            num_passed += 1
    perc_passed = num_passed / float(num)
    assert perc_passed == 0
    
def test_roll_weight_max():
    num = 1000000
    num_passed = 0
    for i in range (0, num):
        if helper.roll_weight(5, 5):
            num_passed += 1
    perc_passed = num_passed / float(num)
    assert perc_passed == 1.0

def test_check_subgraph_spread():
    g = nx.Graph()
    g.add_node(1, flagged=True)
    g.add_node(2, flagged=True)
    g.add_node(3, flagged=True)
    g.add_node(4, flagged=False)
    g.add_edge(1, 2, weight = 1)
    g.add_edge(1, 3, weight = 1)
    assert helper.check_subgraph_spread(g, 'flagged') == True
    g.add_node(5, flagged=True)
    assert helper.check_subgraph_spread(g, 'flagged') == True
    g.add_edge(4, 5, weight=1)
    assert helper.check_subgraph_spread(g, 'flagged') == False

def test_exceeded_round_limit():
    assert helper.exceeded_round_limit(0, 10) == False
    assert helper.exceeded_round_limit(101,101) == False
    assert helper.exceeded_round_limit(102,101) == True
    assert helper.exceeded_round_limit(-1, -2) == True # odd, but should still exceed
    assert helper.exceeded_round_limit(1,2) == False
