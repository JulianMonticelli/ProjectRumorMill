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

SIM_DEBUG = False

maximum_allowed_simulation_rounds = 15000 # Max amount of rounds before we stop running a simulation

heartbeat_interval = 30

num_runs = 1

max_receiving_transmissions = 1

max_rounds_no_update = 64

# The amount of extra random integer results 
rand_extra = 3

csv_file = 'iot/r.csv'

radius_step = 5

#######################
# Global data         #
#######################

last_update_round = 0

total_broadcasts_sent = {}
total_broadcasts_received_successfully = {}
total_broadcasts_received_overall = {}
total_interference_failures = {}

current_broadcasts_sent = {}
current_broadcasts_received_successfully = {}
current_broadcasts_received_overall = {}
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
    global total_broadcasts_sent, total_broadcasts_received_successfully, total_broadcasts_received_overall, total_interference_failures
    global current_broadcasts_sent, current_broadcasts_received_successfully, current_broadcasts_received_overall, current_interference_failures
    
    # First read in a graph with initial
    graph = iot_graph(csv_file)
    
    # Output graph information
    helper.output_graph_information(graph)
    
    # Store number of nodes in graph for later use (possibly)
    num_nodes = helper.num_nodes(graph)
    
    # Initialize total dictionaries
    for node in graph.node:
        # Total dictionaries
        total_broadcasts_sent[node] = 0
        total_broadcasts_received_successfully[node] = 0
        total_broadcasts_received_overall[node] = 0
        total_interference_failures[node] = 0
        # Current dictionaries
        current_broadcasts_sent[node] = 0
        current_broadcasts_received_successfully[node] = 0
        current_broadcasts_received_overall[node] = 0
        current_interference_failures[node] = 0
    
    # Simulation name will be something like "iot_p_10"
    sim_name = 'iot_' + csv_file[:len(csv_file)-4]
    
    init(graph, sim_name)
    engine.simulate(graph, num_runs, sim_name)

    print '*' * 40
    print 'This is the end of the simulation.'
    print '*' * 40
    
    for node in graph.node:
        print node + ':'
        print '>Total broadcasts sent                    = ' + str(total_broadcasts_sent[node])
        print '>Total broadcasts received (successfully) = ' + str(total_broadcasts_received_successfully[node])
        print '>Total broadcasts received (overall)      = ' + str(total_broadcasts_received_overall[node])
        print '>Total interference failures              = ' + str(total_interference_failures[node])
    
    mbcs = str(helper.get_max_in_dict(total_broadcasts_sent))
    mbcrs = str(helper.get_max_in_dict(total_broadcasts_received_successfully))
    mbcro = str(helper.get_max_in_dict(total_broadcasts_received_overall))
    mif = str(helper.get_max_in_dict(total_interference_failures))
    
    print '>Max broadcasts sent:                     = ' + mbcs + '\t(' + str(total_broadcasts_sent[mbcs]) + ')'
    print '>Max broadcasts received (successfully)   = ' + mbcrs + '\t(' + str(total_broadcasts_received_successfully[mbcrs]) + ')'
    print '>Max broadcasts received (overall)        = ' + mbcro + '\t(' + str(total_broadcasts_received_overall[mbcro]) + ')'
    print '>Max interference failures                = ' + mif + '\t(' + str(total_interference_failures[mif]) + ')'
        
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
        csv_data[row['node_name']]['x']     = float(row['x'])
        csv_data[row['node_name']]['y']     = float(row['y'])
        csv_data[row['node_name']]['range'] = float(row['range'])
        print row['node_name'] + ' ' + row['x'] + ' ' + row['y'] + ' ' + row['range']
    
    csvfile.close()
    
    import math
    for node in g.node:
        for node2 in g.node:
            if node is not node2:
                distance = math.sqrt(
                                     (csv_data[node]['x'] - csv_data[node2]['x'])**2
                                    +(csv_data[node]['y'] - csv_data[node2]['y'])**2
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
        csv_data[row['node_name']]['x'] = float(row['x'])
        csv_data[row['node_name']]['y'] = float(row['y'])
        csv_data[row['node_name']]['z'] = float(row['z'])
    
    csvfile.close()
    
    import math
    for node in g.node:
        for node2 in g.node:
            if node is not node2:
                distance = math.sqrt(
                                     (csv_data[node]['x'] - csv_data[node2]['x'])**2
                                    +(csv_data[node]['y'] - csv_data[node2]['y'])**2
                                    +(csv_data[node]['z'] - csv_data[node2]['z'])**2
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
    global current_broadcasts_sent
    for information in graph.node:
        if (graph.node[node]['has_' + information]):
            if (will_broadcast(graph, node, information)):
                current_broadcasts_sent[node] += 1 # << DATA COLLECTION
                for edge_to in graph.edge[node]:
                    graph.edge[node][edge_to]['broadcast_information'] = information
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
                return True # We only need ONE neighbor to not have the information
                            # to transmit the information
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
def on_node(graph, graph_copy, node, max_weight, round_num, run_name, max_receiving_transmissions=max_receiving_transmissions, debug=SIM_DEBUG):
    global last_update_round, current_broadcasts_received_overall, current_broadcasts_received_successfully
    # Check that this node is online before continuing
    if not graph_copy.node[node]['online']:
        return
    
    # Get information about this node's neighbors
    neighbors_list = helper.get_unique_neighbors_list(graph_copy, node)
    
    
    # Figure out what transmissions are being broadcasted by neighbors
    transmission_list = []
    for neighbor in neighbors_list:
        if node in graph_copy.edge[neighbor]:
            if (graph_copy.node[neighbor]['online'] and graph_copy.edge[neighbor][node]['broadcast_information'] is not None):
                current_broadcasts_received_overall[node] += 1 # << DATA COLLECTION
                transmission_list.append(graph_copy.edge[neighbor][node]['broadcast_information'])
            
    # Can we make use of incoming transmissions, or are broadcasts interfering?
    if (len(transmission_list) <= max_receiving_transmissions): # We're fine
        for information in transmission_list:
            current_broadcasts_received_successfully[node] += 1 # << DATA COLLECTION
            if not graph.node[node]['has_' + information]:
                last_update_round = round_num
                if (debug):
                    print node + ' receives ' + information
                graph.node[node]['has_' + information] = True
            
    else: # We have too many incoming transmissions
        if (debug):
            print 'Broadcast delay to all broadcasting neighbors of ' + node
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
    global current_interference_failures
    neighbors_count = len(neighbors_list)
    for neighbor in neighbors_list:
        if node in graph.edge[neighbor]:
            if (graph_copy.edge[neighbor][node]['broadcast_information'] is not None and graph_copy.node[neighbor]['online']):
                if (graph.node[neighbor]['broadcast_delay'] == 0):
                    current_interference_failures[neighbor] += 1
                    graph.node[neighbor]['broadcast_delay'] = rand.randint(1, neighbors_count + rand_extra)
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
    global total_broadcasts_sent, total_broadcasts_received_successfully, total_broadcasts_received_overall, total_interference_failures
    global current_broadcasts_sent, current_broadcasts_received_successfully, current_broadcasts_received_overall, current_interference_failures
    global last_update_round
    
    last_update_round = 0
    
    
    print '\n' + run_name + ' Finished ' + run_name + '.\n'
    
    if (finish_code == -1):
        print 'Exceeded ' + str(max_rounds_no_update) + ' rounds without an update!'
    elif (finish_code == 1):
        print 'Graph finished. Summing results.'
    
    for node in graph.node:
        total_broadcasts_sent[node] += current_broadcasts_sent[node]
        total_broadcasts_received_successfully[node] += current_broadcasts_received_successfully[node]
        total_broadcasts_received_overall[node] += current_broadcasts_received_overall[node]
        total_interference_failures[node] += current_interference_failures[node]
    
    current_broadcasts_sent = {}
    current_broadcasts_received_successfully = {}
    current_broadcasts_received_overall = {}
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
