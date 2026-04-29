# vol_star.py
import numpy as np

#this i don't get
def _choose_batch(n_ineq, target_mb=None):
    """Tamaño de lote automático dado #inequaciones y una meta de memoria (MiB)."""
    if target_mb is None:
        target_mb = 64  # ~64 MiB por defecto
    bytes_target = int(target_mb * 1024 * 1024)
    # Cada muestra ocupa ~ 8 * n_ineq bytes al multiplicar contra A (float64)
    m = max(1, bytes_target // (8 * max(1, n_ineq)))
    return int(m)


def _fiber_vol_est(d, A, b, z, N, tol=1e-9, batch=None, target_mb=None):
    """
    Estima Vol_rel(S_z) = P[(z,p) ∈ C] con p ~ U([0,1]^d), i.e., volumen relativo en la fibra z.
    Devuelve un número en [0,1].
    """
    d = int(d)
    N = int(N)
    if N <= 0 or d <= 0:
        return 0.0

    A = np.asarray(A, float)
    b = np.asarray(b, float)
    if A.shape[1] != 1 + d:
        raise ValueError(f"A tiene {A.shape[1]} columnas; d={d} ⇒ 1+d={1+d}.")

    z_val = float(int(z))

    Ap = A[:, 1:]                  # (#ineq, d)
    b_shift = b - A[:, 0] * z_val  # (#ineq,)
    n_ineq = A.shape[0]

    if batch is None:
        m_auto = _choose_batch(n_ineq, target_mb=target_mb)
        batch = min(N, max(1000, m_auto))
    else:
        batch = int(batch)
        if batch <= 0:
            batch = min(N, max(1000, _choose_batch(n_ineq, target_mb=target_mb)))

    aceptados = 0
    gen = 0
    while gen < N:
        m = min(batch, N - gen)
        p = np.random.rand(m, d)               # (m, d)
        lhs = p @ Ap.T                         # (m, #ineq)
        inside = np.all(lhs <= (b_shift + tol), axis=1)
        aceptados += int(inside.sum())
        gen += m

    return aceptados / float(N)


def ratio_cp(A, b, cp, z_vals, N_hip, d, N, tol=1e-9, batch=None, target_mb=None):
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
    A = np.asarray(A, float)
    b = np.asarray(b, float)
    cp = np.asarray(cp, float)

    if A.shape[1] != 1 + d:
        raise ValueError(f"A tiene {A.shape[1]} columnas; d={d} ⇒ 1+d={1+d}.")
    if cp.shape[0] != 1 + d:
        raise ValueError("cp debe tener dimensión 1+d (incluyendo la coordenada z).")

    p_cp = cp[1:]  # parte continua del cp (en [0,1]^d idealmente)

    # Precompute estructura por fibra (no depende de u)
    Ap = A[:, 1:]  # (#ineq, d)
    n_ineq = A.shape[0]

    # Volumen total (denominador): sum_z Vol_rel(S_z)
    vols = {}
    for z in z_vals:
        vols[int(z)] = _fiber_vol_est(d, A, b, z, N, tol=tol, batch=batch, target_mb=target_mb)

    vol_total = sum(vols.values())
    if vol_total <= 0:
        # No hay volumen, devolvemos ratio 0 y un u neutro
        return 0.0, np.zeros(d, dtype=float)

    # Tamaño de lote para el muestreo por dirección
    if batch is None:
        m_auto = _choose_batch(n_ineq, target_mb=target_mb)
        batch = min(N, max(1000, m_auto))
    else:
        batch = int(batch)
        if batch <= 0:
            batch = min(N, max(1000, _choose_batch(n_ineq, target_mb=target_mb)))

    worst_ratio = 1.0  # buscamos el mínimo sobre direcciones
    best_u = None

    for _ in range(int(N_hip)):
        # normal aleatoria en R^d (solo sobre coords continuas)
        u = np.random.randn(d) #dirección aleatoria no normalizada
        nu = np.linalg.norm(u)
        if nu < 1e-15:
            continue #se salta al sgte pq es muy chiquito
        u /= nu #Normalizado

        # Para esta dirección, estimamos sum_z min(Vol^+, Vol^-)
        sum_min_sides = 0.0

        for z in z_vals:
            z_val = float(int(z))
            b_shift = b - A[:, 0] * z_val  # (#ineq,)
            acc_pos = 0
            acc_neg = 0
            gen = 0

            # Monte Carlo por lotes en p ~ U([0,1]^d)
            while gen < N:
                m = min(batch, N - gen)
                p = np.random.rand(m, d) #genera m puntos aleatorios
                inside = np.all((p @ Ap.T) <= (b_shift + tol), axis=1) #verifica qué puntos caen dentro
                #para los que caen dentro, en qué lado están
                if inside.any():
                    #verifica a qué lado del centerpoint queda cada punto
                    side_val = (p[inside] - p_cp) @ u  # (k,)
                    acc_pos += int((side_val >= 0).sum())
                    acc_neg += int((side_val < 0).sum())
                gen += m

            acc_tot = acc_pos + acc_neg
            if acc_tot > 0:
                min_side = min(acc_pos, acc_neg) / float(N) #normaliza el lado con menos puntos
            else:
                min_side = 0.0

            sum_min_sides += min_side

        #calcula la proporción del volumen que queda del lado con menos puntos
        ratio_u = sum_min_sides / max(vol_total, 1e-16)
        if ratio_u < worst_ratio:
            worst_ratio = ratio_u #busca el peor caso
            best_u = u.copy()

    if best_u is None:
        best_u = np.zeros(d, dtype=float)

    return float(worst_ratio), best_u
    
    #para cada corte, mira cuánto queda en el trozo más pequeño de todo el cuerpo convexo, y devuelve la dirección que lo produce



def estimar_ratio(A, b, cp, z_vals, N_hip, d, N, tol=1e-9, batch=None, target_mb=None):
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
    A = np.asarray(A, float)
    b = np.asarray(b, float)
    cp = np.asarray(cp, float)

    if A.shape[1] != 1 + d:
        raise ValueError(f"A tiene {A.shape[1]} columnas; d={d} ⇒ 1+d={1+d}.")
    if cp.shape[0] != 1 + d:
        raise ValueError("cp debe tener dimensión 1+d (incluyendo la coordenada z).")

    p_cp = cp[1:]  # parte continua del cp (en [0,1]^d idealmente)

    # Precompute estructura por fibra (no depende de u)
    Ap = A[:, 1:]  # (#ineq, d)
    n_ineq = A.shape[0]

    # Volumen total (denominador): sum_z Vol_rel(S_z)
    vols = {}
    for z in z_vals:
        vols[int(z)] = _fiber_vol_est(d, A, b, z, N, tol=tol, batch=batch, target_mb=target_mb)

    vol_total = sum(vols.values())
    if vol_total <= 0:
        # No hay volumen, devolvemos ratio 0 y un u neutro
        return 0.0, np.zeros(d, dtype=float)

    # Tamaño de lote para el muestreo por dirección
    if batch is None:
        m_auto = _choose_batch(n_ineq, target_mb=target_mb)
        batch = min(N, max(1000, m_auto))
    else:
        batch = int(batch)
        if batch <= 0:
            batch = min(N, max(1000, _choose_batch(n_ineq, target_mb=target_mb)))

    worst_ratio = 1.0  # buscamos el mínimo sobre direcciones
    worst_u = None

    for _ in range(int(N_hip)):
        # normal aleatoria en R^d (solo sobre coords continuas)
        u = np.random.randn(d) #dirección aleatoria no normalizada
        nu = np.linalg.norm(u)
        if nu < 1e-15:
            continue #se salta al sgte pq es muy chiquito
        u /= nu #Normalizado

        #para esta dirección, estimamos sum_z min(Vol^+, Vol^-)        
        sum_vol_pos = 0.0
        sum_vol_neg = 0.0

        for z in z_vals:
            z_val = float(int(z))
            b_shift = b - A[:, 0] * z_val
            acc_pos = 0
            acc_neg = 0
            gen = 0

            while gen < N:
                m = min(batch, N - gen)
                p = np.random.rand(m, d)
                #filtro de puntos dentro de la envolvente
                inside = np.all((p @ Ap.T) <= (b_shift + tol), axis=1)
                
                if inside.any():
                    #calculamos el signo respecto al hiperplano H(u, cp)
                    side_val = (p[inside] - p_cp) @ u
                    acc_pos += int((side_val >= 0).sum())
                    acc_neg += int((side_val < 0).sum())
                gen += m

            #convertimos los conteos de esta fibra a su proporción respecto a N
            sum_vol_pos += acc_pos / float(N)
            sum_vol_neg += acc_neg / float(N)

        #ahora el ratio es el mínimo de las sumas globales
        ratio_u = min(sum_vol_pos, sum_vol_neg) / max(vol_total, 1e-16)
        
        if ratio_u < worst_ratio:
            worst_ratio = ratio_u 
            worst_u = u.copy()

    if worst_u is None:
        worst_u = np.zeros(d, dtype=float)

    return float(worst_ratio), worst_u