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
# Julian xMonticelli
#######################

###############
# Important!! #
# Whitespace! #
# -> 3 spaces #
###############


import argparse         # Parse command line args
import copy             # For copying graphs
import networkx as nx   # GraphML




num_runs = 100       # Default number of runs


def main():
   # Program args stuff
   # goes here later
   simulation_graph = nx.read_graphml('test.graphml')
   nx.set_node_attributes(simulation_graph, 'flagged', False)
   simulation_graph.node['n1']['flagged'] = True
   runstospread = run(simulation_graph)
   print 'Took ' + runstospread + ' to spread to the whole graph'



def run(graph):
   # Declare data to gather
   num_rounds = 0

   # Run loop
   while(not finished(graph)):
      num_rounds += 1
      round(graph, round_num)
   return num_rounds



def round(graph, round_num):
   graphcopy = deepcopy(graph)
   for n in nx.nodes(graph):
      
      # n is already flagged - skip
      if (n['flagged'] == True):
         continue

      # Check the unedited copy graph for flagged neighbors
      for g in nx.all_neighbors(graphcopy, n):
         if (g['flagged'] == True):
            print 'Iteration for ' + g + ' which is flagged'
            

def finished(graph):
   for n in nx.nodes(graph):
      if(n['flagged'] == False):
         return false
   return true


class Node:
   flagged = False

###########################
if __name__ == "__main__":
   main()
###########################
