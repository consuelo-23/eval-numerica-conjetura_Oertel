from get_cpoints import random_vertices_by_fiber
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
from scipy.spatial import ConvexHull
from mpl_toolkits.mplot3d.art3d import Poly3DCollection


#del menos f al 2.5 mayor
seeds = [16469,18137,1934,1271,1984,18559,17021,18600,6784,16350]
         #,11394,8973,3931,2716,2693,15777,8739,10997,5060,2909,1958,8347,5672,10819,15139,16480,8197,14514,14834,17042,16283,4358,8222,2164,16300,5650,15743,18744,12723,9787,15565,6595,15274,5786]

for i in seeds:
    seed = np.random.seed(i)
    vertices = random_vertices_by_fiber([0,1,2], 2, 5)

    hull = ConvexHull(vertices)

    print(vertices)

    x = vertices[:,0]
    y = vertices[:,1]
    z = vertices[:,2]

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    ax.scatter(x, y, z, c='blue', s=10, label='Puntos Input', alpha=0.5)
    #ax.plot(x, y, z, c='blue', alpha=0.7, label='Línea de Conexión')

    envoltura = Poly3DCollection(vertices[hull.simplices])
    envoltura.set_facecolor('cyan')
    envoltura.set_alpha(0.3)
    envoltura.set_edgecolor('blue')
    envoltura.set_linewidth(0.5)

    ax.add_collection3d(envoltura)

    plt.show()