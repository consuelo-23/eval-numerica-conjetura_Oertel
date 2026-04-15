import numpy as np
from vol_star import  _choose_batch
from scipy.spatial import ConvexHull

#usando primero la de random points, o asegurando
#que los puntos tengan como primera coordenada las z
def get_centerpoints(verts):
    """
    input: vértices que forman la figura en las 3 slices (tienen que estar las 3 slices en le input)

    output: centróide de cada slice y el punto medio entre
    los centróides de la slice 0 y 2
    """
    verts = np.asarray(verts)
    centroides = []

    for z in [0,1,2]:
        filtro = (verts[:,0] ==z) #filtro para quedarnos sólo con los puntos de la slice z
        puntos__ = verts[filtro][:,1:] #sin la coordenada entera
        
        hull = ConvexHull(puntos__)
        puntos = puntos__[hull.vertices]

        n = puntos.shape[0]

        sum = [z, 0, 0]
        A = 0
        area = 0
        for i in range(puntos.shape[0]): #obtenido de geeks for geeks
            x0 = puntos[i][0]
            y0 = puntos[i][1]
            x1 = puntos[(i + 1) % n][0]
            y1 = puntos[(i + 1) % n][1]

            A = (x0 * y1 - x1 * y0)
            area += A

            sum[1] += A * (x0 + x1)
            sum[2] += A * (y0 + y1)
        area *= 0.5
        v1 = float(sum[1] / (6 * area))
        v2 = float(sum[2] / (6 * area))
        centroides.append([z, v1, v2])

    va = int((centroides[0][0] + centroides[2][0]) / 2)
    vb = float((centroides[0][1] + centroides[2][1]) / 2)
    vc = float((centroides[0][2] + centroides[2][2]) / 2)
    v = [va, vb, vc]
    centroides.append(v)
    return centroides