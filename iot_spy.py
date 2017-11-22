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
Handles humans finding food.
'''
####################################################################################
def handle_find_food(graph, node):
    food_find = rand.randint(min_food_find, max_food_find)
    water_find = rand.randint(min_water_find, max_water_find)
    
    if (DEBUG_STORY):
        print alert_tag + node + ' finds provisions, and gains ' + str(food_find) + ' food and ' + str(water_find) + ' water.'
    
    graph.node[node]['food'] += food_find
    graph.node[node]['water'] += water_find
####################################################################################



####################################################################################
'''
Method that deals with the interaction between humans.
    Args:
        graph: A networkx graph instance
        source: A source node
        dest: A dest node
        max_weight: The maximum weight of the graph
        run_name: The name of the run
'''
####################################################################################
def human_human_interaction(graph, source, dest, max_weight, run_name):
    edge_weight = graph.edge[source][dest]['weight']
    # Does anything happen at all?
    if ( helper.roll_weight( edge_weight, max_weight ) ):
        if ( graph.node[source]['food'] < hunger_threshold_dire):
            if ( helper.roll_weight ( max_morality - graph.node[source]['morality'], max_morality) ):
                if (attempt_to_cannibalize(graph, source, dest)):
                    cannibalism_food_gain = rand.randint(min_cannibalism_food_gain, max_cannibalism_food_gain)
                    cannibalism_water_gain = rand.randint(min_cannibalism_water_gain, max_cannibalism_water_gain)  
                    if (DEBUG_STORY):
                        print alert_tag + source + ' cannibalizes ' + dest + ' and gains ' + str(cannibalism_food_gain) \
                                + ' food and ' + str(cannibalism_water_gain) + ' water.'
        # Cannibalizing is the only concern currently
        if ( is_dead(graph, source) ):
            return
####################################################################################



####################################################################################

####################################################################################
def is_dead(graph, node):
    return graph.node[node]['health'] <= 0
####################################################################################



####################################################################################

####################################################################################
def handle_leader_node(graph, leader, max_weight, run_name):
    for neighbor in nx.all_neighbors(graph, leader):
        edge_weight = graph.edge[leader][neighbor]['weight']
	  
        # If zombie neighbor, try to attack
        if ( graph.node[neighbor]['infected'] and not is_dead(graph, neighbor) ):
            if ( helper.roll_weight(edge_weight, max_weight) ):
                damage = rand.randint(min_human_damage, max_human_damage)
                print human_zombie_tag + 'A leader, ' + leader + ',',
                damage_message(damage, neighbor)
                '. ...what a hero.'
                graph.node[neighbor]['health'] -= damage
                
                # If the leader node has killed a zombie
                if (is_dead(graph, neighbor)):
                    print human_zombie_tag + 'A leader has taken care of another zombie problem. What a nice guy.'

                # TODO: Finish
####################################################################################




####################################################################################
'''
Human-human cannibalization attempt for extremely hungry humans.
    Args:
        graph: A networkx graph instance
        source: A source node (the one attempting to cannibalize the victim)
        dest: A destination node (the victim of the cannibalization attempt)

    Returns:
        True: if the aggressor can cannibalize the victim
        False: if the victim has survived
'''
####################################################################################
def attempt_to_cannibalize(graph, source, dest):
    source_str = graph.node[source]['strength']
    dest_str = graph.node[dest]['strength']
    source_str_advantage = (source_str-dest_str) * strength_multiplier
    if (DEBUG_STORY):
        print human_human_tag + 'Desperate, ' + source + ' tries to attack',
        print dest + ' in an attempt to cannibalize ' + dest + '!'
    if (helper.chance(human_human_damage_chance + source_str_advantage)):
        damage_amount = rand.randint(min_human_damage, max_human_damage)
        graph.node[dest]['health'] -= damage_amount
        if (DEBUG_STORY):
            print human_human_tag + source,
            damage_message(damage_amount, dest)
            print ' for ' + str(damage_amount) + ' damage.'
    if (is_dead(graph, dest)):
        if (DEBUG_STORY):
            print alert_tag + source + ' has killed ' + dest + ' out of hunger.'
            return True
    
    # If the dest is still alive to defend itself, regardless of
    if (DEBUG_STORY):
        print human_human_tag + dest + ' attempts to defend themself from ' + source + '.'
    if (helper.chance(human_human_damage_chance - source_str_advantage)):
        damage_amount = rand.randint(min_human_damage, max_human_damage)
        graph.node[source]['health'] -= damage_amount
        if (DEBUG_STORY):
            print human_human_tag + dest,
            damage_message(damage_amount, source)
            print ' for ' + str(damage_amount) + ' damage.'
    if (is_dead(graph, source)):
        if (DEBUG_STORY):
            print alert_tag + dest + ' has killed ' + source + ' in self-defense.'
    return False
####################################################################################



####################################################################################
'''
Determine if a zombie will infect a human. This also takes care of damage incurred
by a failed or successful transmission.
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
    
    # Get current weight
    curr_weight = graph.edge[source][dest]['weight']
    
    # Will they engage at all?
    if ( helper.roll_weight (curr_weight , max_weight ) ):
        	
        str_chance = (graph.node[source]['strength'] - graph.node[dest]['strength']) * strength_multiplier

        # How many human and zombie neighbors the human we are considering has
        human_neighbor_count = 0
        zombie_neighbor_count = 0

        for neighbor in nx.all_neighbors(graph, dest):
            if (graph.node[neighbor]['infected']):
                zombie_neighbor_count += 1
            else:
                human_neighbor_count += 1

        # Modify the chance of infection based on number of humans and number of zombies surrounding dest node
        inf_chance_mod = min(infection_base_spread_chance-.01, str_chance - ((1 + human_neighbor_count - zombie_neighbor_count) * neighbor_multiplier))
        # Will the human deal damage to the zombie while defending him or herself?
        if ( helper.chance(infection_damage_chance - str_chance) ):
            human_zombie_damage = rand.randint(min_human_damage, max_human_damage)
            graph.node[source]['health'] -= human_zombie_damage
            if (DEBUG_STORY):
                print human_zombie_tag + source + ' approaches ' + dest + ', and ' + dest,
                damage_message(human_zombie_damage, source)
                print ', dealing '  + str(human_zombie_damage) + ' damage to ' + source
                if ( is_dead(graph, source) ):
                    if (DEBUG_STORY):
                        print human_zombie_tag + dest + ' has killed ' + source + ' in self-defense.'
                    return False

        # If we transmit the infection - biting deals no damage
        if ( helper.chance((infection_base_spread_chance + inf_chance_mod)) ):
            if (DEBUG_STORY):
                print zombie_human_tag + source + ' bites ' + dest + '!'
            return True

        # Check for damage to human (if they have not been turned into a zombie)
        if ( helper.chance(infection_damage_chance + str_chance) ):
            zombie_human_damage = rand.randint(min_zombie_damage, max_zombie_damage)
            if (DEBUG_STORY):
                print zombie_human_tag + source + ' closes in on ' + dest + ', and',
                damage_message(zombie_human_damage, dest)
                print ', dealing ' + str(zombie_human_damage) + ' damage to ' + dest
            graph.node[dest]['health'] -= rand.randint(min_zombie_damage, max_zombie_damage)
            if (is_dead(graph, dest)):
                if (DEBUG_STORY):
                    print alert_tag + dest + ' has been killed by a zombie.'
                if (helper.chance(post_zombie_human_death_zombie_conversion_rate)):
                    if (DEBUG_STORY):
                        print alert_tag + dest + ' has risen from the dead and become a zombie.'
                    graph.node[dest]['health'] = rand.randint(rise_from_dead_min_hp, rise_from_dead_max_hp)
                    return True
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
def before_round_start(graph, max_weight, add_edge_list, remove_edge_list, run_name):
    leader_node = helper.get_max_betweenness_node(graph)
    for node in graph.node:
        for neighbor in nx.all_neighbors(graph, node):
            if helper.chance( chance_lose_edge ):
                helper.add_edge_to_list(remove_edge_list, node, neighbor)
            if helper.chance( chance_gain_edge / 2 ):
                gain_edge(graph, node, add_edge_list, run_name)
            if helper.chance( chance_gain_edge / 2 ):
                gain_edge(graph, neighbor, add_edge_list, run_name)
####################################################################################


####################################################################################
'''
A function to gain an edge to a random node.
    Args:
        graph: A graph instance
        node: A node that we want to add an edge from
        add_edge_list: A list of edges passed to us from the engine
        run_name: The name of the run
'''
####################################################################################
def gain_edge(graph, node, add_edge_list, run_name):
    # Avoid self-edges and infinite loops:
    second_node = node
    if (graph.number_of_nodes > 1):
        while(second_node == node):
            second_node = rand.choice(graph.nodes())
    else:
        return
    helper.add_edge_to_list(add_edge_list, node, second_node)
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
Hook for considering a node in the graph.
   Args:
      graph: A networkx graph instance.

   Returns:
      given_flags: An integer showing how many nodes are flagged in this round.
      removed_flags: An integer showing how many nodes are unflagged in this round.
      run_name: The name of the current run.
'''
####################################################################################
def after_round_end(graph, add_node_list, remove_node_list, run_name):
    for node in graph.node:
        is_starving = False
        is_dehydrated = False
        if (is_dead(graph, node)):
            helper.add_node_to_list(remove_node_list, node)
            continue

        graph.node[node]['food'] -= food_per_round
        graph.node[node]['water'] -= water_per_round
	  
        if (graph.node[node]['food'] <= 0):
            is_starving = True
            graph.node[node]['health'] -= starvation_damage
        if (graph.node[node]['water'] <= 0):
            is_dehydrated = True
            graph.node[node]['health'] -= dehydration_damage
        if (is_dead(graph, node)):
            helper.add_node_to_list(remove_node_list, node)
            if (DEBUG_STORY):
                if (is_starving and is_dehydrated):
                    print alert_tag + node + ' died from starvation and dehydration!'
                elif (is_starving):
                    print alert_tag + node + ' died from starvation!'
                elif (is_dehydrated):
                    print alert_tag + node + ' died from dehydration!'
            continue

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

    # Give all nodes a false flag
    helper.create_node_attribute(graph, 'infected', False)
    
    # Save edge weight, as we are going to wipe graph
    dict = nx.get_edge_attributes(graph, 'weight')
    
    # Write 1 weight to all edges
    nx.set_edge_attributes(graph, 'weight', 1)
    
    # Restore initial edges
    for n1,n2 in dict:
        graph.edge[n1][n2]['weight'] = dict[n1,n2]
    
    
    # Set a specific node
    graph.node[node]['infected'] = True
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
     -1: If there are zombies and humans left, but we have ran out of allowed rounds
      0: If there are zombies and humans left
      1: If the virus has spread to all remaining humans
      2: If there are only humans left
      3: If nothing is left
'''
####################################################################################
def finished_hook(graph, current_round, max_allowed_rounds, run_name):
    # Get all attributes and store them in a dictionary
    dict = nx.get_node_attributes(graph, 'infected')
    
    # Make sure we haven't hit the maximum allowed round
    if (current_round > max_allowed_rounds):
        return -1 # -1 means we ran out of allowed rounds
    

    # Iterate the nodes and see if they're flagged or not
    if (len(dict) == 0):
        return 3 # Indicates nothing is left
    for val in dict:
        if(not dict[val]):
            #print '[' + val  + ']: ' + str(dict[val])
            if (helper.num_flagged(graph, 'infected') > 0):
                return 0
            else:
                return 2
    return 1 # 1 indicates that zombies have won (and humans have lost)
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
    global total_simulations
    global zombies_won, humans_won, no_survivors, num_failed
    global humans_left_total, humans_left_min, humans_left_max
    global zombies_left_total, zombies_left_min, zombies_left_max
    run_tag = left_tag_sep + run_name + right_tag_sep + post_tag


    total_simulations += 1
    if (finish_code < 0):
        print run_tag + 'Graph ran until completion. Failed to infect all humans, zombies not dead.'
        num_failed += 1
    elif(finish_code == 1):
        print run_tag + 'Humans are all dead - zombies remain'
        zombies_won += 1
        zombies_left = graph.number_of_nodes()
        zombies_left_total += zombies_left
        zombies_left_min = min(zombies_left, zombies_left_min)
        zombies_left_max = max(zombies_left, zombies_left_max)

    elif(finish_code == 2):
        print run_tag + 'Zombies are all dead - humans have prevailed!'
        humans_won += 1
        humans_left = graph.number_of_nodes()
        humans_left_total += humans_left
        humans_left_min = min(humans_left, humans_left_min)
        humans_left_max = max(humans_left, humans_left_max)
    elif(finish_code == 3):
        print run_tag + 'Somehow, there was nothing left (starvation might have gotten all zombies and humans!)'
        no_survivors += 1

    print '\n\n'
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
