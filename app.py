import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# --- Mapeo de columnas ---
column_map = {
    'Minutos jugados': 'Minutes played',
    'Altura': 'Height',
    'Edad': 'Age'
}

# --- Roles y métricas ---
roles_metrics = {
    "Box Crashers": {
        "Metrics": ["xG per 90", "xA","Successful dribbles, %","Dribbles per 90", "Touches in box per 90", "Progressive runs per 90"],
        "Weights": [0.25, 0.2, 0.1, 0.15, 0.2, 0.1]
    },
    "Creator": {
        "Metrics": ["Key passes per 90", "xG per 90", "xA" ,"Passes to final third per 90", "Progressive passes per 90",
                    "Long passes per 90"],
        "Weights": [0.3, 0.25, 0.2, 0.1, 0.1, 0.05]
    },
    "Orchestrator ": {
        "Metrics": ["Passes per 90", "Accurate passes, %","Short / medium passes per 90", "PAdj Interceptions", "Successful defensive actions per 90", "Key passes per 90", "Defensive duels won, %"],
        "Weights": [0.25, 0.2, 0.15, 0.15, 0.1, 0.1, 0.05]
    },
    "Box to Box": {
        "Metrics": ["Progressive passes per 90", "Defensive duels won, %", "PAdj Interceptions", "Successful defensive actions per 90","xG per 90", "Received passes per 90"],
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
        "Metrics": ["Defensive duels won, %", "Aerial duels won, %", "PAdj Sliding tackles", "PAdj Interceptions",
                    "Successful defensive actions per 90"],
        "Weights": [0.4, 0.1, 0.2, 0.2, 0.1]
    }
}

# --- Funciones ---
def filter_players(df, filter_params):
    for column, value in filter_params.items():
        if column in df.columns:
            if isinstance(value, tuple):
                min_value, max_value = value
                df = df[(df[column] >= min_value) & (df[column] <= max_value)]
            else:
                df = df[df[column] == value]
    return df

def normalize_series(s):
    min_val, max_val = s.min(), s.max()
    if max_val > min_val:
        return (s - min_val) / (max_val - min_val) * 100
    else:
        return s * 0 + 50  # Si no hay variación, dar valor medio

def calculate_score(df, role):
    metrics = roles_metrics[role]["Metrics"]
    weights = roles_metrics[role]["Weights"]

    df = df.copy()
    df["Puntaje"] = 0.0
    for metric, weight in zip(metrics, weights):
        if metric in df.columns:
            df[metric + " Normalized"] = normalize_series(df[metric])
            df["Puntaje"] += df[metric + " Normalized"] * weight

    df["Puntaje Normalizado"] = normalize_series(df["Puntaje"])

    return df[["Player", "Team", "Position", "Puntaje", "Puntaje Normalizado"]].sort_values(by="Puntaje", ascending=False)

def calculate_roles(df):
    df = df.copy()
    for role in roles_metrics.keys():
        df[role] = 0.0
        metrics = roles_metrics[role]["Metrics"]
        weights = roles_metrics[role]["Weights"]

        for metric, weight in zip(metrics, weights):
            if metric in df.columns:
                df[metric + " Normalized"] = normalize_series(df[metric])
                df[role] += df[metric + " Normalized"] * weight

    for role in roles_metrics.keys():
        df[f"{role} Normalized"] = normalize_series(df[role])

    def best_role(row):
        first_group = sorted(list(roles_metrics.keys())[:6], key=lambda role: row[f"{role} Normalized"], reverse=True)[0]
        second_group = sorted(list(roles_metrics.keys())[6:], key=lambda role: row[f"{role} Normalized"], reverse=True)[0]
        return f"{first_group} + {second_group}"

    df["Best Role Combined"] = df.apply(best_role, axis=1)

    columns_to_keep = ["Player", "Team", "Position", "Best Role Combined"] + [f"{role} Normalized" for role in roles_metrics.keys()]
    return df[columns_to_keep]

def plot_radar(player_row, role):
    metrics = roles_metrics[role]["Metrics"]
    weights = roles_metrics[role]["Weights"]

    # Usamos métricas normalizadas
    values = []
    labels = []
    for metric in metrics:
        col_norm = metric + " Normalized"
        if col_norm in player_row:
            values.append(player_row[col_norm])
            labels.append(metric)
    if not values:
        st.warning("No hay métricas para graficar.")
        return

    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=values + [values[0]],  # cerramos círculo
        theta=labels + [labels[0]],
        fill='toself',
        name=player_row["Player"]
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100]
            )
        ),
        showlegend=False,
        title=f"Radar de {player_row['Player']} - Rol: {role}"
    )

    st.plotly_chart(fig, use_container_width=True)

# --- Streamlit App ---
st.title("Filtro y Puntajes de Jugadores")

uploaded_file = st.file_uploader("Sube tu archivo Excel", type=["xlsx"])

if uploaded_file is not None:
    df_raw = pd.read_excel(uploaded_file)

    # Renombrar columnas si están en inglés (al revés del mapping)
    df_raw = df_raw.rename(columns={v: k for k, v in column_map.items()})

    st.write("Datos cargados:")
    st.dataframe(df_raw.head())

    # Sliders para filtro
    minutos_min, minutos_max = int(df_raw['Minutos jugados'].min()), int(df_raw['Minutos jugados'].max())
    altura_min, altura_max = max(0, int(df_raw['Altura'].min())), int(df_raw['Altura'].max())
    edad_min, edad_max = int(df_raw['Edad'].min()), int(df_raw['Edad'].max())

    minutos = st.slider("Minutos jugados", min_value=minutos_min, max_value=minutos_max, value=(minutos_min, minutos_max))
    altura = st.slider("Altura (cm)", min_value=altura_min, max_value=altura_max, value=(altura_min, altura_max))
    edad = st.slider("Edad", min_value=edad_min, max_value=edad_max, value=(edad_min, edad_max))

    role = st.selectbox("Selecciona un rol para puntuar", list(roles_metrics.keys()))

    if st.button("Filtrar y Calcular Puntajes"):
    filter_params = {
        'Minutos jugados': minutos,
        'Altura': altura,
        'Edad': edad
    }

    df_filtered = filter_players(df_raw, filter_params)
    if df_filtered.empty:
        st.warning("No se encontraron jugadores con esos filtros.")
    else:
        # Calculamos scores globales para el rol seleccionado para tabla
        df_score = calculate_score(df_filtered, role)
        df_roles = calculate_roles(df_filtered)
        df_final = pd.merge(df_score, df_roles, on=["Player", "Team", "Position"])

        # --- Normalizamos las métricas para todos los roles y jugadores para los radares ---
        # Creamos un df copia para normalizar métricas usadas en roles
        df_radar = df_filtered.copy()
        for r in roles_metrics.keys():
            for metric in roles_metrics[r]["Metrics"]:
                if metric in df_radar.columns:
                    norm_col = metric + " Normalized"
                    df_radar[norm_col] = normalize_series(df_radar[metric])

        # Estilizado de tabla
        styled_df = df_final.style.background_gradient(subset=["Puntaje", "Puntaje Normalizado"] + [f"{r} Normalized" for r in roles_metrics.keys()], cmap='RdYlGn')

        # Tabs
        tab1, tab2 = st.tabs(["Tabla de Jugadores", "Radar de Jugadores"])

        with tab1:
            st.write("Jugadores filtrados con puntajes:")
            st.dataframe(styled_df, use_container_width=True)

        with tab2:
            st.write("Selecciona un jugador para ver el radar:")
            selected_player = st.selectbox("Jugador", df_final["Player"].unique())
            st.write("Selecciona un rol para radar:")
            selected_role = st.selectbox("Rol para radar", list(roles_metrics.keys()))

            # Obtenemos fila jugador con las métricas normalizadas para radar:
            player_radar_row = df_radar[df_radar["Player"] == selected_player].iloc[0]

            # Preparamos datos para radar: solo métricas normalizadas del rol elegido
            metrics = roles_metrics[selected_role]["Metrics"]
            values = []
            labels = []
            for metric in metrics:
                norm_col = metric + " Normalized"
                if norm_col in player_radar_row:
                    values.append(player_radar_row[norm_col])
                    labels.append(metric)

            if values:
                # Cerramos el círculo para radar
                values += [values[0]]
                labels += [labels[0]]

                fig = go.Figure(go.Scatterpolar(
                    r=values,
                    theta=labels,
                    fill='toself',
                    name=selected_player
                ))

                fig.update_layout(
                    polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
                    showlegend=False,
                    title=f"Radar de {selected_player} - Rol: {selected_role}"
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("No hay métricas disponibles para este jugador y rol.")


# Diccionario con nombres, descripción y número típico de posición
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
        "Descripción": "Especialista en circulación y distribución. Preciso en pases largos y en progresión del balón.",
        "Posición": "6"
    },
    "Builder": {
        "Nombre": "Constructor de Juego",
        "Descripción": "Fomenta la posesión, realiza pases seguros y apoya en recuperación.",
        "Posición": "8 / 6"
    },
    "Defensive Mid": {
        "Nombre": "Mediocampista Defensivo",
        "Descripción": "Especializado en recuperación y contención. Incide en el juego defensivo y equilibrio del equipo.",
        "Posición": "6"
    }
}
