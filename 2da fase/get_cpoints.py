import numpy as np
from vol_star import  _choose_batch
from scipy.spatial import ConvexHull

#primero, averiguar cómo pasar de H representation a V representation

import cdd

def obtener_vertices_desde_paredes(A, b):
    # Combinamos b y A en el formato que pide CDD: [b | -A]
    mat_cdd = np.hstack([np.array(b).reshape(-1, 1), -np.array(A)])
    
    # Creamos la matriz de CDD
    mat = cdd.Matrix(mat_cdd, number_type='float')
    mat.rep_type = cdd.RepType.INEQUALITY
    
    # El algoritmo de Doble Descripción calcula los vértices
    poly = cdd.Polyhedron(mat)
    gen = poly.get_generators()
    
    # Retornamos solo los puntos (ignorando rayos si los hubiera)
    return np.array(gen)[:, 1:]










#usando primero la de random points, o asegurando
#que los puntos tengan como primera coordenada las z
def get_centerpoints(verts):
    """
    input: vértices que forman la figura en las 3 slices (tienen que estar las 3 slices en le input)

    output: centróide de cada slice y el punto medio entre
    los centróides de la slice 0 y 2
    """
    verts = np.asarray(verts)

    """ #primero obtener la envolvente convexa global
    hull_3d = ConvexHull(verts, qhull_options= 'QJ')
    A = hull_3d.equations[:, :-1]
    b = hull_3d.equations[:, -1]

    todo esto no hace nada"""

    centroides = []
    #ahora procesamos cada fibra
    for z_val in [0,1,2]:
        """#reducir las inecuaciones de 3d a 2d para esta z en específico
        Ap = A[:,1:]
        b_shift = b - A[:,0]*z_val

        esto tampoco hace nada"""

        #obtenemos los vértices del polígono 2d en esta rodaja
        mask = (verts[:,0] == z_val)
        puntos_slice = verts[mask][:,1:]

        hull_2d = ConvexHull(puntos_slice)
        puntos = puntos_slice[hull_2d.vertices]
        
        n = puntos.shape[0]

        area = 0
        cx = 0
        cy = 0
        
        for i in range(n):
            x0, y0 = puntos[i]
            x1, y1 = puntos[(i + 1) % n]
            
            f_comun = (x0 * y1 - x1 * y0)
            area += f_comun
            cx += (x0 + x1) * f_comun
            cy += (y0 + y1) * f_comun
            
        area *= 0.5
        # Evitar división por cero
        if abs(area) < 1e-12:
            c_final = np.mean(p, axis=0)
            centroides.append([z_val, float(c_final[0]), float(c_final[1])])
        else:
            centroides.append([z_val, float(cx/(6*area)), float(cy/(6*area))])

    # 4. PUNTO MEDIO (va)
    c0, c1, c2 = centroides
    va = [(c0[0] + c2[0]) / 2, (c0[1] + c2[1]) / 2, (c0[2] + c2[2]) / 2]
    centroides.append(va)
    
    return centroides[0], centroides[1], centroides[2], centroides[3]