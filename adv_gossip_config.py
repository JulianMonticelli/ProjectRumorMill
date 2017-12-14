# Python Library Packages
import networkx as nx
import random as rand
from random import choice
import copy
import simengine as engine
import simhelper as helper
import simdefaults as defaults
import random


#######################
# Global data         #
#######################
num_flagged = 0
num_flagged_successes = 0
max_flagged = 0
total_simulations = 0
total_successes = 0
num_fails = 0
num_forgot = 0
num_given = 0
max_given = 0
max_forgot = 0
total_rounds = 0
max_virality = 0
min_rounds_success = float('inf')
max_rounds_success = float('-inf')

print_output = False


#######################
# Simulation arguments#
#######################
heartbeat_interval = 30 #30 second heartbeat interval
maximum_allowed_simulation_rounds = 100 # Max amount of rounds before we stop running a simulation
num_runs = 30      #Default number of runs per simulation
is_the_gossip_serious = True #if the gossip is serious the chance will increase
is_the_group_discreet = False #if group is discreet the chance of info traveling will decrease
talk_to_transmit = True
transmit_chance = 0.01 #if transmit =/= talk, what is the chance upon talking
spontaneous_forget = False  #Set this to be true, nodes can forget but with a very small chance it's some juicy gossip!
spontaneous_forget_chance = 0.01  #Chance for node to forget
spontaneous_acquisition = True  #Set to true - this is like a person getting the gossip from an outside source
spontaneous_acquisition_chance = 0.01 #the internet exists!

# Whether or not a graph is considered finished if,
# when spontaneous acquisition is not occurring,
# information has spread to all nodes that can become
# spread to.
finished_includes_max_subgraph_spread=True

####################################################################################



####################################################################################
'''
Sets the value of the spontaneous acquisition variable based on a attributes
assigned to the node i.e. if the node is a student or non-student if the gossip is
serious etc.
    Args:
        graph: A networkx graph instance
        node: A networkx node instance
    Returns:
        spontaneous_acquisition_chance: The chance for spontaneous acquisition
        for that node
'''
####################################################################################
def set_spontaneous_aq_val(graph, node):

    attributes = []

    # if node is non-student
    if random.randrange(0,12) == 1:
        attributes.append("Non-student")
        spontaneous_acquisition_chance = .1
    else:
        # node is a student
        attributes.append("Student")
        spontaneous_acquisition_chance = .4

    if is_the_group_discreet:
       attributes.append("discreet")

       if spontaneous_acquisition_chance > .2:
          spontaneous_acquisition_chance = spontaneous_acquisition_chance - .2

    if is_the_group_discreet == False:
        attributes.append("not discreet")

        spontaneous_acquisition_chance = spontaneous_acquisition_chance + .15

    if is_the_gossip_serious:
        attributes.append("serious")

        if spontaneous_acquisition_chance < .5:
            spontaneous_acquisition_chance = spontaneous_acquisition_chance + .1
    else:
        attributes.append("not serious")

        if spontaneous_acquisition_chance <= .1:
            spontaneous_acquisition_chance = .09
        else:
           spontaneous_acquisition_chance = spontaneous_acquisition_chance - .1

    if is_the_gossip_serious == False:
        if spontaneous_acquisition_chance > .1:
           spontaneous_acquisition_chance = spontaneous_acquisition_chance - .1

    # popular outside of school social network
    if random.randrange(0, 20):
        spontaneous_acquisition_chance = spontaneous_acquisition_chance + .1

    # watch or read the news
    if random.randrange(0,50):
        spontaneous_acquisition_chance = spontaneous_acquisition_chance + .1

    if spontaneous_acquisition_chance == 0:
       spontaneous_acquisition_chance = 0.01;
    if spontaneous_acquisition_chance > 1:
       spontaneous_acquisition_chance = .9;

    return spontaneous_acquisition_chance

####################################################################################



####################################################################################
'''
Sets the value of the spontaneous forgetting variable based on a attributes
assigned to the node i.e. if the node is particularly stressed
    Args:
        graph: A networkx graph instance
        node: A networkx node instance
    Returns:
        spontaneous_forget_chance: The chance for spontaneous forgetting
        for that node
'''
####################################################################################
def set_spontaneous_forget_val(graph, node):

    if is_the_gossip_serious:
        spontaneous_forget_chance = .15
    else:
        spontaneous_forget_chance = .3

    if is_the_group_discreet == True:
        spontaneous_forget_chance = spontaneous_forget_chance - .09

    if random.randrange(0,5) == 2: #this means a student is extra super stressed
       spontaneous_forget_chance = spontaneous_forget_chance + .2

    if spontaneous_forget_chance == 0:
       spontaneous_forget_chance = .01;
    if spontaneous_forget_chance > 1:
       spontaneous_forget_chance = .9;

    return spontaneous_forget_chance


####################################################################################



####################################################################################
'''
Determines if the node is in the popular or unpopular crowd based on the nodes
degree_centrality
    Args:
        dict_cent: A dictionary of all the nodes degree_centrality
    Returns:
        pop_nodes: A dictionary of the popular nodes (the top 10% of nodes)
        unpop_nodes: A dictionary of the unpopular nodes (the bottom 10% of nodes)
'''
####################################################################################
def get_pop_and_unpop_nodes(dict_cent):

     # get the number of nodes
     num_nodes = len(dict_cent)

     # get num for 10% of nodes
     ten_per_nodes = int(num_nodes * .1)

     pop_nodes = dict()
     unpop_nodes = dict()

     for i in range(num_nodes):
         if i < ten_per_nodes:
             found_node = min(dict_cent, key=dict_cent.get)
             pop_nodes[found_node] = dict_cent[found_node]
             del dict_cent[found_node]
     dict_cent.update(pop_nodes)

     for i in range(num_nodes):
         if i < ten_per_nodes:
             found_node = max(dict_cent, key=dict_cent.get)
             unpop_nodes[found_node] = dict_cent[found_node]
             del dict_cent[found_node]

     return pop_nodes, unpop_nodes


####################################################################################



####################################################################################
'''
Sets the value of the talk to transmit variable based on attributes
assigned to the node i.e. if the node is a student, what grade they are in and if
they are popular
    Args:
        graph: A networkx graph instance
        node: A networkx node instance
    Returns:
        transmit_chance: The chance that the node will transmit the gossip
        attributes: A list of attributes associated with the node
        (popularity, grade, etc.)
'''
####################################################################################
def set_talk_to_transmit_val(graph, node):

   attributes = []
   dict_cent = nx.degree_centrality(graph)
   num_nodes = len(dict_cent)

   pop_nodes = dict()
   unpop_nodes = dict()

   if is_the_gossip_serious:
       transmit_chance = .5
   else:
       transmit_chance = .3

   if num_nodes >= 3:
      pop_nodes, unpop_nodes = get_pop_and_unpop_nodes(dict_cent = dict_cent)

   # grade
   r_n = random.randrange(0,13)

   if node in pop_nodes:
      attributes.append(" popular")

      transmit_chance = transmit_chance + .2

   if node in unpop_nodes:
      attributes.append("n unpopular")

      transmit_chance = transmit_chance - .2

   if node not in unpop_nodes and node not in unpop_nodes:
      attributes.append("n average")

      # either .1 or .89

   if r_n == 0: #non student
      attributes.append("nonstudent")

      transmit_chance = .05

   if r_n == 1 or r_n == 5 or r_n == 9 : #freshman
      attributes.append("freshman")

      transmit_chance = transmit_chance + .1

   if r_n == 2 or r_n == 6 or r_n == 10: #sophmore
      attributes.append("sophomore")
      transmit_chance = transmit_chance + .05

   if r_n == 3 or r_n == 7 or r_n == 11: #junior
      attributes.append("junior")

      transmit_chance = transmit_chance + .03

   if r_n == 4 or r_n == 8 or r_n == 12: #senior
      attributes.append("senior")

      transmit_chance = transmit_chance + .01

   if is_the_group_discreet == False:
       if transmit_chance < .9:
           transmit_chance = transmit_chance + .1
   if is_the_group_discreet:
      if transmit_chance > .2:
         transmit_chance = transmit_chance - .2
      else:
         transmit_chance = 0.1
   if transmit_chance == 0:
       transmit_chance = .01;
   if transmit_chance > 1:
       transmit_chance = .9;

   return transmit_chance, attributes

####################################################################################
'''
Simulation driver, which will call the engine to begin simulations. Setup should
happen in this method, and data collection should be done inside any method necessary.
A logically sound place to put data processing is at the end of this method.
'''
####################################################################################
def simulation_driver():
    # Read in a graph
    graph = nx.read_graphml('gosspp.graphml')
    helper.output_graph_information(graph)
    type_of_gossip = gossip_type_determination()
    death_sc = False

    skip_nodes, death_sc = set_up_scenario(type_of_gossip, graph, death_sc)

    if death_sc == True:
        for dnode in skip_nodes:
            graph.remove_node(dnode)

    # Start from every node in the graph
    for n in graph.node:
       for skn in skip_nodes:
           if n == skn:
             #   won't pass the gossip
             if(print_output):
                 print(n + " won't pass gossip about themself.")
             continue
    graphcopy = copy.deepcopy(graph)

    # Create a simulation name
    sim_name = 'Gossip_Simulation_' + str(n)

    init(graphcopy, n, sim_name)

    # Start simulation with the simulation name
    engine.simulate(graphcopy, num_runs, sim_name)

    # Data collection per simulation should go here - any global variables should be recorded and reset

    average_rounds = 0
    if (total_successes > 0):
      average_rounds = total_rounds / float(total_successes)
    print '\n' * 2
    print '*' * defaults.asterisk_space_count
    print 'Simulations complete.'
    print '*' * defaults.asterisk_space_count
    print 'Simulations where all individuals at the school learned the rumor: ' + str(total_successes)
    print 'Simulations where the rumor did not spread across entire school: ' + str(num_fails)
    print 'Total number of simulations (complete and incomplete):    ' + str(total_simulations)
    print '\n' + '*' * defaults.asterisk_space_count + '\n'
####################################################################################



####################################################################################
'''
Hook for considering a node in the graph.
   Args:
      graph: A networkx graph instance.
      graph_copy: Another networkx graph instance which is the deep copy of graph.
      node: A networkx node instance.
      max_weight: An integer which is the max weight of edges in this graph.
      run_name: The name of the current run
'''
####################################################################################
def on_node(graph, graph_copy, node, max_weight, run_name):
   # Define relevant globals
   global num_forgot
   global num_given
   global spontaneous_acquisition_chance
   global spontaneous_forget_chance

   spontaneous_acquisition_chance = set_spontaneous_aq_val(graph,node)
   spontaneous_forget_chance = set_spontaneous_forget_val(graph, node)

   if(will_forget(graph, graph_copy, node, 'flagged', run_name, spontaneous_forget, spontaneous_forget_chance)):
      num_forgot += 1 # Update amount of forgotten flags
      return
      # IMPORTANT: So that directed graphs work as well as undirected graphs, consider flagged only
      # Check graph_copy for the flag - if we check graph, we will have leaking
   if (graph_copy.node[node]['flagged']):
      num_given += on_flagged(graph, graph_copy, node, max_weight, run_name)

      # If the node does not know, and we can spontaneously come into knowing
   else:
      num_given += on_not_flagged(graph, graph_copy, node, run_name, spontaneous_acquisition, spontaneous_acquisition_chance)
####################################################################################


####################################################################################
'''
Performs a roll for a node that is in the know to determine whether or not an agent should lose a flag, and if so, updates the graph accordingly.
   Args:
      graph: A networkx graph instance.
      graph_copy: Another networkx graph instance which is the deep copy of graph.
      node: A networkx node instance.
      attr: A string indicating which attribute we currently consider.
      run_name: The name of the current run
      spontaneous_forget: A boolean which indicates whether a node would be able to spontaneous forget information.
      spontaneous_forget_chance: A floating number which is the probability of spontaneous forget if it's able to.
      forget_value: The value of attribute we need to set to nodes which forget.

   Returns:
      True: If spontaneous forget happens in this node operation.
      False: If spontaneous forget doesn't happen in this node operation.
'''
####################################################################################
def will_forget(graph, graph_copy, node, attr, run_name, spontaneous_forget, spontaneous_forget_chance, forget_value=False):
   # Make sure we don't forget what we don't know!

   if (spontaneous_forget and graph.node[node][attr] != forget_value):
      if (helper.chance(spontaneous_forget_chance)):
         # Wipe flag from both graph and graph_copy
         graph.node[node][attr] = forget_value
         graph_copy[node][attr] = forget_value
         return True
   return False
 # Skip this node because it no longer has a flag
####################################################################################


####################################################################################
'''
Runs operations on a flagged node to determine if it will transmit information.
   Args:
      graph: A networkx graph instance.
      graph_copy: Another networkx graph instance which is the deep copy of graph.
      node: A networkx node instance.
      max_weight: An integer which is the max weight of edges in this graph.
      run_name: The name of the current run
      talk_to_transmit: A boolean which indicates whether 'talk' equals to 'transmit'.
      transmit_chance: A floating number which is the probability of transmission when 'talk' doesn't equal to 'transmit'.
   Returns:
      NOTE: returns are optional
      given_flags: An integer showing how many nodes are flagged in this node operation.
'''
####################################################################################
def on_flagged(graph, graph_copy, node, max_weight, run_name,
               talk_to_transmit=talk_to_transmit,
               transmit_chance=transmit_chance):
   given_flags = 0


   #get value for talk_to_transmit
   transmit_chance, attrs = set_talk_to_transmit_val(graph, node)
   strt = str(node), " who is a"+ str(attrs[0]) +" "+ str(attrs[1])

   # Check the unedited copy graph for flagged neighbors
   for neighbor in graph_copy.edge[node]:

      # If a target graph node in both the copy and original aren't flagged
      if (not graph_copy.node[neighbor]['flagged'] and not graph.node[neighbor]['flagged']):

         # If the simulation will actually spread, then spread
         b = will_spread(node, neighbor, graph, max_weight, run_name, talk_to_transmit, transmit_chance)
         if (b):
            graph.node[neighbor]['flagged'] = True
            if(print_output):
                print(str(strt).replace("('","").replace("', '","").replace("')","") +" attempted to spread the rumor")


            # Increment the number of given_flags this round
            given_flags += 1
         else:
            if(print_output):
                print(str(strt).replace("('","").replace("', '","").replace("')","") + " failed to spread the rumor")


   return given_flags
####################################################################################



####################################################################################
'''
Currently will only check whether or not spontaneous acquisition will occur.
   Args:
      graph: A networkx graph instance.
      graph_copy: Another networkx graph instance which is the deep copy of graph.
      node: A networkx node instance.
      run_name: The name of the current method
      spontaneous_acquisition: A boolean which indicates whether a node would be able to spontaneous acquire information.
      spontaneous_acquisition_chance: A floating number which is the probability of spontaneous acquisition if it's able to.

   Returns:
      0: If spontaneous acquisition doesn't happen in this node operation.
      1: If spontaneous acquisition happens in this node operation.
'''
####################################################################################
def on_not_flagged(graph, graph_copy, node, run_name,
                   spontaneous_acquisition=spontaneous_acquisition,
                   spontaneous_acquisition_chance=spontaneous_acquisition_chance):
   # spontaneous_acquisition_chance = set_spontaneous_aq_val(graph)
   if (will_spontaneously_acquire(graph, graph_copy, node, 'flagged', True, spontaneous_acquisition)):
      return 1 # We have made a positive difference in this graph by one
   return 0 # No change
####################################################################################

####################################################################################
'''
Performs a roll for a node that is not in the know to determine whether or not an agent should gain a flag, and if so, updates the graph accordingly.
   Args:
      graph: A networkx graph instance.
      graph_copy: Another networkx graph instance which is the deep copy of graph.
      node: A networkx node instance.
      attr: A string indicating which attribute we currently consider.
      acquisition_value: A value that will be given upon spontaneous acquisition
      run_name: The name of the current run
      spontaneous_acquisition: A boolean which indicates whether a node would be able to spontaneous forget information.
      spontaneous_acquisition_chance: A floating number which is the probability of spontaneous forget if it's able to.

   Returns:
      True: If spontaneous acquisition happens in this node operation.
      False: If spontaneous acquisition doesn't happen in this node operation.
'''
####################################################################################
def will_spontaneously_acquire(
                               graph, graph_copy, node, attr, acquisition_value, run_name,
                               spontaneous_acquisition=spontaneous_acquisition,
                               spontaneous_acquisition_chance=spontaneous_acquisition_chance
                              ):
   # spontaneous_acquisition_chance = set_spontaneous_aq_val(graph)
   if (spontaneous_acquisition and graph.node[node][attr] != acquisition_value):
      if (helper.chance(spontaneous_acquisition_chance)):
         # Apply flag to both graph and graph_copy
         graph.node[node][attr] = acquisition_value
         graph_copy.node[node][attr] = acquisition_value
         return True
   return False
####################################################################################



####################################################################################
'''
Determine if a given source node will transmit information to a given node.
   Args:
      source: A networkx node instance which is the source node in this transmission.
      dest: Another networkx node instance which is the destination node in this transmission.
      graph: A networkx graph instance.
      max_weight: An integer which is the max weight of edges in this graph.
      run_name: The name of the current run
      talk_to_transmit: A boolean which indicates whether 'talk' equals to 'transmit'.
      transmit_chance: A floating number which is the probability of transmission when 'talk' isn't equal to 'transmit'.

   Returns:
      True: If the information is spread in this node operation.
      False: If the information isn't spread in this node operation.
'''
####################################################################################
def will_spread(
                source, dest, graph, max_weight, run_name,
                talk_to_transmit=talk_to_transmit,
				transmit_chance=transmit_chance
               ):
   # Get current weight
   curr_weight = graph.edge[source][dest]['weight']

   # Will they engage at all? This consults the weight of their edge
   if ( helper.roll_weight (curr_weight , max_weight ) ):
      if (talk_to_transmit):
          return True
      else:
         # This is the chance that their engagement will exchange information
         if (helper.chance(transmit_chance)):
            return True, strt
   return False
####################################################################################



####################################################################################
'''
Hook for changing the graph at the beginning of the round. Note that this takes place before the graph is copied in the engine.
   Args:
      graph: A networkx graph instance.
      max_weight: An integer which is the max weight of edges in this graph.
      run_name: The name of the current run
'''
####################################################################################
def before_round_start(graph, add_edge_list, remove_edge_list, add_node_list, remove_node_list, round_num, run_name):

   helper.sleep_ms(100)
   return
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
     for u,v in add_edge_list:
          helper.randomize_edge_list_attribute(graph, add_edge_list, 'weight', 1, max_weight)
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

    # TODO: Do if needed
    pass


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

   return given_flags, removed_flags
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
def on_finished_run(graph, finish_code, round_num, run_name, total_time_seconds):
   global num_given
   global num_forgot
   global total_simulations
   global total_successes
   global num_fails
   global total_rounds
   global num_flagged
   global num_flagged_successes
   global max_flagged
   global min_rounds_success
   global max_rounds_success

   total_simulations += 1
   flagged_nodes = helper.num_flagged(graph, 'flagged')
   num_flagged += flagged_nodes

   if (finish_code < 0):
      print run_name + '> failed! only ' + str(helper.num_flagged(graph, 'flagged')) + ' people at the school learned the rumor, out of ' + str(helper.num_nodes(graph))
      num_given = 0
      num_forgot = 0
      num_fails += 1
      return
   else:
      print run_name + '> succeeded! ' + str(helper.num_flagged(graph, 'flagged')) + ' people at the school learned the rumor, out of ' + str(helper.num_nodes(graph))
      total_rounds
      num_given = 0
      num_forgot = 0
      num_flagged_successes += flagged_nodes
      total_rounds += round_num
      total_successes += 1
      min_rounds_success = min(min_rounds_success, round_num)
      max_rounds_success = max(max_rounds_success, round_num)####################################################################################


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


   # Set an specific node
   graph.node[node]['flagged'] = True
####################################################################################


####################################################################################
'''
Determines whether or not a graph is finished.
   Args:
      graph: A networkx graph instance.
      current_round: An integer recording the current number of rounds.
      max_allowed_rounds: An integer which is set to be the max allowed number of rounds.
      run_name: The name of the current simulation run
	  [spontaneous_acquisition]: An override for the file default state of spontaneous
                                 acquisition
	  [spontaneous_acquisition_chance]: An override for the file default spontaneous
                                        acquisition chance.

   Returns:
      0: If we fail to finish this graph simulation run.
      1: If we succeed to finish this graph simulation run.
      -1: If the current round number exceeds the max allowed number.
'''
####################################################################################
def finished_hook(graph, round_num, run_name):
   # Get all attributes and store them in a dictionary
   dict = nx.get_node_attributes(graph, 'flagged')

   helper.num_flagged(graph, 'flagged')

   # Make sure we haven't hit the maximum allowed round
   if (helper.exceeded_round_limit(round_num, maximum_allowed_simulation_rounds)):
      return -1 # -1 means we failed


   # A subgraph completion check should only be done if we don't spontaneously acquire information
   # and if finished is meant to include max subgraph spread
   if (
       (spontaneous_acquisition == False or spontaneous_acquisition_chance <= 0)
       and
       finished_includes_max_subgraph_spread
	  ):
      return helper.check_subgraph_spread(graph)

   # If the above check is not true, check how many nodes are flagged.
   # If all nodes are flagged, the information has successfully passed itself along.
   # Otherwise, make sure we haven't lost all of the information before trying to spread it further.
   else:
      # Iterate the nodes and see if they're flagged or not
      for val in dict:
         if(not dict[val]):
            if (helper.num_flagged(graph, 'flagged') > 0):
               return 0
            else:
               return -1
      return 1 # 1 is a successful graph
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
   for u,v in add_edge_list:
      helper.randomize_edge_list_attribute(graph, add_edge_list, 'weight', 1, 10)

   # Reconsider max betweenness nodes

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


####################################################################################
'''
Method to determine the type of gossip that will be running through the highschool.
Will print out a menu so user can determine if they want to have a random scenario
or want to choose thier own.
    Command line args: User's choice of gossip scenario
    Returns: Type of gossip which will determine how likely it will spread

'''
####################################################################################
def gossip_type_determination():
    gos_choice = -1
    print("Please select a gossip option below:")
    print("0. Random selection")
    print("1. Death of a student in the school")
    print("2. Death of a teacher in the school")
    print("3. Student is pregnant")
    print("4. Teacher and student having inappropriate relationship")
    print("5. Rumor of a pop quiz coming up")
    print("6. Rumor of a student cheating on a test")
    print("7. Rumor of two students breaking up")
    while (gos_choice < 0 or gos_choice > 7):
       gos_choice = int(input('Choose a type of gossip to spread: '))
       if (gos_choice < 0 or gos_choice > 7):
          print ('Invalid option! Try again.')
    return gos_choice


####################################################################################
'''
Prints out the info about the scenario the user has chosen
    Args:
        gossip_type: The gossip choice they have selected from the menu
        graph: A graphml instance
        death_sc: If the scenario is one involving death
    Returns:
        skip_nodes: The nodes which are to be skipped in the on_node function
        death_sc: The nodes that have died and should be removed

'''
####################################################################################
def set_up_scenario(gossip_type, graph, death_sc):
    death_sc = False
    skip_nodes = []
    if gossip_type == 0:
        gossip_type = rand.randint(1,7)

    if gossip_type == 1:
        dead_node = choice(graph.nodes())
        skip_nodes.append(dead_node)
        death_sc = True
        print("_____________________________________________________________________")
        print("Tragically there has been a death in the school,")
        print("student, " + dead_node + ", has passed away.")
        print("")
        print("Not everyone in the school knows and there is a rumor spreading about")
        print("the circumstances of " + dead_node + "'s death.")
        print("_____________________________________________________________________")

    if gossip_type == 2:
        death_sc = True

        dead_node = choice(graph.nodes())
        skip_nodes.append(dead_node)

        print("_____________________________________________________________________")
        print("Tragically there has been a death in the school.")
        print("Teacher, " + dead_node + ", has passed away.")
        print("Not everyone in the school knows and there is a rumor spreading about")
        print("the circumstances of " + dead_node + "'s death.")
        print("_____________________________________________________________________")

    if gossip_type == 3:
        preg_student = choice(graph.nodes())
        skip_nodes.append(preg_student)

        print("_____________________________________________________________________")
        print("Student, " + preg_student + ", has started coming in late, asking to")
        print("use the bathroom every 10 minutes in first period, and while once petite")
        print("has started to grow a bump in her stomach, leading to some specultation.")
        print("Not everyone in the school has noticed but there is a rumor that is ")
        print("starting to spread about that " + preg_student + " is pregnant.")
        print("_____________________________________________________________________")

    if gossip_type == 4:
        student = choice(graph.nodes())
        teacher = choice(graph.nodes())
        while student == teacher:
            teacher = choice(graph.nodes())
        skip_nodes.append(teacher)
        skip_nodes.append(student)

        print("_____________________________________________________________________")
        print("Student, " + student + ", and Teacher, " + teacher + ", have been caught hanging out")
        print("outside school hours and passing flirtatious glances during")
        print("class. There is a rumor spreading that " + student + " and " + teacher)
        print("have entered an inappropriate relationship.")
        print("_____________________________________________________________________")

    if gossip_type == 5:
        print("_____________________________________________________________________")
        print("Mr. Anderson's Calculus class has been getting harder and harder as the")
        print("semester has gone on. He warned at the beginning of the year that there")
        print("would be a pop-quiz sometime during the year that could count for 20%")
        print("of your grade. Rumors are starting that that pop-quiz will be this week.")
        print("_____________________________________________________________________")

    if gossip_type == 6:
        student = choice(graph.nodes())
        skip_nodes.append(student)
        print("_____________________________________________________________________")
        print("Mr. Anderson's Calculus class has been getting harder and harder as the")
        print("semester has gone on. " + student + " has not been doing well and other")
        print("students have started to notice. However on the last exam " + student)
        print("got a 100%, and now rumors are starting accusing " + student + " of cheating.")
        print("_____________________________________________________________________")

    if gossip_type == 7:
        student = choice(graph.nodes())
        student2 = choice(graph.nodes())

        while student == student2:
            student2 = choice(graph.nodes())
        skip_nodes.append(student)
        skip_nodes.append(student2)

        print("______________________________________________________________________________")
        print(student +" and " + student2 + " have been going out since 9th grade homecoming")
        print("however recently " + student + " has been spotted chatting up a different")
        print("student and " + student2 + " stopped wearing the ring " + student + " got them ")
        print("for thier second year anniversary. Rumors are starting to circulate that ")
        print(student + " and " + student2 + " have broken up." )
        print("_____________________________________________________________________")

    return skip_nodes, death_sc
