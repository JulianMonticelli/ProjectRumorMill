# Python Library Packages
import networkx as nx
import copy

# Cyclical dependency to main
import simengine as engine # < Driver in config requires this
import simhelper as helper
import simdefaults as defaults

#######################
# Simulation arguments#
#######################
maximum_allowed_simulation_rounds = 10 # Max amount of rounds before we stop running a simulation
num_runs = 1      # Default number of runs per simulation

edge_removal_chance = .12
edge_addition_chance = edge_removal_chance / 2

food_per_round = 500
water_per_round = 100
health_regen_per_round = 1



#######################
# Global data         #
#######################
num_nodes = 0 # The number of nodes in a starter graph
total_simulations = 0
humans_lost = 0
humans_won = 0
humans_left_min = float('inf')
humans_left_max = float('-inf')

####################################################################################
'''
Simulation driver, which will call the engine to begin simulations. Setup should
happen in this method, and data collection should be done inside any method necessary.
A logically sound place to put data processing is at the end of this method.
'''
####################################################################################
def simulation_driver():
   global num_nodes
   
   # Read in a graph
   graph = nx.read_graphml('custom_graphs/zombie_adv.graphml')
   helper.output_graph_information(graph)
   num_nodes = helper.num_nodes(graph)
   
   # Start from every node in the graph
   for n in graph.node:
      sim_name = 'zsim_' + str(n)
      graphcopy = copy.deepcopy(graph)
      init(graphcopy, n, sim_name)
      engine.simulate(graphcopy, num_runs, sim_name)
	  

   print '\n' * 2
   print '*' * defaults.asterisk_space_count
   print 'Simulations complete.'
   print '*' * defaults.asterisk_space_count + '\n' * 2
   print 'Simulation runs where humans were desolated: ' + str(humans_lost)
   print 'Simulation runs where humans prevailed: ' + str(humans_won)
   print 'Total number of simulations runs:    ' + str(total_simulations)
   print '\n'
   print 'Humans won statistics:\n'
   print 'Minimum humans left: ' + str(humans_left_min)
   print 'Maximum humans left: ' + str(humans_left_max)
####################################################################################



####################################################################################
'''
Hook for considering a node in the graph.
   Args:
      graph: A networkx graph instance.
      graph_copy: Another networkx graph instance which is the deep copy of graph.
      node: A networkx node instance.
      max_weight: An integer which is the max weight of edges in this graph.
      run_name: The name of the current run
'''
####################################################################################
def on_node(graph, graph_copy, node, max_weight, run_name):

   if (graph_copy.node[node]['infected']):
      on_flagged(graph, graph_copy, node, max_weight, run_name)

      # If the node does not know, and we can spontaneously come into knowing
   else:
      on_not_flagged(graph, graph_copy, node, run_name)
####################################################################################



####################################################################################
'''
Runs operations on a flagged node to determine if it will transmit information.
   Args:
      graph: A networkx graph instance.
      graph_copy: Another networkx graph instance which is the deep copy of graph.
      node: A networkx node instance.
      max_weight: An integer which is the max weight of edges in this graph.
      run_name: The name of the current run
	  
   Returns:
      NOTE: returns are optional
      given_flags: An integer showing how many nodes are flagged in this node operation.
'''
####################################################################################
def on_flagged(graph, graph_copy, node, max_weight, run_name):
   given_flags = 0
   
   # Check the unedited copy graph for flagged neighbors
   for neighbor in graph_copy.edge[node]:
      # If a target graph node in both the copy and original aren't flagged
      if (not graph_copy.node[neighbor]['infected'] and not graph.node[neighbor]['infected']):
         
         # If the simulation will actually spread, then spread
         if (will_spread(node, neighbor, graph, max_weight, run_name)):
            graph.node[neighbor]['infected'] = True
			
            # Increment the number of given_flags this round
            given_flags += 1

   return given_flags			
####################################################################################



####################################################################################
'''
Currently will only check whether or not spontaneous acquisition will occur.
   Args:
      graph: A networkx graph instance.
      graph_copy: Another networkx graph instance which is the deep copy of graph.
      node: A networkx node instance.
      run_name: The name of the current method

   Returns:
      0: If spontaneous acquisition doesn't happen in this node operation.
      1: If spontaneous acquisition happens in this node operation.
'''
####################################################################################
def on_not_flagged(graph, graph_copy, node, run_name):
   return 0 # No change
####################################################################################



####################################################################################
'''
Determine if a given source node will transmit information to a given node.
   Args:
      source: A networkx node instance which is the source node in this transmission.
      dest: Another networkx node instance which is the destination node in this transmission.
      graph: A networkx graph instance.
      max_weight: An integer which is the max weight of edges in this graph.
      run_name: The name of the current run

   Returns:
      True: If the information is spread in this node operation.
      False: If the information isn't spread in this node operation.
'''
####################################################################################
def will_spread(source, dest, graph, max_weight, run_name):
   # TODO: Add more dynamic way to spread flags from nodes to nodes
   
   # Get current weight
   curr_weight = graph.edge[source][dest]['weight']
   
   # Will they engage at all? This consults the weight of their edge
   # Currently, it is set up so that if communication happens at all
   # 
   if ( helper.roll_weight (curr_weight , max_weight ) ):
      return True
   return False
####################################################################################



####################################################################################
'''
Hook for changing the graph at the beginning of the round. Note that this takes place before the graph is copied in the engine.
   Args:
      graph: A networkx graph instance.
      max_weight: An integer which is the max weight of edges in this graph.
      run_name: The name of the current run 
'''
####################################################################################
def before_round_start(graph, max_weight, run_name):
   for edge in graph.edge:
      # do nothing
	  print '',
	     
   return
####################################################################################



####################################################################################
'''
Hook for considering a node in the graph.
   Args:
      graph: A networkx graph instance.

   Returns:
      given_flags: An integer showing how many nodes are flagged in this round.
      removed_flags: An integer showing how many nodes are unflagged in this round.
      run_name: The name of the current run
'''
####################################################################################
def after_round_end(graph, run_name):
   given_flags = 0
   removed_flags = 0
   
   # Modifying iterables can potentially be bad, so create a removal list
   remove_nodes = []
   
   for node in graph.node:
      graph.node[node]['food'] -= food_per_round
      graph.node[node]['water'] -= water_per_round
	  
      if (graph.node[node]['food'] <= 0 or graph.node[node]['water'] <= 0):
         remove_nodes.append(node)

   for node in remove_nodes:
      helper.kill_node(graph, node)
####################################################################################



####################################################################################
'''
Initialize the graph with attributes that are necessary to run a simulation.
Takes a graph and a String node (i.e., 'n10') to initialize as flagged.
Also initializes uninitialized weights on graphs as 1.
   Args:
      graph: A networkx graph instance.
      node: A networkx node instance.
      sim_name: The name of the current simulation
'''
####################################################################################
def init(graph, node, sim_name):

   # Give all nodes a false flag
   helper.create_node_attribute(graph, 'infected', False)
   
   # Save edge weight, as we are going to wipe graph
   dict = nx.get_edge_attributes(graph, 'weight')
   
   # Write 1 weight to all edges
   nx.set_edge_attributes(graph, 'weight', 1)
   
   # Restore initial edges
   for n1,n2 in dict:
      graph.edge[n1][n2]['weight'] = dict[n1,n2]
   
   
   # Set a specific node
   graph.node[node]['infected'] = True
####################################################################################

   
####################################################################################
'''
Determines whether or not a graph is finished.
   Args:
      graph: A networkx graph instance.
      current_round: An integer recording the current number of rounds.
      max_allowed_rounds: An integer which is set to be the max allowed number of rounds.
      run_name: The name of the current simulation run
	  
   Returns:
     -1: If there are zombies and humans left, but we have ran out of allowed rounds
      0: If there are zombies and humans left
      1: If the virus has spread to all remaining humans
      2: If there are only humans left
      3: If nothing is left
'''
####################################################################################
def finished_hook(graph, current_round, max_allowed_rounds, run_name):
   # Get all attributes and store them in a dictionary
   dict = nx.get_node_attributes(graph, 'infected')
   
   # Make sure we haven't hit the maximum allowed round
   if (current_round > max_allowed_rounds):
      return -1 # -1 means we ran out of allowed rounds
   

   # Iterate the nodes and see if they're flagged or not
   if (len(dict) == 0):
      return 3 # Indicates nothing is left
   for val in dict:
      if(not dict[val]):
         #print '[' + val  + ']: ' + str(dict[val])
         if (helper.num_flagged(graph, 'infected') > 0):
            return 0
         else:
            return 2
   return 1 # 1 indicates that zombies have won (and humans have lost)
####################################################################################



####################################################################################
'''
Hook for finishing the simulation run on the current graph.
   Args:
      finish_code: -1, 1, or 2 depend on the finish code we return in finished_hook function.
      round_num: An integer showing how many round we use to finish the graph if succeed.
      num_flags: An integer showing how many nodes are flagged in the end.
      run_name: The name of the current simulation run
'''
####################################################################################
def on_finished(finish_code, round_num, num_flags, run_name):
   global total_simulations, humans_lost, humans_won, humans_left_min, humans_left_max
   
   total_simulations += 1
   if (finish_code < 0):
      print 'Graph ran until completion. Failed to infect all humans, zombies not dead.'
   if (finish_code == 1):
      print 'Humans are all dead - zombies remain'
      humans_lost += 1
   if (finish_code == 2):
      print 'Zombies are all dead - humans have prevailed!'
      humans_won += 1
   if (finish_code == 3):
      print 'Somehow, there was nothing left (starvation might have gotten all zomibes and humans!'
      # DO NOT have data code
####################################################################################