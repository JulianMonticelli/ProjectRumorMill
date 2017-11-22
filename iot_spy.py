# Python Library Packages
import networkx as nx
import random as rand
import sys
import copy
import csv

# Cyclical dependency to main
import simengine as engine # < Driver in config requires this
import simhelper as helper
import simdefaults as defaults


#######################
# Simulation arguments#
#######################
#IS_SIM_GAME = True
SIM_DEBUG = True


#######################
# Global data         #
#######################

val_total = 0
val_min = float('inf')
val_max = float('-inf')


####################################################################################
'''
Simulation driver, which will call the engine to begin simulations. Setup should
happen in this method, and data collection should be done inside any method necessary.
A logically sound place to put data processing is at the end of this method.
'''
####################################################################################
def simulation_driver():
    # Read in a CSV for a graph and 
    helper.output_graph_information(graph)
    num_nodes = helper.num_nodes(graph)

    # Start from every node in the graph
    for n in graph.node:
        sim_name = 'zsim_' + str(n)
        graphcopy = copy.deepcopy(graph)
        init(graphcopy, n, sim_name)
        engine.simulate(graphcopy, num_runs, sim_name)

####################################################################################



####################################################################################
'''
For every node, perform an action.
   Args:
      graph: A networkx graph instance.
      graph_copy: Another networkx graph instance which is the deep copy of graph.
      node: A networkx node instance.
      max_weight: An integer which is the max weight of edges in this graph.
      run_name: The name of the current run
'''
####################################################################################
def iot_graph(__csvfile__, range_of_router):
    # New graph
    g = nx.Graph()
   
   # Open csvfile in rb mode
    csvfile = open(__csvfile__, 'rb')
   
    # Create attributes for the csv file
    csv_fields = ['node_name', 'x', 'y', 'z']
    
    # Create a csv
    csv_reader = csv.DictReader(csvfile, fieldnames=csv_fields)
    
    print csv_reader
    for row in csv_reader:
        g.add_node(row['node_name'])
        g.node[row['node_name']]['x'] = row['x']
        g.node[row['node_name']]['y'] = row['y']
        g.node[row['node_name']]['z'] = row['z']
        print row['node_name'] + ' ' + row['x'] + ' ' + row['y'] + ' ' + row['z']
        
    csvfile.close()
        
    import math
    for node in g:
        for node2 in g:
            if node is not node2:
                distance = math.sqrt(
                                     (float(g.node[node]['x']) - float(g.node[node2]['x']))**2
                                    +(float(g.node[node]['y']) - float(g.node[node2]['y']))**2
                                    +(float(g.node[node]['z']) - float(g.node[node2]['z']))**2
                                    )
                if (distance <= range_of_router):
                    g.add_edge(node, node2)
    
    
    return g
####################################################################################



####################################################################################
'''
For every node, deal with the transmission of information.
   Args:
      graph: A networkx graph instance.
      graph_copy: Another networkx graph instance which is the deep copy of graph.
      node: A networkx node instance.
      max_weight: An integer which is the max weight of edges in this graph.
      run_name: The name of the current run
'''
####################################################################################
def on_node(graph, graph_copy, node, max_weight, run_name):
    noop = 0 # NOOP
####################################################################################



####################################################################################
'''
Determines if information transfer occurs from a broadcast.
    Args:
      source: A networkx node instance which is the source node in this transmission.
      dest: Another networkx node instance which is the destination node in this transmission.
      graph: A networkx graph instance.
      max_weight: An integer which is the max weight of edges in this graph.
      run_name: The name of the current run

   Returns:
      True: If the information is spread in this node operation.
      False: If the information isn't spread in this node operation.
'''
####################################################################################
def will_spread(source, dest, graph, max_weight, run_name):
    # TODO: Add more dynamic way to spread flags from nodes to nodes
    noop = 0
####################################################################################



####################################################################################
'''
Hook for changing the graph at the beginning of the round. Note that this takes place
before the graph is copied in the engine.
   Args:
      graph: A networkx graph instance.
      max_weight: An integer which is the max weight of edges in this graph.
      run_name: The name of the current run 
'''
####################################################################################
def before_round_start(graph, max_weight, add_edge_list, remove_edge_list, run_name):
    noop = 0
####################################################################################



####################################################################################
'''
Hook for fixing edge attributes to freshly added edges.
    Args:
        graph: A networkx graph instance.
        add_edge_list: A list of recently added edges.
        run_name: The name of the current run.
'''
####################################################################################
def post_edge_modification(graph, add_edge_list, run_name):
    noop = 0
####################################################################################



####################################################################################
'''
Hook for dealing with addition/removal of nodes at the end of a round.
   Args:
      graph: A networkx graph instance.
      add_node_list: A list of nodes to be added
      remove_node_list: A list of nodes to be removed
      run_name: The name of the current run
'''
####################################################################################
def after_round_end(graph, add_node_list, remove_node_list, run_name):
    noop = 0
####################################################################################



####################################################################################
'''
Hook for fixing edge attributes to freshly added edges.
    Args:
        graph: A networkx graph instance.
        add_edge_list: A list of recently added edges.
        run_name: The name of the current run.
'''
####################################################################################
def post_node_modification(graph, add_node_list, run_name):
   for n in add_node_list:
      noop = 0 # placeholder - there is no node addition
####################################################################################



####################################################################################
'''
Init method. This has been wiped, because initialization can mean many things.
The IOT graph is constructed at the beginning, so initialization may be entirely
different or not used at all.
   Args:
      graph: A networkx graph instance.
      node: A networkx node instance.
      sim_name: The name of the current simulation
'''
####################################################################################
def init(graph, node, sim_name):
    noop = 0
####################################################################################

   
####################################################################################
'''
Determines whether or not a graph is finished.
   Args:
      graph: A networkx graph instance.
      current_round: An integer recording the current number of rounds.
      max_allowed_rounds: An integer which is set to be the max allowed number of rounds.
      run_name: The name of the current simulation run
	  
   Returns:
      0: If there is still information to be broadcasted
      1: If the information has been broadcasted to all nodes
'''
####################################################################################
def finished_hook(graph, current_round, max_allowed_rounds, run_name):
    noop = 0
####################################################################################



####################################################################################
'''
Hook for finishing the simulation run on the current graph.
   Args:
      finish_code: -1, 1, 2, or 3 depending on the finish code we return in finished_hook function.
      round_num: An integer showing how many round we use to finish the graph if succeed.
      num_flags: An integer showing how many nodes are flagged in the end.
      run_name: The name of the current simulation run
'''
####################################################################################
def on_finished(graph, finish_code, round_num, run_name, total_time_seconds):
    noop = 0
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
