import streamlit as st
import numpy as np
import plotly.graph_objects as go

def format_term(var, offset):
    """Formatea el texto LaTeX para los desplazamientos"""
    if offset == 0: return f"{var}^2"
    elif offset > 0: return f"({var}-{offset})^2"
    else: return f"({var}+{abs(offset)})^2"

def get_sign(val, is_first=False):
    """Evita el '+' inicial innecesario en la ecuación"""
    if is_first: return "" if val == "+" else "-"
    return "+ " if val == "+" else "- "

def render_cuadricas_interactivo():
    st.title("🧊 Laboratorio de Cuádricas y Gradientes")
    st.markdown("Visualiza la geometría del espacio, descubre cómo se calculan sus vectores normales y **domina las trazas (cortes)** para tus exámenes de Análisis II.")

    with st.sidebar:
        st.header("⚙️ Ecuación y Forma")
        familia = st.selectbox("Familia:", [
            "Centradas (Elipsoides/Hiperboloides)", 
            "Paraboloides",
            "Conos",
            "Cilindros (Z libre)"
        ])
        st.divider()
        
        st.subheader("📍 Centro (Traslación)")
        c_h, c_k, c_l = st.columns(3)
        h = c_h.slider("X (h)", -2.0, 2.0, 0.0, 0.5)
        k = c_k.slider("Y (k)", -2.0, 2.0, 0.0, 0.5)
        l = c_l.slider("Z (l)", -2.0, 2.0, 0.0, 0.5) if familia != "Cilindros (Z libre)" else 0.0

        st.divider()
        st.subheader("Signos y Denominadores")
        c1, c2, c3 = st.columns(3)
        sx = c1.radio("Signo X", ["+", "-"])
        sy = c2.radio("Signo Y", ["+", "-"])
        if familia == "Centradas (Elipsoides/Hiperboloides)":
            sz = c3.radio("Signo Z", ["+", "-"])
        elif familia == "Conos":
            sz = "-"
        else:
            sz = None
            
        a = st.slider("Eje a", 0.5, 3.0, 1.5, 0.1)
        b = st.slider("Eje b", 0.5, 3.0, 1.5, 0.1)
        if familia in ["Centradas (Elipsoides/Hiperboloides)", "Conos"]:
            c = st.slider("Eje c", 0.5, 3.0, 1.5, 0.1)
        elif familia == "Paraboloides":
            c = st.slider("Apertura c", 0.5, 3.0, 1.0, 0.1)
        else:
            c = 1.0

        st.divider()
        st.subheader("🛠️ Análisis de Superficie")
        mostrar_gradiente = st.toggle("Mostrar Vectores Gradientes (∇F)", value=False)
        z_slice = st.slider("Plano de Corte Z = k", -4.0, 4.0, 0.0, 0.1)
        st.divider()
        st.subheader("🚀 Punto P₀ y Plano Tangente")
        mostrar_pt = st.toggle("Analizar punto P₀", value=False)
        if mostrar_pt:
            x0 = st.slider("P₀ (X)", -2.0, 2.0, 0.5, 0.1)
            y0 = st.slider("P₀ (Y)", -2.0, 2.0, 0.5, 0.1)

    # --- LÓGICA DE IDENTIFICACIÓN ---
    term_x = format_term("x", h)
    term_y = format_term("y", k)
    term_z = format_term("z", l)

    if familia == "Centradas (Elipsoides/Hiperboloides)":
        negativos = [sx, sy, sz].count("-")
        if negativos == 0:
            tipo, color = ("Esfera", "Viridis") if a == b == c else ("Elipsoide", "Viridis")
        elif negativos == 1:
            tipo, color = "Hiperboloide de Una Hoja", "Plasma"
        elif negativos == 2:
            tipo, color = "Hiperboloide de Dos Hojas", "Inferno"
        else:
            tipo, color = "Superficie Vacía", "Greys"
            
        eq_latex = f"{get_sign(sx, True)}\\frac{{{term_x}}}{{{a**2:.1f}}} {get_sign(sy)} \\frac{{{term_y}}}{{{b**2:.1f}}} {get_sign(sz)} \\frac{{{term_z}}}{{{c**2:.1f}}} = 1"
        iso_target = 1.0

    elif familia == "Paraboloides":
        negativos = [sx, sy].count("-")
        if negativos == 0:
            tipo, color = "Paraboloide Elíptico", "Teal"
        elif negativos == 1:
            tipo, color = "Paraboloide Hiperbólico (Silla)", "Rainbow"
        else:
            tipo, color = "Paraboloide Invertido", "Teal"
            
        eq_latex = f"z - {l} = {c:.1f} \\cdot \\left( {get_sign(sx, True)}\\frac{{{term_x}}}{{{a**2:.1f}}} {get_sign(sy)} \\frac{{{term_y}}}{{{b**2:.1f}}} \\right)"
        iso_target = 0.0

    elif familia == "Conos":
        tipo, color = "Cono Elíptico", "Cividis"
        eq_latex = f"{get_sign(sx, True)}\\frac{{{term_x}}}{{{a**2:.1f}}} {get_sign(sy)} \\frac{{{term_y}}}{{{b**2:.1f}}} - \\frac{{{term_z}}}{{{c**2:.1f}}} = 0"
        iso_target = 0.0

    elif familia == "Cilindros (Z libre)":
        negativos = [sx, sy].count("-")
        if negativos == 0:
            tipo, color = "Cilindro Elíptico", "Blues"
        elif negativos == 1:
            tipo, color = "Cilindro Hiperbólico", "Oranges"
        else:
            tipo, color = "Vacío", "Greys"
            
        eq_latex = f"{get_sign(sx, True)}\\frac{{{term_x}}}{{{a**2:.1f}}} {get_sign(sy)} \\frac{{{term_y}}}{{{b**2:.1f}}} = 1 \\quad (z \\in \\mathbb{{R}})"
        iso_target = 1.0

    st.markdown(f"### ✨ {tipo}")
    st.latex(eq_latex)

    # --- RENDERIZADO 3D (Optimizado) ---
    fig = go.Figure()
    limit = 5.0
    res = 30  # Bajamos resolución para mayor fluidez
    
    x, y, z = np.mgrid[-limit:limit:res*1j, -limit:limit:res*1j, -limit:limit:res*1j]
    xs, ys, zs = x - h, y - k, z - l
    
    val_x = (xs**2 / a**2) * (1 if sx == "+" else -1)
    val_y = (ys**2 / b**2) * (1 if sy == "+" else -1)
    
    if familia == "Centradas (Elipsoides/Hiperboloides)":
        val_z = (zs**2 / c**2) * (1 if sz == "+" else -1)
        f_val = val_x + val_y + val_z
        grad_latex = f"\\nabla F = \\left\\langle {get_sign(sx, True)}\\frac{{2(x-{h})}}{{{a**2:.1f}}}, {get_sign(sy)}\\frac{{2(y-{k})}}{{{b**2:.1f}}}, {get_sign(sz)}\\frac{{2(z-{l})}}{{{c**2:.1f}}} \\right\\rangle"
    elif familia == "Paraboloides":
        f_val = val_x + val_y - (zs / c)
        grad_latex = f"\\nabla F = \\left\\langle {get_sign(sx, True)}\\frac{{2(x-{h})}}{{{a**2:.1f}}}, {get_sign(sy)}\\frac{{2(y-{k})}}{{{b**2:.1f}}}, -\\frac{{1}}{{{c:.1f}}} \\right\\rangle"
    elif familia == "Conos":
        val_z = -(zs**2 / c**2)
        f_val = val_x + val_y + val_z
        grad_latex = f"\\nabla F = \\left\\langle {get_sign(sx, True)}\\frac{{2(x-{h})}}{{{a**2:.1f}}}, {get_sign(sy)}\\frac{{2(y-{k})}}{{{b**2:.1f}}}, -\\frac{{2(z-{l})}}{{{c**2:.1f}}} \\right\\rangle"
    elif familia == "Cilindros (Z libre)":
        f_val = val_x + val_y
        grad_latex = f"\\nabla F = \\left\\langle {get_sign(sx, True)}\\frac{{2(x-{h})}}{{{a**2:.1f}}}, {get_sign(sy)}\\frac{{2(y-{k})}}{{{b**2:.1f}}}, 0 \\right\\rangle"
    # 1. Superficie Principal
    fig.add_trace(go.Isosurface(
        x=x.flatten(), y=y.flatten(), z=z.flatten(),
        value=f_val.flatten(), isomin=iso_target - 0.05, isomax=iso_target + 0.05,
        surface_count=1, colorscale=color, opacity=0.6, showscale=False,
        caps=dict(x_show=False, y_show=False, z_show=False)
    ))

    # 2. Vectores Gradientes
    if mostrar_gradiente:
        st.info("💡 Los vectores rojos representan el Campo Gradiente (∇F). Siempre apuntan en dirección **perpendicular (normal)** a la superficie en cada punto.")
        st.caption("Nota: Se calculan asumiendo que la ecuación está igualada a una constante $K$. Por lo tanto, $F(x,y,z) = K$.")
        mask = np.abs(f_val - iso_target) < 0.2
        xm, ym, zm = x[mask], y[mask], z[mask]
        
        gx = (2 * (xm - h) / a**2) * (1 if sx == "+" else -1)
        gy = (2 * (ym - k) / b**2) * (1 if sy == "+" else -1)
        if familia in ["Centradas (Elipsoides/Hiperboloides)", "Conos"]:
            gz = (2 * (zm - l) / c**2) * (1 if sz == "+" else -1)
        elif familia == "Paraboloides":
            gz = np.full_like(xm, -1.0 / c)
        else:
            gz = np.zeros_like(xm)
            
        sub_step = max(1, len(xm) // 150)
        fig.add_trace(go.Cone(
            x=xm[::sub_step], y=ym[::sub_step], z=zm[::sub_step],
            u=gx[::sub_step], v=gy[::sub_step], w=gz[::sub_step],
            sizemode="absolute", sizeref=0.8, colorscale="Reds", showscale=False
        ))

    # 3. Plano de Corte Dinámico
    # === PLANO TANGENTE EN P0 ===
    if mostrar_pt:
        dx, dy = x0 - h, y0 - k
        z0 = np.nan
        if familia == "Paraboloides":
            f_val = val_x + val_y - (zs / c)
            grad_latex = f"\\nabla F = \\left\\langle {get_sign(sx, True)}\\frac{{2(x-{h})}}{{{a**2:.1f}}}, {get_sign(sy)}\\frac{{2(y-{k})}}{{{b**2:.1f}}}, -\\frac{{1}}{{{c:.1f}}} \\right\\rangle"
        else:
            rhs_z = iso_target - (dx**2 / a**2)*(1 if sx=="+" else -1) - (dy**2 / b**2)*(1 if sy=="+" else -1)
            if sz == "+" and rhs_z >= 0: z0 = l + c * np.sqrt(rhs_z)
            elif sz == "-" and rhs_z <= 0: z0 = l + c * np.sqrt(abs(rhs_z))

        if not np.isnan(z0):
            gx = (2 * dx / a**2) * (1 if sx == "+" else -1)
            gy = (2 * dy / b**2) * (1 if sy == "+" else -1)
            gz = (2 * (z0 - l) / c**2) * (1 if sz == "+" else -1) if familia != "Paraboloides" else -1/c
            
            fig.add_trace(go.Scatter3d(x=[x0], y=[y0], z=[z0], mode='markers', marker=dict(size=6, color='red'), name="P₀"))
            fig.add_trace(go.Cone(x=[x0], y=[y0], z=[z0], u=[gx], v=[gy], w=[gz], sizemode="absolute", sizeref=1.5, colorscale="Reds", showscale=False))
            
            if gz != 0:
                tp_x, tp_y = np.meshgrid(np.linspace(x0-1.5, x0+1.5, 5), np.linspace(y0-1.5, y0+1.5, 5))
                tp_z = z0 - (gx*(tp_x - x0) + gy*(tp_y - y0)) / gz
                fig.add_trace(go.Surface(x=tp_x, y=tp_y, z=tp_z, colorscale="Greens", opacity=0.5, showscale=False))

    # === PLANO DE CORTE Y TRAZAS REALES ===
    px, py = np.meshgrid([-limit, limit], [-limit, limit])
    fig.add_trace(go.Surface(x=px, y=py, z=np.full_like(px, z_slice), colorscale="Greys", opacity=0.3, showscale=False, hoverinfo='skip'))

    t = np.linspace(0, 2*np.pi, 150)
    traza_msg = ""

    # Calcular lado derecho (RHS)
    if familia == "Paraboloides":
        rhs = (z_slice - l) / c
    else:
        z_term = ((z_slice - l)**2 / c**2) * (1 if sz == "+" else -1)
        rhs = iso_target - z_term

    if sx == "+" and sy == "+": # Familia Elíptica
        if rhs > 0:
            rx, ry = a * np.sqrt(rhs), b * np.sqrt(rhs)
            xc, yc = h + rx * np.cos(t), k + ry * np.sin(t)
            fig.add_trace(go.Scatter3d(x=xc, y=yc, z=np.full_like(xc, z_slice), mode='lines', line=dict(color='yellow', width=6)))
            traza_msg = f"🟢 **Traza en Z={z_slice}:** Elipse (Semiejes: {rx:.2f}, {ry:.2f})"
        elif rhs == 0:
            fig.add_trace(go.Scatter3d(x=[h], y=[k], z=[z_slice], mode='markers', marker=dict(color='yellow', size=6)))
            traza_msg = f"🟡 **Traza en Z={z_slice}:** Punto (Vértice)"
        else:
            traza_msg = f"🔴 **Traza en Z={z_slice}:** Conjunto Vacío"
            
    elif sx != sy: # Familia Hiperbólica
        t_h = np.linspace(-2, 2, 100)
        if rhs != 0:
            sc = np.sqrt(abs(rhs))
            if (sx == "+" and rhs > 0) or (sx == "-" and rhs < 0):
                xc1, yc1 = h + a * sc * np.cosh(t_h), k + b * sc * np.sinh(t_h)
                xc2, yc2 = h - a * sc * np.cosh(t_h), k + b * sc * np.sinh(t_h)
            else:
                xc1, yc1 = h + a * sc * np.sinh(t_h), k + b * sc * np.cosh(t_h)
                xc2, yc2 = h + a * sc * np.sinh(t_h), k - b * sc * np.cosh(t_h)
            
            fig.add_trace(go.Scatter3d(x=xc1, y=yc1, z=np.full_like(xc1, z_slice), mode='lines', line=dict(color='yellow', width=6)))
            fig.add_trace(go.Scatter3d(x=xc2, y=yc2, z=np.full_like(xc2, z_slice), mode='lines', line=dict(color='yellow', width=6)))
            traza_msg = f"🟢 **Traza en Z={z_slice}:** Hipérbola con centro en ({h}, {k})"
        else:
            x_line = np.linspace(h-limit, h+limit, 100)
            m = (b/a)
            y_line1, y_line2 = k + m * (x_line - h), k - m * (x_line - h)
            fig.add_trace(go.Scatter3d(x=x_line, y=y_line1, z=np.full_like(x_line, z_slice), mode='lines', line=dict(color='yellow', width=6)))
            fig.add_trace(go.Scatter3d(x=x_line, y=y_line2, z=np.full_like(x_line, z_slice), mode='lines', line=dict(color='yellow', width=6)))
            traza_msg = f"🟡 **Traza en Z={z_slice}:** Par de rectas cruzadas en ({h}, {k})"
            
    else: # Familia Elíptica Invertida (Signos - y -)
        if rhs < 0:
            rx, ry = a * np.sqrt(abs(rhs)), b * np.sqrt(abs(rhs))
            xc, yc = h + rx * np.cos(t), k + ry * np.sin(t)
            fig.add_trace(go.Scatter3d(x=xc, y=yc, z=np.full_like(xc, z_slice), mode='lines', line=dict(color='yellow', width=6)))
            traza_msg = f"🟢 **Traza en Z={z_slice}:** Elipse (Semiejes: {rx:.2f}, {ry:.2f})"
        elif rhs == 0:
            fig.add_trace(go.Scatter3d(x=[h], y=[k], z=[z_slice], mode='markers', marker=dict(color='yellow', size=6)))
            traza_msg = f"🟡 **Traza en Z={z_slice}:** Punto (Vértice)"
        else:
            traza_msg = f"🔴 **Traza en Z={z_slice}:** Conjunto Vacío"

    # Mostrar Información de la Traza
    st.markdown(traza_msg)
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    # Agrega esto justo debajo del gráfico
    st.info(traza_msg)


    st.divider()
    st.header("📝 Análisis Exhaustivo de la Superficie")
    
    t1, t2, t3, t4 = st.tabs(["1. Trazas y Ecuaciones", "2. Vector Gradiente y Plano Tangente", "3. Integrales Múltiples", "4. Tips de Examen"])
    
    with t1:
        st.markdown("### Geometría Analítica")
        st.write("La ecuación superior está en su **forma canónica** (normalizada). Cuando igualas la variable Z a una constante $k$ (usando el slider del plano de corte), pasas de 3 dimensiones a 2. Ese es el truco algebraico para hallar las trazas.")
        if familia == "Centradas (Elipsoides/Hiperboloides)":
            st.latex(f"\\frac{{(x-{h})^2}}{{{a**2:.2f}}} + \\frac{{(y-{k})^2}}{{{b**2:.2f}}} = 1 - \\frac{{({z_slice}-{l})^2}}{{{c**2:.2f}}}")
            st.info("💡 **Análisis del Lado Derecho (RHS):** Si el resultado es positivo, la traza es una elipse o circunferencia. Si es cero, es un punto (vértice). Si es negativo, el plano no intersecta la figura (traza vacía).")
        elif familia == "Paraboloides":
            st.write("Ecuación del corte horizontal para el paraboloide actual:")
            st.latex(f"\\frac{{(x-{h})^2}}{{{a**2:.2f}}} {get_sign(sy)} \\frac{{(y-{k})^2}}{{{b**2:.2f}}} = \\frac{{{z_slice}-{l}}}{{{c:.2f}}}")
        elif familia == "Conos":
            st.write("Ecuación del corte horizontal:")
            st.latex(f"\\frac{{(x-{h})^2}}{{{a**2:.2f}}} {get_sign(sy)} \\frac{{(y-{k})^2}}{{{b**2:.2f}}} = \\frac{{({z_slice}-{l})^2}}{{{c**2:.2f}}}")
            
    with t2:
        st.markdown("### El Campo de Gradientes ($\\nabla F$)")
        st.success("✔️ **Dato Estructural:** El gradiente es siempre un vector **normal (perpendicular)** a la superficie en el punto de evaluación. Esto funciona asumiendo que la superficie es una curva de nivel $F(x,y,z) = K$.")
        st.latex(grad_latex)
        
        st.markdown("### Ecuación del Plano Tangente")
        st.write("Conociendo el gradiente en un punto $P_0(x_0, y_0, z_0)$, la ecuación del plano que \"acaricia\" a la figura se arma con un producto escalar:")
        st.latex(r"F_x(P_0)(x-x_0) + F_y(P_0)(y-y_0) + F_z(P_0)(z-z_0) = 0")
        st.success("✔️ **Dato Estructural:** En un Elipsoide, el gradiente siempre apunta hacia afuera. En un hiperboloide, nos indica hacia dónde se 'abre' la superficie.")

    with t3:
        st.markdown("### Parametrización y Jacobianos")
        st.write("Dependiendo de la simetría de la cuádrica, te conviene cambiar de sistema para resolver **Integrales Triples** (Cálculo de volúmenes o masa):")
        
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**Esféricas (Esferas y Conos)**")
            st.latex(r"\begin{cases} x = \rho \sin(\phi) \cos(\theta) \\ y = \rho \sin(\phi) \sin(\theta) \\ z = \rho \cos(\phi) \end{cases}")
            st.caption("Jacobiano: $J = \rho^2 \sin(\phi)$")
        with c2:
            st.markdown("**Cilíndricas (Cilindros y Paraboloides)**")
            st.latex(r"\begin{cases} x = r \cos(\theta) \\ y = r \sin(\theta) \\ z = z \end{cases}")
            st.caption("Jacobiano: $J = r$")

    with t4:
        st.markdown("### 🚨 Trampas comunes en Finales")
        st.warning("**1. Completar Cuadrados:** Si la ecuación tiene términos lineales (ej: $4x^2 - 8x...$), la figura NO está en el origen. Debes completar cuadrados para hallar el centro $(h, k, l)$ antes de intentar graficarla.")
        st.error("**2. Conos vs Paraboloides:** Un error típico es confundir $z = x^2 + y^2$ (Paraboloide) con $z^2 = x^2 + y^2$ (Cono). ¡Ojo con el exponente de Z!")
        st.info("**3. Cilindros:** Un cilindro se reconoce algebraicamente porque **falta una variable** en su ecuación general.")
