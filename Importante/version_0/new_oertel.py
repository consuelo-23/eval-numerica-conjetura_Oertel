# Nueva función para calcular el radio de oertel a partir de los vértices
import numpy as np


def area_2d(grupo):
    """
    2D -> 2D
    """
    grupo = np.asarray(grupo)
    n = grupo.shape[0]
    area = 0

    for i in range(n):
        x0, y0 = grupo[i]
        x1, y1 = grupo[(i + 1) % n]

        A = (x0 * y1 - x1 * y0)
        area += A

    area *= 0.5        
    return area


def area_total(vertices, z_vals = [0,1,2]):
    """
    Retorna el la suma de los volúmenes de cada slice utilizando la fórmula de shoelace
    3D -> 3D
    """
    sum_area = 0
    for z in z_vals:
        grupo = vertices[np.isclose(vertices[:, 0], z)]
        grupo = grupo[:,1:]

        grupo = np.asarray(grupo)
        n = grupo.shape[0]
        area = 0

        for i in range(n):
            x0, y0 = grupo[i]
            x1, y1 = grupo[(i + 1) % n]

            A = (x0 * y1 - x1 * y0)
            area += A

        area *= 0.5
        area = abs(area)
        sum_area += area
    return sum_area


def lado_hiperplano(punto, z, cp, u):
    """
    determina de qué lado del hiperplano está un punto
    (izq positivo, derecha negativo)
    
    input
    -------------------

    punto : vertice del ConvexHull
    
    z : z de la slice

    cp : centerpoint a comparación
    
    u : dirección hiperplano
    """
    x_prima = np.array([z, punto[0], punto[1]])

    return np.dot(u, x_prima - cp)


def interseccion(p0, p1, val0, val1):
    """
    determina la intersección de una arista al hiperplano
    """
    t = val0/(val0-val1)

    return p0 + t * (p1 - p0)

def clip_poligono(poligono, z, cp, u):

    poligono = np.asarray(poligono, dtype = float)

    n = len(poligono)

    new = []

    for i in range(len(poligono)):
        p_actual = poligono[i]
        p_next = poligono[(i+1) % n]

        val_actual = lado_hiperplano(p_actual, z, cp, u)
        val_next = lado_hiperplano(p_next, z, cp, u)
        
        if val_actual >=0 and val_next >=0:
            new.append(p_next)

        elif val_actual >= 0 and val_next <0:
            inter = interseccion(p_actual, p_next, val_actual, val_next)
            new.append(inter)
        
        elif val_actual <0 and val_next >=0:
            inter = interseccion(p_actual, p_next, val_actual, val_next)
            new.append(inter)
            new.append(p_next)
        
    return new


def ratio(ordenados, cp, Nz = 100, Nd = 100, z_vals = [0,1,2]):
    """
    Obtiene F(cp) y la dirección u* que da el peor corte:

        F(cp) = min_u [ sum_z min(Vol(S_z ∩ H_u^+), Vol(S_z ∩ H_u^-)) ] / sum_z Vol(S_z),

    donde H_u es el hiperplano que pasa por cp con normal u (solo en coords continuas).

    Devuelve
    --------
    worst_ratio : float
        Valor estimado de F(cp).
    best_u      : np.ndarray shape (d,)
        Dirección (normal en coords continuas) que logra el mínimo.
    """

    ordenados = np.asarray(ordenados)
    tot_area = abs(area_total(ordenados)) # suma de las áreas de cada slice -> área total


    if tot_area <= 0:
        # No hay volumen, devolvemos ratio 0 y None u
        return 0.0, None

    worst_ratio = 1.0  # Buscamos el mínimo sobre direcciones
    worst_u = None

    # Vamos a sacar los ángulos en 2 for anidados
    for i in range(Nz):
        alpha = i * np.pi / Nz

        for j in range(Nd):
            beta = j * np.pi / Nd
            
            u = np.array([np.cos(beta), np.cos(alpha) * np.sin(beta), np.sin(alpha) * np.sin(beta)], dtype=float)

            sum_pos_side = 0
            sum_neg_side = 0

            for z in z_vals:
                # Extraer el polígono original de la slice z
                grupo = ordenados[np.isclose(ordenados[:,0], z)][:,1:]

                # Clippear el polígono del lado positivo (H_u^+) y del lado negativo (H_u^-)

                poly_pos = clip_poligono(grupo, z, cp, u)
                sum_pos_side += abs(area_2d(poly_pos))

            sum_neg_side = tot_area - sum_pos_side
            sum_min_slices = min(sum_pos_side, sum_neg_side)

            ratio = sum_min_slices / tot_area

            if ratio < worst_ratio:
                worst_ratio = ratio

                # Actualizar u según qué lado se tomó
                if sum_pos_side <= sum_neg_side:
                    worst_u = u
                else:
                    worst_u = -u

    return worst_ratio, worst_u


def new_oertel(ordenados, puntos_test, z_vals = [0,1,2], Nz= 100, Nd = 100, N_Muestras = 50):
    """
    Busca un centerpoint aproximado maximizando:
        F(cp) = min_u  [ sum_z min(Vol(S_z ∩ H_u^+), Vol(S_z ∩ H_u^-)) ] / sum_z Vol(S_z)

    Devuelve:
    bestCP : mejor centerpoint
    bestF : valor de F(bestCP)
    bestU : dirección que produce el peor corte para bestCP
    """

    #--------- búsqueda de centerpoint sobre puntos específicos ------
    bestF = -np.inf
    bestCP = None
    bestU = None
    
    contador_de_indice = 0
    for candidato in puntos_test: #iterar sobre los centerpoints candidatos
        cp = np.asarray(candidato, dtype = float) #verificar que sea array

        #evaluar el ratio de oertel

        F_cp, u_cp = ratio(ordenados, cp, Nz=Nz, Nd=Nd, z_vals=z_vals)
        #que tan central es el punto

        print(f"Punto{cp} -> F: {F_cp}")

        #guardamos el mejor de los 4 puntos
        if F_cp > bestF:
            bestF = float(F_cp)
            bestCP = cp.copy()
            bestU = None if u_cp is None else np.asarray(u_cp, dtype = float)
            if contador_de_indice <=3:
                indice = contador_de_indice
            else:
                indice = (contador_de_indice - 3) / N_Muestras
        contador_de_indice += 1
    
    print("Best centerpoint: ", bestCP, "Best F: ", bestF, "Best u: ", bestU, "índice: ", indice)
    return bestCP, float(bestF), bestU
