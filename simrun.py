import networkx as nx

# External dependencies
import sim
import defaults
import simround as round



####################################################################################
# A single run of a simulation                                                     #
####################################################################################
def run(graph, max_weight, max_allowed_rounds, 
        talk_to_transmit=defaults.talk_to_transmit,
        transmit_chance=defaults.transmit_chance,
        spontaneous_forget=defaults.spontaneous_forget,
        spontaneous_forget_chance=defaults.spontaneous_forget_chance,
        spontaneous_acquisition=defaults.spontaneous_acquisition,
        spontaneous_acquisition_chance=defaults.spontaneous_acquisition_chance):
   # Declare data to gather
   round_num = 0
   num_flags = num_flagged(graph)
   # print 'Total nodes: ' + str(len(graph.node))
   # TODO: Variable finished condition for easy hook mod
   # Run loop
   
   while(finished(graph, round_num, max_allowed_rounds) == 0):
      round_num += 1

      # Run the round and return the number of successes and add it to the total_successes
      #print round_num #
      num_flags += round.round(graph, round_num, max_weight) # Assumes global variables in sim.py

   # Check why we quit the simulation
   if (finished(graph, round_num, max_allowed_rounds) > 0): # If we've finished the graph
      return round_num,num_flags
   else:
      return -1,num_flags # Fail code
####################################################################################



####################################################################################
# Determines whether or not a graph is finished                                    #
####################################################################################
def finished(graph, current_round, max_allowed_rounds):
   # Get all attributes and store them in a dictionary
   dict = nx.get_node_attributes(graph, 'flagged')
   
   # Make sure we haven't hit the maximum allowed round
   if (current_round > max_allowed_rounds):
      return -1 # -1 means we ran out of allowed rounds
   
   # Iterate the nodes and see if they're flagged or not 
   for val in dict:
      if(not dict[val]):
         #print '[' + val  + ']: ' + str(dict[val])
         return 0 # 0 is an incomplete graph
   return 1 # 1 is a successful graph


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