import sympy as sp
import numpy as np

def compute_analytics(func_input, px, py=0.0):
    x, y = sp.symbols('x y')
    f_sym = sp.simplify(func_input)
    
    vars_presentes = f_sym.free_symbols
    es_am1 = y not in vars_presentes
    
    # Manejo de dominios complejos
    if es_am1:
        f_np_raw = sp.lambdify(x, f_sym, modules=['numpy', {'complex': np.complex128}])
        f_np = lambda val_x, val_y=0: np.where(np.abs(np.imag(f_np_raw(val_x))) > 1e-5, np.nan, np.real(f_np_raw(val_x)))
    else:
        f_np_raw = sp.lambdify((x, y), f_sym, modules=['numpy', {'complex': np.complex128}])
        f_np = lambda val_x, val_y: np.where(np.abs(np.imag(f_np_raw(val_x, val_y))) > 1e-5, np.nan, np.real(f_np_raw(val_x, val_y)))

    # Evaluación y Derivadas base
    z_eval = f_sym.subs({x: px, y: py})
    z0 = float(sp.re(z_eval)) if z_eval.is_real else np.nan
    
    fx = sp.diff(f_sym, x)
    fy = sp.diff(f_sym, y)
    
    try:
        fx_v = float(sp.re(fx.subs({x: px, y: py}))) if z_eval.is_real else np.nan
    except:
        fx_v = np.nan
        
    fy_v = 0.0
    if not es_am1:
        try:
            fy_v = float(sp.re(fy.subs({x: px, y: py})))
        except:
            fy_v = np.nan

    results = {
        "f_sym": f_sym, "f_np": f_np, "es_am1": es_am1, "z0": z0,
        "fx": fx, "fy": fy, "fx_v": fx_v, "fy_v": fy_v,
    }

    if es_am1:
        # Lógica adicional para AM1: Límites y Primitiva
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
        # Lógica AM2 (Hessiano)
        fxx = sp.diff(fx, x)
        fyy = sp.diff(fy, y)
        fxy = sp.diff(fx, y)
        try:
            fxx_v = float(sp.re(fxx.subs({x: px, y: py})))
            fyy_v = float(sp.re(fyy.subs({x: px, y: py})))
            fxy_v = float(sp.re(fxy.subs({x: px, y: py})))
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
    x = sp.Symbol('x')
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