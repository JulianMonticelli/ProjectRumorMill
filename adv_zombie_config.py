# Python Library Packages
import networkx as nx
import random as rand
import sys
import copy

import simengine as engine # < Driver in config requires this
import simhelper as helper
import simdefaults as defaults


'''
What I planned on doing that I didn't do:
    - Implement a purpose for age
    - Make the zombie simulation actually somewhat realistic
    - Balance the simulation
      (oh, but you can play around with it if you want, of course.)
    - Make humans do something more than occasionally cannibalize
        each other when they're desparate.
    - Add spontaneous infection, fix transmission
'''


#######################
# Simulation arguments#
#######################
IS_SIM_GAME = False
DEBUG_STORY = True

max_weight = 10 # 10 is the maximum weight of the given graph, this can be modified

leader_node = 0

heartbeat_interval = 30 # 30 second heartbeat interval
maximum_allowed_simulation_rounds = 15000 # Max amount of rounds before we stop running a simulation
num_runs = 1      # Default number of runs per simulation

edge_removal_chance = .01
edge_addition_chance = .01

max_hp = 100
max_morality = 10

hunger_threshold_mild = 50000
hunger_threshold_medium = 40000
hunger_threshold_serious = 30000
hunger_threshold_starving = 20000
hunger_threshold_dire = 10000

find_food_chance = .01

min_food_find = 0
max_food_find = 6000

min_water_find = 0
max_water_find = 2000

starvation_damage = 1
dehydration_damage = 1

min_cannibalism_food_gain = 5000
max_cannibalism_food_gain = 15000


min_cannibalism_water_gain = 0
max_cannibalism_water_gain = 350

# How much food and water are removed from human nodes per round
food_per_round = 2000
water_per_round = 400

# Keep these low...
strength_multiplier = .005
neighbor_multiplier = .003

heal_food_threshold = 20000
heal_water_threshold = 3000
heal_max_hp = 3
heal_food_per_hp = 100
heal_water_per_hp = 35

infection_base_spread_chance = .15
infection_damage_chance = .1
post_zombie_human_death_zombie_conversion_rate = .5

rise_from_dead_min_hp = 30
rise_from_dead_max_hp = 100


# Since max negative strength count is -.19
human_human_damage_chance = .2

min_zombie_damage = 1
max_zombie_damage = 30

min_human_damage = 1
max_human_damage = 50

chance_lose_edge = .1
chance_gain_edge = .1

body_parts_weak = ['toe', 'finger', 'thumb', 'ear', 'buttcheek', 'elbow',]
body_parts_medium = ['hand', 'foot', 'leg', 'arm', 'shoulder', 'knee', 'shin', 'forearm']
body_parts_severe = ['torso', 'head', 'neck', 'left eye', 'right eye', 'nose', 'groin']

attacks_weak = ['poked', 'smacked', 'slapped', 'stubbed', 'scratched', 'wet willied']
attacks_medium = ['punched', 'elbowed', 'kicked', 'noogied']
attacks_strong = ['bashed', 'karate chopped', 'Vulkan death gripped', 'roundhouse kicked', 'dropkicked', 'backfisted']

left_tag_sep = '['
right_tag_sep = ']'
post_tag = ': '

human_human = 'HH'
human_zombie = 'HZ'
zombie_human = 'ZH'
zombie_zombie = 'ZZ'
alert = '!!'

human_human_tag = left_tag_sep + human_human + right_tag_sep + post_tag
human_zombie_tag = left_tag_sep + human_zombie + right_tag_sep + post_tag
zombie_human_tag = left_tag_sep + zombie_human + right_tag_sep + post_tag
zombie_zombie_tag = left_tag_sep + zombie_zombie + right_tag_sep + post_tag

alert_tag = left_tag_sep + alert + right_tag_sep + post_tag
 

#######################
# Global data         #
#######################
num_nodes = 0 # The number of nodes in a starter graph
total_simulations = 0

zombies_won = 0
humans_won = 0
no_survivors = 0
num_failed = 0

zombies_left_total = 0
zombies_left_min = float('inf')
zombies_left_max = float('-inf')

humans_left_total = 0
humans_left_min = float('inf')
humans_left_max = float('-inf')

humans_left_in_round = []


####################################################################################
'''
Simulation driver, which will call the engine to begin simulations. Setup should
happen in this method, and data collection should be done inside any method necessary.
A logically sound place to put data processing is at the end of this method.
'''
####################################################################################
def simulation_driver():
    if (IS_SIM_GAME):
        zsim_game_runner()

    else:
        global num_nodes
        # Read in a graph
        graph = nx.read_graphml('custom_graphs/xsmall_zombie_adv.graphml')
        helper.output_graph_information(graph)
        num_nodes = helper.num_nodes(graph)
    
        # Start from every node in the graph
        for n in graph.node:
            sim_name = 'zsim_' + str(n)
            graphcopy = copy.deepcopy(graph)
            init(graphcopy, n, sim_name)
            engine.simulate(graphcopy, num_runs, sim_name)

        average_humans_left = 0
        average_zombies_left = 0

        if (humans_won > 0):
            average_humans_left = (humans_left_total / (float(humans_won)))
        if (zombies_won > 0):
            average_zombies_left = (zombies_left_total / (float(zombies_won)))
        
        print '\n' * 2
        print '*' * defaults.asterisk_space_count
        print 'Simulations complete.'
        print '*' * defaults.asterisk_space_count + '\n' * 2
        print 'Simulation runs where humans were desolated: ' + str(zombies_won)
        print 'Simulation runs where humans prevailed: ' + str(humans_won)
        print 'Simulation runs where nothing remained: ' + str(no_survivors)
        print 'Simulation runs that failed (> max rounds): ' + str(num_failed)
        print 'Total number of simulations runs:     ' + str(total_simulations)
        print '\n'
        print 'Zombie won statistics:'
        print '\n'
        print 'Minimum zombies left: ' + str(zombies_left_min)
        print 'Average zombies left: ' + str(average_zombies_left)
        print 'Maximum zombies left: ' + str(zombies_left_max)
        print '\n\n'
        print 'Humans won statistics:\n'
        print 'Minimum humans left: ' + str(humans_left_min)
        print 'Average humans left: ' + str(average_humans_left)
        print 'Maximum humans left: ' + str(humans_left_max)
        
        helper.create_lineplot(humans_left_in_round, \
            ylabel='Humans-Zombies at the end of simulation', \
            xlabel='Simulation run number', grid=True)
####################################################################################



####################################################################################
'''
Runs a game where you can select a node to infect and watch the outcome.
'''
####################################################################################
def zsim_game_runner():
   print '*' * 35 + '\nDESTROY ALL HUMANS IF POSSIBLE\n' + '*' * 35
   print 'The list of all nodes and their betweenness centrality: '
   graph_game = nx.read_graphml('custom_graphs/small_zombie_adv.graphml')
   betweenness_dict = helper.betweenness_centrality(graph_game)
   helper.print_iterable_linebreak(helper.sort_dict_descending(betweenness_dict))
   node_selected = -1
   while (node_selected not in graph_game.node):
      node_selected = str(input('Choose a node to infect: '))
      if (node_selected not in graph_game.node):
         print 'Invalid node! Try again.'
   sim_name = 'zs_game'
   init(graph_game, node_selected, sim_name)
   engine.simulate(graph_game, 1, sim_name)
   if (humans_won > 0):
      print 'You failed to infect all of the humans. Boo.'
   elif (zombies_won > 0):
      print 'You have succeeded to infect all humans. Good job!'
   else:
      print 'All humans and zombies are dead. This means that starvation probably killed humans while they were in the process of killing all the zombies'
####################################################################################



####################################################################################
'''
Prints a non-linebreaked damage message given an amount of damage and the name
of an agent who is receiving damage.
    Args:
        damage: The amount of damage points dealt in a hit
        node: The node that is receiving damage
'''
####################################################################################
def damage_message(damage, node):
    if (damage <= 10):
        print rand.choice(attacks_weak),
    elif (damage <= 30):
        print rand.choice(attacks_medium),
    else:
        print rand.choice(attacks_strong),

    print 'the',
    
    if (damage >= 40):
        print rand.choice(body_parts_severe),
    elif (damage % 2 == 0):
        print rand.choice(body_parts_medium),
    else:
        print rand.choice(body_parts_weak),
    
    print 'of ' + node,

    # Softspace = 0 for damage message
    sys.stdout.softspace = 0
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
    # Leader node should be set to max betweenness node
    leader = helper.get_max_betweenness_node(graph)
    
    # Leader nodes shouldn't act if they're infected.
    if graph.node[leader]['infected']:
        return


    for neighbor in nx.all_neighbors(graph, leader):
        edge_weight = graph.edge[leader][neighbor]['weight']
	  
        # If zombie neighbor, try to attack
        if ( graph.node[neighbor]['infected'] and not is_dead(graph, neighbor) ):
            # Chance  that the action occurs based on weight between the two nodes
            if ( helper.roll_weight(edge_weight, max_weight) ):
                damage = rand.randint(min_human_damage, max_human_damage)
                if (DEBUG_STORY):
                    print human_zombie_tag + 'A leader, ' + leader + ',',
                    damage_message(damage, neighbor)
                    print '. ...what a hero.'
                graph.node[neighbor]['health'] -= damage
                
                # If the leader node has killed a zombie
                if (is_dead(graph, neighbor) and DEBUG_STORY):
                    print human_zombie_tag + 'A leader has taken care of another ' \
                        + 'zombie problem. What a nice guy.'
        else:
            health_to_full = 100 - graph.node[neighbor]['health']
            if (health_to_full > 0):
                # Roll a chance based on edge weight whether or not the leader
                # will attempt to heal his neighbor.
                if ( helper.roll_weight(edge_weight, max_weight) ):
                    leader_heal_amt = rand.randint(1, health_to_full)
                    if (DEBUG_STORY):
                        print 'A leader, ' + leader + ' heals his human neighbor, ' + neighbor \
                            + ', for ' + str(leader_heal_amt) + ' health. Gee, that was nice.'
                
                # TODO: Finish
####################################################################################



####################################################################################
'''
Hook for considering a node in the graph.
    Args:
        graph: A networkx graph instance.
        graph_copy: Another networkx graph instance which is the deep copy of graph.
        node: A networkx node instance.
        round_num: The number of the current round
        run_name: The name of the current run
'''
####################################################################################
def on_node(graph, graph_copy, node, round_num, run_name):

    if (graph_copy.node[node]['infected']):
        on_flagged(graph, graph_copy, node, run_name)

        # If the node does not know, and we can spontaneously come into knowing
    else:
        on_not_flagged(graph, graph_copy, node, run_name)
####################################################################################



####################################################################################
'''
Runs operations on a flagged node to determine if it will transmit information.
    Args:
        graph: A networkx graph instance.
        graph_copy: Another networkx graph instance which is the deep copy of graph.
        node: A networkx node instance.
        run_name: The name of the current run

    Returns:
        NOTE: returns are optional
        given_flags: An integer showing how many nodes are flagged in this node operation.
'''
####################################################################################
def on_flagged(graph, graph_copy, node, run_name):
    
    # Check the unedited copy graph for flagged neighbors
    for neighbor in graph_copy.edge[node]:
        # If a zombie has no health left, forget iterating its neighbors
        if (graph.node[node]['health'] <= 0):
            break # 
	  
        # If a target graph node in both the copy and original aren't flagged
        if (not graph_copy.node[neighbor]['infected'] and not graph.node[neighbor]['infected']):
            
            # If the neighbor will be infected, then infect the neighbor
            if (will_spread(node, neighbor, graph, run_name)):
                if (DEBUG_STORY):
                    print zombie_human_tag + node + ' has infected ' + neighbor + ', who is now a zombie.'
                graph.node[neighbor]['infected'] = True
####################################################################################



####################################################################################
'''
Only humans should trigger this function. Rolls for whether or not a human may find
food or water. If food and water are above a certain level, health regenerates as well.
    Args:
        graph: A networkx graph instance.
        graph_copy: Another networkx graph instance which is the deep copy of graph.
        node: A networkx node instance.
        run_name: The name of the current method
'''
####################################################################################
def on_not_flagged(graph, graph_copy, node, run_name):
    # Are we dead? If so, return
    if (is_dead(graph, node)):
        return

    # Do we find food? 
    if (helper.chance(find_food_chance)):
        handle_find_food(graph, node)

    # Deal with neighbors
    for neighbor in nx.all_neighbors(graph, node):
        if not graph.node[neighbor]['infected']:
            human_human_interaction(graph, node, neighbor, run_name)
            # If ever our currently considered node is dead, return
            if (is_dead(graph, node)):
                return


    # Make sure the player is still alive
    if (is_dead(graph, node)):
            return

    # Heal damage
    node_health = graph.node[node]['health']
    if (node_health < 100):
        heal_amount = min(heal_max_hp, max_hp-node_health) # We don't want to heal to > 100
        if (graph.node[node]['food'] >= heal_food_threshold and graph.node[node]['water'] > heal_water_threshold):
            graph.node[node]['health'] = graph.node[node]['health'] + heal_amount
            # print 'Human ' + str(node) + ' regens ' + str(heal_amount) + ' health (current health now ' + str(graph.node[node]['health']) + ').'
            graph.node[node]['food'] = graph.node[node]['food'] - heal_amount * heal_food_per_hp
            graph.node[node]['water'] = graph.node[node]['water'] - heal_amount * heal_water_per_hp
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
          run_name: The name of the run
'''
####################################################################################
def human_human_interaction(graph, source, dest, run_name):
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
'''
Checks if a given node is dead.
    Args:
        graph: The networkx graph instance.
        node: The node in question
        
    Returns:
        True if the node is dead (health of node 0 or less)
        False if the node is alive (health of node > 0)
'''
####################################################################################
def is_dead(graph, node):
    return graph.node[node]['health'] <= 0
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
      run_name: The name of the current run

   Returns:
      True: If the information is spread in this node operation.
      False: If the information isn't spread in this node operation.
'''
####################################################################################
def will_spread(source, dest, graph, run_name):
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
Hook for considering a node in the graph.
    Args:
        graph: A networkx graph instance.

    Returns:
        given_flags: An integer showing how many nodes are flagged in this round.
        removed_flags: An integer showing how many nodes are unflagged in this round.
        run_name: The name of the current run.
'''
####################################################################################
def after_round_end(graph, add_edge_list, remove_edge_list, add_node_list, remove_node_list, round_num, run_name):
    
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
            graph.node[node]['food'] = 0 # Since we don't want negative food values
            
        if (graph.node[node]['water'] <= 0):
            is_dehydrated = True
            graph.node[node]['health'] -= dehydration_damage
            graph.node[node]['water'] = 0 # Since we don't want negative water values
            
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
        run_name: The name of the current simulation run
	  
    Returns:
       -1: If there are zombies and humans left, but we have ran out of allowed rounds
        0: If there are zombies and humans left
        1: If the virus has spread to all remaining humans
        2: If there are only humans left
        3: If nothing is left
'''
####################################################################################
def finished_hook(graph, current_round, run_name):
    # Get all attributes and store them in a dictionary
    dict = nx.get_node_attributes(graph, 'infected')
    
    # Make sure we haven't hit the maximum allowed round
    if (current_round > maximum_allowed_simulation_rounds):
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
def on_finished_run(graph, finish_code, round_num, run_name, total_time_seconds):
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
        humans_left_in_round.append(-zombies_left)
        
    elif(finish_code == 2):
        print run_tag + 'Zombies are all dead - humans have prevailed!'
        humans_won += 1
        humans_left = graph.number_of_nodes()
        humans_left_total += humans_left
        humans_left_min = min(humans_left, humans_left_min)
        humans_left_max = max(humans_left, humans_left_max)
        humans_left_in_round.append(humans_left)
    elif(finish_code == 3):
        print run_tag + 'Somehow, there was nothing left (starvation may have gotten all humans and zombies died from defense or starvation!)'
        no_survivors += 1
        humans_left_in_round.append(0)

    print '\n\n'
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
