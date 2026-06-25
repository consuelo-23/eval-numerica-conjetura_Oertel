import numpy as np
from scipy.spatial import ConvexHull


def random_vertices_by_fiber(z_vals, d: int, n_per_z: int) -> np.ndarray:
    """Generate random points in each discrete fiber z."""
    z_list = [float(z_vals)] if np.isscalar(z_vals) else [float(z) for z in z_vals]

    blocks = []
    for z in z_list:
        p = np.random.rand(n_per_z, d)
        zcol = np.full((n_per_z, 1), float(z))
        blocks.append(np.hstack([zcol, p]))

    return np.vstack(blocks).astype(float, copy=False)


def ordenar_vertices(vertices_slice, z):
    """Order 2D polygon vertices around their average point."""
    vertices = np.asarray(vertices_slice, dtype=float)
    centro = np.asarray(np.mean(vertices, axis=0))
    vectores = [v - centro for v in vertices]
    u_ref = vectores[0]

    puntos_izq = {tuple(u_ref): 0.0}
    puntos_der = {}

    for u_i in vectores[1:]:
        denom = np.linalg.norm(u_ref) * np.linalg.norm(u_i)
        if denom == 0:
            theta_i = 0.0
        else:
            cos_theta = np.clip(np.dot(u_ref, u_i) / denom, -1.0, 1.0)
            theta_i = np.arccos(cos_theta)

        det = u_ref[0] * u_i[1] - u_ref[1] * u_i[0]
        if det >= 0:
            puntos_izq[tuple(u_i)] = theta_i
        else:
            puntos_der[tuple(u_i)] = theta_i

    puntos_ordenados_izq = dict(sorted(puntos_izq.items(), key=lambda item: item[1]))
    puntos_ordenados_der = dict(sorted(puntos_der.items(), key=lambda item: item[1]))

    puntos_ordenados = []
    for u_i in puntos_ordenados_izq.keys():
        punto_original = np.array(u_i) + centro
        puntos_ordenados.append(np.array([z, punto_original[0], punto_original[1]]))

    for u_i in reversed(puntos_ordenados_der.keys()):
        punto_original = np.array(u_i) + centro
        puntos_ordenados.append(np.array([z, punto_original[0], punto_original[1]]))

    return np.asarray(puntos_ordenados)


def get_centroid(vertices, z):
    """Compute the centroid of an ordered polygon in slice z."""
    vertices = np.asarray(vertices, dtype=float)
    n = vertices.shape[0]
    area = 0.0
    cx = 0.0
    cy = 0.0

    for i in range(n):
        _, x0, y0 = vertices[i]
        _, x1, y1 = vertices[(i + 1) % n]
        cross = x0 * y1 - x1 * y0
        area += cross
        cx += cross * (x0 + x1)
        cy += cross * (y0 + y1)

    area *= 0.5
    if abs(area) <= 1e-15:
        mean_xy = vertices[:, 1:].mean(axis=0)
        return np.asarray([z, mean_xy[0], mean_xy[1]], dtype=float)

    cx = float(cx / (6 * area))
    cy = float(cy / (6 * area))
    return np.asarray([z, cx, cy], dtype=float)


def linea_de_ensayo(v1, va, n_muestras=50):
    """Generate interior points from v1 toward va, excluding t=0 and t=1."""
    v1 = np.asarray(v1, dtype=float)
    va = np.asarray(va, dtype=float)
    ts = np.linspace(1 / n_muestras, 1, n_muestras, endpoint=False)
    return [(1 - t) * v1 + t * va for t in ts]


def obtener_candidatos(vertices, n_muestras=50, z_vals=(0, 1, 2)):
    """
    Build Oertel candidate points.

    candidates[0], candidates[1], candidates[2] are the centroids of slices
    z=0, z=1, z=2. candidates[3] is va=(v0+v2)/2 when distinct from v1.
    Later candidates are points on the segment from v1 to va.
    """
    vertices = np.asarray(vertices, dtype=float)
    candidatos = []

    p_0 = vertices[np.isclose(vertices[:, 0], 0)]
    p_2 = vertices[np.isclose(vertices[:, 0], 2)]
    q = np.asarray([(i + j) / 2 for i in p_0 for j in p_2], dtype=float)

    ordenados_todos = []
    for z in z_vals:
        grupo = vertices[np.isclose(vertices[:, 0], z)]
        if z == 1 and len(q) > 0:
            grupo = np.vstack([grupo, q])

        grupo_xy = grupo[:, 1:]
        hull = ConvexHull(grupo_xy)
        hull_xy = grupo_xy[hull.vertices]
        ordenados = ordenar_vertices(hull_xy, z)
        ordenados_todos.append(ordenados)
        candidatos.append(get_centroid(ordenados, z))

    va = (candidatos[0] + candidatos[2]) / 2
    if not np.allclose(va, candidatos[1]):
        candidatos.append(va)
        candidatos.extend(linea_de_ensayo(candidatos[1], candidatos[3], n_muestras))

    return candidatos, ordenados_todos

