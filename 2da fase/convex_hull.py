import numpy as np
from scipy.spatial import ConvexHull, QhullError


def generate_convex_hull(verts : np.ndarray , tol_jitter : float = 1e-12):

  """
  Construye la envolvente conveza de los vértices y devuelte (A,b) tal que el
  poliedro es {x:Ax <=b}.

  Usa QJ (joggle) para lidiar con degneraciones. Genera una pequeña perturbación
  en los puntos de entrada; mueve ligeramente los puntos de entrada mejorando la
  robustez en el cálculo de envolventes convexas.
  
  Si aún así Qhull falla, aplica un pequeño jitter a las coordenadas continuas y
  reintenta.

  Parámetros 
  --------
  verts : np.ndarray, shape (N, 1+d)
    vértices, donde la primera coordenada es z y las d restantes son continuas.
  tol_jitter  : float
    Escala del jitter gaussiano para el fallback
  

  Retorna
  -------
  A : np.ndarray, shape(#ineq, 1+d)
  b : np.ndarray, shape(#ineq)
    Descripción H: {x : Ax <= b}
  """
  try:
    hull = ConvexHull(verts, qhull_options = "QJ")

  except QhullError:
    #Fallback. metemos jitter sólo en las coordenadas continuas (columna 1: )
    v = verts.copy()
    if v.shape[1]>=2:
      noise = tol_jitter * np.random.randn(*v[:,1:].shape) #todas las filas y desde la segunda columna en adelante
      v[:, 1:] = np.clip(v[:, 1:] + noise, 0.0, 1.0)
    
    hull = ConvexHull(v, qhull_options = "QJ")

  #Ecuaciones de las caras: normales y término independiente
  A = hull.equations[:, :-1]
  b = -hull.equations[:, -1]

  return A, b




def random_vertices_by_fiber(z_vals, d:int, n_per_z:int) -> np.ndarray:
  """
  Genera puntos aleatorios por fibra    --------> qué es una fibra?

  Parámetros
  ----------
  z_vals : escalar o iterable de ints/floats
    valores de z (fibras discretas)
  d : int
    dimensión continua
  n_per_z : int
    número de puntos a generar por cada fibra z


  Retorna
  --------
  verts : np.ndarray de shape (len(z_vals)*n_per_z, 1+d)
    cada fila es (z, p_1, ..., p_d) con p_j ~ U([0,1])
  """

  #permitir z escalar o lista
  z_list = [float(z_vals)] if np.isscalar(z_vals) else [float(z) for z in z_vals]

  blocks = []
  for z in z_list:
    #puntos continuos en [0,1]^d
    p = np.random.rand(n_per_z, d)    #(n_per_z, d)
    #columna z constante
    zcol = np.full((n_per_z, 1), float(z))    #(n_per_z, 1)
    #concatenar (z | p)
    blocks.append(np.hstack([zcol, p]))    #(n_per_z, 1+d)

  verts = np.vstack(blocks).astype(float, copy = False)
  return verts