import copy
import networkx as nx
import random as rand

import sim
import defaults


####################################################################################
# A step in the simulation                                                         #
####################################################################################
def round (
          graph, round_num, max_weight,
          talk_to_transmit=defaults.talk_to_transmit, transmit_chance=defaults.transmit_chance,
		  spontaneous_forget=defaults.spontaneous_forget,
		  spontaneous_forget_chance=defaults.spontaneous_forget_chance,
		  spontaneous_acquisition=defaults.spontaneous_acquisition,
		  spontaneous_acquisition_chance=defaults.spontaneous_acquisition_chance
          ):
   graph_copy = copy.deepcopy(graph)
   given_flags = 0
   forgot_flags = 0
   for node in nx.nodes(graph):
      if(will_forget(graph, graph_copy, node, 'flagged', spontaneous_forget, spontaneous_forget_chance)):
         forgot_flags += 1 # Update amount of forgotten flags
         # If this node forgets, skip iterating its edges
         continue
			
      # IMPORTANT: So that directed graphs work as well as undirected graphs, consider flagged only
	  # Check graph_copy for the flag - if we check graph, we will have leaking
      if (graph_copy.node[node]['flagged']):
         given_flags += on_flagged(graph, graph_copy, node, max_weight)

      # If the node does not know, and we can spontaneously come into knowing
      else:
		given_flags += on_not_flagged(graph, graph_copy, node, spontaneous_acquisition, spontaneous_acquisition_chance)


   return given_flags-forgot_flags # TODO: return forgot flags and given flags?
####################################################################################



####################################################################################
# Runs operations on a flagged node to determine if it will transmit information.  #
####################################################################################
def on_flagged(graph, graph_copy, node, max_weight,
               talk_to_transmit=defaults.talk_to_transmit,
               transmit_chance=defaults.transmit_chance
               ):
   given_flags = 0
   
   # Debug
   if (sim.DEBUG_SEVERE):
      print '[DEBUG]: Node ' + str(node) + ' is flagged.'

   # Check the unedited copy graph for flagged neighbors
   for neighbor in graph_copy.edge[node]:
      # If a target graph node in both the copy and original aren't flagged
      if (not graph_copy.node[neighbor]['flagged'] and not graph.node[neighbor]['flagged']):
         # Debug
         if (sim.DEBUG_SEVERE):
            print '[DEBUG]: Neigbor ' + str(neighbor) +  ' unflagged - ',
         # If the simulation will actually spread, then spread
         if (will_spread(node, neighbor, graph, max_weight, talk_to_transmit, transmit_chance)):
            graph.node[neighbor]['flagged'] = True
			
            # Increment the number of given_flags this round
            given_flags += 1

            # Debug output that we flagged
            if (sim.DEBUG_SEVERE):
               print 'flagged node ' + str(neighbor) + '.'

         # If we cannot acquire...
         if (sim.DEBUG_SEVERE): # Output no change has been made
            print 'no action taken.'
   return given_flags			
####################################################################################


####################################################################################
# Currently will only check whether or not spontaneous acquisition will occur.     #
####################################################################################
def on_not_flagged(graph, graph_copy, node,
                   spontaneous_acquisition=defaults.spontaneous_acquisition,
                   spontaneous_acquisition_chance=defaults.spontaneous_acquisition_chance
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
      if (sim.chance(spontaneous_forget_chance)):
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
                               spontaneous_acquisition=defaults.spontaneous_acquisition,
							   spontaneous_acquisition_chance=defaults.spontaneous_acquisition_chance
                              ):
   if (spontaneous_acquisition and graph.node[node][attr] != acquisition_value):
      if (sim.chance(spontaneous_acquisition_chance)):
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
                talk_to_transmit=defaults.talk_to_transmit,
				transmit_chance=defaults.transmit_chance
               ):
   # TODO: Add more dynamic way to spread flags from nodes to nodes
   
   # Get current weight
   curr_weight = graph.edge[source][dest]['weight']
   
   # Will they engage at all? This consults the weight of their edge
   if ( roll_weight (curr_weight , max_weight ) ):
      if (talk_to_transmit):
          return True
      else:
         # This is the chance that their engagement will exchange information
         if (sim.chance(transmit_chance)):
            return True
   return False
####################################################################################



####################################################################################
# Rolls a chance that nodes will communicate given the weight of an edge and       #
# a given maximum weight (chance = given/maximum)                                  #
####################################################################################

def roll_weight(curr_weight, max_weight):
   # Returns the likelihood of engagement based on weight of graph nodes
   return rand.randint(1, max_weight) > (max_weight - curr_weight)

####################################################################################