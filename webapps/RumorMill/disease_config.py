# Python Library Packages
import networkx as nx
import copy

import simengine as engine
import simhelper as helper
import simdefaults as defaults

#######################
# Simulation arguments#
#######################
heartbeat_interval = 30 # 30 second heartbeat
maximum_allowed_simulation_rounds = 100 # Max amount of rounds before we stop running a simulation
num_runs = 3      # Default number of runs per simulation

# Transmission variables
talk_to_transmit = False   # Transmission = just talking?
transmit_chance = 0.20 # If transmit =/= talk, what is the chance upon talking

# Forgetting variables
spontaneous_forget = True          # Node can forget
spontaneous_forget_chance = 0      # Chance for node to forget

# Spontaneous acquisition
spontaneous_acquisition = True  # Nodes can spontaneously become flagged
spontaneous_acquisition_chance = 0.1

dead_chance = 0.5
#######################
# Round options       #
#######################

# Whether or not a graph is considered finished if,
# when spontaneous acquisition is not occurring,
# information has spread to all nodes that can become
# spread to.
finished_includes_max_subgraph_spread=True

#######################
# Global data         #
#######################
num_infected = 0
num_dead = 0
num_flagged_successes = 0
num_flagged = 0
max_flagged = 0
total_simulations = 0
total_successes = 0
num_fails = 0
num_forgot = 0
num_given = 0
max_given = 0
max_forgot = 0
total_rounds = 0
max_virality = 0
min_rounds_success = float('inf')
max_rounds_success = float('-inf')

####################################################################################
'''
Simulation driver, which will call the engine to begin simulations. Setup should
happen in this method, and data collection should be done inside any method necessary.
A logically sound place to put data processing is at the end of this method.
'''
####################################################################################
def simulation_driver():
   # Read in a graph
   graph = nx.read_graphml('simplemodel.graphml')
   helper.output_graph_information(graph)

   # Start from every node in the graph
   for n in graph.node:
      graphcopy = copy.deepcopy(graph)

      # Create a simulation name
      sim_name = 'sim_' + n

      init(graphcopy, n, sim_name)

      # Start simulation with the simulation name
      engine.simulate(graphcopy, num_runs, sim_name)

      # Data collection per simulation should go here - any global variables should be recorded and reset

   percent_finished = helper.percent(total_successes, total_simulations)
   percent_flagged = helper.total_percent_flagged(graph, num_flagged, total_simulations)
   percent_flagged_successes = helper.total_percent_flagged(graph, num_flagged_successes, total_successes)
   average_rounds = 0
   if (total_successes > 0):
      average_rounds = total_rounds / float(total_successes)
   print '\n' * 2
   print '*' * defaults.asterisk_space_count
   print 'Simulations complete.'
   print '*' * defaults.asterisk_space_count
   print 'Total successful simulations (spread across whole graph): ' + str(total_successes)
   print 'Total failed simulations (could not spread across graph): ' + str(num_fails)
   print 'Total number of simulations (complete and incomplete):    ' + str(total_simulations)
   print '\n' + '*' * defaults.asterisk_space_count + '\n'
   print 'Min rounds until success: ' + str(min_rounds_success)
   print 'Max rounds until success: ' + str(max_rounds_success)
   print 'Average rounds until completion (across ' + str(total_successes) +' simulation runs): ' + str(average_rounds)
   print 'Average graph spread rate (across ' +  str(total_successes) + ' simulation runs): ' + str(percent_flagged_successes) + '%'
   print 'Average graph completion rate (across all graphs): ' + str(percent_finished) + '%'
   print 'Average graph spread rate (across all graphs): ' + str(percent_flagged) + '%'
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
   # Define relevant globals
   global num_forgot
   global num_given
   if graph_copy.node[node]['dead']:
      return

   if(will_forget(graph, graph_copy, node, 'infected', run_name, spontaneous_forget, spontaneous_forget_chance)):
      num_forgot += 1 # Update amount of forgotten flags
      return
      # IMPORTANT: So that directed graphs work as well as undirected graphs, consider flagged only
      # Check graph_copy for the flag - if we check graph, we will have leaking
   if (graph_copy.node[node]['infected']):
      num_given += on_flagged(graph, graph_copy, node, max_weight, run_name)

      # If the node does not know, and we can spontaneously come into knowing
   else:
      num_given += on_not_flagged(graph, graph_copy, node, run_name, spontaneous_acquisition, spontaneous_acquisition_chance)
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
      talk_to_transmit: A boolean which indicates whether 'talk' equals to 'transmit'.
      transmit_chance: A floating number which is the probability of transmission when 'talk' doesn't equal to 'transmit'.
   Returns:
      NOTE: returns are optional
      given_flags: An integer showing how many nodes are flagged in this node operation.
'''
####################################################################################
def on_flagged(graph, graph_copy, node, max_weight, run_name,
               talk_to_transmit=talk_to_transmit,
               transmit_chance=transmit_chance,
               dead_chance=dead_chance):
   given_flags = 0

   # Check the unedited copy graph for flagged neighbors
   for neighbor in graph_copy.edge[node]:
      if graph_copy.node[neighbor]['dead']:
         continue
      # If a target graph node in both the copy and original aren't flagged
      if (not graph_copy.node[neighbor]['infected'] and not graph.node[neighbor]['infected']):

         # If the simulation will actually spread, then spread
         if (will_spread(node, neighbor, graph, max_weight, run_name, talk_to_transmit, transmit_chance)):
            graph.node[neighbor]['infected'] = True

            # Increment the number of given_flags this round
            given_flags += 1

   if (helper.chance(dead_chance)):
      graph.node[node]['dead'] = True
      graph_copy.node[node]['dead'] = True
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
      spontaneous_acquisition: A boolean which indicates whether a node would be able to spontaneous acquire information.
      spontaneous_acquisition_chance: A floating number which is the probability of spontaneous acquisition if it's able to.

   Returns:
      0: If spontaneous acquisition doesn't happen in this node operation.
      1: If spontaneous acquisition happens in this node operation.
'''
####################################################################################
def on_not_flagged(graph, graph_copy, node, run_name,
                   spontaneous_acquisition=spontaneous_acquisition,
                   spontaneous_acquisition_chance=spontaneous_acquisition_chance):
   if (graph_copy.node[node]['dead']):
      return 0
   if (will_spontaneously_acquire(graph, graph_copy, node, 'infected', True, spontaneous_acquisition)):
      return 1 # We have made a positive difference in this graph by one
   return 0 # No change
####################################################################################



####################################################################################
'''
Performs a roll for a node that is in the know to determine whether or not an agent should lose a flag, and if so, updates the graph accordingly.
   Args:
      graph: A networkx graph instance.
      graph_copy: Another networkx graph instance which is the deep copy of graph.
      node: A networkx node instance.
      attr: A string indicating which attribute we currently consider.
      run_name: The name of the current run
      spontaneous_forget: A boolean which indicates whether a node would be able to spontaneous forget information.
      spontaneous_forget_chance: A floating number which is the probability of spontaneous forget if it's able to.
      forget_value: The value of attribute we need to set to nodes which forget.

   Returns:
      True: If spontaneous forget happens in this node operation.
      False: If spontaneous forget doesn't happen in this node operation.
'''
####################################################################################
def will_forget(graph, graph_copy, node, attr, run_name, spontaneous_forget, spontaneous_forget_chance, forget_value=False):
   # Make sure we don't forget what we don't know!
   if (spontaneous_forget and graph.node[node][attr] != forget_value):
      if (helper.chance(spontaneous_forget_chance)):
         # Wipe flag from both graph and graph_copy
         graph.node[node][attr] = forget_value
         graph_copy[node][attr] = forget_value
         return True
   return False
 # Skip this node because it no longer has a flag
####################################################################################



####################################################################################
'''
Performs a roll for a node that is not in the know to determine whether or not an agent should gain a flag, and if so, updates the graph accordingly.
   Args:
      graph: A networkx graph instance.
      graph_copy: Another networkx graph instance which is the deep copy of graph.
      node: A networkx node instance.
      attr: A string indicating which attribute we currently consider.
      acquisition_value: A value that will be given upon spontaneous acquisition
      run_name: The name of the current run
      spontaneous_acquisition: A boolean which indicates whether a node would be able to spontaneous forget information.
      spontaneous_acquisition_chance: A floating number which is the probability of spontaneous forget if it's able to.

   Returns:
      True: If spontaneous acquisition happens in this node operation.
      False: If spontaneous acquisition doesn't happen in this node operation.
'''
####################################################################################
def will_spontaneously_acquire(
                               graph, graph_copy, node, attr, acquisition_value, run_name,
                               spontaneous_acquisition=spontaneous_acquisition,
                               spontaneous_acquisition_chance=spontaneous_acquisition_chance
                              ):
   if (spontaneous_acquisition and graph.node[node][attr] != acquisition_value):
      if (helper.chance(spontaneous_acquisition_chance)):
         # Apply flag to both graph and graph_copy
         graph.node[node][attr] = acquisition_value
         graph_copy.node[node][attr] = acquisition_value
         return True
   return False
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
      talk_to_transmit: A boolean which indicates whether 'talk' equals to 'transmit'.
      transmit_chance: A floating number which is the probability of transmission when 'talk' isn't equal to 'transmit'.

   Returns:
      True: If the information is spread in this node operation.
      False: If the information isn't spread in this node operation.
'''
####################################################################################
def will_spread(
                source, dest, graph, max_weight, run_name,
                talk_to_transmit=talk_to_transmit,
				transmit_chance=transmit_chance
               ):
   # TODO: Add more dynamic way to spread flags from nodes to nodes

   # Get current weight
   curr_weight = graph.edge[source][dest]['weight']

   # Will they engage at all? This consults the weight of their edge
   if (helper.roll_weight (curr_weight , max_weight ) ):
      if (talk_to_transmit):
         return True
      else:
         # This is the chance that their engagement will exchange information
         if (helper.chance(transmit_chance)):
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
   #for edge in graph.edge:
      # do something
   global spontaneous_forget_chance
   #The chance people can cure the disease would increase at the beginning of each round
   if spontaneous_forget_chance < 0.5:
      spontaneous_forget_chance += 0.01
   global dead_chance
   if dead_chance < 1:
      dead_chance += 0.01
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

   #for edge in graph.edge:
      # do something

   return given_flags, removed_flags
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
   # Let the user know what node is the starting node.
   if (defaults.LOGGING or defaults.DEBUG or defaults.defaults.DEBUG_SEVERE):
      print '\n' + '*' * defaults.asterisk_space_count + '\nInitializing graph - \'' + str(node) + '\' is in the know.'

   # Give all nodes a false flag
   helper.create_node_attribute(graph, 'infected', False)
   helper.create_node_attribute(graph, 'dead', False)

   # Save edge weight, as we are going to wipe graph
   dict = nx.get_edge_attributes(graph, 'weight')

   # Write 1 weight to all edges
   nx.set_edge_attributes(graph, 'weight', 1)

   # Restore initial edges
   for n1,n2 in dict:
      graph.edge[n1][n2]['weight'] = dict[n1,n2]


   # Set an specific node
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
	  [spontaneous_acquisition]: An override for the file default state of spontaneous
                                 acquisition
	  [spontaneous_acquisition_chance]: An override for the file default spontaneous
                                        acquisition chance.

   Returns:
      0: If we fail to finish this graph simulation run.
      1: If we succeed to finish this graph simulation run.
      -1: If the current round number exceeds the max allowed number.
'''
####################################################################################
def finished_hook(graph, current_round, max_allowed_rounds, run_name,
                  spontaneous_acquisition = spontaneous_acquisition,
                  spontaneous_acquisition_chance = spontaneous_acquisition_chance):
   # Get all attributes and store them in a dictionary
   dict = nx.get_node_attributes(graph, 'dead')

   helper.num_flagged(graph, 'dead')

   # Make sure we haven't hit the maximum allowed round
   if (helper.exceeded_round_limit(current_round, max_allowed_rounds)):
      return -1 # -1 means we failed

   #if

   # A subgraph completion check should only be done if we don't spontaneously acquire information
   # and if finished is meant to include max subgraph spread
   if (
       (spontaneous_acquisition == False or spontaneous_acquisition_chance <= 0)
       and
       finished_includes_max_subgraph_spread
	  ):
      return helper.check_subgraph_spread(graph)

   # If the above check is not true, check how many nodes are flagged.
   # If all nodes are flagged, the information has successfully passed itself along.
   # Otherwise, make sure we haven't lost all of the information before trying to spread it further.
   else:
      # Iterate the nodes and see if they're flagged or not
      for val in dict:
         if(not dict[val]):
            #print '[' + val  + ']: ' + str(dict[val])
            if (helper.num_flagged(graph, 'dead') > 0):
               return 0
            else:
               return -1
      return 1 # 1 is a successful graph
####################################################################################



####################################################################################
'''
Hook for finishing the simulation run on the current graph.
   Args:
      finish_code: 0 or 1 or -1 depend on the finish code we return in finished_hook function.
      round_num: An integer showing how many round we use to finish the graph if succeed.
      num_flags: An integer showing how many nodes are flagged in the end.
      run_name: The name of the current simulation run
'''
####################################################################################
def on_finished(graph, finish_code, round_num, run_name, total_time_seconds):
   global num_given
   global num_forgot
   global total_simulations
   global total_successes
   global num_fails
   global total_rounds
   global num_flagged
   global num_flagged_successes
   global max_flagged
   global min_rounds_success
   global max_rounds_success

   total_simulations += 1
   flagged_nodes = helper.num_flagged(graph, 'dead')
   num_flagged += flagged_nodes

   if (finish_code < 0):
      print run_name + '> failed! ' + str(helper.num_flagged(graph, 'dead')) + ' flagged out of ' + str(helper.num_nodes(graph))
      num_given = 0
      num_forgot = 0
      num_fails += 1
      return
   else:
      print run_name + '> succeeded! ' + str(helper.num_flagged(graph, 'dead')) + ' flagged out of ' + str(helper.num_nodes(graph))
      total_rounds
      num_given = 0
      num_forgot = 0
      num_flagged_successes += flagged_nodes
      total_rounds += round_num
      total_successes += 1
      min_rounds_success = min(min_rounds_success, round_num)
      max_rounds_success = max(max_rounds_success, round_num)
   # Add simulation-based variables to global sums

####################################################################################



####################################################################################
'''
Hook for performing a heartbeat. This is meant to let the user know that the
simulation is still running and NOT stuck somewhere in an infinite loop.
    Args:
        current_time: A current time timestamp.
        last_heartbeat: The amount of seconds since the last heartbeat.
        run_name: The name of the current run.
'''
####################################################################################
def heartbeat(current_time, last_heartbeat, run_name):
   print '[' + str(current_time) + ']: ' + str(run_name) + ' still alive. Last update was ' \
         + str(last_heartbeat) + ' seconds ago.'
####################################################################################
