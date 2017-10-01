import copy
import networkx as nx
import random as rand

import sim


####################################################################################
# A step in the simulation                                                         #
####################################################################################
def round(graph, round_num, max_weight):
   graphcopy = copy.deepcopy(graph)
   given_flags = 0
   forgot_flags = 0
   for n in nx.nodes(graph):
      # So directed graphs work as well as undirected graphs, consider flagged only
	  # Check graphcopy for the flag - if we check graph, we will have leaking
      if (graphcopy.node[n]['flagged']):
         
         # Node forgetting
         if (sim.can_node_forget):
            if (sim.chance(sim.node_forget_chance)):
                # Wipe flag from both graph and graphcopy
                graph.node[n]['flagged'] = False
                graphcopy.node[n]['flagged'] = False
                forgot_flags += 1
                continue # Skip this node because it no longer has a flag

         # Check the unedited copy graph for flagged neighbors
         for g in graphcopy.edge[n]:
            # If the graph node in both the copy and original aren't flagged
            if (not graphcopy.node[g]['flagged'] and not graph.node[g]['flagged']):

			   #############################DEBUG##########################################
               if (sim.DEBUG_SEVERE):
                  print '[DEBUG]: graph and graphcopy of node ' + str(g) +  ' unflagged...'
               ############################################################################

               # If the simulation will actually spread, then spread
               if (will_spread(n, g, graph, max_weight)):
                  graph.node[g]['flagged'] = True		  
                  # Increment the number of given_flags this round
                  given_flags += 1

               ##################DEBUG#######################
               if (sim.DEBUG_SEVERE):
                  print '[DEBUG]: ...flagged node ' + str(g)
               ##############################################

            # More debug
            elif (sim.DEBUG_SEVERE): # Output no change has been made
               print '[DEBUG]: ...no action taken.'
   return given_flags-forgot_flags # TODO: return forgot flags and given flags
####################################################################################



####################################################################################
# Determine if a given source node will transmit information to a given node       #
####################################################################################
def will_spread(source, dest, graph, max_weight):
   # TODO: Add more dynamic way to spread flags from nodes to nodes
   
   # Get current weight
   curr_weight = graph.edge[source][dest]['weight']
   
   # Will they engage at all? This consults the weight of their edge
   if ( roll_weight (curr_weight , max_weight ) ):
      if (sim.talkToTransmit):
          return True
      else:
         # This is the chance that their engagement will exchange information
         if (sim.chance(chance_to_spread)):
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