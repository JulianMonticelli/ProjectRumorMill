import pytest

import networkx as nx

import simrun as run

@pytest.fixture(scope='function')
def setup_graph():
   g = nx.Graph()   
   g.add_node(1, flagged=True)
   g.add_node(2, flagged=True)
   g.add_node(3, flagged=True)
   g.add_node(4, flagged=True)
   g.add_node(5, flagged=True)
   return g
   
   
def test_finished():
   g = setup_graph()
   assert run.finished(g, 1) == 1 # 1 is a successful finish
   
def test_finished_not_finished():
   g = setup_graph()
   g.add_node(6, flagged=False)
   assert run.finished(g, 1) == 0 # 0 is an unseccessful finish

def test_finished_exceeded_max_rounds():
   g = setup_graph()
   # Assuming that most max_rounds variables will be under 2.147 billion :)
   assert run.finished(g, 2147000000) == -1 # -1 represents exceeding max rounds
   
def test_num_flagged_5():
   g = setup_graph()
   assert run.num_flagged(g) == 5
   
def test_num_flagged_6_flagged_3_unflagged():
   g = setup_graph()
   g.add_node(6, flagged=False)
   g.add_node(7, flagged=False)
   g.add_node(8, flagged=False)
   g.add_node(9, flagged=True)
   assert run.num_flagged(g) == 6