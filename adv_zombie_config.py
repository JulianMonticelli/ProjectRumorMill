# Python Library Packages
import networkx as nx
import random as rand
import sys
import copy

# Cyclical dependency to main
import simengine as engine # < Driver in config requires this
import simhelper as helper
import simdefaults as defaults


#######################
# Simulation arguments#
#######################
IS_SIM_GAME = True
DEBUG_STORY = True

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

body_parts_weak = ['toe', 'finger', 'thumb', 'ear', 'buttcheek']
body_parts_medium = ['hand', 'foot', 'leg', 'arm', 'shoulder', 'knee']
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
      print 'Total number of simulations runs:    ' + str(total_simulations)
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

   if (graph_copy.node[node]['infected']):
      on_flagged(graph, graph_copy, node, max_weight, run_name)

      # If the node does not know, and we can spontaneously come into knowing
   else:
      on_not_flagged(graph, graph_copy, node, max_weight, run_name)
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

   Returns:
      NOTE: returns are optional
      given_flags: An integer showing how many nodes are flagged in this node operation.
'''
####################################################################################
def on_flagged(graph, graph_copy, node, max_weight, run_name):
   
   # Check the unedited copy graph for flagged neighbors
   for neighbor in graph_copy.edge[node]:
      # If a zombie has no health left, forget iterating its neighbors
      if (graph.node[node]['health'] <= 0):
         break # 
	  
      # If a target graph node in both the copy and original aren't flagged
      if (not graph_copy.node[neighbor]['infected'] and not graph.node[neighbor]['infected']):
         
         # If the neighbor will be infected, then infect the neighbor
         if (will_spread(node, neighbor, graph, max_weight, run_name)):
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
      max_weight: The maximum weight of the graph
      run_name: The name of the current method
'''
####################################################################################
def on_not_flagged(graph, graph_copy, node, max_weight, run_name):

   # Are we dead? If so, return
   if (is_dead(graph, node)):
      return

   # Do we find food? 
   if (helper.chance(find_food_chance)):
      handle_find_food(graph, node)

   # Leader nodes and non-leader nodes think differently
   if not node == leader_node:
      for neighbor in nx.all_neighbors(graph, node):
         if not graph.node[neighbor]['infected']:
            human_human_interaction(graph, node, neighbor, max_weight, run_name)
            # If ever our currently considered node is dead, return
            if (is_dead(graph, node)):
               return

   elif node == leader_node:
      print 'detected leader node!!!' 
      handle_leader_node(graph, node)

      # Do something with the neighbor? Could help or harm

      # Make sure the player is still alive

         + str(last_heartbeat) + ' seconds ago.'
####################################################################################
