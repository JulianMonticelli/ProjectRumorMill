import networkx as nx

import pytest

import sim

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
   assert sim.percent(3, 4) == 75.0
   assert sim.percent(3, 5) == 60.0
   

# Tests max_weight against a newly constructed graph
def test_max_weight_normal():
   g = setup_graph_positive()
   assert sim.max_weight(g) == 9

def test_max_weight_negative():
   g = setup_graph_negative()
   assert sim.max_weight(g) == -3


   
def test_chance_zero():
   for i in range (0, 1000):
      assert sim.chance(0) != True
	  
def test_chance_negative():
   for i in range (0, 1000):
      assert sim.chance(-i) != True
	  
def test_chance_absolute():
   for i in range (0, 1000):
      assert sim.chance(1.0) == True


#
# WARNING: There is a chance this will fail - but it will in most instances pass	  
def test_chance_50():
   num = 100000
   trues = 0
   for i in range (0, num):
      if sim.chance(0.5) == True:
	    trues += 1
   percent_pass = trues / float(num)
   assert (percent_pass > .49 and percent_pass < .51)
   
def test_create_node_attribute():
   g = setup_graph_positive()
   sim.create_node_attribute(g, 'test', True)
   for node in g.node:
      assert g.node[node]['test']


def test_randomize_node_attribute():
   g = setup_graph_positive()
   sim.create_node_attribute(g, 'test', -1)
   sim.randomize_node_attribute(g, 'test', 0, 10)
   for node in g.node:
      val = g.node[node]['test']
      assert val >= 0 and val <= 10


def test_randomize_node_attribute_boolean():
   g = setup_many_node_graph()
   sim.randomize_node_attribute_boolean(g, 'test', .50)
   true_nodes = 0
   total_nodes = len(g.node)
   for node in g.node:
      if g.node[node]['test']:
         true_nodes += 1
   perc_nodes = true_nodes / float(total_nodes)
   assert perc_nodes >= .49 and perc_nodes <= .51
   
def test_create_edge_attribute():
   g = setup_graph_positive()
   sim.create_edge_attribute(g, 'test', True)
   for source in g.edge:
      for dest in g.edge[source]:
         assert g.edge[source][dest]['test']


def test_randomize_edge_attribute():
   g = setup_graph_positive()
   sim.create_edge_attribute(g, 'test', -1)
   sim.randomize_edge_attribute(g, 'test', 0, 10)
   for source in g.edge:
      for dest in g.edge[source]:
         val = g.edge[source][dest]['test']
         assert val >= 0 and val <= 10


def test_randomize_edge_attribute_boolean():
   g = setup_very_long_chain_graph()
   sim.create_edge_attribute(g, 'test', False)
   sim.randomize_edge_attribute_boolean(g, 'test', .50)
   true_edges = 0
   total_edges = g.number_of_edges()
   for source in g.edge:
      for dest in g.edge[source]:
         if g.edge[source][dest]['test'] and (source < dest or nx.is_directed(g)):
            true_edges += 1
   perc_edges = true_edges / float(total_edges)
   assert perc_edges >= .49 and perc_edges <= .51