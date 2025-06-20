import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# --- Configuración roles y métricas ---
roles_metrics = {
    "Box Crashers": {
        "Metrics": ["xG per 90", "xA", "Successful dribbles, %", "Dribbles per 90", "Touches in box per 90", "Progressive runs per 90"],
        "Weights": [0.25, 0.2, 0.1, 0.15, 0.2, 0.1]
    },
    "Creator": {
        "Metrics": ["Key passes per 90", "xG per 90", "xA", "Passes to final third per 90", "Progressive passes per 90", "Long passes per 90"],
        "Weights": [0.3, 0.25, 0.2, 0.1, 0.1, 0.05]
    },
    "Orchestrator ": {
        "Metrics": ["Passes per 90", "Accurate passes, %", "Short / medium passes per 90", "PAdj Interceptions",
                    "Successful defensive actions per 90", "Key passes per 90", "Defensive duels won, %"],
        "Weights": [0.25, 0.2, 0.15, 0.15, 0.1, 0.1, 0.05]
    },
    "Box to Box": {
        "Metrics": ["Progressive passes per 90", "Defensive duels won, %", "PAdj Interceptions", "Successful defensive actions per 90",
                    "xG per 90", "Received passes per 90"],
        "Weights": [0.25, 0.2, 0.2, 0.15, 0.1, 0.1]
    },
    "Distributor": {
        "Metrics": ["Passes per 90", "Accurate passes, %", "Forward passes per 90", "Accurate forward passes, %",
                    "Passes to final third per 90", "Long passes per 90"],
        "Weights": [0.25, 0.2, 0.2, 0.15, 0.1, 0.1]
    },
    "Builder": {
        "Metrics": ["Passes per 90", "Accurate passes, %", "Defensive duels won, %", "Successful defensive actions per 90",
                    "PAdj Interceptions", "Progressive passes per 90"],
        "Weights": [0.3, 0.25, 0.15, 0.1, 0.15, 0.05]
    },
    "Defensive Mid": {
        "Metrics": ["Defensive duels won, %", "Aerial duels won, %", "PAdj Sliding tackles", "PAdj Interceptions",
                    "Successful defensive actions per 90"],
        "Weights": [0.4, 0.1, 0.2, 0.2, 0.1]
    }
}

# --- Funciones útiles ---

@st.cache_data(show_spinner=False)
def load_excel(file):
    df = pd.read_excel(file)
    return df

def normalize_column(df, col):
    min_val, max_val = df[col].min(), df[col].max()
    if max_val > min_val:
        return (df[col] - min_val) / (max_val - min_val) * 100
    else:
        return pd.Series(np.zeros(len(df)), index=df.index)

def filter_players(df, filter_params):
    df_filtered = df.copy()
    for col, val in filter_params.items():
        if col in df_filtered.columns:
            if isinstance(val, tuple) and len(val) == 2:
                df_filtered = df_filtered[(df_filtered[col] >= val[0]) & (df_filtered[col] <= val[1])]
            else:
                df_filtered = df_filtered[df_filtered[col] == val]
    return df_filtered

def calculate_score(df, role):
    metrics = roles_metrics[role]["Metrics"]
    weights = roles_metrics[role]["Weights"]
    df = df.copy()
    df["Puntaje"] = 0.0
    for metric, weight in zip(metrics, weights):
        if metric in df.columns:
            df[metric + "_norm"] = normalize_column(df, metric)
            df["Puntaje"] += df[metric + "_norm"] * weight
    # Normalizar Puntaje total
    df["Puntaje Normalizado"] = normalize_column(df, "Puntaje")
    return df[["Player", "Team", "Position", "Puntaje", "Puntaje Normalizado"]].sort_values("Puntaje", ascending=False)

def calculate_roles(df):
    df = df.copy()
    for role in roles_metrics:
        df[role] = 0.0
        metrics = roles_metrics[role]["Metrics"]
        weights = roles_metrics[role]["Weights"]
        for metric, weight in zip(metrics, weights):
            if metric in df.columns:
                df[metric + f"_{role}_norm"] = normalize_column(df, metric)
                df[role] += df[metric + f"_{role}_norm"] * weight
    # Normalizar cada rol
    for role in roles_metrics:
        df[role + " Normalized"] = normalize_column(df, role)
    # Mejor rol (solo uno)
    def best_role(row):
        role_cols = [role + " Normalized" for role in roles_metrics]
        best = row[role_cols].idxmax()
        return best.replace(" Normalized", "")
    df["Best Role"] = df.apply(best_role, axis=1)
    cols_to_show = ["Player", "Team", "Position", "Best Role"] + [role + " Normalized" for role in roles_metrics]
    return df[cols_to_show]

# --- Styling tablas ---
def style_roles_table(df):
    cmap = "RdYlGn"
    roles_norm_cols = [role + " Normalized" for role in roles_metrics]
    styler = df.style.background_gradient(subset=roles_norm_cols, cmap=cmap)
    # Resaltar la columna Best Role
    styler = styler.applymap(lambda v: "font-weight: bold; color: #003300;" if v == df["Best Role"].iloc[0] else "", subset=["Best Role"])
    return styler

# --- App ---

st.title("Scout de Roles de Futbol")

uploaded_file = st.file_uploader("Sube tu archivo Excel", type=["xlsx"])

if uploaded_file:
    with st.spinner("Cargando archivo..."):
        df_raw = load_excel(uploaded_file)

    # Validar columnas necesarias para filtros y roles
    required_cols = ["Player", "Team", "Position", "Minutos jugados", "Altura", "Edad"]
    missing = [col for col in required_cols if col not in df_raw.columns]
    if missing:
        st.error(f"Faltan columnas necesarias en el archivo: {missing}")
        st.stop()

    # Filtros
    minutos_min, minutos_max = int(df_raw['Minutos jugados'].min()), int(df_raw['Minutos jugados'].max())
    altura_min, altura_max = max(0, int(df_raw['Altura'].min())), int(df_raw['Altura'].max())
    edad_min, edad_max = int(df_raw['Edad'].min()), int(df_raw['Edad'].max())

    st.sidebar.header("Filtros de jugadores")
    minutos = st.sidebar.slider("Minutos jugados", minutos_min, minutos_max, (minutos_min, minutos_max))
    altura = st.sidebar.slider("Altura (cm)", altura_min, altura_max, (altura_min, altura_max))
    edad = st.sidebar.slider("Edad", edad_min, edad_max, (edad_min, edad_max))

    # Tabs para separar visualizaciones
    tab1, tab2 = st.tabs(["Tabla y Puntajes", "Radar de Jugadores"])

    with tab1:
        role = st.selectbox("Selecciona un rol para calcular puntajes", list(roles_metrics.keys()))

        if st.button("Filtrar y Calcular Puntajes"):
            filter_params = {
                "Minutos jugados": minutos,
                "Altura": altura,
                "Edad": edad
            }
            with st.spinner("Procesando datos..."):
                df_filtered = filter_players(df_raw, filter_params)
                if df_filtered.empty:
                    st.warning("No se encontraron jugadores con esos filtros.")
                else:
                    df_score = calculate_score(df_filtered, role)
                    df_roles = calculate_roles(df_filtered)
                    df_final = pd.merge(df_score, df_roles, on=["Player", "Team", "Position"])

                    styled_df = df_final.style.background_gradient(
                        subset=[role + " Normalized" for role in roles_metrics.keys()],
                        cmap="RdYlGn"
                    ).highlight_max(subset=["Puntaje Normalizado"], color="#00FF00").set_precision(1)

                    st.write("Jugadores filtrados con puntajes:")
                    st.dataframe(styled_df, use_container_width=True)

                    # Exportar Excel
                    def to_excel(df):
                        import io
                        output = io.BytesIO()
                        with pd.ExcelWriter(output, engine='openpyxl') as writer:
                            df.to_excel(writer, index=False)
                        processed_data = output.getvalue()
                        return processed_data

                    excel_data = to_excel(df_final)
                    st.download_button("Exportar a Excel", data=excel_data,
                                       file_name="jugadores_puntajes.xlsx",
                                       mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    with tab2:
        st.header("Radar de Jugadores")
        # Elegir jugador y rol para radar
        jugadores = df_raw["Player"].unique()
        selected_player = st.selectbox("Selecciona jugador", jugadores)
        selected_role = st.selectbox("Selecciona rol", list(roles_metrics.keys()))

        # Mostrar radar solo si jugador seleccionado está en df
        df_player = df_raw[df_raw["Player"] == selected_player]
        if df_player.empty:
            st.warning("Jugador no encontrado en datos.")
        else:
            with st.spinner("Generando gráfico radar..."):
                metrics = roles_metrics[selected_role]["Metrics"]
                weights = roles_metrics[selected_role]["Weights"]

                # Extraer datos métricas y normalizar
                player_metrics = {}
                for metric in metrics:
                    if metric in df_raw.columns:
                        col_norm = normalize_column(df_raw, metric)
                        player_metrics[metric] = col_norm[df_raw["Player"] == selected_player].values[0]
                    else:
                        player_metrics[metric] = 0

                categories = metrics + [metrics[0]]

                values = list(player_metrics.values())
                values += [values[0]]  # Cerrar círculo

                fig = go.Figure(
                    data=[
                        go.Scatterpolar(r=values, theta=categories, fill='toself', name=selected_player)
                    ],
                    layout=go.Layout(
                        polar=dict(
                            radialaxis=dict(visible=True, range=[0, 100])
                        ),
                        showlegend=True,
                        title=f"Radar del jugador {selected_player} para el rol {selected_role}"
                    )
                )
                st.plotly_chart(fig, use_container_width=True)
