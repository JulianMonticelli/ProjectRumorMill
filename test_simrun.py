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
   
   
def test_finished():
   g = setup_graph()
   assert run.finished(g, 1, 1000) == 1 # 1 is a successful finish
   
def test_finished_not_finished():
   g = setup_graph()
   g.add_node(6, flagged=False)
   assert run.finished(g, 1, 1000) == 0 # 0 is an unseccessful finish

def test_finished_exceeded_max_rounds():
   g = setup_graph()
   # Assuming that most max_rounds variables will be under 2.147 billion :)
   assert run.finished(g, 2147000000, 10000) == -1 # -1 represents exceeding max rounds
   assert run.finished(g, 9001, 9000) == -1
   assert run.finished(g, 0, -1) == -1
   
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

def test_run_passed_success():
   g = setup_short_chain_graph(True, False, 1)
   return_code, throwaway = run.run(g, 1, 20, False, False)
   assert return_code > 1 # Return code should be number of rounds it took to get a successful solution
   
   
def test_run_failed_out_of_rounds():
   g = setup_short_chain_graph(True, False, 0)
   return_code, throwaway = run.run(g, 1, 2, False, False)
   assert return_code == -1
   
   
# Tests to make sure that a num_flagged error doesn't happen when considering spontaneous forgetting & acquisition
def test_sim_round_num_flagged_forgetting_acquisition():
   for i in range (0, 50):
      g = setup_long_chain_graph(True, False, 0)
      throwaway, num_flagged = run.run(g, 1, 2000, talk_to_transmit=True, spontaneous_acquisition=True, spontaneous_acquisition_chance=.01, spontaneous_forget=True, spontaneous_forget_chance=.01)
      assert num_flagged == run.num_flagged(g)

# Tests to make sure that a num_flagged error doesn't happen when considering spontaneous forgetting
def test_sim_round_num_flagged_forgetting():
   for i in range (0, 50):
      g = setup_short_chain_graph(True, False, 0)
      throwaway, num_flagged = run.run(g, 1, 1000, talk_to_transmit=True, spontaneous_acquisition=False, spontaneous_forget=True, spontaneous_forget_chance=.01)
      assert num_flagged == run.num_flagged(g)


# Tests to make sure that a num_flagged error doesn't happen when considering spontaneous acquisition
def test_sim_round_num_flagged_acquisition():
   for i in range (0, 50):
     g = setup_short_chain_graph(False, True, 0)
     throwaway, num_flagged = run.run(g, 1, 1000, talk_to_transmit=True, spontaneous_acquisition=True, spontaneous_acquisition_chance=.01, spontaneous_forget=False)
     assert num_flagged == run.num_flagged(g)