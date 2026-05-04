import streamlit as st
import numpy as np
import plotly.graph_objects as go
import sympy as sp
from sympy import S
from modules.geometria import render_trigonometria_interactiva
from modules.cuadricas import render_cuadricas_interactivo

try:
    from .math_engine import compute_analytics, analyze_polares_process, compute_directional, get_taylor_step_by_step, get_full_analysis
    from .plotter import create_3d_plot
except (ImportError, ValueError):
    from math_engine import compute_analytics, analyze_polares_process, compute_directional, get_taylor_step_by_step, get_full_analysis
    from plotter import create_3d_plot

st.set_page_config(page_title="Analizador Matemático", layout="wide")

# --- FIX: Inicialización global para evitar errores "not defined" ---
px, py = 0.0, 0.0

# --- SIDEBAR ---
st.sidebar.header("🎓 Modo de Estudio")
modo = st.sidebar.selectbox("Seleccionar Materia", 
    ["Análisis Matemático I", "Análisis Matemático II", "Trigonometría Interactiva", "Laboratorio de Cuádricas"])

# Inicialización global para evitar errores al cambiar entre materias
px, py = 0.0, 0.0
config = {}


if modo == "Trigonometría Interactiva":
    # Llamamos a la función del nuevo archivo
    render_trigonometria_interactiva()


elif modo == "Análisis Matemático II":
    st.sidebar.subheader("📝 Configuración")
    funciones_predeterminadas = {
        "Personalizada": "", "Silla de Montar": "x**2 - y**2", "Paraboloide": "x**2 + y**2",
        "Esfera": "sqrt(9 - x**2 - y**2)", "Cono": "sqrt(x**2 + y**2)", 
        "Límite Crítico": "(x**2 * y) / (x**4 + y**2)", "Monkey Saddle": "x**3 - 3*x*y**2"
    }
    seleccion = st.sidebar.selectbox("Función predeterminada:", list(funciones_predeterminadas.keys()))
    val_default = funciones_predeterminadas[seleccion] if funciones_predeterminadas[seleccion] else "x**2 - y**2"
    func_input = st.sidebar.text_input("f(x, y):", value=val_default)

    col1, col2 = st.sidebar.columns(2)
    px = col1.number_input("x0:", value=0.0, step=0.5)
    py = col2.number_input("y0:", value=0.0, step=0.5)

    st.sidebar.subheader("🎯 Límites y Polares")
    analizar_tray = st.sidebar.checkbox("Analizar por Trayectorias")
    tray_opcion = st.sidebar.selectbox("Camino:", ["y=mx", "y=ax^2", "Eje X", "Eje Y"], disabled=not analizar_tray)
    param = st.sidebar.slider("Parámetro (m o a):", -5.0, 5.0, 1.0, disabled=not analizar_tray)
    ver_polares = st.sidebar.checkbox("Analizar por Polares", value=True)

    st.sidebar.subheader("🏹 Derivadas Direccionales")
    analizar_dir = st.sidebar.checkbox("Calcular Direccional")
    angulo_deg = st.sidebar.slider("Ángulo θ:", 0, 360, 45, disabled=not analizar_dir)

    st.sidebar.subheader("🚀 Análisis Avanzado")
    ver_campo_grad = st.sidebar.checkbox("Campo de Gradientes")
    ver_diferencial = st.sidebar.checkbox("Diferencial Total", value=True)

    st.sidebar.subheader("📍 Planos de Corte")
    c_x1, c_x2 = st.sidebar.columns(2)
    ver_px = c_x1.checkbox("Plano x=k")
    t_x = c_x2.radio("Estilo X", ["Línea", "Sólido"], label_visibility="collapsed")
    c_y1, c_y2 = st.sidebar.columns(2)
    ver_py = c_y1.checkbox("Plano y=k")
    t_y = c_y2.radio("Estilo Y", ["Línea", "Sólido"], label_visibility="collapsed")

    config.update({
        'ver_ejes': st.sidebar.checkbox("Mostrar Ejes", value=True), 'ver_plano_tan': st.sidebar.checkbox("Plano Tangente", value=True),
        'ver_rectas': st.sidebar.checkbox("Rectas Tangentes", value=True), 'ver_punto': st.sidebar.checkbox("Punto Diamante", value=True),
        'ver_campo_grad': ver_campo_grad, 'analizar_tray': analizar_tray, 'analizar_dir': analizar_dir,
        'ver_plano_x': ver_px, 'tipo_x': t_x, 'ver_plano_y': ver_py, 'tipo_y': t_y
    })
elif modo == "Laboratorio de Cuádricas":
    render_cuadricas_interactivo()

else:
    # --- MODO AM1: INTERFAZ PEDAGÓGICA ---
    st.sidebar.subheader("📝 Configuración AM1")
    presets_am1 = {
        "Personalizada": "", 
        "Seno de x²": "sin(x**2)", 
        "Exponencial x³": "exp(x**3)",
        "Logaritmo Natural": "log(x)", 
        "Función Racional": "1/(x-1)", 
        "Raíz Cuadrada": "sqrt(x+2)",
        "Valor Absoluto (Módulo)": "Abs(x)",
        "Función a Trozos": "Piecewise((x**2, x < 1), (2*x, x >= 1))"
    }
    sel_am1 = st.sidebar.selectbox("Funciones predeterminadas:", list(presets_am1.keys()))
    func_input = st.sidebar.text_input("f(x):", value=presets_am1[sel_am1] if presets_am1[sel_am1] else "sin(x**2)")
    
    px = st.sidebar.slider("Punto de Estudio (x0):", -5.0, 5.0, 0.0, step=0.1)
    py = 0.0 # Aseguramos que 'py' exista siempre para el motor matemático
    
    st.sidebar.subheader("⚙️ Herramientas de Análisis")
    grado_taylor = st.sidebar.slider("Grado Taylor (n):", 1, 10, 2)
    ver_tangente_am1 = st.sidebar.checkbox("Ver Recta Tangente", value=True)

    st.sidebar.subheader("🧱 Integración Definida")
    ver_riemann = st.sidebar.checkbox("Ver Sumas de Riemann", value=False)
    n_rects = st.sidebar.slider("Cant. Rectángulos:", 5, 100, 10, disabled=not ver_riemann)
    lim_a = st.sidebar.number_input("Límite inferior (a):", value=float(px))
    lim_b = st.sidebar.number_input("Límite superior (b):", value=float(px + 2.0))

# --- PROCESAMIENTO PRINCIPAL ---
if modo in ["Análisis Matemático I", "Análisis Matemático II"]:
    try:
        data = compute_analytics(func_input, px, py)
        st.title(f"🎓 {modo}")
        
        

        col_calc, col_graph = st.columns([1.3, 2])

        with col_calc:
            # ---COMPROBACIÓN DE DOMINIO ---
            # ---COMPROBACIÓN DE DOMINIO ---
            if np.isnan(data['z0']):
                if modo == "Análisis Matemático II":
                    st.error(f"❌ El punto $(x_0, y_0) = ({px}, {py})$ está fuera del dominio de la función.")
                else:
                    st.error(f"❌ El punto $x_0 = {px}$ está fuera del dominio de la función.")
                st.warning("No es posible realizar el análisis en este valor (Indeterminación o Complejo).")
                st.stop() # Esto detiene la ejecución de los tabs para que no tiren error
            # ------------------------------------

            if modo == "Análisis Matemático II":
                st.markdown(f"### 📐 Función Analizada:\n$f(x,y) = {sp.latex(data['f_sym'])}$")
                
                # 1. POLARES
                if ver_polares:
                    f_sub, f_simp, lim_r = analyze_polares_process(data['f_sym'])
                    with st.expander("🌀 Proceso: Cambio a Polares", expanded=True):
                        st.write(r"1. Sustitución: $x = r\cos\theta, \quad y = r\sin\theta$")
                        st.latex(rf"f(r, \theta) = {sp.latex(f_sub)}")
                        st.write("**2. Simplificación:**")
                        st.latex(rf"f(r, \theta) = {sp.latex(f_simp)}")
                        st.write("**3. Límite cuando $r \\to 0$:**")
                        st.latex(rf"\lim_{{r \to 0}} f(r, \theta) = {sp.latex(lim_r)}")

                # 2. DIFERENCIAL TOTAL
                if ver_diferencial:
                    with st.expander("📐 Diferencial Total", expanded=True):
                        st.latex(r"dz = \frac{\partial f}{\partial x} dx + \frac{\partial f}{\partial y} dy")
                        st.latex(rf"dz = ({data['fx_v']:.4f})dx + ({data['fy_v']:.4f})dy")

                # 3. EVALUACIÓN Y GRADIENTE
                st.subheader("🔢 Evaluación")
                if np.isnan(data['z0']):
                    st.error("Punto fuera de dominio real")
                else:
                    st.latex(rf"f({px}, {py}) = {data['z0']:.4f}")
                    st.write("**Vector Gradiente:**")
                    st.latex(rf"\nabla f({px}, {py}) = \langle {data['fx_v']:.4f}, {data['fy_v']:.4f} \rangle")

                # 4. DERIVADA DIRECCIONAL
                if analizar_dir:
                    ux, uy, d_dir = compute_directional(data, angulo_deg)
                    config.update({'ux': ux, 'uy': uy})
                    with st.expander("🏹 Análisis Direccional", expanded=True):
                        st.latex(rf"\vec{{u}} = \langle {ux:.4f}, {uy:.4f} \rangle")
                        st.success(rf"D_u f({px}, {py}) = {d_dir:.4f}")

                # 5. DERIVADAS SUCESIVAS
                with st.expander("📝 Derivadas de 1° y 2° Orden", expanded=True):
                    st.write("**Derivadas Primeras:**")
                    st.latex(rf"f_x = {sp.latex(data['fx'])} \quad \rightarrow \quad f_x({px}, {py}) = {data['fx_v']:.2f}")
                    st.latex(rf"f_y = {sp.latex(data['fy'])} \quad \rightarrow \quad f_y({px}, {py}) = {data['fy_v']:.2f}")
                    st.divider()
                    st.write("**Derivadas Segundas:**")
                    st.latex(rf"f_{{xx}} = {sp.latex(data['fxx'])} \quad \rightarrow \quad f_{{xx}}({px}, {py}) = {data.get('fxx_v', 0):.2f}")
                    st.latex(rf"f_{{yy}} = {sp.latex(data['fyy'])} \quad \rightarrow \quad f_{{yy}}({px}, {py}) = {data.get('fyy_v', 0):.2f}")
                    st.latex(rf"f_{{xy}} = {sp.latex(data['fxy'])} \quad \rightarrow \quad f_{{xy}}({px}, {py}) = {data.get('fxy_v', 0):.2f}")

            else:
                # --- TABS PEDAGÓGICOS AM1 ---
                st.markdown(f"### 📐 Función Analizada:\n$$f(x) = {sp.latex(data['f_sym'])}$$")
                # --- ACTUALIZAR LA LISTA DE TABS ---
                tabs = st.tabs(["📉 Derivada y Tangente", "📝 Taylor", "⚖️ Continuidad", "∫ Integración", "🔎 Estudio Completo"])
                
                with tabs[0]:
                    st.subheader("La Recta Tangente")
                    st.write("La derivada en un punto representa la pendiente de la recta tangente.")
                    st.latex(r"y = f(x_0) + f'(x_0)(x - x_0)")
                    st.write("**1. Derivada analítica:**")
                    st.latex(rf"f'(x) = {sp.latex(data['fx'])}")
                    st.write(f"**2. Evaluación en $x_0 = {px}$:**")
                    if not np.isnan(data['fx_v']):
                        st.latex(rf"f'({px}) = {data['fx_v']:.4f}")
                        st.write("**3. Ecuación final:**")
                        st.latex(rf"y = {data['z0']:.2f} + ({data['fx_v']:.4f})(x - {px})")
                    else:
                        st.error("La función no es derivable en este punto.")

                with tabs[1]:
                    st.subheader("Proceso de Taylor")
                    st.write("Aproximación por suma de potencias:")
                    st.latex(r"P_n(x) = \sum_{k=0}^{n} \frac{f^{(k)}(x_0)}{k!}(x - x_0)^k")
                    pasos = get_taylor_step_by_step(data['f_sym'], px, grado_taylor)
                    for p in pasos:
                        with st.expander(f"Término de orden $k = {p['orden']}$"):
                            st.write("**Derivada simbólica:**")
                            st.latex(sp.latex(p['derivada_simbolica']))
                            st.write(f"**Evaluada en $x_0 = {px}$:**")
                            try:
                                # Forzamos evaluación numérica con evalf()
                                val_num = float(p['valor_evaluado'].evalf())
                                st.latex(rf"f^{{({p['orden']})}}({px}) = {val_num:.4f}")
                            except:
                                st.latex(rf"f^{{({p['orden']})}}({px}) = \text{{Indefinido}}")
                            st.write("**Término resultante:**")
                            st.latex(sp.latex(p['termino_completo']))
                    
                    polinomio_final = sum([p['termino_completo'] for p in pasos])
                    st.success(f"**Polinomio de Taylor Grado {grado_taylor}:**")
                    st.latex(sp.latex(polinomio_final))

                with tabs[2]:
                    st.subheader("Análisis Gráfico de Límites y Continuidad")
                    
                    # --- DETECCIÓN DE FUNCIÓN A TROZOS ---
                    if "Piecewise" in str(data['f_sym']):
                        st.info("💡 **Nota:** Has ingresado una función a trozos. El análisis de continuidad es clave en los puntos donde cambia la regla (por ejemplo, en $x=1$). Usa el deslizador para estudiar ese punto exacto.")
                    # -------------------------------------
                    
                    st.write(f"Estudiamos el comportamiento de la función en el entorno de $x_0 = {px}$:")
                    
                    # --- LÓGICA DE GRÁFICO DE LÍMITES ---
                    # Creamos un zoom mucho más cerrado alrededor de px
                    x_env = np.linspace(px - 1.5, px + 1.5, 400)
                    y_env = data["f_np"](x_env)
                    
                    fig_lim = go.Figure()
                    
                    # 1. Dibujar la función
                    fig_lim.add_trace(go.Scatter(x=x_env, y=y_env, name="f(x)", line=dict(color='#1f77b4', width=3)))
                    
                    # 2. Dibujar indicadores de límites laterales (si son finitos)
                    try:
                        l_izq = float(data['lim_izq'])
                        l_der = float(data['lim_der'])
                        
                        # Línea desde la izquierda
                        fig_lim.add_trace(go.Scatter(x=[px-1, px], y=[l_izq, l_izq], 
                                                    mode='lines', name="Límite Izq",
                                                    line=dict(color='green', dash='dot')))
                        # Línea desde la derecha
                        fig_lim.add_trace(go.Scatter(x=[px, px+1], y=[l_der, l_der], 
                                                    mode='lines', name="Límite Der",
                                                    line=dict(color='orange', dash='dot')))
                    except: pass

                    # 3. Punto de la imagen real f(x0)
                    if not np.isnan(data['z0']):
                        fig_lim.add_trace(go.Scatter(x=[px], y=[data['z0']], mode='markers',
                                                    marker=dict(size=12, color='blue', symbol='circle'),
                                                    name=f"Imagen f({px})"))
                    else:
                        # Si no hay imagen, dibujamos un círculo vacío (punto abierto)
                        fig_lim.add_trace(go.Scatter(x=[px], y=[l_izq if 'l_izq' in locals() else 0], 
                                                    mode='markers',
                                                    marker=dict(size=12, color='red', symbol='circle-open'),
                                                    name="Punto Abierto"))

                    fig_lim.update_layout(height=400, title="Zoom del Entorno de x0", showlegend=True)
                    st.plotly_chart(fig_lim, width='stretch')

                    # --- EXPLICACIÓN TEÓRICA PASO A PASO ---
                    st.divider()
                    col_l, col_r = st.columns(2)
                    with col_l:
                        st.write("**1. Límites Laterales:**")
                        st.latex(rf"\lim_{{x \to {px}^-}} f(x) = {sp.latex(data['lim_izq'])}")
                        st.latex(rf"\lim_{{x \to {px}^+}} f(x) = {sp.latex(data['lim_der'])}")
                    
                    with col_r:
                        st.write("**2. Existencia de Imagen:**")
                        if np.isnan(data['z0']):
                            st.error(f"❌ $f({px})$ no existe.")
                        else:
                            st.success(f"✅ $f({px}) = {data['z0']:.4f}$")

                    # Conclusión de Continuidad
                    # Conclusión de Continuidad
                    try:
                        l_i = float(data['lim_izq'])
                        l_d = float(data['lim_der'])
                        z_v = float(data['z0'])
                        
                        # Verificamos que sean números finitos y que la diferencia entre ellos sea casi cero
                        if np.isfinite(l_i) and np.isfinite(l_d) and np.isfinite(z_v) and \
                        np.isclose(l_i, l_d, atol=1e-4) and np.isclose(l_d, z_v, atol=1e-4):
                            st.success(f"**Conclusión:** La función es **Continua** en $x = {px}$ porque los límites laterales coinciden con la imagen.")
                        else:
                            st.warning("**Conclusión:** Hay una **Discontinuidad**. Observa en el gráfico si los límites 'se encuentran' o si hay un salto.")
                    except:
                        # Si falla al convertir a número (ej. el límite dio infinito o la imagen es compleja)
                        st.warning("**Conclusión:** Hay una **Discontinuidad** (límite infinito o imagen no real).")

                with tabs[3]:
                    st.subheader("Integración y Regla de Barrow")
                    st.write("El cálculo de la integral definida consta de hallar la primitiva y evaluarla en los extremos del intervalo.")
                    
                    if data.get('primitiva'):
                        with st.expander("1️⃣ Paso 1: Integral Indefinida (Primitiva)", expanded=True):
                            st.write("Buscamos la familia de primitivas aplicando las reglas de integración:")
                            st.latex(rf"\int {sp.latex(data['f_sym'])} \, dx = {sp.latex(data['primitiva'])} + C")
                            
                            # --- TRADUCTOR INTELIGENTE DE INTEGRALES ---
                            prim_str = str(data['primitiva'])
                            if any(func in prim_str.lower() for func in ["erf", "fresnel", "gamma", "si(", "ci("]):
                                st.info("💡 **Aviso sobre este resultado:** Esta función no posee una primitiva que pueda expresarse mediante funciones matemáticas simples. SymPy debió utilizar **Funciones Especiales** (como la función Gamma o las integrales de Fresnel) para resolverla de forma exacta. ¡Por eso se ve tan compleja!")

                        with st.expander("2️⃣ Paso 2: Teorema Fundamental del Cálculo", expanded=True):
                            st.write("La Regla de Barrow establece que:")
                            st.latex(rf"\int_{{{lim_a}}}^{{{lim_b}}} f(x) \, dx = \left[ F(x) \right]_{{{lim_a}}}^{{{lim_b}}} = F({lim_b}) - F({lim_a})")
                            
                        with st.expander("3️⃣ Paso 3: Evaluación y Sustitución", expanded=True):
                            try:
                                # Reemplazos simbólicos explícitos
                                F_b_sym = data['primitiva'].subs(sp.Symbol('x'), lim_b)
                                F_a_sym = data['primitiva'].subs(sp.Symbol('x'), lim_a)
                                
                                st.write(f"👉 **Evaluando el límite superior ($b = {lim_b}$):**")
                                st.latex(rf"F({lim_b}) = {sp.latex(F_b_sym)}")
                                
                                st.write(f"👉 **Evaluando el límite inferior ($a = {lim_a}$):**")
                                st.latex(rf"F({lim_a}) = {sp.latex(F_a_sym)}")
                                
                                st.divider()
                                fa = float(data['primitiva'].subs(sp.Symbol('x'), lim_a).evalf())
                                fb = float(data['primitiva'].subs(sp.Symbol('x'), lim_b).evalf())
                                st.write("**Realizamos la resta final:**")
                                st.latex(rf"F({lim_b}) - F({lim_a}) = {fb:.4f} - ({fa:.4f})")
                                st.success(rf"**Resultado del Área / Integral:** {fb - fa:.4f}")
                            except:
                                st.warning("El cálculo numérico es demasiado complejo para ser evaluado numéricamente en este intervalo.")
                    else:
                        st.warning("No se halló una primitiva analítica. La integral debe resolverse por métodos de aproximación numérica (ej. Sumas de Riemann).")

                with tabs[4]:
                    st.subheader("Estudio Completo Paso a Paso")
                    analisis = get_full_analysis(data['f_sym'])
                    
                    with st.expander("1️⃣ Dominio", expanded=True):
                        st.write("**Cálculo Analítico del Dominio:**")
                        if analisis['denominador'] != 1:
                            st.write("Identificamos un denominador en la función. Para que exista, el denominador no puede ser cero:")
                            st.latex(rf"{sp.latex(analisis['denominador'])} \neq 0")
                            try:
                                sing = sp.solveset(analisis['denominador'], sp.Symbol('x'), domain=S.Reals)
                                if isinstance(sing, sp.FiniteSet) and len(sing) > 0:
                                    st.write("Despejando, vemos que la función se rompe en:")
                                    st.latex(rf"x \notin {sp.latex(sing)}")
                            except: pass
                        else:
                            st.write("No se identificaron denominadores polinómicos (no hay divisiones por cero evidentes).")
                            
                        if analisis['dominio'] is not None:
                            st.success("**Resultado:**")
                            st.latex(rf"\text{{Dom}}(f) = {sp.latex(analisis['dominio'])}")
                        else:
                            st.info("El cálculo requiere análisis numérico complejo.")
                    
                    with st.expander("2️⃣ Raíces y Conjuntos ($C^+, C^-$)", expanded=True):
                        st.write("**Paso 1: Igualar a cero para hallar Raíces ($C^0$).**")
                        st.latex(rf"{sp.latex(data['f_sym'])} = 0")
                        if analisis['raices'] is not None and not isinstance(analisis['raices'], sp.ConditionSet):
                            latex_raices = sp.latex(analisis['raices'])
                            st.latex(rf"C^0 = {latex_raices}")
                            
                            if r"\mathbb{Z}" in latex_raices or "ImageSet" in str(analisis['raices']):
                                st.info("💡 **¿Qué significa este resultado?**\nComo la función es periódica (tiene ondas), cruza el eje X infinitas veces. Esa fórmula general te permite calcular la posición de cualquier raíz simplemente reemplazando la $n$ por números enteros ($0, 1, 2, -1, -2 \dots$).")
                        else:
                            st.info("No se pudo resolver de forma analítica.")
                        
                        if analisis['bolzano']:
                            for b in analisis['bolzano']:
                                inter_str = f"({b['intervalo'][0]:.2f}, {b['intervalo'][1]:.2f})".replace('inf', r'\infty')
                                st.write(f"🔹 **Intervalo** ${inter_str}$ 👉 Elegimos $x_p = {b['pt']:.2f}$")
                                
                                # FIX 3: Evitar renderizar "NaN" si el punto de prueba no es real
                                if not np.isnan(b['valor']):
                                    st.latex(rf"f({b['pt']:.2f}) = {b['valor']:.4f} \quad \rightarrow \quad \text{{Pertenece a }} {b['signo']}")
                                else:
                                    st.latex(rf"f({b['pt']:.2f}) \notin \mathbb{{R}} \quad \rightarrow \quad \text{{{b['signo']}}}")
                        else:
                            st.info("No se pudieron generar los intervalos automáticamente.")
                        
                        st.divider()
                        st.write("**Paso 2: Teorema de Bolzano para Positividad/Negatividad.**")
                        st.write("Según el Teorema de Bolzano, si $f$ es continua en un intervalo y no tiene raíces allí, conserva el mismo signo en todo el intervalo.")
                        st.write("Para hallar $C^+$ y $C^-$, volcá las **raíces** y los puntos fuera del **dominio** en una recta real, y evaluá un punto de prueba en cada intervalo formado.")

                    with st.expander("3️⃣ Crecimiento y Extremos (Máximos y Mínimos)", expanded=True):
                        st.write("**Paso 1: Puntos Críticos ($f'(x) = 0$).**")
                        st.write("Punto candidato a ser máximo o mínimo de la función.")
                        st.latex(rf"f'(x) = {sp.latex(analisis['fx'])} = 0")
                        
                        if analisis['p_criticos'] is not None and not isinstance(analisis['p_criticos'], sp.ConditionSet):
                            latex_criticos = sp.latex(analisis['p_criticos'])
                            st.latex(rf"x_c \in {latex_criticos}")
                            
                            # --- EL TRADUCTOR INTELIGENTE ---
                            if r"\mathbb{Z}" in latex_criticos or "ImageSet" in str(analisis['p_criticos']):
                                st.info("💡 **Aviso sobre funciones periódicas:**\nAl igual que con las raíces, la función tiene **infinitos 'picos' y 'valles'**. La letra $n$ en la fórmula te indica que hay un punto crítico nuevo en cada ciclo de la onda.")
                            # ---------------------------------
                            
                            st.divider()
                            st.write("**Paso 2: Criterio de la Derivada Segunda.**")
                            st.write("Para clasificar, evaluamos cada punto crítico en $f''(x)$:")
                            st.latex(rf"f''(x) = {sp.latex(analisis['fxx'])}")
                            
                            if analisis['clasificacion']:
                                for item in analisis['clasificacion']:
                                    st.write(f"👉 **En $x = {sp.latex(item['x'])}$:**")
                                    st.latex(rf"f''({sp.latex(item['x'])}) = {sp.latex(item['fxx_val'])}")
                                    if item['fxx_val'] > 0:
                                        st.success(f"Como $f''(x) > 0$, la curva es cóncava hacia arriba. Hay un **{item['tipo']}**.")
                                    elif item['fxx_val'] < 0:
                                        st.error(f"Como $f''(x) < 0$, la curva es cóncava hacia abajo. Hay un **{item['tipo']}**.")
                                    else:
                                        st.warning(f"Criterio no concluyente. Posible {item['tipo']}.")
                            else:
                                st.write("No hay puntos críticos finitos para evaluar.")
                        else:
                            st.info("No se pudo resolver $f'(x) = 0$ algebraicamente.")

        with col_graph:
            if modo == "Análisis Matemático II":
                # GRÁFICO 3D AM2
                rango = 5
                x_vals = np.linspace(px - rango, px + rango, 100)
                y_vals = np.linspace(py - rango, py + rango, 100)
                X, Y = np.meshgrid(x_vals, y_vals)

                if analizar_tray:
                    t = np.linspace(px - rango, px + rango, 100)
                    if tray_opcion == "y=mx": yt = py + param*(t-px); xt = t
                    elif tray_opcion == "y=ax^2": yt = py + param*(t-px)**2; xt = t
                    elif tray_opcion == "Eje X": yt = np.full_like(t, py); xt = t
                    else: xt = np.full_like(t, px); yt = t
                    config.update({'xt': xt, 'yt': yt, 'zt': data['f_np'](xt, yt)})

                fig = create_3d_plot(X, Y, data['f_np'](X,Y), px, py, data['z0'], data, config)
                fig.update_layout(height=650)
                st.plotly_chart(fig, width="stretch")

            else:
                # --- GRÁFICO 2D AM1 (Tangente + Riemann + Escala Inteligente) ---
                xv = np.linspace(px - 5, px + 5, 500)
                yv = data["f_np"](xv)
                
                # --- Ruptura de Asíntotas ---
                # Evita la línea vertical recta en funciones racionales como 1/(x-1)
                yv_plot = np.copy(yv)
                diffs = np.abs(np.diff(yv))
                # Si el salto entre un punto y otro es mayor a 50, rompemos la línea (NaN)
                yv_plot[1:][diffs > 50] = np.nan 
                
                fig1d = go.Figure()
                
                # Dibujar la función original (Azul) con el filtro aplicado
                fig1d.add_trace(go.Scatter(x=xv, y=yv_plot, name="f(x)", line=dict(color='#1f77b4', width=3)))
                
                # --- 2. Calcular Taylor ---
                pasos_taylor = get_taylor_step_by_step(data['f_sym'], px, grado_taylor)
                polinomio_final = sum([p['termino_completo'] for p in pasos_taylor])
                
                try:
                    t_np = sp.lambdify(sp.Symbol('x'), polinomio_final, 'numpy')
                    yt_vals = t_np(xv) if not isinstance(t_np(xv), (int, float)) else np.full_like(xv, t_np(xv))
                    
                    # También rompemos el gráfico de Taylor si se dispara abruptamente
                    yt_plot = np.copy(yt_vals)
                    diffs_t = np.abs(np.diff(yt_vals))
                    yt_plot[1:][diffs_t > 50] = np.nan
                    
                    fig1d.add_trace(go.Scatter(x=xv, y=yt_plot, name="Taylor", line=dict(dash='dash', color='red')))
                except:
                    pass

                # --- 3. Dibujar Recta Tangente ---
                if ver_tangente_am1 and not np.isnan(data['fx_v']):
                    y_tan = data['z0'] + data['fx_v'] * (xv - px)
                    fig1d.add_trace(go.Scatter(x=xv, y=y_tan, name="Tangente", line=dict(color='orange', dash='dot')))

                # --- 4. Dibujar Sumas de Riemann ---
                if ver_riemann:
                    delta_x = (lim_b - lim_a) / n_rects
                    xr = np.linspace(lim_a, lim_b, n_rects, endpoint=False)
                    yr_r = data["f_np"](xr)
                    for i in range(len(xr)):
                        # FIX: Solo dibuja el rectángulo si la altura es un número real válido
                        if np.isfinite(yr_r[i]):
                            fig1d.add_shape(
                                type="rect", x0=xr[i], y0=0, x1=xr[i]+delta_x, y1=yr_r[i],
                                fillcolor="rgba(0, 255, 0, 0.3)", line=dict(color="green", width=1)
                            )

                # --- 5. Punto de estudio ---
                fig1d.add_trace(go.Scatter(x=[px], y=[data['z0']], mode='markers+text', text=["P0"], 
                                        marker=dict(size=12, color='black', symbol='diamond')))
                
                # --- 6. ESCALA INTELIGENTE (El gran fix visual) ---
                y_valid = yv[np.isfinite(yv)]
                if len(y_valid) > 0:
                    # Calculamos percentiles para ignorar los infinitos o las explosiones exponenciales
                    p5, p95 = np.percentile(y_valid, 5), np.percentile(y_valid, 95)
                    margen = max((p95 - p5) * 0.2, 5.0)
                    
                    y_min_plot = p5 - margen
                    y_max_plot = p95 + margen

                    if not np.isnan(data['z0']):
                        # Si incluso cortando el 10% de los extremos la escala es inmensa,
                        # hacemos un "zoom forzado" alrededor del punto de análisis P0
                        if (y_max_plot - y_min_plot) > 100:
                            y_min_plot = data['z0'] - 20
                            y_max_plot = data['z0'] + 20
                        else:
                            # Aseguramos que el punto de estudio siempre quede en cámara
                            y_min_plot = min(y_min_plot, data['z0'] - 5)
                            y_max_plot = max(y_max_plot, data['z0'] + 5)

                    fig1d.update_yaxes(range=[y_min_plot, y_max_plot])

                fig1d.update_layout(height=650, title="Visualización Análisis I")
                st.plotly_chart(fig1d, width="stretch")
        if modo == "Análisis Matemático II":
            # --- DASHBOARD INTEGRAL AM2 (RESTAURADO) ---
            st.divider()
            st.header("🕵️ Dashboard de Análisis Integral Paso a Paso")
            tab1, tab2, tab3 = st.tabs(["🌐 Geometría y Superficie", "📝 Diferenciabilidad y Extremos", "🎯 Continuidad y Límites"])

            with tab1:
                st.markdown(f"### 📍 Análisis Geométrico en $P_0({px}, {py}, {data['z0']:.2f})$")
                col_g1, col_g2 = st.columns(2)
                
                with col_g1:
                    st.subheader("🗺️ Curvas de Nivel")
                    xr = np.linspace(px-5, px+5, 80); yr = np.linspace(py-5, py+5, 80)
                    X_c, Y_c = np.meshgrid(xr, yr)
                    fig_c = go.Figure(data=go.Contour(x=xr, y=yr, z=data['f_np'](X_c, Y_c), colorscale='Viridis'))
                    st.plotly_chart(fig_c, width="stretch")
                    
                    with st.expander("💡 ¿Qué nos dicen las Curvas de Nivel?", expanded=True):
                        st.write("Las curvas de nivel representan los cortes de la superficie con planos $z = k$.")
                        if data['hessiano'] > 0:
                            st.success("Al tener un extremo relativo cerca, notarás que las curvas de nivel **se cierran sobre sí mismas** formando elipses o circunferencias alrededor del punto.")
                        elif data['hessiano'] < 0:
                            st.warning("Al tener un punto de silla, las curvas de nivel toman forma de **hipérbolas** que se alejan del punto central, indicando direcciones de ascenso y descenso.")
                        else:
                            st.info("Observando el espaciado: donde las curvas están más juntas, la superficie es más empinada (mayor magnitud del gradiente).")

                with col_g2:
                    st.subheader("🔪 Trazas (Cortes Transversales)")
                    f2d = go.Figure()
                    f2d.add_trace(go.Scatter(x=yr, y=data['f_np'](px, yr), name=f"Traza x={px} (Variando y)"))
                    f2d.add_trace(go.Scatter(x=xr, y=data['f_np'](xr, py), name=f"Traza y={py} (Variando x)"))
                    st.plotly_chart(f2d, width="stretch")
                    
                    with st.expander("💡 ¿Qué nos dicen las Trazas?", expanded=True):
                        st.write(f"Al fijar una variable, reducimos la función a 1D, permitiendo ver las pendientes parciales:")
                        st.write(f"- **La curva azul** asume $x={px}$. Su pendiente exacta en $y={py}$ es $f_y = {data['fy_v']:.2f}$.")
                        st.write(f"- **La curva roja** asume $y={py}$. Su pendiente exacta en $x={px}$ es $f_x = {data['fx_v']:.2f}$.")

            with tab2:
                col_d1, col_d2 = st.columns(2)
                with col_d1:
                    st.subheader("🔍 Derivabilidad y Diferenciabilidad")
                    st.write("**1. Derivabilidad (Existencia de derivadas parciales):**")
                    st.latex(rf"f_x({px}, {py}) = {data['fx_v']:.2f} \quad \text{{y}} \quad f_y({px}, {py}) = {data['fy_v']:.2f}")
                    st.write("Como pudimos evaluarlas, la función es **derivable** en el punto.")
                    
                    st.write("**2. Diferenciabilidad (Condición Suficiente):**")
                    st.info("El Teorema de Diferenciabilidad indica que si $f_x$ y $f_y$ existen en un entorno del punto y son **continuas** en dicho punto, entonces $f$ es diferenciable.")
                    if sp.simplify(data['fx']).is_polynomial() and sp.simplify(data['fy']).is_polynomial():
                        st.success("Como las derivadas parciales son polinómicas (y por ende continuas en $\\mathbb{R}^2$), la función es **diferenciable**.")
                    else:
                        st.warning("Las derivadas parciales no son estrictamente polinómicas. Se debe verificar algebraicamente su continuidad en el punto para garantizar diferenciabilidad.")

                    st.write("**3. Consecuencia Geométrica (Plano Tangente):**")
                    st.write("Al ser diferenciable, la superficie admite un plano tangente no vertical que la aproxima perfectamente localmente:")
                    st.latex(rf"z \approx {data['z0']:.2f} + ({data['fx_v']:.2f})(x - {px}) + ({data['fy_v']:.2f})(y - {py})")

                with col_d2:
                    st.subheader("⛰️ Clasificación de Extremos (Hessiano)")
                    st.write("Para clasificar el punto, primero verificamos la condición necesaria (Punto Crítico):")
                    
                    es_critico = abs(data['fx_v']) < 1e-3 and abs(data['fy_v']) < 1e-3
                    
                    if es_critico:
                        st.success(rf"\nabla f = \langle 0, 0 \rangle \implies \text{{Es un punto crítico.}}")
                    else:
                        st.error(rf"\nabla f = \langle {data['fx_v']:.2f}, {data['fy_v']:.2f} \rangle \neq \langle 0, 0 \rangle \implies \text{{NO es un punto crítico.}}")

                    st.write("**Cálculo Paso a Paso del Determinante (H):**")
                    st.latex(rf"\Delta = f_{{xx}} \cdot f_{{yy}} - (f_{{xy}})^2")
                    st.latex(rf"\Delta = ({data['fxx_v']:.2f}) \cdot ({data['fyy_v']:.2f}) - ({data['fxy_v']:.2f})^2 = {data['hessiano']:.4f}")
                    
                    if es_critico:
                        if data['hessiano'] > 0:
                            tipo = "Mínimo Relativo" if data['fxx_v'] > 0 else "Máximo Relativo"
                            razon = "f_{xx} > 0" if data['fxx_v'] > 0 else "f_{xx} < 0"
                            st.success(f"**Conclusión:** Como $\\Delta > 0$ y ${razon}$, hay un **{tipo}**.")
                        elif data['hessiano'] < 0:
                            st.warning("**Conclusión:** Como $\\Delta < 0$, hay un **Punto de Silla** (la función sube en una dirección y baja en otra).")
                        else:
                            st.info("**Conclusión:** Como $\\Delta = 0$, el criterio **falla**. Se requiere un estudio por definición (ej. incremento $\\Delta z$).")

            with tab3:
                st.subheader("⚖️ Evaluación de Continuidad en el Punto")
                st.write("Para que una función sea continua en $(x_0, y_0)$, debe cumplir 3 condiciones:")
                
                # Condición 1
                st.write(f"**1. ¿La función está definida en el punto?**")
                if np.isnan(data['z0']):
                    st.error(f"Falla: $f({px}, {py})$ NO existe (Indeterminación o Complejo). Por lo tanto, **la función es discontinua**.")
                else:
                    st.success(f"Cumple: $f({px}, {py}) = {data['z0']:.4f}$")
                
                # Condición 2
                st.write("**2. ¿Existe el Límite Doble?**")
                st.write("En AM2, el límite doble existe solo si da el mismo resultado acercándonos por **todas** las infinitas trayectorias posibles.")
                if analizar_tray:
                    t_sym = sp.Symbol('t')
                    x_tray = t_sym if tray_opcion in ["y=mx", "y=ax^2", "Eje X"] else px
                    y_tray = py + param*(t_sym - px) if tray_opcion == "y=mx" else (py + param*(t_sym - px)**2 if tray_opcion == "y=ax^2" else (py if tray_opcion == "Eje X" else t_sym))
                    
                    f_tray = data['f_sym'].subs({'x': x_tray, 'y': y_tray})
                    try:
                        limite_tray = sp.limit(f_tray, t_sym, px)
                        st.latex(rf"\lim_{{x \to {px}}} f(x, y(x)) = {sp.latex(limite_tray)}")
                        st.info("⚠️ *Nota: Que este límite direccional exista no garantiza que el límite doble exista, pero si da distinto a otros caminos, asegura que NO existe.*")
                    except:
                        st.warning("El cálculo del límite algebraico falló por complejidad matemática.")
                else:
                    st.info("*(Activa el análisis por trayectorias o polares en el panel lateral para evaluar límites específicos)*.")

                # Condición 3
                st.write("**3. ¿El límite es igual al valor de la función?**")
                if not np.isnan(data['z0']):
                    st.write("Si el límite por trayectorias o coordenadas polares resultó igual a la evaluación directa, entonces la función es continua.")
                    st.success("✔ Si superó las pruebas, hay **Continuidad**. El paso siguiente es verificar su diferenciabilidad.")

    except Exception as e:
        st.error(f"❌ Ocurrió un error al procesar la ecuación: {e}")