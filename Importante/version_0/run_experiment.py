import sys
import os
import numpy as np
from get_cpoints import random_vertices_by_fiber
from get_cpoints import obtener_candidatos
from new_oertel import new_oertel
from new_oertel import linea_de_ensayo


seed = int(sys.argv[1])
np.random.seed(seed)

vertices = random_vertices_by_fiber


print("Running seed", seed)

# guarda resultados en archivo
np.save(f"result_{seed}.npy", np.array([seed]))