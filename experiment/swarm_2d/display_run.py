from datetime import datetime
from experiment.swarm_2d.experiment import NeatBrain2D
from experiment.swarm_2d.swarm_2d import Swarm2D, Swarm2DConfig, visualize
from experiment.swarm_2d.experiment import CreatureBrain2D
from experiment.swarm_2d.experiment import steep_sigmoid
import pickle
import sys
from experiment.save_genome import open_genome
import multiprocessing as mp


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

brains = [NeatBrain2D(genome)
          for i in range(num_birds)]
simulation = Swarm2D(brains, Swarm2DConfig(
    detector_noise_std=noise, communication=comms))

visualize(simulation, 200)
exit()
