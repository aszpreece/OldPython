from experiment.save_genome import open_genome
import pickle
from experiment.flappy_swarm.flappy_swarm import FlappySwarm, FlappySwarmConfig
from experiment.flappy_swarm.experiment import NeatBirdBrain
# For each result file, access the genomes for that run and run a version without communication enabled

def run_genomes(run_num, noise):
    num_birds = 12
    def bird_fitness(genotype):
        # Create a bunch of bird brains and put them in a simulation
        
        n = 5
        score_total = 0
        for i in range(n):
            brains = [NeatBirdBrain(genotype) for i in range(num_birds)]
            simulation = FlappySwarm(brains, FlappySwarmConfig(detector_noise_std=noise, communication=False))

            while len(simulation.birds) and simulation.obstacles_cleared < 10:
                simulation.update()

            if simulation.bird_edge_crashes == 0:
                score_total += simulation.score

        return score_total / n

    fitnesses = []
    for i in range(1, 121):
        genome = open_genome(f'[{noise}][{run_num}]', 'flappy', i, path='genomes')
        score = bird_fitness(genome)
        fitnesses.append(score)
    return fitnesses

noises = ['0', '0.2', '0.4', '0.6', '0.8']
runs = 14
all_scores = []

c = 0
total_its = 14 * 5

for noise in noises:
    
    noise_scores = []
    for i in range(runs):
        c+=1
        print(f'{c}/{total_its}')
        scores= run_genomes(i, float(noise) if float(noise) > 0 else 0)
        noise_scores.append(scores)
    all_scores.append(noise_scores)

with open('./resultsnc/res.p', 'wb') as fh:
    pickle.dump(all_scores, fh)