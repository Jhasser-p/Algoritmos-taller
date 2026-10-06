"""
ordenamiento.py
taller metodos
Joan rivero
Laura Almeida
Jhasser Piña
Samuel Cala
Nicolas Gonzalez

Uso:
    python ordenamiento.py            # corrida completa (puede tardar varios minutos)
    python ordenamiento.py --rapido   # corrida reducida, solo para probar que todo funciona

"""
import sys
import json
import random
from time import perf_counter_ns

import numpy as np
import matplotlib.pyplot as plt

# Quicksort con pivote = último elemento puede recursar muy profundo (entrada ordenada
# o con muchos duplicados). Subimos el límite; si aun así se excede, lo registramos.
sys.setrecursionlimit(10000)

# ---------------------------------------------------------------------
# True  = corrida corta (segundos): úsala primero para probar que todo funciona.
# False = corrida completa del taller (varios minutos o más; en Colab puede
#         parecer que "se queda pensando", pero está midiendo).
MODO_RAPIDO = True
# ---------------------------------------------------------------------


# =====================================================================
# 1. ALGORITMOS  (todos: def nombre(A) -> ordena A ascendente y retorna A)
# =====================================================================

def bubble_sort(A):
    """Burbuja con bandera de parada temprana."""
    n = len(A)
    for i in range(n - 1):                  # cada pasada deja el mayor restante al final
        hubo_intercambio = False
        for j in range(n - 1 - i):          # los últimos i ya están en su sitio
            if A[j] > A[j + 1]:             # vecinos desordenados -> se intercambian
                A[j], A[j + 1] = A[j + 1], A[j]
                hubo_intercambio = True
        if not hubo_intercambio:            # una pasada sin cambios: ya está ordenado
            break
    return A


def selection_sort(A):
    """Selección clásica: en cada pasada ubica el mínimo del subarreglo no ordenado."""
    n = len(A)
    for i in range(n - 1):
        idx_min = i
        for j in range(i + 1, n):           # busca el mínimo en A[i..n-1]
            if A[j] < A[idx_min]:
                idx_min = j
        if idx_min != i:                    # a lo sumo un intercambio por pasada
            A[i], A[idx_min] = A[idx_min], A[i]
    return A


def insertion_sort(A):
    """Inserción clásica por desplazamiento (no por intercambios sucesivos)."""
    for i in range(1, len(A)):
        clave = A[i]                        # elemento a insertar en la parte ordenada
        j = i - 1
        while j >= 0 and A[j] > clave:      # desplaza a la derecha los mayores que clave
            A[j + 1] = A[j]
            j -= 1
        A[j + 1] = clave                    # coloca la clave en su hueco
    return A


# --- Quicksort: esquema de Lomuto, PIVOTE = ÚLTIMO ELEMENTO del subarreglo ---------

def _particion_lomuto(A, lo, hi):
    pivote = A[hi]                          # pivote: último elemento
    i = lo                                  # frontera de los elementos <= pivote
    for j in range(lo, hi):
        if A[j] <= pivote:
            A[i], A[j] = A[j], A[i]
            i += 1
    A[i], A[hi] = A[hi], A[i]               # el pivote queda en su posición final
    return i


def _quick_rec(A, lo, hi):
    if lo < hi:
        p = _particion_lomuto(A, lo, hi)
        _quick_rec(A, lo, p - 1)
        _quick_rec(A, p + 1, hi)


def quick_sort(A):
    _quick_rec(A, 0, len(A) - 1)
    return A


# --- Corrección para duplicados (pregunta 7): partición en 3 vías + pivote aleatorio ---

def quick_sort_3vias(A):
    def rec(lo, hi):
        while lo < hi:
            pivote = A[random.randint(lo, hi)]       # pivote aleatorio
            lt, i, gt = lo, lo, hi
            while i <= gt:                           # bandera holandesa
                if A[i] < pivote:
                    A[lt], A[i] = A[i], A[lt]
                    lt += 1
                    i += 1
                elif A[i] > pivote:
                    A[i], A[gt] = A[gt], A[i]
                    gt -= 1
                else:
                    i += 1
            # A[lo:lt] < pivote | A[lt:gt+1] == pivote | A[gt+1:hi+1] > pivote
            # Recursión sobre el lado menor, bucle sobre el mayor -> profundidad O(log n)
            if lt - lo < hi - gt:
                rec(lo, lt - 1)
                lo = gt + 1
            else:
                rec(gt + 1, hi)
                hi = lt - 1
    rec(0, len(A) - 1)
    return A


# --- Algoritmo avanzado: MERGE SORT (top-down, con arreglo auxiliar) -------------

def merge_sort(A):
    aux = A.copy()

    def ordenar(lo, hi):                    # ordena A[lo:hi]
        if hi - lo < 2:
            return
        mid = (lo + hi) // 2
        ordenar(lo, mid)
        ordenar(mid, hi)
        i, j, k = lo, mid, lo               # mezcla A[lo:mid] y A[mid:hi] en aux
        while i < mid and j < hi:
            if A[i] <= A[j]:                # "<=" mantiene la estabilidad
                aux[k] = A[i]
                i += 1
            else:
                aux[k] = A[j]
                j += 1
            k += 1
        while i < mid:
            aux[k] = A[i]
            i += 1
            k += 1
        while j < hi:
            aux[k] = A[j]
            j += 1
            k += 1
        A[lo:hi] = aux[lo:hi]

    ordenar(0, len(A))
    return A


def avanzado(A):
    """Algoritmo avanzado elegido: merge sort."""
    return merge_sort(A)


# --- Referencias (SOLO para verificar y comparar, no son parte de los 5 algoritmos) ---
def ref_sorted(A):
    return sorted(A)


def ref_npsort(A):
    return np.sort(A)


# =====================================================================
# 2. VERSIONES CON CONTADORES (pregunta 5)
# =====================================================================

def contar_burbuja(A):
    A = list(A)
    n = len(A)
    comp = inter = 0
    for i in range(n - 1):
        hubo = False
        for j in range(n - 1 - i):
            comp += 1
            if A[j] > A[j + 1]:
                A[j], A[j + 1] = A[j + 1], A[j]
                inter += 1
                hubo = True
        if not hubo:
            break
    return comp, inter            # comparaciones, intercambios (cada uno = 2 escrituras)


def contar_seleccion(A):
    A = list(A)
    n = len(A)
    comp = inter = 0
    for i in range(n - 1):
        m = i
        for j in range(i + 1, n):
            comp += 1
            if A[j] < A[m]:
                m = j
        if m != i:
            A[i], A[m] = A[m], A[i]
            inter += 1
    return comp, inter


def contar_insercion(A):
    A = list(A)
    comp = escrituras = 0
    for i in range(1, len(A)):
        clave = A[i]
        j = i - 1
        while j >= 0:
            comp += 1
            if A[j] > clave:
                A[j + 1] = A[j]
                escrituras += 1
                j -= 1
            else:
                break
        A[j + 1] = clave
        escrituras += 1
    return comp, escrituras


# =====================================================================
# 3. UTILIDADES DE MEDICIÓN
# =====================================================================

def generar(n, rango, tipo="aleatoria", dtype=np.int32):
    """Vector de n enteros en [0, rango). int32 admite hasta ~2.1e9 (sobra para 10**6)."""
    v = np.random.randint(0, rango, n, dtype=dtype)
    if tipo == "ordenada":
        v = np.sort(v)
    elif tipo == "inversa":
        v = np.sort(v)[::-1].copy()
    return v


def medir(func, base, reps, referencia=None):
    """Mediana (en segundos) de `reps` corridas; cada una con una COPIA de `base`.
    Verifica cada resultado contra np.sort()."""
    if referencia is None:
        referencia = np.sort(base)
    tiempos = []
    for _ in range(reps):
        entrada = base.copy()
        t0 = perf_counter_ns()
        salida = func(entrada)
        t1 = perf_counter_ns()
        tiempos.append((t1 - t0) / 1e9)                      # ns -> s
        if not np.array_equal(salida, referencia):
            raise AssertionError(f"{func.__name__} ordenó mal (n={len(base)})")
    return float(np.median(tiempos))


def medir_seguro(func, base, reps, referencia=None):
    try:
        return medir(func, base, reps, referencia)
    except RecursionError:
        return float("nan")                                  # se registra como "no terminó"


def reps_para(n):
    return 5 if n <= 2000 else 3


def humano(s):
    if s < 60:
        return f"{s:.1f} s"
    if s < 3600:
        return f"{s / 60:.1f} min"
    if s < 86400:
        return f"{s / 3600:.1f} horas"
    if s < 86400 * 365:
        return f"{s / 86400:.1f} días"
    return f"{s / (86400 * 365):.1f} años"


def ajustar(ns, ts, n_min):
    """Ajuste log t = m log n + b descartando n < n_min. Retorna (m, b)."""
    ns, ts = np.asarray(ns, float), np.asarray(ts, float)
    mask = ns >= n_min
    m, b = np.polyfit(np.log(ns[mask]), np.log(ts[mask]), 1)
    return float(m), float(b)


def mostrar(fig):
    """Ajusta y muestra la gráfica sin guardarla en PNG."""
    fig.tight_layout()
    plt.show()
    plt.close(fig)


def autotest():
    """Casos borde: vacío, un elemento, duplicados, negativos."""
    casos = [[], [1], [2, 2, 2, 2], [3, -1, 2, -5, 0], list(range(10, 0, -1))]
    for f in (bubble_sort, selection_sort, insertion_sort, quick_sort,
              quick_sort_3vias, avanzado):
        for c in casos:
            a = np.array(c, dtype=np.int32)
            assert np.array_equal(f(a.copy()), np.sort(a)), f.__name__
            assert f(list(c)) == sorted(c), f.__name__        # también con listas
    print("Autotest OK (casos borde, arreglos y listas)")


# =====================================================================
# 4. EXPERIMENTOS
# =====================================================================

COLOR = {"Burbuja": "tab:red", "Selección": "tab:orange", "Inserción": "tab:green",
         "Quicksort": "tab:blue", "Avanzado (merge sort)": "tab:purple",
         "sorted() de Python": "tab:brown", "np.sort()": "tab:gray"}
MARC = {"Burbuja": "o", "Selección": "s", "Inserción": "^", "Quicksort": "D",
        "Avanzado (merge sort)": "v", "sorted() de Python": "x", "np.sort()": "+"}

CUAD = {"Burbuja": bubble_sort, "Selección": selection_sort, "Inserción": insertion_sort}
RAP = {"Quicksort": quick_sort, "Avanzado (merge sort)": avanzado}
REF = {"sorted() de Python": ref_sorted, "np.sort()": ref_npsort}


def estimar_duracion(rango_cuad, rango_rap):
    """Calibra con una corrida pequeña y extrapola (n^2 y n log n)."""
    total = 0.0
    base = generar(500, 10**6)
    for f in CUAD.values():
        t0 = medir(f, base, 1)
        total += sum(reps_para(n) * t0 * (n / 500) ** 2 for n in rango_cuad)
    base = generar(5000, 10**6)
    for f in RAP.values():
        t0 = medir(f, base, 1)
        k = t0 / (5000 * np.log2(5000))
        total += sum(reps_para(n) * k * n * np.log2(n) for n in rango_rap)
    return total


def experimento_principal(rango_cuad, rango_rap, n_min_cuad, n_min_rap):
    """G1-G4 (+ pregunta 8): mismo vector para todos, copias, repeticiones y mediana."""
    tiempos = {nombre: {} for nombre in list(CUAD) + list(RAP) + list(REF)}
    todos_n = sorted(set(rango_cuad) | set(rango_rap))
    for n in todos_n:
        n = int(n)
        base = generar(n, 10**6)                  # UN solo vector por n
        ref = np.sort(base)
        reps = reps_para(n)
        if n in rango_cuad:
            for nombre, f in CUAD.items():
                tiempos[nombre][n] = medir(f, base, reps, ref)
        if n in rango_rap:
            for nombre, f in RAP.items():
                tiempos[nombre][n] = medir(f, base, reps, ref)
            tiempos["np.sort()"][n] = medir(ref_npsort, base, reps, ref)
            tiempos["sorted() de Python"][n] = medir(ref_sorted, base.tolist(), reps, ref)
        print(f"  n={n:>7} listo")

    series = {k: (np.array(sorted(v)), np.array([v[n] for n in sorted(v)]))
              for k, v in tiempos.items()}
    ajustes = {}
    for k, (ns, ts) in series.items():
        ajustes[k] = ajustar(ns, ts, n_min_cuad if k in CUAD else n_min_rap)
    return series, ajustes


def graficos_principales(series, ajustes, n_min_cuad, n_min_rap):
    # G1: cuadráticos, escala lineal
    fig, ax = plt.subplots(figsize=(8, 5))
    for k in CUAD:
        ns, ts = series[k]
        ax.plot(ns, ts, marker=MARC[k], color=COLOR[k], label=k)
    ax.set(title="G1. Tiempo de ejecución vs n - algoritmos O(n²) (escala lineal)",
           xlabel="Tamaño del arreglo, n (elementos)", ylabel="Tiempo de ejecución (s)")
    ax.grid(True)
    ax.legend()
    mostrar(fig)

    # G2: quicksort y avanzado, escala lineal
    fig, ax = plt.subplots(figsize=(8, 5))
    for k in RAP:
        ns, ts = series[k]
        ax.plot(ns, ts, marker=MARC[k], color=COLOR[k], label=k, markersize=4)
    ax.set(title="G2. Tiempo de ejecución vs n - quicksort y merge sort (escala lineal)",
           xlabel="Tamaño del arreglo, n (elementos)", ylabel="Tiempo de ejecución (s)")
    ax.grid(True)
    ax.legend()
    mostrar(fig)

    # G3: todos, log-log con rectas de ajuste
    fig, ax = plt.subplots(figsize=(9, 6))
    for k, (ns, ts) in series.items():
        m, b = ajustes[k]
        ax.loglog(ns, ts, marker=MARC[k], color=COLOR[k], linestyle="none",
                  markersize=5, label=f"{k} (m = {m:.2f})")
        nn = np.array([ns.min(), ns.max()], float)
        ax.loglog(nn, np.exp(b) * nn ** m, "--", color=COLOR[k], linewidth=1)
    ax.set(title="G3. Tiempo vs n en escala log-log (líneas punteadas: ajuste, m = pendiente)",
           xlabel="Tamaño del arreglo, n (elementos)", ylabel="Tiempo de ejecución (s)")
    ax.grid(True, which="both", alpha=0.4)
    ax.legend(fontsize=8)
    mostrar(fig)

    # G4: tiempo normalizado
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(13, 5))
    for k in CUAD:
        ns, ts = series[k]
        a1.plot(ns, ts / ns**2 * 1e9, marker=MARC[k], color=COLOR[k], label=k)
    a1.set(title="G4a. t / n² (cuadráticos)", xlabel="Tamaño del arreglo, n (elementos)",
           ylabel="t / n² (ns por elemento²)")
    for k in RAP:
        ns, ts = series[k]
        a2.plot(ns, ts / (ns * np.log2(ns)) * 1e9, marker=MARC[k], color=COLOR[k],
                label=k, markersize=4)
    a2.set(title="G4b. t / (n·log₂ n) (quicksort y merge sort)",
           xlabel="Tamaño del arreglo, n (elementos)",
           ylabel="t / (n·log₂ n) (ns por elemento·bit)")
    for a in (a1, a2):
        a.grid(True)
        a.legend()
    mostrar(fig)


def experimento_tipos(rapido):
    """G5: aleatoria / ordenada / inversa para inserción, burbuja y quicksort."""
    ns = list(range(100, 801, 100)) if rapido else list(range(200, 3001, 200))
    algs = {"Inserción": insertion_sort, "Burbuja": bubble_sort,
            "Quicksort (pivote = último)": quick_sort}
    tipos = ["aleatoria", "ordenada", "inversa"]
    res = {a: {t: [] for t in tipos} for a in algs}
    for n in ns:
        for tipo in tipos:
            base = generar(n, 10**6, tipo)
            ref = np.sort(base)
            for a, f in algs.items():
                res[a][tipo].append(medir_seguro(f, base, 3, ref))
        print(f"  G5 n={n} listo")

    fig, axes = plt.subplots(1, 3, figsize=(16, 5))
    for ax, a in zip(axes, algs):
        for tipo, mk in zip(tipos, ["o", "s", "^"]):
            ax.plot(ns, res[a][tipo], marker=mk, label=f"entrada {tipo}")
        ax.set(title=f"G5. {a}", xlabel="Tamaño del arreglo, n (elementos)",
               ylabel="Tiempo de ejecución (s)")
        ax.grid(True)
        ax.legend()
    mostrar(fig)
    return ns, res


def experimento_rango_valores(rapido):
    """G6: quicksort con valores 0-99 vs 0-10^6, y versión corregida (3 vías)."""
    ns = list(range(500, 4001, 500)) if rapido else list(range(1000, 20001, 1000))
    series = {"Lomuto, valores 0-99": [], "Lomuto, valores 0-10⁶": [],
              "3 vías + pivote aleatorio, valores 0-99": []}
    for n in ns:
        b_pocos = generar(n, 100)                 # int32 en ambos: aísla el efecto del rango
        b_muchos = generar(n, 10**6)
        series["Lomuto, valores 0-99"].append(medir_seguro(quick_sort, b_pocos, 3))
        series["Lomuto, valores 0-10⁶"].append(medir_seguro(quick_sort, b_muchos, 3))
        series["3 vías + pivote aleatorio, valores 0-99"].append(
            medir_seguro(quick_sort_3vias, b_pocos, 3))
        print(f"  G6 n={n} listo")
    fig, ax = plt.subplots(figsize=(8, 5))
    for (k, v), mk in zip(series.items(), ["o", "s", "^"]):
        ax.plot(ns, v, marker=mk, label=k)
    ax.set(title="G6. Quicksort: efecto de los valores duplicados",
           xlabel="Tamaño del arreglo, n (elementos)", ylabel="Tiempo de ejecución (s)")
    ax.grid(True)
    ax.legend()
    mostrar(fig)
    return ns, series


def experimento_pequenos():
    """Pregunta 9: inserción vs quicksort para n entre 5 y 200 (punto de cruce)."""
    ns = list(range(5, 201, 5))
    t_ins, t_qs = [], []
    for n in ns:
        base = generar(n, 10**6)
        ref = np.sort(base)
        t_ins.append(medir(insertion_sort, base, 50, ref))
        t_qs.append(medir(quick_sort, base, 50, ref))
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(ns, np.array(t_ins) * 1e6, "^-", color=COLOR["Inserción"], label="Inserción")
    ax.plot(ns, np.array(t_qs) * 1e6, "D-", color=COLOR["Quicksort"], label="Quicksort")
    ax.set(title="G7. Inserción vs quicksort para n pequeño",
           xlabel="Tamaño del arreglo, n (elementos)", ylabel="Tiempo de ejecución (µs)")
    ax.grid(True)
    ax.legend()
    mostrar(fig)
    cruce = None
    for i in range(len(ns)):                      # primer n desde el cual quicksort gana siempre
        if all(t_qs[j] < t_ins[j] for j in range(i, len(ns))):
            cruce = ns[i]
            break
    return ns, t_ins, t_qs, cruce


def main():
    rapido = MODO_RAPIDO or "--rapido" in sys.argv
    np.random.seed(42)
    random.seed(42)
    autotest()

    if rapido:
        rango_cuad = np.arange(100, 1001, 100)
        rango_rap = np.arange(1000, 10001, 1000)
        n_min_cuad, n_min_rap = 200, 3000
    else:
        rango_cuad = np.arange(500, 10001, 500)
        rango_rap = np.arange(1000, 100001, 1000)
        n_min_cuad, n_min_rap = 1000, 5000

    est = estimar_duracion(rango_cuad, rango_rap)
    print(f"Estimación aproximada de la medición principal: {humano(est)}\n")

    R = {}
    print("== Medición principal (G1-G4, pregunta 8) ==")
    series, ajustes = experimento_principal(rango_cuad, rango_rap, n_min_cuad, n_min_rap)
    graficos_principales(series, ajustes, n_min_cuad, n_min_rap)
    R["tiempos"] = {k: {"n": ns.tolist(), "t_s": ts.tolist()} for k, (ns, ts) in series.items()}
    R["pendientes"] = {k: {"m": m, "b": b} for k, (m, b) in ajustes.items()}
    R["n_min_ajuste"] = {"cuadraticos": n_min_cuad, "otros": n_min_rap}

    print("\nPendientes log-log (pregunta 2):")
    for k, (m, b) in ajustes.items():
        print(f"  {k:<24} m = {m:.3f}")

    print("\nCocientes normalizados al último n medido (pregunta 3):")
    for k in CUAD:
        ns, ts = series[k]
        print(f"  {k:<24} t/n² = {ts[-1] / ns[-1]**2 * 1e9:.1f} ns")
    for k in RAP:
        ns, ts = series[k]
        print(f"  {k:<24} t/(n log2 n) = {ts[-1] / (ns[-1] * np.log2(ns[-1])) * 1e9:.1f} ns")

    print("\nExtrapolación con la recta ajustada (pregunta 4):")
    R["extrapolacion"] = {}
    for k in ("Burbuja", "Quicksort"):
        m, b = ajustes[k]
        for n in (10**6, 10**7):
            t = float(np.exp(b) * n ** m)
            R["extrapolacion"][f"{k}_{n}"] = t
            print(f"  {k:<10} n={n:>9,}: {t:,.0f} s = {humano(t)}")

    print("\n== G5: tipos de entrada ==")
    ns5, res5 = experimento_tipos(rapido)
    R["g5"] = {"n": ns5, "res": res5}

    print("\n== G6: rango de valores ==")
    ns6, res6 = experimento_rango_valores(rapido)
    R["g6"] = {"n": ns6, "res": res6}
    print("  (nan = RecursionError: quicksort no terminó)")

    print("\n== Pregunta 9: n pequeño ==")
    ns9, ti, tq, cruce = experimento_pequenos()
    R["g7"] = {"n": ns9, "insercion_s": ti, "quicksort_s": tq, "cruce": cruce}
    print("  Punto de cruce (quicksort gana desde n =):", cruce)

    print("\n== Pregunta 5: contadores (n = 1000, aleatorio) ==")
    base = generar(1000, 10**6)
    R["contadores"] = {}
    for nombre, f in (("Burbuja", contar_burbuja), ("Selección", contar_seleccion),
                      ("Inserción", contar_insercion)):
        c, o = f(base)
        R["contadores"][nombre] = {"comparaciones": c, "intercambios_o_escrituras": o}
        print(f"  {nombre:<10} comparaciones={c:>8}  intercambios/escrituras={o:>8}")

    print("\n== Pregunta 10: ndarray vs lista (n = 2000) ==")
    n10 = 2000
    arr = generar(n10, 10**6)
    ref = np.sort(arr)
    R["ndarray_vs_lista"] = {}
    for nombre, f in CUAD.items():
        t_arr = medir(f, arr, 3, ref)
        t_lis = medir(f, arr.tolist(), 3, ref)
        R["ndarray_vs_lista"][nombre] = {"ndarray_s": t_arr, "lista_s": t_lis}
        print(f"  {nombre:<10} ndarray={t_arr:.3f} s   lista={t_lis:.3f} s   "
              f"cociente={t_arr / t_lis:.2f}")

    with open("resultados.json", "w", encoding="utf-8") as fh:
        json.dump(R, fh, ensure_ascii=False, indent=1)
   


if __name__ == "__main__":
    main()