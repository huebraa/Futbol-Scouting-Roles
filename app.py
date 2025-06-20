tengo esto:
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

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
    "Orchestrator ": {
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
    "Orchestrator ": {
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
        return series * 0 + 50

def calculate_score_all_roles_wide(df, roles_metrics):
    df = df.copy()
    df_final = df[['Player', 'Team', 'Position']].drop_duplicates().reset_index(drop=True)
    
    for role in roles_metrics.keys():
        metrics = roles_metrics[role]["Metrics"]
        weights = roles_metrics[role]["Weights"]
        puntaje = pd.Series(0.0, index=df.index)
        for metric, weight in zip(metrics, weights):
            if metric in df.columns:
                norm_metric = normalize_series(df[metric])
                puntaje += norm_metric * weight
        # Normalizamos puntaje final para el rol
        puntaje_norm = normalize_series(puntaje)
        df_final["Puntaje_" + role.strip()] = puntaje_norm.values

    return df_final


# --- Streamlit App ---

st.title("Análisis de Jugadores y Roles")

st.sidebar.header("Carga de datos")

uploaded_file_mid = st.sidebar.file_uploader("Sube archivo mediocampistas", type=["xlsx"], key="mid")
uploaded_file_cbs = st.sidebar.file_uploader("Sube archivo defensas centrales", type=["xlsx"], key="cbs")

tab1, tab2, tab3, tab4 = st.tabs(["Mediocampistas", "Radar Mediocampistas", "Defensas Centrales", "Radar Defensas Centrales"])

with tab1:
    if uploaded_file_mid is not None:
        df_mid = pd.read_excel(uploaded_file_mid)
        df_mid = df_mid.rename(columns={v: k for k, v in column_map.items()})

        minutos_min, minutos_max = int(df_mid['Minutos jugados'].min()), int(df_mid['Minutos jugados'].max())
        altura_min, altura_max = max(0, int(df_mid['Altura'].min())), int(df_mid['Altura'].max())
        edad_min, edad_max = int(df_mid['Edad'].min()), int(df_mid['Edad'].max())

        st.header("Filtrar y visualizar tabla - Mediocampistas")
        minutos = st.slider("Minutos jugados", min_value=minutos_min, max_value=minutos_max, value=(minutos_min, minutos_max))
        altura = st.slider("Altura (cm)", min_value=altura_min, max_value=altura_max, value=(altura_min, altura_max))
        edad = st.slider("Edad", min_value=edad_min, max_value=edad_max, value=(edad_min, edad_max))

        # Mostrar descripciones de roles
        st.subheader("Roles y Descripciones")
        for role, desc in role_descriptions.items():
            st.markdown(f"**{desc['Nombre']} ({role.strip()})**")
            st.markdown(f"Posición típica: {desc['Posición']}")
            st.markdown(f"{desc['Descripción']}\n")

        filter_params = {
            'Minutos jugados': minutos,
            'Altura': altura,
            'Edad': edad
        }
        df_filtered = filter_players(df_mid, filter_params)
        if df_filtered.empty:
            st.warning("No se encontraron jugadores con esos filtros.")
        else:
            df_score = calculate_score_all_roles_wide(df_filtered, roles_metrics_mid)
            st.dataframe(df_score, use_container_width=True)
    else:
        st.info("Por favor, sube el archivo de mediocampistas desde la barra lateral.")


# --- Radar Mediocampistas (modificado) ---
with tab2:
    if uploaded_file_mid is not None:
        df_radar = pd.read_excel(uploaded_file_mid)
        df_radar = df_radar.rename(columns={v: k for k, v in column_map.items()})

        for r in roles_metrics_mid.keys():
            for metric in roles_metrics_mid[r]["Metrics"]:
                if metric in df_radar.columns:
                    norm_col = metric + " Normalized"
                    df_radar[norm_col] = normalize_series(df_radar[metric])

        selected_players = st.multiselect("Selecciona uno o varios jugadores", df_radar["Player"].unique())
        selected_role = st.selectbox("Selecciona un rol para el radar", list(roles_metrics_mid.keys()))

        if selected_players:
            metrics = roles_metrics_mid[selected_role]["Metrics"]
            labels = metrics + [metrics[0]]  # cerrar círculo
            fig = go.Figure()

            for player in selected_players:
                player_radar_row = df_radar[df_radar["Player"] == player]
                if not player_radar_row.empty:
                    player_radar_row = player_radar_row.iloc[0]
                    values = []
                    for metric in metrics:
                        norm_col = metric + " Normalized"
                        values.append(player_radar_row[norm_col] if norm_col in player_radar_row else 0)
                    values += [values[0]]  # cerrar círculo

                    fig.add_trace(go.Scatterpolar(
                        r=values,
                        theta=labels,
                        fill='toself',
                        name=player
                    ))

            fig.update_layout(
                polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
                title=f"Radar de jugadores - Rol: {selected_role}",
                legend_title_text="Jugadores"
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Selecciona al menos un jugador para visualizar el radar.")
    else:
        st.info("Por favor, sube el archivo de mediocampistas desde la barra lateral para usar el radar.")


# --- Defensas Centrales ---
with tab3:
    if uploaded_file_cbs is not None:
        df_cbs = pd.read_excel(uploaded_file_cbs)
        df_cbs = df_cbs.rename(columns={v: k for k, v in column_map.items()})

        minutos_min_cbs, minutos_max_cbs = int(df_cbs['Minutos jugados'].min()), int(df_cbs['Minutos jugados'].max())
        altura_min_cbs, altura_max_cbs = max(0, int(df_cbs['Altura'].min())), int(df_cbs['Altura'].max())
        edad_min_cbs, edad_max_cbs = int(df_cbs['Edad'].min()), int(df_cbs['Edad'].max())

        st.header("Filtrar y visualizar tabla - Defensas Centrales")
        minutos_cbs = st.slider("Minutos jugados", min_value=minutos_min_cbs, max_value=minutos_max_cbs, value=(minutos_min_cbs, minutos_max_cbs))
        altura_cbs = st.slider("Altura (cm)", min_value=altura_min_cbs, max_value=altura_max_cbs, value=(altura_min_cbs, altura_max_cbs))
        edad_cbs = st.slider("Edad", min_value=edad_min_cbs, max_value=edad_max_cbs, value=(edad_min_cbs, edad_max_cbs))

        filter_params_cbs = {
            'Minutos jugados': minutos_cbs,
            'Altura': altura_cbs,
            'Edad': edad_cbs
        }
        df_filtered_cbs = filter_players(df_cbs, filter_params_cbs)
        if df_filtered_cbs.empty:
            st.warning("No se encontraron defensas centrales con esos filtros.")
        else:
            df_score_cbs = calculate_score_all_roles_wide(df_filtered_cbs, roles_metrics_cbs)
            st.dataframe(df_score_cbs, use_container_width=True)
    else:
        st.info("Por favor, sube el archivo de defensas centrales desde la barra lateral.")


# --- Radar Defensas Centrales (modificado) ---
with tab4:
    if uploaded_file_cbs is not None:
        df_radar_cbs = pd.read_excel(uploaded_file_cbs)
        df_radar_cbs = df_radar_cbs.rename(columns={v: k for k, v in column_map.items()})

        for r in roles_metrics_cbs.keys():
            for metric in roles_metrics_cbs[r]["Metrics"]:
                if metric in df_radar_cbs.columns:
                    norm_col = metric + " Normalized"
                    df_radar_cbs[norm_col] = normalize_series(df_radar_cbs[metric])

        selected_players_cbs = st.multiselect("Selecciona uno o varios defensas centrales", df_radar_cbs["Player"].unique())
        selected_role_cbs = st.selectbox("Selecciona un rol para el radar (Defensas Centrales)", list(roles_metrics_cbs.keys()))

        if selected_players_cbs:
            metrics_cbs = roles_metrics_cbs[selected_role_cbs]["Metrics"]
            labels_cbs = metrics_cbs + [metrics_cbs[0]]  # cerrar círculo
            fig_cbs = go.Figure()

            for player_cbs in selected_players_cbs:
                player_radar_row_cbs = df_radar_cbs[df_radar_cbs["Player"] == player_cbs]
                if not player_radar_row_cbs.empty:
                    player_radar_row_cbs = player_radar_row_cbs.iloc[0]
                    values_cbs = []
                    for metric in metrics_cbs:
                        norm_col = metric + " Normalized"
                        values_cbs.append(player_radar_row_cbs[norm_col] if norm_col in player_radar_row_cbs else 0)
                    values_cbs += [values_cbs[0]]  # cerrar círculo

                    fig_cbs.add_trace(go.Scatterpolar(
                        r=values_cbs,
                        theta=labels_cbs,
                        fill='toself',
                        name=player_cbs
                    ))

            fig_cbs.update_layout(
                polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
                title=f"Radar de defensas centrales - Rol: {selected_role_cbs}",
                legend_title_text="Jugadores"
            )
            st.plotly_chart(fig_cbs, use_container_width=True)
        else:
            st.info("Selecciona al menos un defensa central para visualizar el radar.")
    else:
        st.info("Por favor, sube el archivo de defensas centrales desde la barra lateral para usar el radar.")
