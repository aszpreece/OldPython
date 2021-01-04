from datetime import datetime
from experiment.flappy_swarm.flappy_swarm import FlappySwarm, visualize, FlappySwarmConfig
from experiment.flappy_swarm.experiment import NeatBirdBrain
import pickle
import sys
from experiment.save_genome import open_genome

path = ''
if len(sys.argv) < 2:
    path = input('Please provide file path:')
else:
    path = sys.argv[1]

noise = float(input('Please provide noise:'))

comms = input('enter y if comms enabled') == 'y'

num_birds = 12
fh = open(path, 'rb')
print(fh.name)
genome = pickle.load(fh)
fh.close()

brains = [NeatBirdBrain(genome)
          for i in range(num_birds)]
simulation = FlappySwarm(brains, FlappySwarmConfig(detector_noise_std=noise, communication=comms))
visualize(simulation, 200)
exit()
