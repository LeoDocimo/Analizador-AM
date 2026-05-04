import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import streamlit as st
import fractions

# --- AYUDANTES MATEMÁTICOS ---
def get_exact_latex(deg):
    """Retorna valores exactos en LaTeX para ángulos notables."""
    notables = {
        0:   {"sin": "0", "cos": "1", "tan": "0"},
        30:  {"sin": r"1/2", "cos": r"\sqrt{3}/2", "tan": r"\sqrt{3}/3"},
        45:  {"sin": r"\sqrt{2}/2", "cos": r"\sqrt{2}/2", "tan": "1"},
        60:  {"sin": r"\sqrt{3}/2", "cos": r"1/2", "tan": r"\sqrt{3}"},
        90:  {"sin": "1", "cos": "0", "tan": r"\infty"},
        180: {"sin": "0", "cos": "-1", "tan": "0"},
        270: {"sin": "-1", "cos": "0", "tan": r"-\infty"},
        360: {"sin": "0", "cos": "1", "tan": "0"}
    }
    return notables.get(deg, None)

def get_rad_label(deg):
    if deg == 0: return "0"
    frac = fractions.Fraction(int(deg), 180).limit_denominator(12)
    n, d = frac.numerator, frac.denominator
    if n == 1 and d == 1: return "π"
    if n == 1: return f"π/{d}"
    if d == 1: return f"{n}π"
    return f"{n}π/{d}"

# --- MOTOR DE ANIMACIÓN ---
def build_frames(deg_steps, rad_steps, show_tan, show_cos, a, b, d_off, unidad):
    frames = []
    steps = []
    
    # Pre-cálculo de funciones transformadas
    sin_trans = a * np.sin(b * rad_steps) + d_off
    cos_trans = a * np.cos(b * rad_steps) + d_off
    tan_vals_full = np.where(np.abs(np.tan(rad_steps)) > 4, np.nan, np.tan(rad_steps))
    C_SIN, C_COS, C_TAN = '#00f2fe', '#ff0844', '#00ff87'

    for i, d in enumerate(deg_steps):
        r = rad_steps[i]
        s, c = np.sin(r), np.cos(r) # Valores del círculo unitario (siempre r=1)
        s_t = sin_trans[i]          # Valor transformado para la onda
        
        # Visibilidad
        wave_tan_y = tan_vals_full[:i+1] if show_tan else [np.nan]*(i+1)
        wave_cos_y = cos_trans[:i+1] if show_cos else [np.nan]*(i+1)

        # 16 capas fijas para estabilidad
        frame_data = [
            go.Scatter(x=np.cos(np.linspace(0, 2*np.pi, 100)), y=np.sin(np.linspace(0, 2*np.pi, 100))), # 0: Círculo
            go.Scatter(x=[-1.5, 1.5], y=[0,0]), # 1
            go.Scatter(x=[0,0], y=[-1.5, 1.5]), # 2
            go.Scatter(x=[0.866, 0.707, 0.5, 0, -1, 0], y=[0.5, 0.707, 0.866, 1, 0, -1]), # 3: Puntos Notables
            go.Scatter(x=[90, 90], y=[-5, 5]),   # 4
            go.Scatter(x=[270, 270], y=[-5, 5]), # 5
            go.Scatter(x=[0, c, c, 0], y=[0, 0, s, 0], fill='toself'), # 6
            go.Scatter(x=[0, c], y=[0, 0]),      # 7
            go.Scatter(x=[c, c], y=[0, s]),      # 8
            go.Scatter(x=[0, c], y=[0, s]),      # 9
            go.Scatter(x=deg_steps[:i+1], y=sin_trans[:i+1]), # 10 Seno Trans
            go.Scatter(x=deg_steps[:i+1], y=wave_cos_y),      # 11 Coseno Trans
            go.Scatter(x=deg_steps[:i+1], y=wave_tan_y),      # 12 Tangente
            go.Scatter(x=[d], y=[s_t], mode='markers'),       # 13 Punto Activo
            go.Scatter(x=[c, 1.6], y=[s, s]),   # 14 Puente inicio
            go.Scatter(x=[-40, d], y=[s_t, s_t]) # 15 Puente fin
        ]

        val_label = f"{d}°" if unidad == "Grados (°)" else get_rad_label(d)
        
        # OBTENEMOS VALORES EXACTOS SI ES POSIBLE (Feedback 5)
        exact_vals = get_exact_latex(d)
        if exact_vals:
            str_s = exact_vals['sin']
            str_c = exact_vals['cos']
            str_t = exact_vals['tan']
        else:
            str_s = f"{s:.2f}"
            str_c = f"{c:.2f}"
            t_val = np.tan(r)
            str_t = f"{t_val:.2f}" if abs(t_val) < 20 else "∞"
            
        title_html = f"<b>θ = {val_label}</b> &nbsp;|&nbsp; <span style='color:{C_SIN}'>sen({val_label}) = {str_s}</span> &nbsp;|&nbsp; <span style='color:{C_COS}'>cos({val_label}) = {str_c}</span> &nbsp;|&nbsp; <span style='color:{C_TAN}'>tg({val_label}) = {str_t}</span>"
        
        frames.append(go.Frame(data=frame_data, layout=go.Layout(title=dict(text=title_html)), name=str(d)))
        steps.append(dict(
            method="animate", label=val_label,
            args=[[str(d)], dict(mode="immediate", frame=dict(duration=30, redraw=True), transition=dict(duration=0))]
        ))
    return frames, steps

def render_trigonometria_interactiva():
    st.title("🌌 Laboratorio Trigonométrico Pro")
    
    with st.sidebar:
        st.header("🎛️ Modo Generalizado")
        st.latex(r"f(x) = a \cdot \sin(bx) + d")
        a = st.slider("Amplitud (a)", 0.5, 2.0, 1.0, 0.1)
        b = st.slider("Frecuencia (b)", 0.5, 3.0, 1.0, 0.1)
        d_off = st.slider("Desplazamiento (d)", -1.0, 1.0, 0.0, 0.1)
        
        st.divider()
        unidad = st.selectbox("Unidad de medida", ["Grados (°)", "Radianes (rad)"])
        show_cos = st.toggle("Mostrar Onda Coseno", value=False)
        show_tan = st.toggle("Mostrar Onda Tangente", value=False)

    deg_steps = np.arange(0, 361, 3) 
    rad_steps = np.deg2rad(deg_steps)
    C_SIN, C_COS, C_GRID = '#00f2fe', '#ff0844', '#2b2b2b'

    # Escala
    tick_vals = [0, 90, 180, 270, 360]
    tick_text = ["0", "π/2", "π", "3π/2", "2π"] if unidad == "Radianes (rad)" else ["0°", "90°", "180°", "270°", "360°"]

    fig = make_subplots(rows=1, cols=2, column_widths=[0.4, 0.6], horizontal_spacing=0.05,
                        subplot_titles=("⭕ Círculo de Estudio", "📈 Función Generalizada"))

    # Capas Iniciales (Mismo orden que frames)
    t = np.linspace(0, 2*np.pi, 100)
    fig.add_trace(go.Scatter(x=np.cos(t), y=np.sin(t), mode='lines', line=dict(color='#444', width=2), hoverinfo='skip'), row=1, col=1)
    fig.add_trace(go.Scatter(x=[-1.5, 1.5], y=[0,0], mode='lines', line=dict(color=C_GRID)), row=1, col=1)
    fig.add_trace(go.Scatter(x=[0,0], y=[-1.5, 1.5], mode='lines', line=dict(color=C_GRID)), row=1, col=1)
    fig.add_trace(go.Scatter(x=[0.866, 0.707, 0.5, 0, -1, 0], y=[0.5, 0.707, 0.866, 1, 0, -1], mode='markers+text', 
                             text=["30°", "45°", "60°", "90°", "180°", "270°"], textposition="top right",
                             marker=dict(color='white', size=4), hoverinfo='skip'), row=1, col=1)
    
    fig.add_trace(go.Scatter(x=[90, 90], y=[-5, 5], mode='lines', line=dict(color='rgba(255,0,0,0.2)', dash='dash')), row=1, col=2)
    fig.add_trace(go.Scatter(x=[270, 270], y=[-5, 5], mode='lines', line=dict(color='rgba(255,0,0,0.2)', dash='dash')), row=1, col=2)
    fig.add_trace(go.Scatter(x=[0,1,1,0], y=[0,0,0,0], fill='toself', fillcolor='rgba(255,255,255,0.05)', mode='none'), row=1, col=1)
    fig.add_trace(go.Scatter(x=[0,1], y=[0,0], mode='lines', line=dict(color=C_COS, width=6)), row=1, col=1)
    fig.add_trace(go.Scatter(x=[1,1], y=[0,0], mode='lines', line=dict(color=C_SIN, width=6)), row=1, col=1)
    fig.add_trace(go.Scatter(x=[0,1], y=[0,0], mode='lines+markers', line=dict(color='white', width=3)), row=1, col=1)
    
    fig.add_trace(go.Scatter(x=[0], y=[0], mode='lines', line=dict(color=C_SIN, width=4)), row=1, col=2)
    fig.add_trace(go.Scatter(x=[0], y=[0], mode='lines', line=dict(color=C_COS, width=4)), row=1, col=2)
    fig.add_trace(go.Scatter(x=[0], y=[0], mode='lines', line=dict(color='#00ff87', width=3)), row=1, col=2)
    fig.add_trace(go.Scatter(x=[0], y=[0], mode='markers', marker=dict(color=C_SIN, size=14, line=dict(color='white', width=2))), row=1, col=2)
    
    fig.add_trace(go.Scatter(x=[1, 1.6], y=[0, 0], mode='lines', line=dict(color='white', dash='dot', width=1)), row=1, col=1)
    fig.add_trace(go.Scatter(x=[-40, 0], y=[0, 0], mode='lines', line=dict(color='white', dash='dot', width=1)), row=1, col=2)

    frames, steps = build_frames(deg_steps, rad_steps, show_tan, show_cos, a, b, d_off, unidad)
    fig.frames = frames

    fig.update_layout(
        plot_bgcolor='#0E1117', paper_bgcolor='#0E1117', font=dict(color='white'),
        height=550, showlegend=False, margin=dict(l=10, r=10, t=50, b=100),
        xaxis1=dict(range=[-1.4, 1.4], visible=False), yaxis1=dict(range=[-1.4, 1.4], visible=False, scaleanchor="x1", scaleratio=1),
        xaxis2=dict(range=[0, 360], tickvals=tick_vals, ticktext=tick_text, gridcolor=C_GRID),
        yaxis2=dict(range=[-3, 3], gridcolor=C_GRID),
        sliders=[dict(active=0, steps=steps, x=0.45, len=0.55, currentvalue=dict(visible=False), bgcolor="#333")],
        updatemenus=[dict(type="buttons", showactive=False, x=0.15, y=-0.15, buttons=[dict(label="▶ Play", method="animate", args=[None, dict(frame=dict(duration=30, redraw=True), fromcurrent=True)])], bgcolor="#333")]
    )

    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

    # --- ANÁLISIS DE EVENTOS ---
    st.divider()
    st.header("📝 Análisis Integral de Funciones")
    
    tab_sin, tab_cos, tab_tan = st.tabs(["🟦 Seno: sen(x)", "🟥 Coseno: cos(x)", "🟩 Tangente: tg(x)"])

    with tab_sin:
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("### 📊 Propiedades de la Función")
            st.write(f"**Definición:** Proyección sobre el eje Y (Cateto Opuesto / Hipotenusa).")
            st.write(f"**Dominio:** $\\mathbb{{R}}$")
            st.write(f"**Imagen:** $[{d_off-a:.2f}, {d_off+a:.2f}]$")
            st.write(f"**Amplitud Actual:** {a}")
            st.write(f"**Período:** $2\\pi / {b:.2f}$")
            st.write("**Paridad:** Función Impar ($\\sin(-x) = -\\sin(x)$).")
        with c2:
            st.markdown("### ⚙️ Puntos Críticos y Derivadas")
            st.latex(r"f'(x) = a \cdot b \cdot \cos(bx)")
            st.latex(r"\int f(x) dx = -\frac{a}{b} \cos(bx) + dx + C")
            st.info("💡 **Evento:** Alcanzas un Máximo cuando el punto está en la cima del círculo.")

    with tab_cos:
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("### 📊 Propiedades de la Función")
            st.write(f"**Definición:** Proyección sobre el eje X (Cateto Adyacente / Hipotenusa).")
            st.write(f"**Dominio:** $\\mathbb{{R}}$")
            st.write(f"**Imagen:** $[{d_off-a:.2f}, {d_off+a:.2f}]$")
            st.write(f"**Período:** $2\\pi / {b:.2f}$")
            st.write("**Paridad:** Función Par ($\\cos(-x) = \\cos(x)$).")
        with c2:
            st.markdown("### ⚙️ Puntos Críticos y Derivadas")
            st.latex(r"f'(x) = -a \cdot b \cdot \sin(bx)")
            st.latex(r"\int f(x) dx = \frac{a}{b} \sin(bx) + dx + C")
            st.info("💡 **Evento:** Alcanzas un Cero cuando el radio es totalmente vertical.")

    with tab_tan:
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("### 📊 Propiedades de la Función")
            st.markdown(r"**Definición:** Razón entre seno y coseno: $\tan(x) = \frac{\sin(x)}{\cos(x)}$")
            st.markdown(r"**Dominio:** $\mathbb{R} \setminus \{ \frac{\pi}{2} + k\pi, k \in \mathbb{Z} \}$ (Falla si el coseno es 0).")
            st.write("**Imagen:** $\\mathbb{R}$ (De $-\\infty$ a $+\\infty$).")
            st.write("**Período:** $\\pi$ (Se repite cada media vuelta).")
            st.markdown(r"**Asíntotas:** Verticales en $x = \frac{\pi}{2} + k\pi$")
        with c2:
            st.markdown("### ⚙️ Puntos Críticos y Derivadas")
            st.latex(r"f'(x) = \sec^2(x) = \frac{1}{\cos^2(x)}")
            st.success("🟩 Geométricamente representa la **pendiente**. Concepto vital para hallar el Vector Gradiente y derivadas direccionales en Análisis II.")
            st.error("⚠️ La tangente tiende a infinito en las líneas rojas punteadas.")