import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import io

# --- Mapeo de columnas ---
column_map = {
    'Minutos jugados': 'Minutes played',
    'Altura': 'Height',
    'Edad': 'Age'
}

# --- Roles y métricas mediocampistas ---
roles_metrics_mid = {
    "Box Crashers": {
        "Metrics": ["xG per 90", "xA", "Successful dribbles, %", "Dribbles per 90", "Touches in box per 90", "Progressive runs per 90"],
        "Weights": [0.25, 0.2, 0.1, 0.15, 0.2, 0.1]
    },
    "Creator": {
        "Metrics": ["Key passes per 90", "xG per 90", "xA", "Passes to final third per 90", "Progressive passes per 90", "Long passes per 90"],
        "Weights": [0.3, 0.25, 0.2, 0.1, 0.1, 0.05]
    },
    "Orchestrator": {  # Corregido espacio extra
        "Metrics": ["Passes per 90", "Accurate passes, %", "Short / medium passes per 90", "PAdj Interceptions", "Successful defensive actions per 90", "Key passes per 90", "Defensive duels won, %"],
        "Weights": [0.25, 0.2, 0.15, 0.15, 0.1, 0.1, 0.05]
    },
    "Box to Box": {
        "Metrics": ["Progressive passes per 90", "Defensive duels won, %", "PAdj Interceptions", "Successful defensive actions per 90", "xG per 90", "Received passes per 90"],
        "Weights": [0.25, 0.2, 0.2, 0.15, 0.1, 0.1]
    },
    "Distributor": {
        "Metrics": ["Passes per 90", "Accurate passes, %", "Forward passes per 90", "Accurate forward passes, %", "Passes to final third per 90", "Long passes per 90"],
        "Weights": [0.25, 0.2, 0.2, 0.15, 0.1, 0.1]
    },
    "Builder": {
        "Metrics": ["Passes per 90", "Accurate passes, %", "Defensive duels won, %", "Successful defensive actions per 90", "PAdj Interceptions", "Progressive passes per 90"],
        "Weights": [0.3, 0.25, 0.15, 0.1, 0.15, 0.05]
    },
    "Defensive Mid": {
        "Metrics": ["Defensive duels won, %", "Aerial duels won, %", "PAdj Sliding tackles", "PAdj Interceptions", "Successful defensive actions per 90"],
        "Weights": [0.4, 0.1, 0.2, 0.2, 0.1]
    }
}

# --- Roles y métricas defensas centrales ---
roles_metrics_cbs = {
    "Ball playing CB": {
        "Metrics": ["Accurate long passes, %", "Passes to final third per 90", "Deep completions per 90", "Progressive passes per 90",
                    "Passes per 90", "Aerial duels won, %", "Defensive duels won, %"],
        "Weights": [0.15, 0.2, 0.075, 0.15, 0.325, 0.05, 0.05]
    },
    "Defensive CB": {
        "Metrics": ["Defensive duels won, %", "Aerial duels won, %", "PAdj Sliding tackles", "PAdj Interceptions",
                    "Successful defensive actions per 90"],
        "Weights": [0.3, 0.2, 0.2, 0.2, 0.1]
    },
    "Wide CB": {
        "Metrics": ["Progressive passes per 90", "Progressive runs per 90", "Passes per 90", "Defensive duels won, %",
                    "Accurate short / medium passes, %", "Accurate long passes, %"],
        "Weights": [0.125, 0.275, 0.2, 0.2, 0.15, 0.05]
    }
}

# --- Diccionario con nombres, descripción y número típico de posición ---
role_descriptions = {
    "Box Crashers": {
        "Nombre": "Interior Llegador",
        "Descripción": "Mediocampista con alta capacidad de irrumpir en el área rival. Aporta en generación ofensiva, conducción y finalización.",
        "Posición": "8 / 10"
    },
    "Creator": {
        "Nombre": "Creador de Juego",
        "Descripción": "Centrado en generar ocasiones de gol desde zonas avanzadas. Preciso en pases clave, visión ofensiva.",
        "Posición": "10 / 8"
    },
    "Orchestrator": {
        "Nombre": "Organizador de Medio Campo",
        "Descripción": "Controla el ritmo del partido. Distribuye el balón con precisión y colabora en tareas defensivas.",
        "Posición": "6 / 8"
    },
    "Box to Box": {
        "Nombre": "Volante Mixto",
        "Descripción": "Participa tanto en defensa como en ataque. Recorre grandes distancias y tiene impacto en ambas áreas.",
        "Posición": "8"
    },
    "Distributor": {
        "Nombre": "Distribuidor de Juego",
        "Descripción": "Especialista en circulación y distribución. Preciso en pases hacia el frente y cambios de orientación.",
        "Posición": "6 / 8"
    },
    "Builder": {
        "Nombre": "Constructor desde Atrás",
        "Descripción": "Inicia la jugada desde zonas más retrasadas. Seguro con el balón y fuerte en tareas defensivas básicas.",
        "Posición": "5 / 6"
    },
    "Defensive Mid": {
        "Nombre": "Mediocentro Defensivo",
        "Descripción": "Recuperador puro. Interrumpe el juego rival y protege la zona delante de la defensa.",
        "Posición": "6"
    }
}

# --- Funciones con cache para mejorar performance ---
@st.cache_data
def load_excel(file):
    try:
        df = pd.read_excel(file)
        return df
    except Exception as e:
        st.error(f"Error al cargar archivo Excel: {e}")
        return None

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
    if max_val > min_val:
        return (series - min_val) / (max_val - min_val) * 100
    else:
        return series * 0 + 50  # valor neutro si no hay rango

def calculate_score_all_roles(df, roles_metrics):
    df = df.copy()
    df_scores = []
    for role in roles_metrics.keys():
        metrics = roles_metrics[role]["Metrics"]
        weights = roles_metrics[role]["Weights"]
        df["Puntaje_" + role] = 0.0
        for metric, weight in zip(metrics, weights):
            if metric in df.columns:
                norm_col = metric + " Normalized"
                df[norm_col] = normalize_series(df[metric])
                df["Puntaje_" + role] += df[norm_col] * weight
            else:
                st.warning(f"Métrica '{metric}' no encontrada en datos para el rol '{role}'")
        df["Puntaje Normalizado_" + role] = normalize_series(df["Puntaje_" + role])
        df_scores.append(
            df[["Player", "Team", "Position", "Puntaje_" + role, "Puntaje Normalizado_" + role]]
            .rename(columns={"Puntaje_" + role: "Puntaje", "Puntaje Normalizado_" + role: "Puntaje Normalizado"})
            .assign(Rol=role)
        )
    df_final = pd.concat(df_scores).sort_values(by=["Rol", "Puntaje"], ascending=[True, False])
    return df_final

# Función para exportar DataFrame a CSV y descargar
def get_table_download_link(df, filename="resultados.csv"):
    csv = df.to_csv(index=False).encode('utf-8')
    return st.download_button(
        label="📥 Descargar resultados como CSV",
        data=csv,
        file_name=filename,
        mime='text/csv'
    )

# --- Streamlit App ---

st.title("Análisis de Jugadores y Roles")
st.markdown("""
Esta aplicación permite analizar jugadores de fútbol según sus métricas y roles, filtrando por atributos como minutos jugados, edad y altura, y calculando puntajes personalizados por rol.
""")

st.sidebar.header("Carga de datos")

uploaded_file_mid = st.sidebar.file_uploader("Sube archivo mediocampistas (.xlsx)", type=["xlsx"], key="mid")
uploaded_file_cbs = st.sidebar.file_uploader("Sube archivo defensas centrales (.xlsx)", type=["xlsx"], key="cbs")

tab1, tab2, tab3, tab4 = st.tabs(["Mediocampistas", "Radar Mediocampistas", "Defensas Centrales", "Radar Defensas Centrales"])

# --- Mediocampistas ---
with tab1:
    if uploaded_file_mid is not None:
        df_mid = load_excel(uploaded_file_mid)
        if df_mid is not None:
            # Validar columnas esenciales
            required_cols_mid = ["Player", "Team", "Position"] + [col for role in roles_metrics_mid.values() for col in role["Metrics"]] + list(column_map.values())
            missing_cols = [c for c in required_cols_mid if c not in df_mid.columns]
            if missing_cols:
                st.error(f"Faltan columnas necesarias en mediocampistas: {missing_cols}")
            else:
                # Parámetros filtro
                st.sidebar.subheader("Filtros Mediocampistas")
                min_minutos, max_minutos = st.sidebar.slider("Minutos jugados", 0, int(df_mid["Minutes played"].max()), (0, int(df_mid["Minutes played"].max())), key="minutos_mid")
                min_altura, max_altura = st.sidebar.slider("Altura (cm)", int(df_mid["Height"].min()), int(df_mid["Height"].max()), (int(df_mid["Height"].min()), int(df_mid["Height"].max())), key="altura_mid")
                min_edad, max_edad = st.sidebar.slider("Edad", int(df_mid["Age"].min()), int(df_mid["Age"].max()), (int(df_mid["Age"].min()), int(df_mid["Age"].max())), key="edad_mid")

                # Filtros extra: equipo y posición
                equipos = ["Todos"] + sorted(df_mid["Team"].unique().tolist())
                equipo_seleccionado = st.sidebar.selectbox("Equipo", equipos, key="equipo_mid")
                posiciones = ["Todas"] + sorted(df_mid["Position"].unique().tolist())
                posicion_seleccionada = st.sidebar.selectbox("Posición", posiciones, key="posicion_mid")

                # Aplicar filtros
                filter_params = {
                    "Minutes played": (min_minutos, max_minutos),
                    "Height": (min_altura, max_altura),
                    "Age": (min_edad, max_edad)
                }
                if equipo_seleccionado != "Todos":
                    filter_params["Team"] = equipo_seleccionado
                if posicion_seleccionada != "Todas":
                    filter_params["Position"] = posicion_seleccionada

                df_filtered = filter_players(df_mid, filter_params)

                # Calcular puntajes
                with st.spinner("Calculando puntajes..."):
                    df_scores = calculate_score_all_roles(df_filtered, roles_metrics_mid)

                st.write(f"Jugadores filtrados: {df_filtered.shape[0]}")
                st.dataframe(df_scores)

                # Opción de descarga CSV
                get_table_download_link(df_scores, filename="puntajes_mediocampistas.csv")

# --- Radar Mediocampistas ---
with tab2:
    if uploaded_file_mid is not None:
        df_mid = load_excel(uploaded_file_mid)
        if df_mid is not None:
            jugadores = df_mid["Player"].unique().tolist()
            roles = list(roles_metrics_mid.keys())

            jugador_seleccionado = st.selectbox("Selecciona un jugador", jugadores, key="radar_jugador_mid")
            rol_seleccionado = st.selectbox("Selecciona un rol", roles, key="radar_rol_mid")

            if jugador_seleccionado and rol_seleccionado:
                metrics = roles_metrics_mid[rol_seleccionado]["Metrics"]
                weights = roles_metrics_mid[rol_seleccionado]["Weights"]

                jugador_data = df_mid[df_mid["Player"] == jugador_seleccionado]
                if jugador_data.empty:
                    st.warning("Jugador no encontrado en datos.")
                else:
                    values = []
                    for metric in metrics:
                        if metric in jugador_data.columns:
                            val = jugador_data.iloc[0][metric]
                            values.append(val)
                        else:
                            values.append(0)

                    # Normalizar valores para radar (0-100)
                    series = pd.Series(values)
                    norm_values = normalize_series(series)

                    fig = go.Figure(data=go.Scatterpolar(
                        r=norm_values,
                        theta=metrics,
                        fill='toself',
                        name=jugador_seleccionado
                    ))
                    fig.update_layout(
                        polar=dict(
                            radialaxis=dict(visible=True, range=[0, 100])
                        ),
                        showlegend=True,
                        title=f"Radar - {jugador_seleccionado} ({rol_seleccionado})"
                    )
                    st.plotly_chart(fig, use_container_width=True)

                    # Mostrar descripción del rol
                    if rol_seleccionado in role_descriptions:
                        desc = role_descriptions[rol_seleccionado]
                        st.markdown(f"**{desc['Nombre']}** - Posición típica: {desc['Posición']}")
                        st.markdown(desc['Descripción'])
# --- Defensas Centrales ---
with tab3:
    if uploaded_file_cbs is not None:
        df_cbs = load_excel(uploaded_file_cbs)
        if df_cbs is not None:
            # Validar columnas esenciales
            required_cols_cbs = ["Player", "Team", "Position"] + [col for role in roles_metrics_cbs.values() for col in role["Metrics"]] + list(column_map.values())
            missing_cols = [c for c in required_cols_cbs if c not in df_cbs.columns]
            if missing_cols:
                st.error(f"Faltan columnas necesarias en defensas centrales: {missing_cols}")
            else:
                # Parámetros filtro
                st.sidebar.subheader("Filtros Defensas Centrales")
                min_minutos_cbs, max_minutos_cbs = st.sidebar.slider("Minutos jugados (Defensas)", 0, int(df_cbs["Minutes played"].max()), (0, int(df_cbs["Minutes played"].max())), key="minutos_cbs")
                min_altura_cbs, max_altura_cbs = st.sidebar.slider("Altura (cm) (Defensas)", int(df_cbs["Height"].min()), int(df_cbs["Height"].max()), (int(df_cbs["Height"].min()), int(df_cbs["Height"].max())), key="altura_cbs")
                min_edad_cbs, max_edad_cbs = st.sidebar.slider("Edad (Defensas)", int(df_cbs["Age"].min()), int(df_cbs["Age"].max()), (int(df_cbs["Age"].min()), int(df_cbs["Age"].max())), key="edad_cbs")

                # Filtros extra: equipo y posición
                equipos_cbs = ["Todos"] + sorted(df_cbs["Team"].unique().tolist())
                equipo_seleccionado_cbs = st.sidebar.selectbox("Equipo (Defensas)", equipos_cbs, key="equipo_cbs")
                posiciones_cbs = ["Todas"] + sorted(df_cbs["Position"].unique().tolist())
                posicion_seleccionada_cbs = st.sidebar.selectbox("Posición (Defensas)", posiciones_cbs, key="posicion_cbs")

                # Aplicar filtros
                filter_params_cbs = {
                    "Minutes played": (min_minutos_cbs, max_minutos_cbs),
                    "Height": (min_altura_cbs, max_altura_cbs),
                    "Age": (min_edad_cbs, max_edad_cbs)
                }
                if equipo_seleccionado_cbs != "Todos":
                    filter_params_cbs["Team"] = equipo_seleccionado_cbs
                if posicion_seleccionada_cbs != "Todas":
                    filter_params_cbs["Position"] = posicion_seleccionada_cbs

                df_filtered_cbs = filter_players(df_cbs, filter_params_cbs)

                # Calcular puntajes
                with st.spinner("Calculando puntajes..."):
                    df_scores_cbs = calculate_score_all_roles(df_filtered_cbs, roles_metrics_cbs)

                st.write(f"Jugadores filtrados: {df_filtered_cbs.shape[0]}")
                st.dataframe(df_scores_cbs)

                # Opción de descarga CSV
                get_table_download_link(df_scores_cbs, filename="puntajes_defensas.csv")

# --- Radar Defensas Centrales ---
with tab4:
    if uploaded_file_cbs is not None:
        df_cbs = load_excel(uploaded_file_cbs)
        if df_cbs is not None:
            jugadores_cbs = df_cbs["Player"].unique().tolist()
            roles_cbs = list(roles_metrics_cbs.keys())

            jugador_seleccionado_cbs = st.selectbox("Selecciona un jugador (Defensas)", jugadores_cbs, key="radar_jugador_cbs")
            rol_seleccionado_cbs = st.selectbox("Selecciona un rol (Defensas)", roles_cbs, key="radar_rol_cbs")

            if jugador_seleccionado_cbs and rol_seleccionado_cbs:
                metrics_cbs = roles_metrics_cbs[rol_seleccionado_cbs]["Metrics"]
                weights_cbs = roles_metrics_cbs[rol_seleccionado_cbs]["Weights"]

                jugador_data_cbs = df_cbs[df_cbs["Player"] == jugador_seleccionado_cbs]
                if jugador_data_cbs.empty:
                    st.warning("Jugador no encontrado en datos.")
                else:
                    values_cbs = []
                    for metric in metrics_cbs:
                        if metric in jugador_data_cbs.columns:
                            val = jugador_data_cbs.iloc[0][metric]
                            values_cbs.append(val)
                        else:
                            values_cbs.append(0)

                    # Normalizar valores para radar (0-100)
                    series_cbs = pd.Series(values_cbs)
                    norm_values_cbs = normalize_series(series_cbs)

                    fig_cbs = go.Figure(data=go.Scatterpolar(
                        r=norm_values_cbs,
                        theta=metrics_cbs,
                        fill='toself',
                        name=jugador_seleccionado_cbs
                    ))
                    fig_cbs.update_layout(
                        polar=dict(
                            radialaxis=dict(visible=True, range=[0, 100])
                        ),
                        showlegend=True,
                        title=f"Radar - {jugador_seleccionado_cbs} ({rol_seleccionado_cbs})"
                    )
                    st.plotly_chart(fig_cbs, use_container_width=True)

                    # Mostrar descripción del rol si existe
                    if rol_seleccionado_cbs in role_descriptions:
                        desc = role_descriptions[rol_seleccionado_cbs]
                        st.markdown(f"**{desc['Nombre']}** - Posición típica: {desc['Posición']}")
                        st.markdown(desc['Descripción'])
