import numpy as np
from itertools import combinations
from convex_hull import generate_convex_hull
import matplotlib.pyplot as plt
from oertel import linea_de_ensayo


def h_to_v_rep(A, b, tol = 1e-12):
    """
    Obtiene la V-representation de un cuerpo convexo a partir de la H-representation

    Input
    --------------
    A : Matriz de coeficientes (m x n)
    b : Vector (m)
    """
    m, n = A.shape # n debería ser 3
    vertices = []

    # Buscamos intersecciones de 3 planos
    for indice in combinations(range(m),n):
        # Seleccionamos las 3 filas correspondientes a los planos mediante combinación de los índices
        A_sub = A[list(indice)]
        b_sub = b[list(indice)]
        
        # Chequear que A_Sub es invertiblee
        if A_sub.shape[0] != A_sub.shape[1] or abs(np.linalg.det(A_sub)) <= tol:
            continue        

        # Obtener el valor de x
        punto = np.linalg.solve(A_sub, b_sub)

        # Verificar validez del punto encontrado
        if np.all(np.dot(A, punto) <= b + tol):
            # Verificar unicidad del punto
            new_point = True
            for v in vertices:
                if np.allclose(v, punto): # Si los puntos son iguales tira True, sino False
                    new_point = False
                    break
            if new_point: # Si es único => append
                vertices.append(punto)
        
    return np.asarray(vertices)

# Tengo que sacar los vertices por cada slice
# Luego los ordeno

def ordenar_vertices(vertices_slice, z):
    """
    ordenar los vértices (de cada slice) para poder ocupar la fórmula en la sgte función

    Input
    -----------
    vertices_slice : vértices por correspondientes a cada slice
    """
    # Trabajamos como array
    vertices = np.asarray(vertices_slice)
    
    # Elegir un centro
    # Podría ser el centro de Chebyshev, pero necesito su H representation para eso
    # Así que por mientra trabajo con el promedio de los puntos
    # Que es un punto interior por lo menos
    centro = np.asarray(np.mean(vertices, axis = 0))


    # Sacarle vector a los vértices desde el centro hasta cada uno
    vectores = []
    for i in vertices:
        u_i = i - centro
        vectores.append(u_i)

    # Ahora calcular el ángulo respecto al centro con cada uno de los vectores
    # El primero vector en de referencia
    u_ref = vectores[0]

    # Como arccos me entrega valores entre [0,pi], se ordenan por los puntos a su izquierda
    # y los puntos a su derecha, de menor a mayor ángulo
    # Luego se pueden juntar en una lista
    puntos_izq = {tuple(u_ref) : 0}
    puntos_der = {}
    
    vectores_a_ordenar = vectores[1:] # Sublista con los que hay que ordenar
    for i in vectores_a_ordenar:
        # Siguiendo la fórmula theta_i = arccos( <u_ref, u_i> / (||u_ref|| ||u_i||) )
        theta_i = np.arccos(np.dot(u_ref, i)/(np.linalg.norm(u_ref) * np.linalg.norm(i)))

        #determinar si quedó a la izquiera o la derecha
        det = u_ref[0]*i[1] - u_ref[1]*i[0]
        if det >= 0:
            puntos_izq.update({tuple(i) : theta_i})
        else:
            puntos_der.update({tuple(i) : theta_i})

    # Ahora hay que sortear los diccionarios según ángulo
    puntos_ordenados_izq = dict(sorted(puntos_izq.items(), key = lambda item : item[1]))
    puntos_ordenados_der = dict(sorted(puntos_der.items(), key = lambda item : item[1]))

    # Y juntar las listas
    puntos_ordenados = []

    for i in puntos_ordenados_izq.keys():
        punto_original = np.array(i) + centro
        punto_3d = np.array([z, punto_original[0], punto_original[1]])
        puntos_ordenados.append(punto_3d)
        
    for i in reversed(puntos_ordenados_der.keys()):
        punto_original = np.array(i) + centro
        punto_3d = np.array([z, punto_original[0], punto_original[1]])
        puntos_ordenados.append(punto_3d)
       
        
    return np.asarray(puntos_ordenados)
    


def get_centroid(vertices, z): 
    """
    Obtiene los puntos candidatos a centerpoint
    
    Input
    ----------------
    vertices : vertices previamente ordenados

    Output
    ----------------
    punto candidato a centerpoint
    """
    vertices = np.asarray(vertices)
    n = vertices.shape[0]
    area = 0
    
    v1=0
    v2=0
    for i in range(n):
        z0, x0, y0 = vertices[i]
        z1, x1, y1 = vertices[(i + 1) % n]

        A = (x0 * y1 - x1 * y0)
        area += A

        v1 += A * (x0 + x1)
        v2 += A * (y0 + y1)

    area *= 0.5
    v1 = float(v1 / (6 * area))
    v2 = float(v2 / (6 * area))

    return np.asarray([z, v1, v2])





"""
Ahora a construir la gran función
"""

def obtener_candidatos(vertices, k=5):
    """
    juntando todas la funciones en el gran output
    
    -------------------
    Parámetros:
    vértices de la figura

    -------------------
    Retorna:
    candidatos a centerpoint para procesar después con Oertel
    """

    

    candidatos = []

    # Formar Q
    Q = []
    P_0 = vertices[np.isclose(vertices[:, 0], 0)]
    P_2 = vertices[np.isclose(vertices[:, 0], 2)]

    for i in P_0:
        for j in P_2:
            q = (i + j)/2
            Q.append(q)
    Q = np.asarray(Q)


    # Proceso por slice
    for z in [0, 1, 2]:
        grupo = vertices[np.isclose(vertices[:, 0], z)]

        print("slice:", z)
        print(grupo)
    
        if z == 1:
            grupo = np.vstack([grupo, Q])


        # Nos quedamos con las coordenadas (x,y)
        grupo = grupo[:, 1:]
        
        A, b = generate_convex_hull(grupo)
        verts = h_to_v_rep(A,b)
        #QuickHUl devuelve vertices, averiguar cómo

        ordenados = ordenar_vertices(verts, z)
        
        x = [v[1] for v in ordenados]
        y = [v[2] for v in ordenados]

        plt.plot(x, y, marker="o")
        plt.show()
        print(ordenados)

        candidato = get_centroid(ordenados, z)
        candidatos.append(candidato)
        

    va = (candidatos[0] + candidatos[2])/2
    #chequear que sean distintos va y candidatos[1]
    candidatos.append(va)


    muestras = linea_de_ensayo(candidatos[1], candidatos[3])
    candidatos.append(muestras)

    return candidatos, ordenados