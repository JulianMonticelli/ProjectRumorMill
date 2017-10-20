#!/usr/bin/env python

#######################
# PROJECT RUMOR MILL
# ==================
# Project Director:
# Michael Bigrigg
# 
# Team Members:
# Emily Hannah
# Tianjian Meng
# Julian Monticelli
#######################

###############
# Important!! #
# Whitespace! #
# -> 3 spaces #
###############


import argparse         # Parse command line args
import copy             # For copying graphs
import networkx as nx   # GraphML
import random as rand

# Simulation setup
import simhelper as helper
import simconfig as config
import simdefaults as defaults
# Replace ^ that argument for different simulations

####################################################################################
# Program entry point. Setup, etc.                                                 #
####################################################################################
def main():
   # Config is responsible for the simulation_driver
   config.simulation_driver()

####################################################################################



####################################################################################
# Simulation function - to be changed and altered. Highly volatile.                #
####################################################################################
def simulate(graph, num_simulations):
   weight_max = helper.max_weight(graph)
   sum_time = 0
   num_fails = 0
   current_run = 1
   total_flagged = 0
   
   while (current_run <= num_simulations):
      graph_instance = copy.deepcopy(graph)
      run_time,num_flagged = run(graph_instance, weight_max, config.maximum_allowed_simulation_rounds)
      total_flagged += num_flagged
	  
	  # WARNING: Incomplete graphs return -1, so no sum_time is added
      if (run_time < 0):
         if (defaults.LOGGING or defaults.DEBUG or defaults.DEBUG_SEVERE):
            print 'Run ' + str(current_run) + ' failed to spread across graph! ' + str(num_flagged) + '/' + str(len(graph.node)) + ' flagged. (' + str(helper.percent_flagged(graph, num_flagged)) + '% complete)'
         num_fails += 1
      else:
         if (defaults.LOGGING or defaults.DEBUG or defaults.DEBUG_SEVERE):
            print 'Run ' + str(current_run) + ' took ' + str(run_time) + ' rounds. ' + str(num_flagged) + '/' + str(len(graph.node)) + ' flagged. (' + str(helper.percent(num_flagged, len(graph.node))) + '% complete)'
         sum_time += run_time

      current_run += 1
   if (num_simulations == num_fails): # Avoid division by 0
      print 'All runs failed. maximum_allowed_simulation_rounds = ' + str(config.maximum_allowed_simulation_rounds) + ' (Average completion rate: ' + str(helper.total_percent_flagged(graph, total_flagged, num_simulations)) + '%)'
   else:
      print str(num_simulations) + ' simulations finished. ' + str(num_fails) + ' simulations failed. Average run time: ' + str(sum_time/ (num_simulations - num_fails) ) + ' rounds'
      print 'Average completion rate: ' + str(helper.total_percent_flagged(graph, total_flagged, num_simulations)) + '%)'

   return total_flagged, len(graph.node) * num_simulations, sum_time, num_fails
####################################################################################




####################################################################################
# A single run of a simulation                                                     #
####################################################################################
def run(
        graph, max_weight, max_allowed_rounds
       ):

   # Declare data to gather
   round_num = 0
   num_flags = helper.num_flagged(graph)

   # print 'Total nodes: ' + str(len(graph.node))
   # TODO: Variable finished condition for easy hook mod
   # Run loop
   
   while(config.finished(graph, round_num, max_allowed_rounds) == 0):
      round_num += 1

      # Run the round and return the number of successes and add it to total_successes
      num_flags += round(graph, round_num, max_weight)

   # Check why we quit the simulation
   if (config.finished(graph, round_num, max_allowed_rounds) > 0): # If we've finished the graph
      return round_num,num_flags
   else:
      return -1,num_flags # Fail code
####################################################################################



####################################################################################
# A step in the simulation                                                         #
####################################################################################
def round (
          graph, round_num, max_weight
          ):
		  
   config.before_round_start(graph) # DOES NOT alter max_weight!
   
   graph_copy = copy.deepcopy(graph)
   
   given_flags = 0
   removed_flags = 0
   
   for node in nx.nodes(graph):
      delta_given_flags, delta_removed_flags = config.on_node(graph, graph_copy, node, max_weight)
      given_flags += delta_given_flags
      removed_flags += delta_removed_flags
	  
   config.after_round_end(graph)
   
   return given_flags-removed_flags # TODO: return forgot flags and given flags?
####################################################################################



###########################
# END OF FUNCTIONS.       #
###########################
if __name__ == "__main__":
   main()
#######i####################
