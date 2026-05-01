import streamlit as st
import numpy as np
import plotly.graph_objects as go
import sympy as sp
from math_engine import compute_analytics, analyze_polares_process, compute_directional
from plotter import create_3d_plot

st.set_page_config(page_title="Analizador AM2 Pro - UNTREF", layout="wide")

funciones_predeterminadas = {
    "Personalizada": "", "Esfera": "sqrt(9 - x**2 - y**2)", "Silla de Montar": "x**2 - y**2", 
    "Paraboloide": "x**2 + y**2", "Cono": "sqrt(x**2 + y**2)", "Hiperboloide": "sqrt(x**2 + y**2 - 1)",
    "Cilindro": "x**2", "Límite Crítico": "(x**2 * y) / (x**4 + y**2)", "Monkey Saddle": "x**3 - 3*x*y**2"
}

# --- SIDEBAR ---
st.sidebar.header("📝 Configuración")
seleccion = st.sidebar.selectbox("Función:", list(funciones_predeterminadas.keys()))
func_input = st.sidebar.text_input("f(x, y):", value=funciones_predeterminadas[seleccion] if funciones_predeterminadas[seleccion] else "x**2 - y**2")
px = st.sidebar.number_input("x0:", value=0.0); py = st.sidebar.number_input("y0:", value=0.0)

st.sidebar.subheader("🎯 Límites y Polares")
analizar_tray = st.sidebar.checkbox("Analizar por Trayectorias")
tray_opcion = st.sidebar.selectbox("Camino:", ["y=mx", "y=ax^2", "Eje X", "Eje Y"], disabled=not analizar_tray)
param = st.sidebar.slider("Parámetro:", -5.0, 5.0, 1.0, disabled=not analizar_tray)
ver_polares = st.sidebar.checkbox("Analizar por Polares")

st.sidebar.subheader("🏹 Derivadas Direccionales")
analizar_dir = st.sidebar.checkbox("Calcular Direccional")
angulo_deg = st.sidebar.slider("Ángulo θ:", 0, 360, 45, disabled=not analizar_dir)

st.sidebar.subheader("🚀 Análisis Avanzado (UNTREF)")
ver_campo_grad = st.sidebar.checkbox("Campo de Gradientes")
ver_diferencial = st.sidebar.checkbox("Diferencial Total")

st.sidebar.subheader("📍 Planos de Corte")
col_x1, col_x2 = st.sidebar.columns(2)
ver_px = col_x1.checkbox("Plano x=k"); t_x = col_x2.radio("Estilo X", ["Línea", "Sólido"], label_visibility="collapsed")
col_y1, col_y2 = st.sidebar.columns(2)
ver_py = col_y1.checkbox("Plano y=k"); t_y = col_y2.radio("Estilo Y", ["Línea", "Sólido"], label_visibility="collapsed")

config = {
    'ver_ejes': st.sidebar.checkbox("Mostrar Ejes", value=True), 'ver_plano_tan': st.sidebar.checkbox("Plano Tangente", value=True),
    'ver_rectas': st.sidebar.checkbox("Rectas Tangentes", value=True), 'ver_punto': st.sidebar.checkbox("Punto Diamante", value=True),
    'ver_campo_grad': ver_campo_grad, 'analizar_tray': analizar_tray, 'analizar_dir': analizar_dir,
    'ver_plano_x': ver_px, 'tipo_x': t_x, 'ver_plano_y': ver_py, 'tipo_y': t_y
}

# --- PROCESAMIENTO ---
try:
    data = compute_analytics(func_input, px, py)
    st.markdown(f"### 📐 Función Analizada: $f(x, y) = {sp.latex(data['f_sym'])}$")
    
    if analizar_tray:
        t = np.linspace(px-5, px+5, 100)
        if tray_opcion == "y=mx": yt = py + param*(t-px); xt = t
        elif tray_opcion == "y=ax^2": yt = py + param*(t-px)**2; xt = t
        elif tray_opcion == "Eje X": yt = np.full_like(t, py); xt = t
        else: xt = np.full_like(t, px); yt = t
        zt_raw = data['f_np'](xt, yt)
        config.update({'xt': xt, 'yt': yt, 'zt': np.where(np.abs(np.imag(zt_raw)) > 1e-5, np.nan, np.real(zt_raw))})
        z_limit_val = float(sp.re(data['f_sym'].subs({sp.Symbol('x'): px, sp.Symbol('y'): py})))

    if analizar_dir:
        ux, uy, d_dir = compute_directional(data, angulo_deg)
        config.update({'ux': ux, 'uy': uy})

    c_calc, c_graph = st.columns([1.2, 2])
    c_calc, c_graph = st.columns([1.2, 2])
    c_calc, c_graph = st.columns([1.2, 2])
    with c_calc:
        if ver_polares:
            f_sub, f_simp, lim_r = analyze_polares_process(data['f_sym'])
            with st.expander("🌀 Proceso: Cambio a Polares", expanded=True):
                st.write("**1. Sustitución:** $x = r\cos\\theta, y = r\sin\\theta$")
                st.latex(rf"f = {sp.latex(f_sub)}")
                st.write("**2. Simplificación:**")
                st.latex(rf"f = {sp.latex(f_simp)}")
                st.write(f"**3. Límite $r \\to 0$:** ${sp.latex(lim_r)}$")
        
        if ver_diferencial:
            with st.expander("📐 Diferencial Total", expanded=True):
                st.latex(rf"dz = f_x dx + f_y dy")
                st.latex(rf"dz = ({data['fx_v']:.2f})dx + ({data['fy_v']:.2f})dy")

        st.subheader("🔢 Evaluación")
        if np.isnan(data['z0']): 
            st.error("Punto fuera de dominio")
        else:
            st.latex(rf"f({px}, {py}) = {data['z0']:.2f}")
            st.write("**Vector Gradiente:**")
            # Corregido: usa el símbolo matemático \nabla en vez de texto
            st.latex(rf"\nabla f({px}, {py}) = \langle {data['fx_v']:.2f}, {data['fy_v']:.2f} \rangle")
            
            # Muestra el valor del límite si hay una trayectoria activa
            if analizar_tray: 
                st.info(rf"Valor del límite por trayectoria {tray_opcion}: **{z_limit_val:.4f}**")

        if analizar_dir:
            with st.expander("🏹 Análisis Direccional", expanded=True):
                st.write(f"**Versor unitario:** $u = \\langle \\cos({angulo_deg}^\circ), \\sin({angulo_deg}^\circ) \\rangle$")
                st.latex(rf"u = \langle {ux:.2f}, {uy:.2f} \rangle")
                st.success(rf"**Derivada Direccional:** {d_dir:.4f}")

        with st.expander("📝 Derivadas de 1° y 2° Orden", expanded=True):
            st.write("**Derivadas Primeras:**")
            # Formato: Expresión -> Evaluación
            st.latex(rf"f_x = {sp.latex(data['fx'])} \quad \rightarrow \quad f_x({px}, {py}) = {data['fx_v']:.2f}")
            st.latex(rf"f_y = {sp.latex(data['fy'])} \quad \rightarrow \quad f_y({px}, {py}) = {data['fy_v']:.2f}")
            
            st.divider()
            st.write("**Derivadas Segundas:**")
            st.latex(rf"f_{{xx}} = {sp.latex(data['fxx'])} \quad \rightarrow \quad f_{{xx}}({px}, {py}) = {data['fxx_v']:.2f}")
            st.latex(rf"f_{{yy}} = {sp.latex(data['fyy'])} \quad \rightarrow \quad f_{{yy}}({px}, {py}) = {data['fyy_v']:.2f}")
            st.latex(rf"f_{{xy}} = {sp.latex(data['fxy'])} \quad \rightarrow \quad f_{{xy}}({px}, {py}) = {data['fxy_v']:.2f}")

        with st.expander("📐 Matriz Hessiana", expanded=True):
            st.latex(r"H = \begin{pmatrix} " + f"{data['fxx_v']:.2f}" + r" & " + f"{data['fxy_v']:.2f}" + r" \\ " + f"{data['fxy_v']:.2f}" + r" & " + f"{data['fyy_v']:.2f}" + r" \end{pmatrix}")
            st.latex(rf"|H| = {data['hessiano']:.2f}")
            if data['hessiano'] > 0: 
                st.success("Extremo Relativo (Máximo)" if data['fxx_v'] < 0 else "Extremo Relativo (Mínimo)")
            elif data['hessiano'] < 0: 
                st.warning("Punto de Silla")

    with c_graph:
        xr = np.linspace(px-5, px+5, 60); yr = np.linspace(py-5, py+5, 60)
        X, Y = np.meshgrid(xr, yr); Z_raw = data['f_np'](X, Y)
        Z = np.where(np.abs(np.imag(Z_raw)) > 1e-5, np.nan, np.real(Z_raw))
        st.plotly_chart(create_3d_plot(X, Y, Z, px, py, data['z0'], data, config), use_container_width=True)

   # --- SECCIÓN TRAZAS 2D Y CURVAS DE NIVEL ---
    st.divider()
    t1, t2 = st.columns(2)
    
    with t1:
        st.subheader("📉 Trazas 2D (Cortes en el punto)")
        f2d = go.Figure()
        
        # Evaluación segura para Traza X (Plano YZ)
        z_traza_x = data['f_np'](px, yr)
        if np.isscalar(z_traza_x): 
            z_traza_x = np.full_like(yr, z_traza_x)
        
        # Evaluación segura para Traza Y (Plano XZ)
        z_traza_y = data['f_np'](xr, py)
        if np.isscalar(z_traza_y): 
            z_traza_y = np.full_like(xr, z_traza_y)

        # Agregamos las líneas al gráfico
        f2d.add_trace(go.Scatter(x=yr, y=np.real(z_traza_x), name=f"Traza x={px}", line=dict(color='black')))
        f2d.add_trace(go.Scatter(x=xr, y=np.real(z_traza_y), name=f"Traza y={py}", line=dict(color='magenta')))
        
        f2d.update_layout(xaxis_title="Eje variable", yaxis_title="z", height=400, legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01))
        st.plotly_chart(f2d, use_container_width=True)

    with t2:
        st.subheader("🗺️ Curvas de Nivel (Plano XY)")
        fig_contour = go.Figure(data=go.Contour(
            x=xr, 
            y=yr, 
            z=Z, 
            colorscale='Viridis',
            contours=dict(showlabels=True, labelfont=dict(size=12, color='white'))
        ))
        fig_contour.update_layout(xaxis_title="x", yaxis_title="y", height=400)
        st.plotly_chart(fig_contour, use_container_width=True)

    st.divider()
    st.header("🕵️ Dashboard de Análisis Integral - Reporte UNTREF")
    
    tab_geo, tab_calc, tab_lim = st.tabs([
        "🌐 Geometría y Trazas", 
        "📝 Cálculo Diferencial", 
        "🎯 Límites y Continuidad"
    ])

    with tab_geo:
        col_t1, col_t2 = st.columns([1, 1])
        with col_t1:
            st.subheader("Análisis de Superficie")
            st.write(f"**Objeto:** {seleccion}")
            st.write(f"**Punto de estudio:** $P_0({px}, {py}, {data['z0']:.2f})$")
            st.latex(rf"z = {sp.latex(data['f_sym'])}")
            
            # Clasificación por Hessiano
            if data['hessiano'] > 0:
                tipo = "Extremo Local (Cóncava)" if data['fxx_v'] > 0 else "Extremo Local (Convexa)"
                st.success(f"**Clasificación:** {tipo}")
            elif data['hessiano'] < 0:
                st.warning("**Clasificación:** Punto de Silla (Saddle Point)")
            else:
                st.info("**Clasificación:** El criterio del Hessiano no concluye.")

        with col_t2:
            st.subheader("Intersección con Planos")
            st.write(f"**Traza x = {px}:** Curva en el plano YZ")
            st.write(f"**Traza y = {py}:** Curva en el plano XZ")
            st.write("**Curvas de Nivel:** Proyecciones en el plano XY para $z=k$")

    with tab_calc:
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            st.subheader("Primer Orden")
            st.latex(rf"\nabla f = \langle {sp.latex(data['fx'])}, {sp.latex(data['fy'])} \rangle")
            st.latex(rf"\nabla f({px}, {py}) = \langle {data['fx_v']:.2f}, {data['fy_v']:.2f} \rangle")
            st.write("**Plano Tangente en $P_0$:**")
            st.latex(rf"z = {data['z0']:.2f} + {data['fx_v']:.2f}(x-{px}) + {data['fy_v']:.2f}(y-{py})")
        
        with col_c2:
            st.subheader("Segundo Orden (Hessiano)")
            st.latex(r"H = \begin{pmatrix} f_{xx} & f_{xy} \\ f_{yx} & f_{yy} \end{pmatrix}")
            st.latex(rf"|H| = ({data['fxx_v']:.2f} \cdot {data['fyy_v']:.2f}) - ({data['fxy_v']:.2f})^2 = {data['hessiano']:.2f}")
            if ver_diferencial:
                st.write("**Diferencial Total:**")
                st.latex(rf"dz = {data['fx_v']:.2f}dx + {data['fy_v']:.2f}dy")

    with tab_lim:
        st.subheader("Estudio de Límites en el Punto")
        c_l1, c_l2 = st.columns(2)
        with c_l1:
            st.write("**Análisis por Trayectorias:**")
            if analizar_tray:
                st.code(f"Trayectoria elegida: {tray_opcion}")
                st.info(rf"$\lim_{{(x,y) \to ({px},{py})}} f(x,y) \text{{ (por {tray_opcion})}} = {z_limit_val:.4f}$")
            else:
                st.write("Activa 'Analizar por Trayectorias' en la barra lateral para ver resultados.")
        
        with c_l2:
            st.write("**Análisis por Coordenadas Polares:**")
            if ver_polares:
                _, _, lim_pol = analyze_polares_process(data['f_sym'])
                st.latex(rf"\lim_{{r \to 0}} f(r, \theta) = {sp.latex(lim_pol)}")
                if lim_pol.is_number:
                    st.success("El límite parece ser independiente de $\\theta$.")
                else:
                    st.error("El límite depende de $\\theta$ (No existe o es asintótico).")
            else:
                st.write("Activa 'Analizar por Polares' para ver el desarrollo.")

except Exception as e:
    st.error(f"Error: {e}")


