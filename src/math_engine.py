import sympy as sp
import numpy as np
from sympy.calculus.util import continuous_domain, function_range
from sympy import S, oo, Interval

def compute_analytics(func_input, px, py=0.0):
    x, y = sp.symbols('x y', real=True)
    
    # 1. FIX CLAVE: Forzar a SymPy a leer el texto usando nuestros símbolos reales explícitos
    try:
        f_sym = sp.sympify(func_input, locals={'x': x, 'y': y})
        f_sym = sp.simplify(f_sym)
    except:
        f_sym = sp.sympify(func_input, locals={'x': x, 'y': y})
    
    vars_presentes = f_sym.free_symbols
    es_am1 = y not in vars_presentes
    
    if es_am1:
        f_np_raw = sp.lambdify(x, f_sym, modules=['numpy', {'complex': np.complex128}])
        f_np = lambda val_x, val_y=0: np.where(np.abs(np.imag(f_np_raw(val_x))) > 1e-5, np.nan, np.real(f_np_raw(val_x)))
    else:
        f_np_raw = sp.lambdify((x, y), f_sym, modules=['numpy', {'complex': np.complex128}])
        f_np = lambda val_x, val_y: np.where(np.abs(np.imag(f_np_raw(val_x, val_y))) > 1e-5, np.nan, np.real(f_np_raw(val_x, val_y)))

    # --- INICIO BLINDAJE NUMÉRICO ---
    # 2. FIX: Evaluación usando evalf() y float() nativo para rechazar complejos automáticamente
    try:
        z_eval = f_sym.subs({x: px, y: py}).evalf()
        z0 = float(z_eval)
    except:
        z0 = np.nan
    
    fx = sp.diff(f_sym, x)
    fy = sp.diff(f_sym, y)
    
    # --- INICIO BLINDAJE DE DERIVABILIDAD ---
    try:
        if es_am1:
            # Evaluamos las derivadas laterales para detectar puntos angulosos
            l_izq_d = sp.limit(fx, x, px, dir='-')
            l_der_d = sp.limit(fx, x, px, dir='+')
            
            # Si coinciden, es derivable. Si no, forzamos NaN (No existe)
            if l_izq_d == l_der_d:
                fx_v = float(l_izq_d.evalf()) if not np.isnan(z0) else np.nan
            else:
                fx_v = np.nan 
        else:
            fx_v = float(fx.subs({x: px, y: py}).evalf()) if not np.isnan(z0) else np.nan
    except:
        fx_v = np.nan
        
    fy_v = 0.0
    if not es_am1:
        try:
            fy_v = float(fy.subs({x: px, y: py}).evalf()) if not np.isnan(z0) else np.nan
        except:
            fy_v = np.nan

    results = {
        "f_sym": f_sym, "f_np": f_np, "es_am1": es_am1, "z0": z0,
        "fx": fx, "fy": fy, "fx_v": fx_v, "fy_v": fy_v,
    }

    if es_am1:
        try:
            results["primitiva"] = sp.integrate(f_sym, x)
        except:
            results["primitiva"] = None
        try:
            results["lim_izq"] = sp.limit(f_sym, x, px, dir='-')
            results["lim_der"] = sp.limit(f_sym, x, px, dir='+')
        except:
            results["lim_izq"] = sp.nan; results["lim_der"] = sp.nan
    else:
        fxx, fyy, fxy = sp.diff(fx, x), sp.diff(fy, y), sp.diff(fx, y)
        try:
            fxx_v = float(fxx.subs({x: px, y: py}).evalf())
            fyy_v = float(fyy.subs({x: px, y: py}).evalf())
            fxy_v = float(fxy.subs({x: px, y: py}).evalf())
            results.update({
                "fxx": fxx, "fyy": fyy, "fxy": fxy,
                "fxx_v": fxx_v, "fyy_v": fyy_v, "fxy_v": fxy_v,
                "hessiano": fxx_v * fyy_v - fxy_v**2
            })
        except:
            results.update({"hessiano": 0, "fxx_v": 0, "fyy_v": 0, "fxy_v": 0})
        
    return results

def analyze_polares_process(f_sym):
    x, y, r, theta = sp.symbols('x y r theta', real=True)
    f_sub = f_sym.subs({x: r*sp.cos(theta), y: r*sp.sin(theta)})
    f_simp = sp.simplify(f_sub)
    try:
        lim_r = sp.limit(f_simp, r, 0)
    except:
        lim_r = sp.nan
    return f_sub, f_simp, lim_r

def compute_directional(data, angle_deg):
    angle_rad = np.radians(angle_deg)
    ux, uy = np.cos(angle_rad), np.sin(angle_rad)
    d_dir = data['fx_v'] * ux + data['fy_v'] * uy
    return ux, uy, d_dir

def get_taylor_step_by_step(f_sym, x0, n):
    x = sp.Symbol('x', real=True)
    steps = []
    for k in range(n + 1):
        derivada = sp.diff(f_sym, x, k)
        valor_eval = derivada.subs(x, x0)
        coeficiente = valor_eval / sp.factorial(k)
        termino = coeficiente * (x - x0)**k
        steps.append({
            "orden": k, "derivada_simbolica": derivada,     
            "valor_evaluado": valor_eval, "termino_completo": termino         
        })
    return steps

def get_full_analysis(f_sym):
    x = sp.Symbol('x', real=True)
    res = {}
    
    # 1. Dominio y Restricciones
    try: res['dominio'] = continuous_domain(f_sym, x, S.Reals)
    except: res['dominio'] = None
    
    try: res['denominador'] = f_sym.as_numer_denom()[1]
    except: res['denominador'] = 1

    # 2. Imagen (Deshabilitada por seguridad computacional)
    res['imagen'] = "Cálculo analítico desactivado (riesgo de bucle infinito). Estimar mediante el gráfico."

    # 3. Raíces
    try:
        raices_set = sp.solveset(f_sym, x, domain=S.Reals)
        res['raices'] = raices_set
    except:
        raices_set = None
        res['raices'] = None

    # 4. Cálculo de Bolzano (Intervalos y puntos de prueba)
    res['bolzano'] = []
    try:
        puntos_criticos_bolzano = set()
        
        if isinstance(raices_set, sp.FiniteSet):
            puntos_criticos_bolzano.update([float(r) for r in raices_set if r.is_real])
            
        if res['denominador'] != 1:
            sing = sp.solveset(res['denominador'], x, domain=S.Reals)
            if isinstance(sing, sp.FiniteSet):
                puntos_criticos_bolzano.update([float(s) for s in sing if s.is_real])
                
        puntos_ordenados = sorted(list(puntos_criticos_bolzano))
        
        if len(puntos_ordenados) == 0:
            res['bolzano'].append({'intervalo': (-float('inf'), float('inf')), 'pt': 0.0})
        else:
            res['bolzano'].append({'intervalo': (-float('inf'), puntos_ordenados[0]), 'pt': puntos_ordenados[0] - 1.0})
            for i in range(len(puntos_ordenados)-1):
                medio = (puntos_ordenados[i] + puntos_ordenados[i+1]) / 2.0
                res['bolzano'].append({'intervalo': (puntos_ordenados[i], puntos_ordenados[i+1]), 'pt': medio})
            res['bolzano'].append({'intervalo': (puntos_ordenados[-1], float('inf')), 'pt': puntos_ordenados[-1] + 1.0})

        for b in res['bolzano']:
            val_eval = f_sym.subs(x, b['pt'])
            if val_eval.is_real:
                val = float(sp.re(val_eval))
                b['valor'] = val
                b['signo'] = "C^+" if val > 0 else "C^-"
            else:
                b['valor'] = np.nan
                b['signo'] = "Fuera de Dominio"
    except:
        pass

    # 5. Preparar Derivadas
    fx = sp.diff(f_sym, x)
    fxx = sp.diff(fx, x)
    res['fx'] = fx
    res['fxx'] = fxx

    # 6. Puntos Críticos y Clasificación
    try:
        criticos = sp.solveset(fx, x, domain=S.Reals)
        res['p_criticos'] = criticos
        clasificacion = []
        if isinstance(criticos, sp.FiniteSet):
            for c in criticos:
                if c.is_real:
                    val_fxx = fxx.subs(x, c)
                    if val_fxx > 0: tipo = "Mínimo Relativo"
                    elif val_fxx < 0: tipo = "Máximo Relativo"
                    else: tipo = "Indeterminado / Inflexión"
                    clasificacion.append({'x': c, 'fxx_val': val_fxx, 'tipo': tipo})
        res['clasificacion'] = clasificacion
    except:
        res['p_criticos'] = None
        res['clasificacion'] = []

    # 7. Inflexión
    try: res['p_inflexion'] = sp.solveset(fxx, x, domain=S.Reals)
    except: res['p_inflexion'] = None

    return res