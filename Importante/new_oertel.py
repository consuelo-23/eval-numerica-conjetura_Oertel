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

        inter = interseccion(p_actual, p_next, val_actual, val_next)

        if val_actual >=0 and val_next >=0:
            new.append(p_next)

        elif val_actual >= 0 and val_next <0:
            new.append(inter)
        
        elif val_actual <0 and val_next >=0:
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

    # Vamos a sacar los ángulos uniformemente
    alphas = np.linspace(0, np.pi, Nz, endpoint=False) #excluyendo el dígito final
    betas = np.linspace(0, np.pi, Nd, endpoint=False)

    for alpha in alphas:
        # ¿Cómo defino los vectores para definir el hiperplano?
        v_z =

        for beta in betas:
            v_d =


            u = 


            # Parchar el vector en caso de... (no sé para qué casos debo parchar)

            sum_pos_side = 0
            sum_neg_side = 0

            for z in z_vals:
                # Extraer el polígono original de la slice z
                grupo = ordenados[np.isclose(ordenados[:,0], z)][:,1:]

                # Clippear el polígono del lado positivo (H_u^+) y del lado negativo (H_u^-)

                poly_pos = clip_poligono(grupo, z, cp, u)
                poly_neg = clip_poligono(grupo, z, cp, -u)

                sum_pos_side += abs(area_2d(poly_pos))
                sum_neg_side += abs(area_2d(poly_neg))

            sum_min_slices = min(sum_pos_side, sum_neg_side)

            ratio = sum_min_slices / tot_area

            if ratio < worst_ratio:
                worst_ratio = ratio
                worst_u = u
    
    return worst_ratio, worst_u