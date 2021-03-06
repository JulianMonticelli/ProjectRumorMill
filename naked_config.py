# Python Library Packages
import networkx as nx
import copy

# Cyclical dependency to main
import simengine as engine # < Driver in config requires this
import simhelper as helper
import simdefaults as defaults

#######################
# Simulation arguments#
#######################
heartbeat_interval = 30 # 30 second heartbeat interval
maximum_allowed_simulation_rounds = 100 # Max amount of rounds before we stop running a simulation
max_weight = 0 # Maximum weight is set in simulation driver
num_runs = 3      # Default number of runs per simulation

#######################
# Global data         #
#######################


####################################################################################
'''
Simulation driver, which will call the engine to begin simulations. Setup should
happen in this method, and data collection should be done inside any method necessary.
A logically sound place to put data processing is at the end of this method.
'''
####################################################################################
def simulation_driver():
   global max_weight
   # Read in a graph
   graph = nx.read_graphml('simplemodel.graphml')
   max_weight = helper.max_weight(graph)
   helper.output_graph_information(graph)

   
   
   # Start from every node in the graph
   for n in graph.node:
      sim_name = 'sim_' + str(n)
      graphcopy = copy.deepcopy(graph)
      init(graphcopy, n, sim_name)
      engine.simulate(graphcopy, num_runs, sim_name)
      
   # Output data
####################################################################################



####################################################################################
'''
Handles a special node (or multiple special nodes). It is up to the user to define
this hook's behavior, otherwise the correct move would be to pass.
    Args:
        graph: A networkx graph instance.
        graphcopy: An unedited copy of the networkx graph instance.
        round_num: The current round number
        run_name: The name of the current simulation run.
'''
####################################################################################
def special_node_handle(graph, graph_copy, round_num, run_name):
    pass
####################################################################################



####################################################################################
'''
Hook for considering a node in the graph.
   Args:
      graph: A networkx graph instance.
      graph_copy: Another networkx graph instance which is the deep copy of graph.
      node: A networkx node instance.
      run_name: The name of the current run
'''
####################################################################################
def on_node(graph, graph_copy, node, round_num, run_name):

   # Example branching - branch functions depending on a flag condition

   # If node is flagged
   if (graph_copy.node[node]['flagged']):
      on_flagged(graph, graph_copy, node, run_name)

   # If the node is not flagged
   else:
      on_not_flagged(graph, graph_copy, node, run_name)
####################################################################################



####################################################################################
'''
Runs operations on a flagged node to determine if it will transmit a flag.
   Args:
      graph: A networkx graph instance.
      graph_copy: Another networkx graph instance which is the deep copy of graph.
      node: A networkx node instance.
      run_name: The name of the current run
'''
####################################################################################
def on_flagged(graph, graph_copy, node, run_name):
   given_flags = 0
   
   # Check the unedited copy graph for flagged neighbors
   for neighbor in graph_copy.edge[node]:

      # If a target graph node in both the copy and original aren't flagged
      if (not graph_copy.node[neighbor]['flagged'] and not graph.node[neighbor]['flagged']):
         
         # If the simulation will actually spread, then spread
         if (will_spread(node, neighbor, graph, run_name)):
            graph.node[neighbor]['flagged'] = True			
####################################################################################



####################################################################################
'''
Currently will only check whether or not spontaneous acquisition will occur.
   Args:
      graph: A networkx graph instance.
      graph_copy: Another networkx graph instance which is the deep copy of graph.
      node: A networkx node instance.
      run_name: The name of the current method

   Returns:
      0: If spontaneous acquisition doesn't happen in this node operation.
      1: If spontaneous acquisition happens in this node operation.
'''
####################################################################################
def on_not_flagged(graph, graph_copy, node, run_name):
   return 0 # No change
####################################################################################



####################################################################################
'''
Determine if a given source node will transmit a flag to a given node.
   Args:
      source: A networkx node instance which is the source node in this transmission.
      dest: Another networkx node instance which is the destination node in this transmission.
      graph: A networkx graph instance.
      run_name: The name of the current run

   Returns:
      True: If the flag is spread in this node operation.
      False: If the flag isn't spread in this node operation.
'''
####################################################################################
def will_spread(source, dest, graph, run_name):
   # TODO: Add more dynamic way to spread flags from nodes to nodes
   
   # Get current weight
   curr_weight = graph.edge[source][dest]['weight']
   
   # Will they engage at all? This consults the weight of their edge
   # Currently, it is set up so that if communication happens at all
   # 
   if ( helper.roll_weight (curr_weight , max_weight ) ):
      return True
   return False
####################################################################################



####################################################################################
'''
Hook for changing the graph at the beginning of the round. Note that this takes place before the graph is copied in the engine.
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
def before_round_start(graph, add_edge_list, remove_edge_list, add_node_list, remove_node_list, round_num, run_name):
   #for edge in graph.edge:
      # do something
   return
####################################################################################



####################################################################################
'''
Hook for making changes to the graph after the we have modified its edges and nodes.
If there are attributes that are critical to the simulation, you should define them
for each of 

    Args:
        graph: A networkx graph instance
        add_edge_list: A list of edges we have added to the graph
        add_node_list: A list of edges we have added to the graph
        run_name: A name for the simulation run
'''
####################################################################################
def post_graph_modification(graph, add_edge_list, add_node_list, run_name):
   return
####################################################################################



####################################################################################
'''
Hook for considering a node in the graph.
    Args:
        graph: A networkx graph instance.

    Returns:
        given_flags: An integer showing how many nodes are flagged in this round.
        removed_flags: An integer showing how many nodes are unflagged in this round.
        run_name: The name of the current run
'''
####################################################################################
def after_round_end(graph, add_edge_list, remove_edge_list, add_node_list, remove_node_list, round_num, run_name):
   given_flags = 0
   removed_flags = 0
   
   #for edge in graph.edge:
      # do something
	  
   return given_flags, removed_flags
####################################################################################



####################################################################################
'''
Initialize the graph with attributes that are necessary to run a simulation.
Takes a graph and a String node (i.e., 'n10') to initialize as flagged.
Also initializes uninitialized weights on graphs as 1.
    Args:
        graph: A networkx graph instance.
        node: A networkx node instance.
        sim_name: The name of the current simulation
'''
####################################################################################
def init(graph, node, sim_name):
   # Let the user know what node is the starting node.
   if (defaults.LOGGING or defaults.DEBUG or defaults.defaults.DEBUG_SEVERE):
      print '\n' + '*' * defaults.asterisk_space_count + '\nInitializing graph - \'' + str(node) + '\' is in the know.'

   # Give all nodes a false flag
   helper.create_node_attribute(graph, 'flagged', False)
   
   # Save edge weight, as we are going to wipe graph
   dict = nx.get_edge_attributes(graph, 'weight')
   
   # Write 1 weight to all edges
   nx.set_edge_attributes(graph, 'weight', 1)
   
   # Restore initial edges
   for n1,n2 in dict:
      graph.edge[n1][n2]['weight'] = dict[n1,n2]
   
   
   # Set an arbitrary node
   graph.node[node]['flagged'] = True
####################################################################################

   
####################################################################################
'''
Determines whether or not a graph is finished.
    Args:
        graph: A networkx graph instance.
        current_round: An integer recording the current number of rounds.
        run_name: The name of the current simulation run
	  
    Returns:
        0: If we fail to finish this graph simulation run.
        1: If we succeed to finish this graph simulation run.
       -1: If the current round number exceeds the max allowed number.
'''
####################################################################################
def finished_hook(graph, current_round, run_name):
   # Get all attributes and store them in a dictionary
   dict = nx.get_node_attributes(graph, 'flagged')
   
   # Make sure we haven't hit the maximum allowed round
   if (helper.exceeded_round_limit(current_round, maximum_allowed_simulation_rounds)):
      return -1 # -1 means we ran out of allowed rounds
   

   # Iterate the nodes and see if they're flagged or not 
   for val in dict:
      if(not dict[val]):
         #print '[' + val  + ']: ' + str(dict[val])
         if (helper.num_flagged(graph, 'flagged') > 0):
            return 0
         else:
            return -1
   return 1 # 1 is a successful graph
####################################################################################



####################################################################################
'''
Hook for finishing the simulation run on the current graph.
    Args:
        finish_code: 0 or 1 or -1 depend on the finish code we return in finished_hook function.
        round_num: An integer showing how many round we use to finish the graph if succeed.
        num_flags: An integer showing how many nodes are flagged in the end.
        run_name: The name of the current simulation run
'''
####################################################################################
def on_finished_run(graph, finish_code, round_num, run_name, total_time_seconds):
   print 'Finished ' + run_name + ' - you should do something with this!'
####################################################################################



####################################################################################
'''
Hook for dealing with data across a simulation on the given graph. Specifically, this
was designed for dealing with looking at differences across the whole simulation.
    Args:
        num_runs: The number of runs in a given simulation.
        graphs: A list of graphs which correspond to the finished graph for each run
                in the simulation.
        sim_name: The name of the simulation.
'''
####################################################################################
def on_finished_simulation(num_runs, graphs, sim_name):
    pass
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
   print '[' + str(current_time) + ']: ' + str(run_name) + ' still alive. Last update was ' \
         + str(last_heartbeat) + ' seconds ago.'
####################################################################################
