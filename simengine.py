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


import argparse         # Parse command line args
import copy             # For copying graphs
import networkx as nx   # GraphML
import random as rand
import datetime


# Simulation setup
import simdefaults as defaults
import simhelper as helper
import iot_spy as config
# Replace ^ that argument for different simulations




####################################################################################
'''
Program entry point.
'''
####################################################################################
def main():

    if (defaults.display_banner):
        display_banner()
    config.simulation_driver()
####################################################################################



####################################################################################
def display_banner():
    # Banner from http://patorjk.com/software/taag/
    print '______          _           _  ______                          ___  ____ _ _'
    print '| ___ \        (_)         | | | ___ \                         |  \/  (_) | |'
    print '| |_/ / __ ___  _  ___  ___| |_| |_/ /   _ _ __ ___   ___  _ __| .  . |_| | |'
    print '|  __/ \'__/ _ \| |/ _ \/ __| __|    / | | | \'_ ` _ \ / _ \| \'__| |\/| | | | |'
    print '| |  | | | (_) | |  __/ (__| |_| |\ \ |_| | | | | | | (_) | |  | |  | | | | |'
    print '\_|  |_|  \___/| |\___|\___|\__\_| \_\__,_|_| |_| |_|\___/|_|  \_|  |_/_|_|_|'
    print '              _/ |'
    print '             |__/'
    print '                               Emily Hannah, Tianjian Meng, Julian Monticelli'
    if (defaults.pause_after_display):
        helper.sleep_ms(defaults.pause_sleep_time_ms)
####################################################################################



####################################################################################
'''
Simulation function, which will run as many instances of the same simulation with the
same starting graph as desired, in order to curb randomness.
    Args:
        graph: A networkx graph instance.
        num_simulations: An integer indicating how many time we want to run in this execution.
        sim_name: A string that describes the current simulation
'''
####################################################################################
def simulate(graph, num_simulation_runs, sim_name):
    current_simulation_run = 1
    graphs_list = []
    while (current_simulation_run <= num_simulation_runs):
        # Correct simulation run information
        current_simulation_run += 1
        run_name = sim_name + '_r' + str(current_simulation_run)
        
        # Copy the graph given to the simulation
        graph_instance = copy.deepcopy(graph)
        
        # Run graph until completion
        run(graph_instance, run_name)
        
        # Append a frozen graph to preserve data without mutation
        graphs_list.append(graph_instance)
        
    # When we are finished with the simulation, send the graphs to collect data
    config.on_finished_simulation(num_simulation_runs, graphs_list, sim_name)
####################################################################################




####################################################################################
'''
A single run of a simulation.
    Args:
        graph: A networkx graph instance.
        run_name: The name of the run
'''
####################################################################################
def run(graph, run_name):
    round_num = 0

    last_timestamp = 0
    start_timestamp = 0
    
    start_timestamp = helper.date_time()
    last_timestamp = start_timestamp

    print '[' + str(last_timestamp) + ']' ': Beginning simulation run ' + str(run_name) + '...'
    
    while(not config.finished_hook(graph, round_num, run_name)):
        # Increment round number
        round_num += 1

	  # Get time difference determine if a heartbeat is necessary
        now = helper.date_time()
        last_heartbeat = helper.time_diff(now, last_timestamp)
        if (last_heartbeat >= config.heartbeat_interval):
            last_timestamp = now
            config.heartbeat(now, last_heartbeat, round_num, run_name)
        
	  # Run the round
        round(graph, round_num, run_name)

    # Check why we quit the simulation
    finish_code = config.finished_hook(graph, round_num, run_name)
    
    # Calculate the amount of time that the run took
    total_time_seconds = helper.time_diff(start_timestamp, helper.date_time())
    
    # Pass along frozen graph and relevant information to the on_finished_run hook
    nx.freeze(graph)
    config.on_finished_run(graph, finish_code, round_num, run_name, total_time_seconds)
####################################################################################



####################################################################################
'''
A step in the simulation.
    Args:
        graph: A networkx graph instance.
        run_name: The name of the run
'''
####################################################################################
def round(graph, round_num, run_name):
    # Declare empty list for graph changes
    add_node_list = []
    remove_node_list = []
    add_edge_list = []
    remove_edge_list = []
    
    # Deal with potential before-round graph changes 
    config.before_round_start(graph, add_edge_list, remove_edge_list, add_node_list, remove_node_list, round_num, run_name)

    # Perform graph changes, if there are any
    helper.modify_graph(graph, add_edge_list, remove_edge_list, add_node_list, remove_node_list)

    # Fix edge attributes as config deems necessary
    config.post_graph_modification(graph, add_edge_list, add_node_list, run_name)
    
    add_node_list = []
    remove_node_list = []
    add_edge_list = []
    remove_edge_list = []

    # Deep copy graph after pre-round graph changes
    graph_copy = helper.copy_graph(graph)

    for node in nx.nodes(graph):
        config.on_node(graph, graph_copy, node, round_num, run_name)

    # Deal with potential post-round graph changes 
    config.after_round_end(graph, add_edge_list, remove_edge_list, add_node_list, remove_node_list, round_num, run_name)

    # Fix node attributes as config deems necessary
    # Also, any reconsiderations 
    config.post_graph_modification(graph, add_edge_list, add_node_list, run_name)

    # Perform graph changes, if there are any
    helper.modify_graph(graph, add_edge_list, remove_edge_list, add_node_list, remove_node_list)
####################################################################################



###########################
# END OF FUNCTIONS.       #
###########################
if __name__ == "__main__":
    main()
#######i####################	
