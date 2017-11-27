import networkx as nx

import pytest

import simhelper as helper
import adv_zombie_config as config

test_food_amount = 50000
test_water_amount = 10000

@pytest.fixture(scope='function')
def setup_two_graph():
    g = nx.Graph()
    g.add_node('1', infected=False, health=100, strength=1, food=test_food_amount, water=test_water_amount)
    g.add_node('2', infected=False, health=100, strength=1, food=test_food_amount, water=test_water_amount)
    g.add_edge('1','2', weight=1)
    return g

'''
Test that a zombie transmits an infection to a human successfully.
'''
def test_zombie_to_human_transmission():
    g = setup_two_graph()
    g.node['1']['infected'] = True
    gc = helper.copy_graph(g)
    
    config.infection_base_spread_chance = 1.00 # Set spread chance to 100%
    config.on_node(g, gc, '1', 1, 1, 'run_name')
    
    assert(g.node['2']['infected'])

'''
Test that a zombie does not transmit an infection to a human if there is no infection chance.
'''
def test_zombie_to_human_transmission_0_chance():
    g = setup_two_graph()
    g.node['1']['infected'] = True
    gc = helper.copy_graph(g)
    
    config.infection_base_spread_chance = 0 # Set spread chance to 100%
    config.on_node(g, gc, '1', 1, 1, 'run_name')
    
    assert not g.node['2']['infected']


'''
Test that a human heals given proper food and water levels.
'''    
def test_human_heal():
    g = setup_two_graph()
    g.node['1']['health'] = 1
    gc = helper.copy_graph(g)
    
    config.on_node(g, gc, '1', 1, 1, 'run_name')
    
    # Make sure that we have healed
    assert(g.node['1']['health'] > 1)

'''
Test that a human does not heal without proper food and water levels.
'''      
def test_human_heal_under_food_and_water_threshold():
    g = setup_two_graph()
    g.node['1']['health'] = 1
    gc = helper.copy_graph(g)
    
    # Set our threshold to be above the amount of food and water
    config.heal_food_threshold = test_food_amount+1
    config.heal_water_threshold = test_water_amount+1
    
    # Make sure we didn't heal
    assert(g.node['1']['health'] == 1)
    
'''
Test that a human does not heal without proper food levels.
'''      
def test_human_heal_under_food_threshold():
    g = setup_two_graph()
    g.node['1']['health'] = 1
    gc = helper.copy_graph(g)
    
    # Set our threshold to be above the amount of food and water
    config.heal_food_threshold = test_food_amount+1
    config.heal_water_threshold = 0 # No water threshold
    
    # Make sure we didn't heal
    assert(g.node['1']['health'] == 1)
    
'''
Test that a human does not heal without proper water levels.
'''     
def test_human_heal_under_water_threshold():
    g = setup_two_graph()
    g.node['1']['health'] = 1
    gc = helper.copy_graph(g)
    
    # Set our threshold to be above the amount of food and water
    config.heal_food_threshold = 0
    config.heal_water_threshold = test_water_amount+1
    
    # Make sure we didn't heal
    assert(g.node['1']['health'] == 1)

'''
Test that a human finds provisions given a 100% chance to find provisions.
'''         
def test_find_provisions():
    g = setup_two_graph()
    gc = helper.copy_graph(g)
    config.find_food_chance = 1.00
    config.on_not_flagged(g, gc, '1', 1, 'run_name')
    
    assert g.node['1']['food'] > test_food_amount
    assert g.node['1']['water'] > test_water_amount
    
'''
Test that a human finds no provisions given a 0% chance to find provisions.
'''     
def test_find_provisions_0_chance():
    g = setup_two_graph()
    gc = helper.copy_graph(g)
    config.find_food_chance = 0.00
    config.on_not_flagged(g, gc, '1', 1, 'run_name')
    
    assert g.node['1']['food'] == test_food_amount
    assert g.node['1']['water'] == test_water_amount
    
'''
Tests that food and water are drained at the end of a given round.
''' 
def test_food_and_water_deplete_at_end_of_round():
    g = setup_two_graph()
    
    config.food_per_round = 1000
    config.water_per_round = 1000
    
    config.after_round_end(g, [], [], [], [], 1, 'run_name')
    
    assert g.node['1']['food'] == test_food_amount - 1000
    assert g.node['1']['water'] == test_water_amount - 1000
    assert g.node['2']['food'] == test_food_amount - 1000
    assert g.node['2']['water'] == test_water_amount - 1000 
    
    
'''
Tests that starvation actually hurts a human.
'''
def test_starvation_damage():
    g = setup_two_graph()
    
    g.node['1']['food'] = 0
    g.node['2']['food'] = 0
    
    config.after_round_end(g, [], [], [], [], 1, 'run_name')
    
    assert g.node['1']['health'] < 100
    assert g.node['2']['health'] < 100
    
'''
Tests that dehydration actually hurts a human.
'''
def test_dehydration_damage():
    g = setup_two_graph()
    
    g.node['1']['water'] = 0
    g.node['2']['water'] = 0
    
    config.after_round_end(g, [], [], [], [], 1, 'run_name')
    
    assert g.node['1']['health'] < 100
    assert g.node['2']['health'] < 100