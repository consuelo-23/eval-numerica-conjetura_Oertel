import numpy as np
from scipy.optimize import linprog
from scipy.special import gamma
import time as time

#encontrar puntos interiores, partiendo por el centro de chebyshev
def CentroChebyshev(A, b):
    #x_n variables de x, más una de radio
    c = np.zeros(A.shape[1]+1)
    c[-1] = -1 #maximizar el radio equivale a minimizar -r

    #normas de cada fila de A
    norms = np.linalg.norm(A, axis=1)

    #agrego la columna de las normas a A
    A_norm = np.hstack((A, norms.reshape(-1, 1)))
    b_norm = b

    resultado = linprog(c, A_ub=A_norm, b_ub=b_norm)

    center = resultado.x[:-1]
    radio = resultado.x[-1]

    if resultado.success:
        return center, radio
    else:
        raise ValueError("No se pudo encontrar un punto interior.")

def VolumenBolaInicial(n, r_inicial):
    return (np.pi ** (n / 2) * (r_inicial ** n)) / gamma((n / 2) + 1)


def EstimarRadioExterno(A, b, centro_cheby):
  n = A.shape[1]
  distancias_max = []

  for i in range(n):
    c = np.zeros(n)
    c[i] = 1

    sol_min = linprog(c, A_ub = A, b_ub = b, bounds=(None, None))
    sol_max = linprog(-c, A_ub = A, b_ub = b, bounds=(None, None))

    d1 = abs(sol_min.fun - centro_cheby[i])
    d2 = abs(-sol_max.fun - centro_cheby[i])

    distancias_max.append(max(d1, d2))

  return np.linalg.norm(distancias_max)

def HITnRUNstep(x, A, b, center, r):
  n = len(x)
  d = np.random.normal(0, 1, n)
  d = d / np.linalg.norm(d)  #normalizar

  #encontrar la intersección con las restricciones
  Ad = A @ d
  b_Ax = b - A @ x

  t_min = -1e20 #cambié los infty por números grandes
  t_max = 1e20

  #restricciones  (acá tengo dudas pero parece q funciona)
  for i in range(len(b_Ax)):
      val = b_Ax[i] / Ad[i]
      if Ad[i] >0:
          t_max = min(t_max, val)
      elif Ad[i] < 0:
          t_min = max(t_min, val)

  #necesito que esté dentro de la bola de radio r_next
  a_cuad = 1 #np.linalg.norm(d)**2 ya es 1
  b_cuad = 2 * np.dot(x - center, d)
  c_cuad = np.linalg.norm(x - center)**2 - r**2

  disc = b_cuad**2 - 4*a_cuad*c_cuad
  if disc >= 0:
      sqrt_disc = np.sqrt(disc)
      t1 = (-b_cuad - sqrt_disc) / (2*a_cuad)
      t2 = (-b_cuad + sqrt_disc) / (2*a_cuad)

      t_min = max(t_min, t1)
      t_max = min(t_max, t2)

  if t_min < t_max:
      t = np.random.uniform(t_min, t_max)
      x = x + t * d

  return x


def EstimateVolumeConvex(A, b, samples=10**7, tol = 0.9999):
    #start_time = time.time()

    #inicialización
    m,n = A.shape  # Dimensión del espacio
    center, r_inicial = CentroChebyshev(A, b)
    r_outer = EstimarRadioExterno(A, b, center)

    vol = VolumenBolaInicial(n, r_inicial)

    #calcular número de pasos (n*log2(ratio))
    ratio_radios = r_outer / r_inicial
    num_steps = int(np.ceil(n * np.log2(ratio_radios)))
    factor_expansion = (ratio_radios) ** (1/num_steps)
    ###############print(f"Número de pasos: {num_steps}")

    x = center.copy()
    r_actual = r_inicial

    ######################print(f"Radio inicial: {r_inicial}, Volumen inicial: {vol}")

    for k in range(num_steps):
        r_next = r_actual * factor_expansion
        contador = 0

        for _ in range(samples):
            x = HITnRUNstep(x, A, b, center, r_next)

            if np.linalg.norm(x - center) <= r_actual:
                contador += 1

        #calcular volúmen
        alpha = (contador / samples)
        #####################print(f"Radio siguiente: {r_next}, Alpha: {alpha}")

        #fórmula de expansión de volumen
        vol /= alpha


        #condición de parada
        if alpha >tol:
            break

        r_actual = r_next

    #tiempo_total = time.time() - start_time
    return vol #tiempo_total