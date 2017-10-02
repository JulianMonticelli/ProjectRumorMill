import pytest

import networkx as nx

import simround as round
import simrun as run # Needed for num_flagged helper function


@pytest.fixture(scope='function')
def setup_graph():
   g = nx.Graph()   
   g.add_node('1', flagged=False)
   g.add_node('2', flagged=False)
   g.add_node('3', flagged=False)
   g.add_node('4', flagged=False)
   g.add_node('5', flagged=False)
   g.add_edge('1', '2', weight=1)
   g.add_edge('2', '3', weight=1)
   g.add_edge('3', '4', weight=1)
   g.add_edge('4', '5', weight=1)
   return g

   
# Test to make sure that flags don't leak farther than they should
def test_round_spread_no_leak():
   g = setup_graph()
   g.node['1']['flagged'] = True
   num_before = run.num_flagged(g)
   round.round(g, 1, 1, False, False)
   num_after = run.num_flagged(g)
   assert (num_after - num_before) == 1
   
# (Probably unnecessary) test that checks for a leak among a middle node (more than one potential transmission)
def test_round_spread_no_leak_2():
   g = setup_graph()
   g.node['3']['flagged'] = True
   num_before = run.num_flagged(g)
   round.round(g, 1, 1, False, False)
   num_after = run.num_flagged(g)
   assert (num_after - num_before) == 2
   
def test_roll_weight():
   num = 1000000
   num_passed = 0
   for i in range (0, num):
      if round.roll_weight(3, 5):
         num_passed += 1
   perc_passed = num_passed / float(num)
   assert perc_passed >= .59 and perc_passed <= .61
   
def test_roll_weight_zero():
   num = 1000000
   num_passed = 0
   for i in range (0, num):
      if round.roll_weight(0, 5):
         num_passed += 1
   perc_passed = num_passed / float(num)
   assert perc_passed == 0
   
def test_roll_weight_max():
   num = 1000000
   num_passed = 0
   for i in range (0, num):
      if round.roll_weight(5, 5):
         num_passed += 1
   perc_passed = num_passed / float(num)
   assert perc_passed == 1.0