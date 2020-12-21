from datetime import datetime
from experiment.flappy_swarm.flappy_swarm import FlappySwarm, visualize
from experiment.flappy_swarm.experiment import NeatBirdBrain
import pickle
import sys


if len(sys.argv) < 1:
    print('Please provide file path.')

num_birds = 12
fh = open(sys.argv[1], 'rb')
print(fh.name)
genome = pickle.load(fh)
fh.close()

brains = [NeatBirdBrain(genome)
          for i in range(num_birds)]
simulation = FlappySwarm(brains)
visualize(simulation, 200)
exit()
