# Nueva función para calcular el radio de oertel a partir de los vértices
import numpy as np

def _inside_(point, vertices, z):
    
    return

def area_por_slice(grupo, z):
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
        sum_area += area
    return sum_area




def ratio(vertices, cp, N_hip = 2000, z_vals = [0,1,2]):
    """
    Estima F(cp) y la dirección u* que da el peor corte:

        F(cp) = min_u [ sum_z min(Vol(S_z ∩ H_u^+), Vol(S_z ∩ H_u^-)) ] / sum_z Vol(S_z),

    donde H_u es el hiperplano que pasa por cp con normal u (solo en coords continuas).

    Devuelve
    --------
    worst_ratio : float
        Valor estimado de F(cp).
    best_u      : np.ndarray shape (d,)
        Dirección (normal en coords continuas) que logra el mínimo.
    """

    vertices = np.asarray(vertices)
    vol_total = area_total(vertices)

    if vol_total <= 0:
        # No hay volumen, devolvemos ratio 0 y un u neutro
        return 0.0, np.zeros(d, dtype=float)

    worst_ratio = 1.0  # buscamos el mínimo sobre direcciones
    worst_u = None

    for _ in range(int(N_hip)):
        # Normal aleatoria en R^d (sólo sobre coordenadas continuas)
        
        u = np.random.randn(d) # Dirección aleatoria no normalizada
        nu = np.linalg.norm(u)
        if nu < 1e-15:
            continue # Se salta al sgte pq es muy chiquito
        u /= nu #Normalizado

        # Para esta dirección, estimamos sum_z min(Vol^+, Vol^-)        
        sum_vol_pos = 0.0
        sum_vol_neg = 0.0
        
        # Voy cortando por slice
        for z in z_vals:
            z_val = float(int(z))
            acc_pos = 0
            acc_neg = 0

            # Me quedo con (x,y)
            grupo = vertices(np.isclose(vertices[:,0],z))
            grupo = grupo[:,1:]


            