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

roles_metrics_wingers = {
    "Inverted Winger": {
        "Metrics": ["Shots per 90", "xG per 90", "Touches in box per 90", "Successful dribbles, %", "Shot assists per 90", "Deep completed crosses per 90", "Accurate short / medium passes, %" ],
        "Weights": [0.3, 0.15, 0.15, 0.15, 0.1, 0.1, 0.05]
    },
    "Traditional Winger": {
        "Metrics": ["Shot assists per 90", "Successful dribbles, %", "Deep completed crosses per 90", "Accelerations per 90", "xA" , "Accurate crosses, %"],
        "Weights": [0.2, 0.175, 0.225, 0.2, 0.1, 0.1]
    },
    "Playmaking Winger": {
        "Metrics": ["Key passes per 90", "Shot assists per 90","Passes to final third per 90", "Deep completions per 90", "Progressive passes per 90", "Smart passes per 90", "Second assists per 90", "Third assists per 90"],
        "Weights": [0.25, 0.1, 0.1, 0.1, 0.15, 0.2, 0.05, 0.05]
    },
    "Inside Forward": {
        "Metrics": ["Touches in box per 90", "xG per 90", "Progressive runs per 90", "Goals per 90","Successful dribbles, %", "Goal conversion, %", "xA"],
        "Weights": [0.2, 0.2, 0.1, 0.15, 0.1, 0.1, 0.15]
    }
}

roles_metrics_laterales = {
    "Attacking FB": {
        "Metrics": ["Passes to penalty area per 90", "Passes to final third per 90", "Progressive runs per 90", "Offensive duels won, %",
                    "Successful dribbles, %", "xA per 90", "Accelerations per 90", "Accurate crosses, %"],
        "Weights": [0.075, 0.075, 0.05, 0.325, 0.15, 0.1, 0.05, 0.1]
    },
    "Inverted FB": {
        "Metrics": ["Passes per 90", "Smart passes per 90", "Through passes per 90", "Progressive passes per 90",
                    "PAdj Sliding tackles", "PAdj Interceptions", "Short / medium passes per 90", "Defensive duels won, %"],
        "Weights": [0.35, 0.075, 0.1, 0.2, 0.05, 0.05, 0.125, 0.05]
    },
    "Defensive FB": {
        "Metrics": ["Defensive duels won, %", "Aerial duels won, %", "PAdj Sliding tackles", "PAdj Interceptions"],
        "Weights": [0.55, 0.15, 0.15, 0.15]
    }
}

roles_metrics_delanteros = {


    "Second Striker": {
        "Metrics": ["xG per 90", "Touches in box per 90", "Non-penalty goals per 90", "xA", "Goal conversion, %", "Successful dribbles, %", "Progressive runs per 90" ],
        "Weights": [0.2, 0.2, 0.15, 0.15, 0.1, 0.1, 0.1]
    },
    "Deep-Lying Striker": {
        "Metrics": ["xG per 90", "Non-penalty goals per 90", "Deep completions per 90", "Received passes per 90", "Assists per 90" , "Shot assists per 90", "Second assists per 90", "Third assists per 90"],
        "Weights": [0.125, 0.125, 0.15, 0.15, 0.15, 0.05, 0.025, 0.125]
    },
    "Target Man": {
        "Metrics": ["Touches in box per 90", "Aerial duels won, %","xG per 90", "Shots on target, %", "Non-penalty goals per 90"],
        "Weights": [0.1, 0.425, 0.225, 0.2, 0.05]
    },
    "Playmaking Striker": {
        "Metrics": ["Short / medium passes per 90", "Received passes per 90", "Shot assists per 90", "Key passes per 90","xG per 90", "Non-penalty goals per 90", "Offensive duels won, %"],
        "Weights": [0.25, 0.25, 0.1, 0.1, 0.1, 0.1, 0.1]
    },
    "Advanced Striker": {
        "Metrics": ["Accelerations per 90", "Touches in box per 90", "Progressive runs per 90", "Goals per 90","xG per 90", "Goal conversion, %", "xA", "Successful dribbles, %"],
        "Weights": [0.2, 0.1, 0.2, 0.1, 0.1, 0.1, 0.1, 0.1]
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

def highlight_scores(df):
    score_cols = [col for col in df.columns if col.startswith("Puntaje_")]
    return df.style.background_gradient(subset=score_cols, cmap='Greens')


# --- Streamlit App ---

st.title("Análisis de Jugadores y Roles")

st.sidebar.header("Carga de datos")

uploaded_file_mid = st.sidebar.file_uploader("Sube archivo mediocampistas", type=["xlsx"], key="mid")
uploaded_file_cbs = st.sidebar.file_uploader("Sube archivo defensas centrales", type=["xlsx"], key="cbs")
uploaded_file_wingers = st.sidebar.file_uploader("Sube archivo extremos", type=["xlsx"], key="wingers")
uploaded_file_laterales = st.sidebar.file_uploader("Sube archivo laterales", type=["xlsx"], key="laterales")
uploaded_file_delanteros = st.sidebar.file_uploader("Sube archivo de delanteros", type=["xlsx"], key="delanteros")



tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10 = st.tabs([
    "Mediocampistas", "Radar Mediocampistas", "Centrales", "Radar Centrales", "Extremos", "Radar Extremos", "Laterales", "Radar Laterales", "Delanteros", "Radar Delanteros"
])



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
            st.dataframe(highlight_scores(df_score), use_container_width=True)

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
            st.dataframe(highlight_scores(df_score_cbs), use_container_width=True)

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

# --- Extremos ---
with tab5:
    if uploaded_file_wingers is not None:
        df_wingers = pd.read_excel(uploaded_file_wingers)
        df_wingers = df_wingers.rename(columns={v: k for k, v in column_map.items()})

        minutos_min_w, minutos_max_w = int(df_wingers['Minutos jugados'].min()), int(df_wingers['Minutos jugados'].max())
        altura_min_w, altura_max_w = max(0, int(df_wingers['Altura'].min())), int(df_wingers['Altura'].max())
        edad_min_w, edad_max_w = int(df_wingers['Edad'].min()), int(df_wingers['Edad'].max())

        st.header("Filtrar y visualizar tabla - Extremos")
        minutos_w = st.slider("Minutos jugados", min_value=minutos_min_w, max_value=minutos_max_w, value=(minutos_min_w, minutos_max_w))
        altura_w = st.slider("Altura (cm)", min_value=altura_min_w, max_value=altura_max_w, value=(altura_min_w, altura_max_w))
        edad_w = st.slider("Edad", min_value=edad_min_w, max_value=edad_max_w, value=(edad_min_w, edad_max_w))

        filter_params_w = {
            'Minutos jugados': minutos_w,
            'Altura': altura_w,
            'Edad': edad_w
        }

        df_filtered_wingers = filter_players(df_wingers, filter_params_w)

        if df_filtered_wingers.empty:
            st.warning("No se encontraron extremos con esos filtros.")
        else:
            df_score_wingers = calculate_score_all_roles_wide(df_filtered_wingers, roles_metrics_wingers)
            st.dataframe(highlight_scores(df_score_wingers), use_container_width=True)

    else:
        st.info("Por favor, sube el archivo de extremos desde la barra lateral.")


# --- Radar Extremos ---
with tab6:
    if uploaded_file_wingers is not None:
        df_radar_wingers = pd.read_excel(uploaded_file_wingers)
        df_radar_wingers = df_radar_wingers.rename(columns={v: k for k, v in column_map.items()})

        for r in roles_metrics_wingers.keys():
            for metric in roles_metrics_wingers[r]["Metrics"]:
                if metric in df_radar_wingers.columns:
                    norm_col = metric + " Normalized"
                    df_radar_wingers[norm_col] = normalize_series(df_radar_wingers[metric])

        selected_players_wingers = st.multiselect("Selecciona uno o varios extremos", df_radar_wingers["Player"].unique())
        selected_role_wingers = st.selectbox("Selecciona un rol para el radar (Extremos)", list(roles_metrics_wingers.keys()))

        if selected_players_wingers:
            metrics_w = roles_metrics_wingers[selected_role_wingers]["Metrics"]
            labels_w = metrics_w + [metrics_w[0]]  # cerrar círculo
            fig_w = go.Figure()

            for player_w in selected_players_wingers:
                player_radar_row_w = df_radar_wingers[df_radar_wingers["Player"] == player_w]
                if not player_radar_row_w.empty:
                    player_radar_row_w = player_radar_row_w.iloc[0]
                    values_w = []
                    for metric in metrics_w:
                        norm_col = metric + " Normalized"
                        values_w.append(player_radar_row_w[norm_col] if norm_col in player_radar_row_w else 0)
                    values_w += [values_w[0]]  # cerrar círculo

                    fig_w.add_trace(go.Scatterpolar(
                        r=values_w,
                        theta=labels_w,
                        fill='toself',
                        name=player_w
                    ))

            fig_w.update_layout(
                polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
                title=f"Radar de extremos - Rol: {selected_role_wingers}",
                legend_title_text="Jugadores"
            )
            st.plotly_chart(fig_w, use_container_width=True)
        else:
            st.info("Selecciona al menos un extremo para visualizar el radar.")
    else:
        st.info("Por favor, sube el archivo de extremos desde la barra lateral para usar el radar.")


# --- Laterales ---
with tab7:
    if uploaded_file_laterales is not None:
        df_laterales = pd.read_excel(uploaded_file_laterales)
        df_laterales = df_laterales.rename(columns={v: k for k, v in column_map.items()})

        minutos_min_l, minutos_max_l = int(df_laterales['Minutos jugados'].min()), int(df_laterales['Minutos jugados'].max())
        altura_min_l, altura_max_l = max(0, int(df_laterales['Altura'].min())), int(df_laterales['Altura'].max())
        edad_min_l, edad_max_l = int(df_laterales['Edad'].min()), int(df_laterales['Edad'].max())

        st.header("Filtrar y visualizar tabla - Laterales")
        minutos_l = st.slider("Minutos jugados", min_value=minutos_min_l, max_value=minutos_max_l, value=(minutos_min_l, minutos_max_l))
        altura_l = st.slider("Altura (cm)", min_value=altura_min_l, max_value=altura_max_l, value=(altura_min_l, altura_max_l))
        edad_l = st.slider("Edad", min_value=edad_min_l, max_value=edad_max_l, value=(edad_min_l, edad_max_l))

        filter_params_l = {
            'Minutos jugados': minutos_l,
            'Altura': altura_l,
            'Edad': edad_l
        }

        df_filtered_laterales = filter_players(df_laterales, filter_params_l)

        if df_filtered_laterales.empty:
            st.warning("No se encontraron laterales con esos filtros.")
        else:
            df_score_laterales = calculate_score_all_roles_wide(df_filtered_laterales, roles_metrics_laterales)
            st.dataframe(highlight_scores(df_score_laterales), use_container_width=True)

    else:
        st.info("Por favor, sube el archivo de laterales desde la barra lateral.")


# --- Radar Laterales ---
with tab8:
    if uploaded_file_laterales is not None:
        df_radar_laterales = pd.read_excel(uploaded_file_laterales)
        df_radar_laterales = df_radar_laterales.rename(columns={v: k for k, v in column_map.items()})

        for r in roles_metrics_laterales.keys():
            for metric in roles_metrics_laterales[r]["Metrics"]:
                if metric in df_radar_laterales.columns:
                    norm_col = metric + " Normalized"
                    df_radar_laterales[norm_col] = normalize_series(df_radar_laterales[metric])

        selected_players_laterales = st.multiselect("Selecciona uno o varios laterales", df_radar_laterales["Player"].unique())
        selected_role_laterales = st.selectbox("Selecciona un rol para el radar (Laterales)", list(roles_metrics_laterales.keys()))

        if selected_players_laterales:
            metrics_l = roles_metrics_laterales[selected_role_laterales]["Metrics"]
            labels_l = metrics_l + [metrics_l[0]]  # cerrar círculo
            fig_l = go.Figure()

            for player_l in selected_players_laterales:
                player_radar_row_l = df_radar_laterales[df_radar_laterales["Player"] == player_l]
                if not player_radar_row_l.empty:
                    player_radar_row_l = player_radar_row_l.iloc[0]
                    values_l = []
                    for metric in metrics_l:
                        norm_col = metric + " Normalized"
                        values_l.append(player_radar_row_l[norm_col] if norm_col in player_radar_row_l else 0)
                    values_l += [values_l[0]]  # cerrar círculo

                    fig_l.add_trace(go.Scatterpolar(
                        r=values_l,
                        theta=labels_l,
                        fill='toself',
                        name=player_l
                    ))

            fig_l.update_layout(
                polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
                title=f"Radar de laterales - Rol: {selected_role_laterales}",
                legend_title_text="Jugadores"
            )
            st.plotly_chart(fig_l, use_container_width=True)
        else:
            st.info("Selecciona al menos un lateral para visualizar el radar.")
    else:
        st.info("Por favor, sube el archivo de laterales desde la barra lateral para usar el radar.")

# --- Delanteros Tabla ---
with tab9:
    if uploaded_file_delanteros is not None:
        df_delanteros = pd.read_excel(uploaded_file_delanteros)
        df_delanteros = df_delanteros.rename(columns={v: k for k, v in column_map.items()})

        minutos_min_d, minutos_max_d = int(df_delanteros['Minutos jugados'].min()), int(df_delanteros['Minutos jugados'].max())
        altura_min_d, altura_max_d = max(0, int(df_delanteros['Altura'].min())), int(df_delanteros['Altura'].max())
        edad_min_d, edad_max_d = int(df_delanteros['Edad'].min()), int(df_delanteros['Edad'].max())

        st.header("Filtrar y visualizar tabla - Delanteros")
        minutos_d = st.slider("Minutos jugados", min_value=minutos_min_d, max_value=minutos_max_d, value=(minutos_min_d, minutos_max_d))
        altura_d = st.slider("Altura (cm)", min_value=altura_min_d, max_value=altura_max_d, value=(altura_min_d, altura_max_d))
        edad_d = st.slider("Edad", min_value=edad_min_d, max_value=edad_max_d, value=(edad_min_d, edad_max_d))

        filter_params_d = {
            'Minutos jugados': minutos_d,
            'Altura': altura_d,
            'Edad': edad_d
        }

        df_filtered_delanteros = filter_players(df_delanteros, filter_params_d)

        if df_filtered_delanteros.empty:
            st.warning("No se encontraron delanteros con esos filtros.")
        else:
            df_score_delanteros = calculate_score_all_roles_wide(df_filtered_delanteros, roles_metrics_delanteros)
            st.dataframe(highlight_scores(df_score_delanteros), use_container_width=True)

    else:
        st.info("Por favor, sube el archivo de delanteros desde la barra lateral.")

# --- Radar Delanteros ---
with tab10:
    if uploaded_file_delanteros is not None:
        df_radar_delanteros = pd.read_excel(uploaded_file_delanteros)
        df_radar_delanteros = df_radar_delanteros.rename(columns={v: k for k, v in column_map.items()})

        for r in roles_metrics_delanteros.keys():
            for metric in roles_metrics_delanteros[r]["Metrics"]:
                if metric in df_radar_delanteros.columns:
                    norm_col = metric + " Normalized"
                    df_radar_delanteros[norm_col] = normalize_series(df_radar_delanteros[metric])

        selected_players_delanteros = st.multiselect("Selecciona uno o varios delanteros", df_radar_delanteros["Player"].unique())
        selected_role_delanteros = st.selectbox("Selecciona un rol para el radar (Delanteros)", list(roles_metrics_delanteros.keys()))

        if selected_players_delanteros:
            metrics_d = roles_metrics_delanteros[selected_role_delanteros]["Metrics"]
            labels_d = metrics_d + [metrics_d[0]]  # cerrar círculo
            fig_d = go.Figure()

            for player_d in selected_players_delanteros:
                player_radar_row_d = df_radar_delanteros[df_radar_delanteros["Player"] == player_d]
                if not player_radar_row_d.empty:
                    player_radar_row_d = player_radar_row_d.iloc[0]
                    values_d = []
                    for metric in metrics_d:
                        norm_col = metric + " Normalized"
                        values_d.append(player_radar_row_d[norm_col] if norm_col in player_radar_row_d else 0)
                    values_d += [values_d[0]]  # cerrar círculo

                    fig_d.add_trace(go.Scatterpolar(
                        r=values_d,
                        theta=labels_d,
                        fill='toself',
                        name=player_d
                    ))

            fig_d.update_layout(
                polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
                title=f"Radar de delanteros - Rol: {selected_role_delanteros}",
                legend_title_text="Jugadores"
            )
            st.plotly_chart(fig_d, use_container_width=True)
        else:
            st.info("Selecciona al menos un delantero para visualizar el radar.")
    else:
        st.info("Por favor, sube el archivo de delanteros desde la barra lateral para usar el radar.")

