import os
import re
import pickle
import matplotlib.pyplot as plt
import numpy as np
from experiment.flappy_swarm.f_test import f_test


def tolerant_mean(arrs):
    lens = [len(i) for i in arrs]
    arr = np.ma.empty((np.max(lens),len(arrs)))
    arr.mask = True
    for idx, l in enumerate(arrs):
        arr[:len(l),idx] = l
    return arr.mean(axis = -1), arr.std(axis=-1)

def plot_mean(results, axis, keys):
    
    for noise in results:
        y, error = tolerant_mean(noise)
        axis.plot(np.arange(len(y))+1, y)
        axis.fill_between(np.arange(len(y))+1, y-error, y+error, alpha=0.1)
        axis.legend(keys)

def get_run_scores(folder, keys):
        
    onlyfiles = [f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))]

    re_dict = {}

    for result_file in onlyfiles:
        match = re.search('^\[(0\.?\d?)', result_file, flags=0)
        key = match.group(1)
        re_dict.setdefault(key, []).append(result_file) 


    scores = []
    for key in keys:
        result_files = re_dict[key]
        noise_score = []
        for res in result_files:
            with open(os.path.join(folder, res), 'rb') as fh:
                error, complexity, species_count = pickle.load(fh)
                noise_score.append(error)
        scores.append(noise_score)

    scores = np.array(scores, dtype=object)
    return scores 

# with open('resultsnc/res_ce.p', 'rb') as fh:
#     nc = np.array(pickle.load(fh))

fig, ax = plt.subplots(2, sharex=True, sharey=True)

keys = ['0', '0.1', '0.2', '0.4', '0.6', '0.8']

# folder = './results/flappy_ce'
ce_scores = get_run_scores('./results/flappy_ce', keys)
cd_scores = get_run_scores('./results/flappy_cd', keys)

ax[0].set_title('Communication Enabled')
plot_mean(ce_scores, ax[0], keys)
ax[1].set_title('Communication Disabled')
plot_mean(cd_scores, ax[1], keys)

def plot_scatter_generation(scores, generation_num, axis):
    # scores[a, b, c] where a is noise b is run c is generation
    last_gen_scores = scores[:, :, generation_num]
    data = np.array([(float(noise), data) for i, noise in enumerate(keys) for data in last_gen_scores[i]])
    x, y = data.T
    axis.scatter(x, y, marker='x')
    #ax2.legend(keys)
    
     


# Display results of last run in a scatter graph
fig2, ax2 = plt.subplots(2, sharex=True, sharey=True)
ax2[0].set_title('Communication Enabled')
plot_scatter_generation(ce_scores, -1, ax2[0])
ax2[1].set_title('Communication Disabled')
plot_scatter_generation(cd_scores, -1, ax2[1])


# print(f_test(scores[:, :, -1]))

fig2.show()
fig.show()
plt.show()