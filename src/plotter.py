import plotly.graph_objects as go
import numpy as np
import sympy as sp

def create_3d_plot(X, Y, Z, px, py, z0, data, config):
    z_min, z_max = np.nanmin(Z), np.nanmax(Z)
    margen = (z_max - z_min) * 0.1 if z_max != z_min else 1.0
    
    fig = go.Figure(data=[go.Surface(x=X, y=Y, z=Z, colorscale='Viridis', opacity=0.8, showscale=False)])
    
    # Trayectorias (Unidad II) [cite: 1201, 1307]
    if config.get('analizar_tray') and 'xt' in config:
        fig.add_trace(go.Scatter3d(x=config['xt'], y=config['yt'], z=config['zt'], mode='lines', line=dict(color='orange', width=10), name="Tray."))
        fig.add_trace(go.Scatter3d(x=config['xt'], y=config['yt'], z=np.full_like(config['xt'], z_min), mode='lines', line=dict(color='blue', width=6), name="Sombra"))

    # Planos de Corte X e Y (Unidad I) [cite: 1198, 1307, 1412]
    if config.get('ver_plano_x'):
        zx = np.where(np.abs(np.imag(data['f_np'](px, Y[:,0]))) > 1e-5, np.nan, np.real(data['f_np'](px, Y[:,0])))
        fig.add_trace(go.Scatter3d(x=[px]*len(zx), y=Y[:,0], z=zx, mode='lines', line=dict(color='white', width=8)))
        if config.get('tipo_x') == "Sólido":
            fig.add_trace(go.Surface(x=[[px, px]]*2, y=[[np.min(Y), np.max(Y)]]*2, z=[[z_min, z_min], [z_max, z_max]], opacity=0.2, colorscale=[[0,'white'],[1,'white']], showscale=False))

    if config.get('ver_plano_y'):
        zy = np.where(np.abs(np.imag(data['f_np'](X[0,:], py))) > 1e-5, np.nan, np.real(data['f_np'](X[0,:], py)))
        fig.add_trace(go.Scatter3d(x=X[0,:], y=[py]*len(zy), z=zy, mode='lines', line=dict(color='magenta', width=8)))
        if config.get('tipo_y') == "Sólido":
            fig.add_trace(go.Surface(x=[[np.min(X), np.max(X)]]*2, y=[[py, py]]*2, z=[[z_min, z_min], [z_max, z_max]], opacity=0.2, colorscale=[[0,'magenta'],[1,'magenta']], showscale=False))

    # Geometría Local y Gradiente (Unidad III y V) [cite: 1205, 1212, 1307]
    if not np.isnan(z0):
        if config.get('ver_plano_tan'):
            Z_tan = z0 + data['fx_v']*(X - px) + data['fy_v']*(Y - py)
            fig.add_trace(go.Surface(x=X, y=Y, z=Z_tan, opacity=0.3, colorscale='Reds', showscale=False))
        if config.get('ver_rectas'):
            tr = np.linspace(px-5, px+5, 40)
            fig.add_trace(go.Scatter3d(x=tr, y=[py]*40, z=z0+data['fx_v']*(tr-px), mode='lines', line=dict(color='yellow', width=6)))
            fig.add_trace(go.Scatter3d(x=[px]*40, y=tr, z=z0+data['fy_v']*(tr-py), mode='lines', line=dict(color='cyan', width=6)))
        if config.get('ver_punto'):
            fig.add_trace(go.Scatter3d(x=[px], y=[py], z=[z0], mode='markers', marker=dict(size=10, color='red', symbol='diamond')))

    if config.get('ver_campo_grad'):
        xg, yg = np.meshgrid(np.linspace(np.min(X), np.max(X), 10), np.linspace(np.min(Y), np.max(Y), 10))
        gx = sp.lambdify((sp.symbols('x'), sp.symbols('y')), data['fx'], 'numpy')(xg, yg)
        gy = sp.lambdify((sp.symbols('x'), sp.symbols('y')), data['fy'], 'numpy')(xg, yg)
        fig.add_trace(go.Cone(x=xg.flatten(), y=yg.flatten(), z=np.full_like(xg.flatten(), z_min), u=gx.flatten(), v=gy.flatten(), w=np.zeros_like(gx.flatten()), colorscale='Reds', sizemode="scaled", sizeref=2))

    if config.get('analizar_dir') and not np.isnan(z0):
        ux, uy = config['ux'], config['uy']
        fig.add_trace(go.Scatter3d(x=[px, px + ux*2], y=[py, py + uy*2], z=[z0, z0], mode='lines+markers', line=dict(color='blue', width=8), name="u"))
        fig.add_trace(go.Scatter3d(x=[px, px + data['fx_v']], y=[py, py + data['fy_v']], z=[z0, z0], mode='lines+markers', line=dict(color='red', width=8), name="Grad"))

    fig.update_layout(scene=dict(xaxis=dict(range=[px-5, px+5], title='X', visible=config['ver_ejes']), yaxis=dict(range=[py-5, py+5], title='Y', visible=config['ver_ejes']), zaxis=dict(range=[z_min - margen, z_max + margen], title='Z', visible=config['ver_ejes']), aspectmode='manual', aspectratio=dict(x=1, y=1, z=0.8)), margin=dict(l=0, r=0, b=0, t=0), height=750)
    return fig