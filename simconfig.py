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
maximum_allowed_simulation_rounds = 100 # Max amount of rounds before we stop running a simulation
num_runs = 3      # Default number of runs per simulation

# Transmission variables
talk_to_transmit = True   # Transmission = just talking?
transmit_chance = 0.20 # If transmit =/= talk, what is the chance upon talking

# Forgetting variables
spontaneous_forget = True          # Node can forget
spontaneous_forget_chance = 0.01      # Chance for node to forget

# Spontaneous acquisition
spontaneous_acquisition = True  # Nodes can spontaneously become flagged
spontaneous_acquisition_chance = 0.01

#######################
# Round options       #
#######################

# Whether or not a graph is considered finished if,
# when spontaneous acquisition is not occurring,
# information has spread to all nodes that can become
# spread to.
finished_includes_max_subgraph_spread=True


def simulation_driver():
   
   # Read in a graph
   graph = nx.read_graphml('simplemodel.graphml')
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
      flagged, max_flags, sum_rounds, num_fails = engine.simulate(graphcopy, num_runs)
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



####################################################################################
# Hook for considering a node in the graph.                                        #
####################################################################################
def on_node(graph, graph_copy, node, max_weight):
   given_flags = 0
   removed_flags = 0
   if(will_forget(graph, graph_copy, node, 'flagged', spontaneous_forget, spontaneous_forget_chance)):
      removed_flags += 1 # Update amount of forgotten flags
      return given_flags, removed_flags
      # IMPORTANT: So that directed graphs work as well as undirected graphs, consider flagged only
      # Check graph_copy for the flag - if we check graph, we will have leaking
   if (graph_copy.node[node]['flagged']):
      given_flags += on_flagged(graph, graph_copy, node, max_weight)

      # If the node does not know, and we can spontaneously come into knowing
   else:
      given_flags += on_not_flagged(graph, graph_copy, node, spontaneous_acquisition, spontaneous_acquisition_chance)
   return given_flags, removed_flags
####################################################################################



####################################################################################
# Runs operations on a flagged node to determine if it will transmit information.  #
####################################################################################
def on_flagged(graph, graph_copy, node, max_weight,
               talk_to_transmit=talk_to_transmit,
               transmit_chance=transmit_chance
               ):
   given_flags = 0
   
   # Debug
   if (defaults.DEBUG_SEVERE):
      print '[defaults.DEBUG]: Node ' + str(node) + ' is flagged.'

   # Check the unedited copy graph for flagged neighbors
   for neighbor in graph_copy.edge[node]:
      # If a target graph node in both the copy and original aren't flagged
      if (not graph_copy.node[neighbor]['flagged'] and not graph.node[neighbor]['flagged']):
         # Debug
         if (defaults.DEBUG_SEVERE):
            print '[defaults.DEBUG]: Neigbor ' + str(neighbor) +  ' unflagged - ',
         # If the simulation will actually spread, then spread
         if (will_spread(node, neighbor, graph, max_weight, talk_to_transmit, transmit_chance)):
            graph.node[neighbor]['flagged'] = True
			
            # Increment the number of given_flags this round
            given_flags += 1

            # Debug output that we flagged
            if (defaults.DEBUG_SEVERE):
               print 'flagged node ' + str(neighbor) + '.'

         # If we cannot acquire...
         if (defaults.DEBUG_SEVERE): # Output no change has been made
            print 'no action taken.'
   return given_flags			
####################################################################################



####################################################################################
# Currently will only check whether or not spontaneous acquisition will occur.     #
####################################################################################
def on_not_flagged(graph, graph_copy, node,
                   spontaneous_acquisition=spontaneous_acquisition,
                   spontaneous_acquisition_chance=spontaneous_acquisition_chance
                   ):
   if (will_spontaneously_acquire(graph, graph_copy, node, 'flagged', True, spontaneous_acquisition)):
      return 1 # We have made a positive difference in this graph by one
   return 0 # No change
####################################################################################



####################################################################################
# Performs a roll for a node that is in the know to determine whether or not an    #
# agent should lose a flag, and if so, updates the graph accordingly.              #
####################################################################################
def will_forget(graph, graph_copy, node, attr, spontaneous_forget, spontaneous_forget_chance, forget_value=False):
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
# Performs a roll for a node that is not in the know to determine whether or not   #
# an agent should gain a flag, and if so, updates the graph accordingly.           #
####################################################################################
def will_spontaneously_acquire(
                               graph, graph_copy, node, attr, acquisition_value,
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
# Determine if a given source node will transmit information to a given node       #
####################################################################################
def will_spread(
                source, dest, graph, max_weight,
                talk_to_transmit=talk_to_transmit,
				transmit_chance=transmit_chance
               ):
   # TODO: Add more dynamic way to spread flags from nodes to nodes
   
   # Get current weight
   curr_weight = graph.edge[source][dest]['weight']
   
   # Will they engage at all? This consults the weight of their edge
   if ( helper.roll_weight (curr_weight , max_weight ) ):
      if (talk_to_transmit):
          return True
      else:
         # This is the chance that their engagement will exchange information
         if (helper.chance(transmit_chance)):
            return True
   return False
####################################################################################



####################################################################################
# Hook for changing the graph at the beginning of the round. Note that this takes  #
# place before the graph is copied in the engine.                                  #
####################################################################################
def before_round_start(graph, max_weight):
   #for edge in graph.edge:
      # do something
   return
####################################################################################



####################################################################################
# Hook for considering a node in the graph.                                        #
####################################################################################
def after_round_end(graph):
   given_flags = 0
   removed_flags = 0
   
   #for edge in graph.edge:
      # do something
	  
   return given_flags, removed_flags
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
def finished_hook(
             graph, current_round, max_allowed_rounds
            ):
   # Get all attributes and store them in a dictionary
   dict = nx.get_node_attributes(graph, 'flagged')
   
   # Make sure we haven't hit the maximum allowed round
   if (helper.exceeded_round_limit(current_round, max_allowed_rounds)):
      return -1 # -1 means we ran out of allowed rounds
   
   
   if (
       (spontaneous_acquisition == False or spontaneous_acquisition_chance <= 0)
       and 
       finished_includes_max_subgraph_spread == True
	  ):
      return check_subgraph_spread(graph)
   else:
      # Iterate the nodes and see if they're flagged or not 
      for val in dict:
         if(not dict[val]):
            #print '[' + val  + ']: ' + str(dict[val])
            if (helper.num_flagged(graph) > 0):
               return 0
            else:
               return -1
      return 1 # 1 is a successful graph
####################################################################################



####################################################################################
# Determines whether or not a graph is finished.                                   #
####################################################################################
def on_finished(finish_code, round_num, num_flags):
   if (finish_code == 1): # If we've finished the graph
      return round_num,num_flags
   else:
      return -1,num_flags # Sim Engine expects -1 to indicate a failure
####################################################################################
