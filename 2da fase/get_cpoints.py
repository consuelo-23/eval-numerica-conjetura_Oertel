import numpy as np
from vol_star import  _choose_batch
from scipy.spatial import ConvexHull


def get_centerpoints(
        A, #matriz
        b, #vector
        N, #puntos aleatorios a generar por cada slice
):
    
    d = A[:, 1:].shape[1] #dimensiones continuas
    z_vals = [0,1,2] #valores para z dimensión entera
    centroides = []

#primero obtener los vértices
#ocupar la fórmula para obtener el centroide




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