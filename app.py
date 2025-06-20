import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# --- Mapeo de columnas ---
column_map = {
    'Minutos jugados': 'Minutes played',
    'Altura': 'Height',
    'Edad': 'Age'
}

# --- Diccionario con nombres, descripción y número típico de posición ---
role_descriptions = {
    "Box Crashers": {"Nombre": "Interior Llegador", "Descripción": "Mediocampista con alta capacidad de irrumpir en el área rival. Aporta en generación ofensiva, conducción y finalización.", "Posición": "8 / 10"},
    "Creator": {"Nombre": "Creador de Juego", "Descripción": "Centrado en generar ocasiones de gol desde zonas avanzadas. Preciso en pases clave, visión ofensiva.", "Posición": "10 / 8"},
    "Orchestrator ": {"Nombre": "Organizador de Medio Campo", "Descripción": "Controla el ritmo del partido. Distribuye el balón con precisión y colabora en tareas defensivas.", "Posición": "6 / 8"},
    "Box to Box": {"Nombre": "Volante Mixto", "Descripción": "Participa tanto en defensa como en ataque. Recorre grandes distancias y tiene impacto en ambas áreas.", "Posición": "8"},
    "Distributor": {"Nombre": "Distribuidor de Juego", "Descripción": "Especialista en circulación y distribución. Preciso en pases hacia el frente y cambios de orientación.", "Posición": "6 / 8"},
    "Builder": {"Nombre": "Constructor desde Atrás", "Descripción": "Inicia la jugada desde zonas más retrasadas. Seguro con el balón y fuerte en tareas defensivas básicas.", "Posición": "5 / 6"},
    "Defensive Mid": {"Nombre": "Mediocentro Defensivo", "Descripción": "Recuperador puro. Interrumpe el juego rival y protege la zona delante de la defensa.", "Posición": "6"}
}

# --- Roles y métricas mediocampistas ---
roles_metrics_mid = {
    "Box Crashers": {"Metrics": ["xG per 90", "xA", "Successful dribbles, %", "Dribbles per 90", "Touches in box per 90", "Progressive runs per 90"], "Weights": [0.25, 0.2, 0.1, 0.15, 0.2, 0.1]},
    "Creator": {"Metrics": ["Key passes per 90", "xG per 90", "xA", "Passes to final third per 90", "Progressive passes per 90", "Long passes per 90"], "Weights": [0.3, 0.25, 0.2, 0.1, 0.1, 0.05]},
    "Orchestrator ": {"Metrics": ["Passes per 90", "Accurate passes, %", "Short / medium passes per 90", "PAdj Interceptions", "Successful defensive actions per 90", "Key passes per 90", "Defensive duels won, %"], "Weights": [0.25, 0.2, 0.15, 0.15, 0.1, 0.1, 0.05]},
    "Box to Box": {"Metrics": ["Progressive passes per 90", "Defensive duels won, %", "PAdj Interceptions", "Successful defensive actions per 90", "xG per 90", "Received passes per 90"], "Weights": [0.25, 0.2, 0.2, 0.15, 0.1, 0.1]},
    "Distributor": {"Metrics": ["Passes per 90", "Accurate passes, %", "Forward passes per 90", "Accurate forward passes, %", "Passes to final third per 90", "Long passes per 90"], "Weights": [0.25, 0.2, 0.2, 0.15, 0.1, 0.1]},
    "Builder": {"Metrics": ["Passes per 90", "Accurate passes, %", "Defensive duels won, %", "Successful defensive actions per 90", "PAdj Interceptions", "Progressive passes per 90"], "Weights": [0.3, 0.25, 0.15, 0.1, 0.15, 0.05]},
    "Defensive Mid": {"Metrics": ["Defensive duels won, %", "Aerial duels won, %", "PAdj Sliding tackles", "PAdj Interceptions", "Successful defensive actions per 90"], "Weights": [0.4, 0.1, 0.2, 0.2, 0.1]}
}

# --- Roles y métricas defensas centrales ---
roles_metrics_cbs = {
    "Ball playing CB": {"Metrics": ["Accurate long passes, %", "Passes to final third per 90", "Deep completions per 90", "Progressive passes per 90", "Passes per 90", "Aerial duels won, %", "Defensive duels won, %"], "Weights": [0.15, 0.2, 0.075, 0.15, 0.325, 0.05, 0.05]},
    "Defensive CB": {"Metrics": ["Defensive duels won, %", "Aerial duels won, %", "PAdj Sliding tackles", "PAdj Interceptions", "Successful defensive actions per 90"], "Weights": [0.3, 0.2, 0.2, 0.2, 0.1]},
    "Wide CB": {"Metrics": ["Progressive passes per 90", "Progressive runs per 90", "Passes per 90", "Defensive duels won, %", "Accurate short / medium passes, %", "Accurate long passes, %"], "Weights": [0.125, 0.275, 0.2, 0.2, 0.15, 0.05]}
}

# --- Funciones auxiliares ---
def filter_players(df, filter_params):
    for column, value in filter_params.items():
        if column in df.columns:
            if isinstance(value, tuple):
                min_value, max_value = value
                df = df[(df[column] >= min_value) & (df[column] <= max_value)]
            else:
                df = df[df[column] == value]
    return df

def normalize_series(series):
    min_val, max_val = series.min(), series.max()
    return ((series - min_val) / (max_val - min_val) * 100) if max_val > min_val else series * 0 + 50

def calculate_all_scores(df, roles_metrics):
    scores = []
    for role in roles_metrics:
        df_role = df.copy()
        metrics = roles_metrics[role]["Metrics"]
        weights = roles_metrics[role]["Weights"]

        score = 0.0
        for m, w in zip(metrics, weights):
            if m in df.columns:
                df_role[m + " Normalized"] = normalize_series(df[m])
                score += df_role[m + " Normalized"] * w

        df[role + " Score"] = score
    return df

def render_radar(df, selected_players, role, roles_metrics):
    metrics = roles_metrics[role]["Metrics"]
    labels = metrics + [metrics[0]]
    fig = go.Figure()
    for player in selected_players:
        row = df[df["Player"] == player]
        if not row.empty:
            row = row.iloc[0]
            values = [row.get(m + " Normalized", 0) for m in metrics] + [row.get(metrics[0] + " Normalized", 0)]
            fig.add_trace(go.Scatterpolar(r=values, theta=labels, fill='toself', name=player))
    fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), showlegend=True)
    st.plotly_chart(fig, use_container_width=True)

# --- Streamlit App ---
st.title("Análisis de Jugadores y Roles")

st.sidebar.header("Carga de datos")
uploaded_file_mid = st.sidebar.file_uploader("Sube archivo mediocampistas", type=["xlsx"], key="mid")
uploaded_file_cbs = st.sidebar.file_uploader("Sube archivo defensas centrales", type=["xlsx"], key="cbs")

tab1, tab2, tab3, tab4 = st.tabs(["Mediocampistas", "Radar Mediocampistas", "Defensas Centrales", "Radar Defensas Centrales"])

# --- Tab 1: Mediocampistas ---
with tab1:
    if uploaded_file_mid is not None:
        df = pd.read_excel(uploaded_file_mid)
        df = df.rename(columns={v: k for k, v in column_map.items()})

        minutos = st.slider("Minutos jugados", int(df['Minutos jugados'].min()), int(df['Minutos jugados'].max()), (int(df['Minutos jugados'].min()), int(df['Minutos jugados'].max())))
        altura = st.slider("Altura", int(df['Altura'].min()), int(df['Altura'].max()), (int(df['Altura'].min()), int(df['Altura'].max())))
        edad = st.slider("Edad", int(df['Edad'].min()), int(df['Edad'].max()), (int(df['Edad'].min()), int(df['Edad'].max())))

        if st.button("Filtrar y calcular todo"):
            df_filtered = filter_players(df, {'Minutos jugados': minutos, 'Altura': altura, 'Edad': edad})
            df_scored = calculate_all_scores(df_filtered, roles_metrics_mid)
            st.dataframe(df_scored, use_container_width=True)
    else:
        st.info("Sube el archivo de mediocampistas")

# --- Tab 2: Radar Mediocampistas ---
with tab2:
    if uploaded_file_mid is not None:
        df = pd.read_excel(uploaded_file_mid)
        df = df.rename(columns={v: k for k, v in column_map.items()})
        for role in roles_metrics_mid:
            for m in roles_metrics_mid[role]['Metrics']:
                if m in df.columns:
                    df[m + " Normalized"] = normalize_series(df[m])

        players = st.multiselect("Selecciona jugadores", df["Player"].unique())
        role = st.selectbox("Selecciona rol", list(roles_metrics_mid.keys()))
        render_radar(df, players, role, roles_metrics_mid)
    else:
        st.info("Sube el archivo de mediocampistas")

# --- Tab 3: Defensas Centrales ---
with tab3:
    if uploaded_file_cbs is not None:
        df = pd.read_excel(uploaded_file_cbs)
        df = df.rename(columns={v: k for k, v in column_map.items()})

        minutos = st.slider("Minutos jugados", int(df['Minutos jugados'].min()), int(df['Minutos jugados'].max()), (int(df['Minutos jugados'].min()), int(df['Minutos jugados'].max())), key="cb_minutos")
        altura = st.slider("Altura", int(df['Altura'].min()), int(df['Altura'].max()), (int(df['Altura'].min()), int(df['Altura'].max())), key="cb_altura")
        edad = st.slider("Edad", int(df['Edad'].min()), int(df['Edad'].max()), (int(df['Edad'].min()), int(df['Edad'].max())), key="cb_edad")

        if st.button("Filtrar y calcular todo", key="btn_cb"):
            df_filtered = filter_players(df, {'Minutos jugados': minutos, 'Altura': altura, 'Edad': edad})
            df_scored = calculate_all_scores(df_filtered, roles_metrics_cbs)
            st.dataframe(df_scored, use_container_width=True)
    else:
        st.info("Sube el archivo de defensas centrales")

# --- Tab 4: Radar Defensas Centrales ---
with tab4:
    if uploaded_file_cbs is not None:
        df = pd.read_excel(uploaded_file_cbs)
        df = df.rename(columns={v: k for k, v in column_map.items()})
        for role in roles_metrics_cbs:
            for m in roles_metrics_cbs[role]['Metrics']:
                if m in df.columns:
                    df[m + " Normalized"] = normalize_series(df[m])

        players = st.multiselect("Selecciona jugadores", df["Player"].unique())
        role = st.selectbox("Selecciona rol", list(roles_metrics_cbs.keys()))
        render_radar(df, players, role, roles_metrics_cbs)
    else:
        st.info("Sube el archivo de defensas centrales")
