import networkx as nx

import pytest

import sim

# Run in command line as 'pytest simtest.py' if you are not familiar with pytest
# You will need to pip install pytest if you don't have it installed.

# Tests percentage function
def test_percent():
   assert sim.percent(3, 4) == 75.0
   assert sim.percent(3, 5) == 60.0
   

# Tests max_weight against a newly constructed graph
def test_max_weight_normal():
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
   assert sim.max_weight(g) == 9

def test_max_weight_negative():
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