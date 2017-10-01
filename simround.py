import copy
import networkx as nx

import sim


####################################################################################
# A step in the simulation                                                         #
####################################################################################
def round(graph, round_num, max_weight):
   graphcopy = copy.deepcopy(graph)
   given_flags = 0
   forgot_flags = 0
   for n in nx.nodes(graph):
      # For directed graphs, consider flagged only
      if (graph.node[n]['flagged']):
         
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
               if (sim.will_spread(n, g, graph, max_weight)):
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