#
# Program default variables - these are used
# throughout the files and were moved from
# sim.py to avoid circular dependencies.
#

# Simulation arguments
maximum_allowed_simulation_rounds = 100 # Max amount of rounds before we stop running a simulation
num_runs = 3      # Default number of runs per simulation

# Transmission variables
talk_to_transmit = True   # Transmission = just talking?
transmit_chance = 0.20 # If transmit =/= talk, what is the chance upon talking

# Forgetting variables
spontaneous_forget = True          # Node can forget
spontaneous_forget_chance = 0.01      # Chance for node to forget

# Spontaneous acquisition
spontaneous_acquisition = True  # Nodes can spontaneously become flagged
spontaneous_acquisition_chance = 0.01
