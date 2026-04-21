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



def get_cpoints(
        A, #matriz
        b, #vector
        d= 2, #dimensiones continuas
        z_vals = [0,1,2], #valores para z dimensión entera
        N=10**7, #número de puntos aleatorios a generar para cada slice
        batch = None, #tamaño de lote para la generación de puntos aleatorios
        target_mb = None, #memoria target para calcular el tamaño de lote
        tol = 1e-9 #tolerancia
    ):
    
    """
    Devuelve
    -----------
    v0, v1, v2 y va, puntos que nos interesan
    """

    n_ineq = A.shape[0]

    #para controlar la memoria RAM, lo mismo que hizo la María
    if batch is None:
        m_auto = _choose_batch(n_ineq, target_mb=target_mb)
        batch = min(N, max(1000, m_auto))
    else:
        batch = int(batch)
        if batch <= 0:
            batch = min(N, max(1000, _choose_batch(n_ineq, target_mb=target_mb)))



    centroides = []
    for z in z_vals:
        Az = A[:,0] #sólo primera columna de A
        Ap = A[:,1:] #le saco la primera columna a A
        b_p = b - Az*z #ahora tenemos la desigualdad para un figura 2D
        #Ax*x + Ay*y <= b - Az*z
        #siendo z la primera coordenada fija


        gen = 0
        points_inside = []
        #para cada z, encuentra el centroide de la slice definida por Ap y b_p
        while gen < N:
            m = min(batch, N-gen)
            p = np.random.rand(m,d) #generamos puntos aleatorios entre 0 y 1
            inside = np.all((p @ Ap.T) <= (b_p + tol), axis=1) 
            #verificamos cuáles caen dentro de la slice
            if inside.any():
                points_inside.append(p[inside]) #guardamos los que caen dentro
            gen += m
        
        if points_inside:
            points_inside = np.vstack(points_inside) #unimos todos los puntos dentro
            centroide = points_inside.mean(axis=0) #calculamos el centroide de esos puntos
            centroides.append(np.concatenate([[z], centroide])) #guardamos el centroide con su z correspondiente

        #ahora falta agregar el 4to punto de interés
        #el promedio entre el centroide de la slice 0 y de la slice 2
    
    v_a = (centroides[0] + centroides[2]) / 2
    return centroides[0], centroides[1], centroides[2], v_a