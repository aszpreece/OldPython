
import os
import pickle
def save_genome(genome, run_id, experiment_name, genome_id, path='genomes'):
    if not os.path.isdir(f'./{path}/{experiment_name}'):
        os.mkdir(f'./{path}/{experiment_name}')
    if not os.path.isdir(f'./{path}/{experiment_name}/{run_id}'):
        os.mkdir(f'./{path}/{experiment_name}/{run_id}')
    
    with open(f'./{path}/{experiment_name}/{run_id}/{genome_id}', 'wb') as fh:
        pickle.dump(genome, fh)

def open_genome(run_id, experiment_name, genome_id, path='genomes'):
    fh = open(f'./{path}/{experiment_name}/{run_id}/{genome_id}', 'rb')
    genome = pickle.load(fh)
    fh.close()
    return genome