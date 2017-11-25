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

SIM_DEBUG = True

maximum_allowed_simulation_rounds = 15000 # Max amount of rounds before we stop running a simulation

heartbeat_interval = 30

num_runs = 1

max_receiving_transmissions = 1

max_rounds_no_update = 1000

# The amount of extra random integer results 
rand_extra = 3

csv_file = 'iot/p.csv'

radius_step = 5

#######################
# Global data         #
#######################

last_update_round = 0

total_broadcasts_sent = {}
total_broadcasts_received = {}
total_interference_failures = {}

current_broadcasts_sent = {}
current_broadcasts_received = {}
current_interference_failures = {}

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
    
    # First read in a graph with initial
    graph = iot_graph(csv_file)
    
    # Output graph information
    helper.output_graph_information(graph)
    
    # Store number of nodes in graph for later use (possibly)
    num_nodes = helper.num_nodes(graph)
    
    # Initialize total dictionaries
    for node in graph.node:
        total_broadcasts_sent[node] = 0
        total_broadcasts_received[node] = 0
        total_interference_failures[node] = 0

    
    
    # Set up empty dictionaries for current value
    for node in graph.node:
        current_broadcasts_sent[node] = 0
        current_broadcasts_received[node] = 0
        current_interference_failures[node] = 0
    
    # Simulation name will be something like "iot_p_10"
    sim_name = 'iot_' + csv_file[:len(csv_file)-4]
    
    init(graph, sim_name)
    engine.simulate(graph, num_runs, sim_name)

    print 'This is the end of the simulation.'
    for node in graph.node:
        print node + ':'
        print '>Total broadcasts sent       = ' + str(total_broadcasts_sent[node])
        print '>Total broadcasts receieved  = ' + str(total_broadcasts_received[node])
        print '>Total interference failures = ' + str(total_interference_failures[node])
####################################################################################



####################################################################################
'''
Take a CSV file with x,y coordinates and a range for each node and determine 
what nodes will be connected.
    Args:
        __csvfile__: A CSV file passed that we are to read
        range: The maximum broadcast range
'''
####################################################################################
def iot_graph(__csvfile__):
    # New graph
    g = nx.DiGraph()
   
   # Open csvfile in rb mode
    csvfile = open(__csvfile__, 'rb')
   
    # Create attributes for the csv file
    csv_fields = ['node_name', 'x', 'y', 'range']
    
    # Create a csv
    csv_reader = csv.DictReader(csvfile, fieldnames=csv_fields)
    
    csv_data = {}
    
    #print csv_reader
    for row in csv_reader:
        g.add_node(row['node_name'])
        csv_data[row['node_name']] = {}
        csv_data[row['node_name']]['x'] = row['x']
        csv_data[row['node_name']]['y'] = row['y']
        csv_data[row['node_name']]['range'] = row['range']
    #print row['node_name'] + ' ' + row['x'] + ' ' + row['y'] + ' ' + row['range']
    
    csvfile.close()
    
    import math
    for node in g.node:
        for node2 in g.node:
            if node is not node2:
                distance = math.sqrt(
                                     (float(csv_data[node]['x']) - float(csv_data[node2]['x']))**2
                                    +(float(csv_data[node]['y']) - float(csv_data[node2]['y']))**2
                                    )
                if (distance <= csv_data[node]['range']):
                    g.add_edge(node, node2)
    
    
    for node in g.node:
        g.node[node]['online'] = True # Each node should be online at first
        g.node[node]['broadcast_delay'] = 0
        for hasnode in g.node:
            g.node[node]['has_' + hasnode] = False # Every node should not have each other's information
    
    
    # Set broadcast information to None on every edge
    for u in g.edge:
        for v in g.edge[u]:
            g.edge[u][v]['broadcast_information'] = None
            
            
    return g
####################################################################################



####################################################################################
'''
Take a CSV file with x,y,z coordinates and determine what nodes will be connected
given a broadcast range.
    Args:
        __csvfile__: A CSV file passed that we are to read
        range: The maximum broadcast range
'''
####################################################################################
def iot_graph_xyz(__csvfile__, range):
    # New graph
    g = nx.Graph()
   
   # Open csvfile in rb mode
    csvfile = open(__csvfile__, 'rb')
   
    # Create attributes for the csv file
    csv_fields = ['node_name', 'x', 'y', 'z']
    
    # Create a csv
    csv_reader = csv.DictReader(csvfile, fieldnames=csv_fields)
    
    csv_data = {}
    
    #print csv_reader
    for row in csv_reader:
        g.add_node(row['node_name'])
        csv_data[row['node_name']] = {}
        csv_data[row['node_name']]['x'] = row['x']
        csv_data[row['node_name']]['y'] = row['y']
        csv_data[row['node_name']]['z'] = row['z']
    #print row['node_name'] + ' ' + row['x'] + ' ' + row['y'] + ' ' + row['z']
    
    csvfile.close()
    
    import math
    for node in g.node:
        for node2 in g.node:
            if node is not node2:
                distance = math.sqrt(
                                     (float(csv_data[node]['x']) - float(csv_data[node2]['x']))**2
                                    +(float(csv_data[node]['y']) - float(csv_data[node2]['y']))**2
                                    +(float(csv_data[node]['z']) - float(csv_data[node2]['y']))**2
                                    )
                if (distance <= range):
                    g.add_edge(node, node2)
    
    
    for node in g.node:
        g.node[node]['online'] = True # Each node should be online at first
        g.node[node]['broadcast_delay'] = 0
        for hasnode in g.node:
            g.node[node]['has_' + hasnode] = False # Every node should not have each other's information
    
    # Turn the undirected graph into a directed graph
    ug = helper.to_directed(g)
    
    # Set broadcast information to None on every edge
    for u in ug.edge:
        for v in ug.edge[u]:
            ug.edge[u][v]['broadcast_information'] = None
            
            
    return ug
####################################################################################



####################################################################################
'''
Hook for changing the graph at the beginning of the round. Note that this takes place
before the graph is copied in the engine.
    Args:
        graph: A networkx graph instance.
        max_weight: An integer which is the max weight of edges in this graph.
        add_edge_list: A list for adding new edges from the graph
        remove_edge_list: A list for removing edges from the graph
        add_node_list: A list for adding new nodes to the graph
        remove_node_list: A list for removing nodes from the graph
        round_num: The number of the current round
        run_name: The name of the current run 
'''
####################################################################################
def before_round_start(graph, max_weight, add_edge_list, remove_edge_list, add_node_list, remove_node_list, round_num, run_name):
    for node in graph.node:
        if (graph.node[node]['broadcast_delay'] <= 0): # <= for safety (although it shouldn't matter)
            create_broadcast(graph, node)
        else:
            graph.node[node]['broadcast_delay'] -= 1
####################################################################################



####################################################################################
'''
Hook for creating a broadcast from a given node.
    Args:
        graph: A networkx graph instance.
        node: The node we are creating a broadcast from
'''
####################################################################################
def create_broadcast(graph, node):
    for information in graph.node:
        if (graph.node[node]['has_' + information]):
            print node + ': has_' + information ####################################!!
            if (will_broadcast(graph, node, information)):
                for edge_to in graph.edge[node]:
                    graph.edge[node][edge_to]['broadcast_information'] = information
                    print node + ' to ' + edge_to + ' bears ' + information ########!!
                    return
####################################################################################



####################################################################################
'''
Hook for determining whether or not a node will broadcast a given bit of information.
   Args:
      graph: A networkx graph instance.
      node: A given node we are considering
      information: The bit of information (origin node) that we are considering transmitting
'''
####################################################################################
def will_broadcast(graph, node, information):
    for neighbor in helper.get_neighbors(graph, node):
        if not graph.node[neighbor]['has_' + information]:
            if neighbor in graph.edge[node]:
                print node + ' will broadcast to its neighbors!' ###################!!
                return True
    return False
####################################################################################



####################################################################################
'''
Hook for fixing edge attributes to freshly added edges and nodes.
    Args:
        graph: A networkx graph instance.
        add_edge_list: A list of recently added edges.
        run_name: The name of the current run.
'''
####################################################################################
def post_graph_modification(graph, add_edge_list, add_node_list, run_name):
    pass
####################################################################################



####################################################################################
'''
For every node, deal with the transmission of information.
    Args:
        graph: A networkx graph instance.
        graph_copy: Another networkx graph instance which is the deep copy of graph.
        node: A networkx node instance.
        max_weight: An integer which is the max weight of edges in this graph.
        round_num: The current round number
        run_name: The name of the current run
        debug: An optional variable that defaults to false. If debugging is required,
               obviously, you can create some debug prints and toggle them as necessary.
'''
####################################################################################
def on_node(graph, graph_copy, node, max_weight, round_num, run_name, debug=False):
    print 'entered on node ' + node

    global last_update_round
    # Check that this node is online before continuing
    if not graph_copy.node[node]['online']:
        return
    
    # Get information about this node's neighbors
    neighbors_list = helper.get_unique_neighbors_list(graph_copy, node)
    
    for ngb in neighbors_list:
        if node in graph.edge[ngb]:
            print ngb + ' to ' + node + ' inf: ' + graph.edge[ngb][node]['broadcast_information']##!!
    
    
    # Figure out what transmissions are being broadcasted by neighbors
    transmission_list = []
    for neighbor in neighbors_list:
        if (graph_copy.node[neighbor]['online'] and graph_copy.edge[neighbor][node]['broadcast_information'] is not None):
            transmission_list.append(graph_copy.edge[neighbor][node]['broadcast_information'])
            
    print transmission_list ########################################################!!
    # Can we make use of incoming transmissions, or are broadcasts interfering?
    if (len(transmission_list) <= max_receiving_transmissions): # We're fine
        for information in transmission_list:
            if not graph.node[node]['has_' + information]:
                last_update_round = round_num
                print node + ' receives ' + information ############################!!
            graph.node[node]['has_' + information] = True
            
    else: # We have too many incoming transmissions
        print 'There is a broadcast delay for conflicts with ' + node ##############!!
        broadcast_delay(graph, graph_copy, node, neighbors_list)
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
        debug: An optional variable that defaults to false. If debugging is required,
               obviously, you can create some debug prints and toggle them as necessary.
'''
####################################################################################
def broadcast_delay(graph, graph_copy, node, neighbors_list):
    neighbors_count = len(neighbors_list)
    for neighbor in neighbors_list:
        if (graph_copy.edge[neighbor][node]['broadcast_information'] is not None and graph_copy.node[neighbor]['online']):
            if (graph.node[neighbor]['broadcast_delay'] == 0):
                graph.node[neighbor]['broadcast_delay'] = rand.randint(1, neighbors_count + rand_extra)
                #graph.node[neighbor]['broadcast_delay'] = max(graph.node[neighbor]['broadcast_delay'], rand.randint(1, neighbors_count + rand_extra))
####################################################################################



####################################################################################
'''
Hook for dealing with addition/removal of nodes at the end of a round.
    Args:
        graph: A networkx graph instance.
        add_edge_list: A list for adding new edges from the graph
        remove_edge_list: A list for removing edges from the graph
        add_node_list: A list for adding new nodes to the graph
        remove_node_list: A list for removing nodes from the graph
        round_num: The number of the current round
        run_name: The name of the current run
'''
####################################################################################
def after_round_end(graph, add_edge_list, remove_edge_list, add_node_list, remove_node_list, round_num, run_name):
    for e in graph.edges():
        graph.edge[e[0]][e[1]]['broadcast_information'] = None
####################################################################################



####################################################################################
'''
Init method. This currently only starts each node with its own information.
    Args:
        graph: A networkx graph instance.
        node: A networkx node instance.
        sim_name: The name of the current simulation
'''
####################################################################################
def init(graph, sim_name):
    for node in graph.node:
        graph.node[node]['has_' + node] = True
####################################################################################

   
####################################################################################
'''
Determines whether or not a graph is finished.
    Args:
        graph: A networkx graph instance.
        round_num: An integer recording the current number of rounds.
        max_allowed_rounds: An integer which is set to be the max allowed number of rounds.
        run_name: The name of the current simulation run
	  
    Returns:
       -1: If we have exceeded our max_allowed_rounds
        0: If there is still information to be broadcasted
        1: If the information has been broadcasted to all nodes
'''
####################################################################################
def finished_hook(graph, round_num, max_allowed_rounds, run_name):
    #if (round_num == 300):
    #    for node in graph.node:
    #        print graph.node[node]
    if (helper.exceeded_round_no_update_limit(last_update_round, round_num, max_rounds_no_update)):
        return -1
    for node in graph.node:
        for information in graph.node:
            if not graph.node[node]['has_' + information]:
                return 0 # Return that there is an incomplete graph
    # If we reached this point, all nodes have every bit of information
    return 1
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
    global total_broadcasts_sent, total_broadcasts_received, total_interference_failures
    global current_broadcasts_sent, current_broadcasts_received, current_interference_failures
    global last_update_round
    
    last_update_round = 0
    
    
    print '\n' + run_name + ' Finished ' + run_name + '.\n'
    
    if (finish_code == -1):
        print 'Exceeded ' + str(max_rounds_no_update) + ' rounds without an update!'
    elif (finish_code == 1):
        print 'Graph finished. Summing results.'
    
    for node in graph.node:
        total_broadcasts_sent[node] = current_broadcasts_sent[node]
        total_broadcasts_received[node] = current_broadcasts_received[node]
        total_interference_failures[node] = current_interference_failures[node]
    
    current_broadcasts_sent = {}
    current_broadcasts_received = {}
    current_interference_failures = {}
    
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
def heartbeat(current_time, last_heartbeat, round_num, run_name):
    print '[' + str(current_time) + ']: ' + str(run_name) + ' still alive. Last heartbeat was ' \
            + str(last_heartbeat) + ' seconds ago.\nCurrent round is ' + str(round_num) + '. Round ' + str(last_update_round) + ' was last graph update.'
####################################################################################
