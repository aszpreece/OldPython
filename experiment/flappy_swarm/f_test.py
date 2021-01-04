import numpy as np

def f_test(results):
    """Where results is a 2D numpy array where results[a, b] where a is group b is sample
    """

    print(results.shape)
    NBar = np.mean(results)
    GBar = np.mean(results, axis=1)
    print(NBar)
    print(GBar)

