import sympy as sp
import numpy as np

def compute_analytics(func_input, px, py):
    x, y = sp.symbols('x y') # Definir solo x e y aquí para evitar conflictos
    f_sym = sp.simplify(func_input)
    
    # FORZAR que lambdify siempre reciba x e y, aunque la función sea solo f(x)=x^2
    f_np = sp.lambdify((x, y), f_sym, modules=['numpy'])
    
    # Derivadas (ahora SymPy tratará a la variable faltante como constante = 0)
    df_dx = sp.diff(f_sym, x)
    df_dy = sp.diff(f_sym, y)
    fxx = sp.diff(df_dx, x)
    fyy = sp.diff(df_dy, y)
    fxy = sp.diff(df_dx, y)
    
    # ... resto del código de evaluaciones numéricas igual ...
    
    # Evaluaciones numéricas
    z_eval = f_sym.subs({x: px, y: py})
    z0 = float(sp.re(z_eval)) if z_eval.is_real else np.nan
    fx_v = float(sp.re(df_dx.subs({x: px, y: py})))
    fy_v = float(sp.re(df_dy.subs({x: px, y: py})))
    fxx_v = float(sp.re(fxx.subs({x: px, y: py})))
    fyy_v = float(sp.re(fyy.subs({x: px, y: py})))
    fxy_v = float(sp.re(fxy.subs({x: px, y: py})))
    
    return {
        "f_sym": f_sym, "f_np": f_np, "z0": z0,
        "fx": df_dx, "fy": df_dy, "fx_v": fx_v, "fy_v": fy_v,
        "fxx": fxx, "fyy": fyy, "fxy": fxy,
        "fxx_v": fxx_v, "fyy_v": fyy_v, "fxy_v": fxy_v,
        "hessiano": fxx_v * fyy_v - fxy_v**2
    }

def analyze_polares_process(f_sym):
    x, y, r, theta = sp.symbols('x y r theta')
    # Sustitución analítica (Unidad II)
    f_pol_sub = f_sym.subs({x: r*sp.cos(theta), y: r*sp.sin(theta)})
    f_pol_simp = sp.simplify(f_pol_sub)
    lim_r = sp.limit(f_pol_simp, r, 0)
    return f_pol_sub, f_pol_simp, lim_r

def compute_directional(data, angle_deg):
    alpha = np.deg2rad(angle_deg)
    ux, uy = np.cos(alpha), np.sin(alpha)
    # Derivada direccional (Unidad III)
    deriv_dir = data['fx_v'] * ux + data['fy_v'] * uy
    return ux, uy, deriv_dir