# Change output to be gossip specific
# Change percentages of individual nodes based on whether they are popular, not popular, direct friend with popular, or other
# if pop higher chance of spreading always
# if friend of pop 

# Python Library Packages
import networkx as nx
import copy

# Cyclical dependency?
import simengine as engine
import simhelper as helper
import simdefaults as defaults

#######################
# Simulation arguments#
#######################
heartbeat_interval = 30 # 30 second heartbeat interval
maximum_allowed_simulation_rounds = 100 # Max amount of rounds before we stop running a simulation
num_runs = 3      # Default number of runs per simulation

max_weight = 0 # Upon initialization of graph, max_weight will be calculated

# Transmission variables

# Set to true so that just because 2 people talk doesn't mean they exchanged the gossip
talk_to_transmit = False   # Transmission = just talking?

# make this dependent on something! 
# not everyone has the same chance of passing the info - what if they're friends or nah
# friends have more of the same connecting nodes
transmit_chance = 0.20 # If transmit =/= talk, what is the chance upon talking

# Forgetting variables

# Set this to be true but with a very small chance it's some juicy gossip!
spontaneous_forget = True          # Node can forget
spontaneous_forget_chance = 0.01      # Chance for node to forget

# Spontaneous acquisition

# Set to true - this is like a person getting the gossip from an outside source
spontaneous_acquisition = True  # Nodes can spontaneously become flagged
# Set to be more likely than forgetting - the internet exists!
spontaneous_acquisition_chance = 0.10

#######################
# Round options       #
#######################

# Whether or not a graph is considered finished if,
# when spontaneous acquisition is not occurring,
# information has spread to all nodes that can become
# spread to.
finished_includes_max_subgraph_spread=True


def simulation_driver():
   global max_weight # Hack to replace max_weight (< Julian did this)
   
   # Read in a graph
   graph = nx.read_graphml('simplemodel.graphml')
   max_weight = helper.max_weight(graph)
   helper.output_graph_information(graph)

   total_rounds = 0
   total_flagged = 0
   total_max_flags = 0
   total_fails = 0
   total_simulations = 0
   total_successes = 0
   
   # Start from every node in the graph
   for n in graph.node:
      graphcopy = copy.deepcopy(graph)
      init(graphcopy, n)
      flagged, max_flags, sum_rounds, num_fails = engine.simulate(graphcopy, num_runs, 'gossip_' + n)
      total_rounds += sum_rounds
      total_flagged += flagged
      total_max_flags += max_flags
      total_fails += num_fails
      total_simulations += num_runs
      
   total_successes = total_simulations-total_fails
   
   percent_finished = helper.percent(total_successes, total_simulations)
   percent_flagged = helper.total_percent_flagged(graph, total_flagged, total_simulations)
   
   average_rounds = 0
   if (total_successes > 0):
      average_rounds = total_successes / float(total_simulations) * 100
   print '\n' * 2
   print '*' * defaults.asterisk_space_count
   print 'Simulations complete.'
   print '*' * defaults.asterisk_space_count
   print 'Total successful simulations (spread across whole graph): ' + str(total_successes)
   print 'Total failed simulations (could not spread across graph): ' + str(total_fails)
   print 'Total number of simulations (complete and incomplete):    ' + str(total_simulations)
   print '\n'
   print 'Average rounds until completion (across ' + str(total_successes) +' simulation runs): ' + str(average_rounds) + '%'
   print 'Average graph completion rate (across all graphs): ' + str(percent_finished) + '%'
   print 'Average graph spread rate (across all graphs): ' + str(percent_flagged) + '%'
####################################################################################



# add options for popularity 
# if popular something
# if direct friend of popular
# if unpopular
# everyone else

####################################################################################
# Hook for considering a node in the graph.                                        #
####################################################################################
def on_node(graph, graph_copy, node,  round_num, run_name):
   given_flags = 0
   removed_flags = 0
   if(will_forget(graph, graph_copy, node, 'flagged')):
      removed_flags += 1 # Update amount of forgotten flags
      return given_flags, removed_flags
      # IMPORTANT: So that directed graphs work as well as undirected graphs, consider flagged only
      # Check graph_copy for the flag - if we check graph, we will have leaking
   if (graph_copy.node[node]['flagged']):
      given_flags += on_flagged(graph, graph_copy, node)

      # If the node does not know, and we can spontaneously come into knowing
   else:
      given_flags += on_not_flagged(graph, graph_copy, node)
   return given_flags, removed_flags
####################################################################################

# add options for popularity 
# if popular something
# if direct friend of popular
# if unpopular
# everyone else

####################################################################################
# Runs operations on a flagged node to determine if it will transmit information.  #
####################################################################################
def on_flagged(graph, graph_copy, node):
   given_flags = 0
   
   # Check the unedited copy graph for flagged neighbors
   for neighbor in graph_copy.edge[node]:
      # If a target graph node in both the copy and original aren't flagged
      if (not graph_copy.node[neighbor]['flagged'] and not graph.node[neighbor]['flagged']):
         
         # If the simulation will actually spread, then spread
         if (will_spread(node, neighbor, graph, talk_to_transmit, transmit_chance)):
            graph.node[neighbor]['flagged'] = True
			
            # Increment the number of given_flags this round
            given_flags += 1

   return given_flags			
####################################################################################



####################################################################################
# Currently will only check whether or not spontaneous acquisition will occur.     #
####################################################################################
def on_not_flagged(graph, graph_copy, node):
   return 0 # No change
####################################################################################



####################################################################################
# Determine if a given source node will transmit information to a given node       #
####################################################################################
def will_spread(source, dest, graph):
   # TODO: Add more dynamic way to spread flags from nodes to nodes
   
   # Get current weight
   curr_weight = graph.edge[source][dest]['weight']
   
   # Will they engage at all? This consults the weight of their edge
   if ( helper.roll_weight (curr_weight , max_weight ) ):
      return True
   return False
####################################################################################



####################################################################################
# Hook for changing the graph at the beginning of the round. Note that this takes  #
# place before the graph is copied in the engine.                                  #
####################################################################################
def before_round_start(graph, add_edge_list, remove_edge_list, add_node_list, remove_node_list, round_num, run_name):
   #for edge in graph.edge:
      # do something
   return
####################################################################################



####################################################################################
# Hook for considering a node in the graph.                                        #
####################################################################################
def after_round_end(graph, add_edge_list, remove_edge_list, add_node_list, remove_node_list, round_num, run_name):
   given_flags = 0
   removed_flags = 0
   
   #for edge in graph.edge:
      # do something
	  
   return given_flags, removed_flags
####################################################################################

####################################################################################
# Hook for modifying new graph edges and nodes.                                    #
####################################################################################
def post_graph_modification(graph, add_edge_list, add_node_list, run_name):
    pass # Do nothing
####################################################################################



####################################################################################
# Initialize the graph with attributes that are necessary to run a simulation.     #
# Takes a graph and a String node (i.e., 'n10') to initialize as flagged.          #
# Also initializes uninitialized weights on graphs as 1.                           #
####################################################################################
def init(graph, node):
   # Let the user know what node is the starting node.
   if (defaults.LOGGING or defaults.DEBUG or defaults.defaults.DEBUG_SEVERE):
      print '\n' + '*' * defaults.asterisk_space_count + '\nInitializing graph - \'' + str(node) + '\' is in the know.'

   # Give all nodes a false flag
   helper.create_node_attribute(graph, 'flagged', False)
   
   # Save edge weight, as we are going to wipe graph
   dict = nx.get_edge_attributes(graph, 'weight')
   
   # Write 1 weight to all edges
   nx.set_edge_attributes(graph, 'weight', 1)
   
   # Restore initial edges
   for n1,n2 in dict:
      graph.edge[n1][n2]['weight'] = dict[n1,n2]
   
   
   # Set an arbitrary node
   graph.node[node]['flagged'] = True
####################################################################################

   
####################################################################################
# Determines whether or not a graph is finished.                                   #
####################################################################################
def finished_hook(graph, current_round, run_name):
   # Get all attributes and store them in a dictionary
   dict = nx.get_node_attributes(graph, 'flagged')
   
   # Make sure we haven't hit the maximum allowed round
   if (current_round > maximum_allowed_simulation_rounds):
      return -1 # -1 means we ran out of allowed rounds
   

   # Iterate the nodes and see if they're flagged or not 
   for val in dict:
      if(not dict[val]):
         #print '[' + val  + ']: ' + str(dict[val])
         if (helper.num_flagged(graph, 'flagged') > 0):
            return 0
         else:
            return -1
   return 1 # 1 is a successful graph
####################################################################################



####################################################################################
# Determines whether or not a graph is finished.                                   #
####################################################################################
def on_finished_run(graph, finish_code, round_num, num_flags, run_name, total_time_seconds):
   if (finish_code == 1): # If we've finished the graph
      return round_num,num_flags
   else:
      return -1,num_flags # Sim Engine expects -1 to indicate a failure
####################################################################################



####################################################################################
'''
Hook for dealing with data across a simulation on the given graph. Specifically, this
was designed for dealing with looking at differences across the whole simulation.
    Args:
        num_runs: The number of runs in a given simulation.
        graphs: A list of graphs which correspond to the finished graph for each run
                in the simulation.
        sim_name: The name of the simulation.
'''
####################################################################################
def on_finished_simulation(num_runs, graphs, sim_name):
    pass
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
def heartbeat(current_time, last_heartbeat, round_num, run_name):
   print '[' + str(current_time) + ']: ' + str(run_name) + ' still alive. Last update was ' \
         + str(last_heartbeat) + ' seconds ago.'
####################################################################################