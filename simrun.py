import networkx as nx

# External dependencies
import sim
import defaults
import simround as round




####################################################################################
# A single run of a simulation                                                     #
####################################################################################
def run(
        graph, max_weight, max_allowed_rounds, 
        talk_to_transmit=defaults.talk_to_transmit,
        transmit_chance=defaults.transmit_chance,
        spontaneous_forget=defaults.spontaneous_forget,
        spontaneous_forget_chance=defaults.spontaneous_forget_chance,
        spontaneous_acquisition=defaults.spontaneous_acquisition,
        spontaneous_acquisition_chance=defaults.spontaneous_acquisition_chance
       ):
   # Declare data to gather
   round_num = 0
   num_flags = num_flagged(graph)
   # print 'Total nodes: ' + str(len(graph.node))
   # TODO: Variable finished condition for easy hook mod
   # Run loop
   
   while(finished(graph, round_num, max_allowed_rounds) == 0):
      round_num += 1

      # Run the round and return the number of successes and add it to total_successes
      num_flags += round.round(graph, round_num, max_weight)

   # Check why we quit the simulation
   if (finished(graph, round_num, max_allowed_rounds) > 0): # If we've finished the graph
      return round_num,num_flags
   else:
      return -1,num_flags # Fail code
####################################################################################



####################################################################################
# Determines whether or not a graph is finished.                                   #
####################################################################################
def finished(
             graph, current_round, max_allowed_rounds,
			 finished_includes_max_subgraph_spread=defaults.finished_includes_max_subgraph_spread,
             spontaneous_acquisition = defaults.spontaneous_acquisition,
			 spontaneous_acquisition_chance = defaults.spontaneous_acquisition_chance
            ):
   # Get all attributes and store them in a dictionary
   dict = nx.get_node_attributes(graph, 'flagged')
   
   # Make sure we haven't hit the maximum allowed round
   if (current_round > max_allowed_rounds):
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
            if (num_flagged(graph) > 0):
               return 0
            else:
               return -1
      return 1 # 1 is a successful graph


####################################################################################



####################################################################################
# Subgraph completion check, takes only a graph argument.                          #
####################################################################################
# Subgraph stuff
def check_subgraph_spread(graph):
   if (subgraph_max_spread(graph)):
      return 1
   else:
      if (num_flagged(graph) > 0):
         return 0 # We've finished the graph, as best we could.
      else:
         return -1 # We have 0 infected nodes. Graph failed.
####################################################################################



####################################################################################
# Determines whether or not a graph is finished by considering subgraph spread.    #
# May run into problems if directed graphs are ever considered.                    #
####################################################################################
def subgraph_max_spread(g):
   graphs = list(nx.connected_component_subgraphs(g, copy=True))
   num_subgraphs = len(graphs)
   graphs_max_spread = 0
   graphs_partial_spread = 0
   for graph in graphs:
      all_flagged = True
      has_any_flag = False
      for node in graph.node:
         if not graph.node[node]['flagged']:
            all_flagged = False
         else:
            has_any_flag = True
      if (all_flagged):
         graphs_max_spread += 1
      elif (has_any_flag == True):
         graphs_partial_spread += 1

   if graphs_max_spread >= 1 and graphs_partial_spread == 0:
      return True
   else:
      return False
####################################################################################



####################################################################################
# Returns an integer value with the number of flagged nodes                        #
####################################################################################
def num_flagged(graph):
   num_flagged = 0
   nodes = nx.get_node_attributes(graph, 'flagged')
   for val in nodes:
      if (nodes[val]):
         num_flagged += 1
   return num_flagged
####################################################################################