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

# --- Funciones ---
def filter_players(df, filter_params):
    for column, value in filter_params.items():
        if column in df.columns:
            if isinstance(value, tuple):
                df = df[(df[column] >= value[0]) & (df[column] <= value[1])]
            else:
                df = df[df[column] == value]
    return df

def normalize_series(series):
    return (series - series.min()) / (series.max() - series.min()) * 100 if series.max() > series.min() else series * 0 + 50

def calculate_all_scores(df, roles_metrics):
    all_results = []
    for role_name, config in roles_metrics.items():
        metrics = config["Metrics"]
        weights = config["Weights"]
        df_copy = df.copy()
        df_copy["Puntaje"] = 0.0

        for metric, weight in zip(metrics, weights):
            if metric in df_copy.columns:
                norm_col = metric + f" ({role_name})"
                df_copy[norm_col] = normalize_series(df_copy[metric])
                df_copy["Puntaje"] += df_copy[norm_col] * weight

        df_copy["Puntaje Normalizado"] = normalize_series(df_copy["Puntaje"])
        df_copy["Rol"] = role_name
        all_results.append(df_copy[["Player", "Team", "Position", "Puntaje", "Puntaje Normalizado", "Rol"] +
                                   [metric + f" ({role_name})" for metric in config["Metrics"]]])

    df_concat = pd.concat(all_results)
    df_optimo = df_concat.loc[df_concat.groupby("Player")["Puntaje"].idxmax()].copy()
    df_optimo.rename(columns={"Rol": "Rol Óptimo"}, inplace=True)

    return df_optimo.sort_values(by="Puntaje", ascending=False)

def style_score_table(df):
    styled = df.style
    if "Puntaje Normalizado" in df.columns:
        styled = styled.background_gradient(subset=["Puntaje Normalizado"], cmap="Greens")
    metric_cols = [col for col in df.columns if " (" in col and "Normalized" in col]
    if metric_cols:
        styled = styled.highlight_max(subset=metric_cols, color="lightblue")
    return styled

# --- App Streamlit ---
st.title("Análisis de Jugadores y Roles")

st.sidebar.header("Carga de datos")
uploaded_file_mid = st.sidebar.file_uploader("Sube archivo mediocampistas", type=["xlsx"], key="mid")
uploaded_file_cbs = st.sidebar.file_uploader("Sube archivo defensas centrales", type=["xlsx"], key="cbs")

tab1, tab2, tab3 = st.tabs(["Mediocampistas", "Radar Mediocampistas", "Defensas Centrales"])

# --- Mediocampistas ---
with tab1:
    if uploaded_file_mid:
        df_mid = pd.read_excel(uploaded_file_mid)
        df_mid = df_mid.rename(columns={v: k for k, v in column_map.items()})

        minutos = st.slider("Minutos jugados", int(df_mid['Minutos jugados'].min()), int(df_mid['Minutos jugados'].max()), (int(df_mid['Minutos jugados'].min()), int(df_mid['Minutos jugados'].max())))
        altura = st.slider("Altura (cm)", int(df_mid['Altura'].min()), int(df_mid['Altura'].max()), (int(df_mid['Altura'].min()), int(df_mid['Altura'].max())))
        edad = st.slider("Edad", int(df_mid['Edad'].min()), int(df_mid['Edad'].max()), (int(df_mid['Edad'].min()), int(df_mid['Edad'].max())))

        if st.button("Filtrar y Calcular (Mediocampistas)"):
            filtros = {'Minutos jugados': minutos, 'Altura': altura, 'Edad': edad}
            df_filtrado = filter_players(df_mid, filtros)

            if df_filtrado.empty:
                st.warning("No se encontraron jugadores con esos filtros.")
            else:
                df_score_all = calculate_all_scores(df_filtrado, roles_metrics_mid)
                st.dataframe(style_score_table(df_score_all), use_container_width=True)
    else:
        st.info("Sube el archivo de mediocampistas.")

# --- Radar ---
with tab2:
    if uploaded_file_mid:
        df_radar = pd.read_excel(uploaded_file_mid)
        df_radar = df_radar.rename(columns={v: k for k, v in column_map.items()})

        for r in roles_metrics_mid:
            for m in roles_metrics_mid[r]["Metrics"]:
                if m in df_radar.columns:
                    df_radar[m + " Normalized"] = normalize_series(df_radar[m])

        player = st.selectbox("Jugador", df_radar["Player"].unique())
        role = st.selectbox("Rol", list(roles_metrics_mid.keys()))

        row = df_radar[df_radar["Player"] == player].iloc[0]
        labels = roles_metrics_mid[role]["Metrics"]
        values = [row[m + " Normalized"] if m + " Normalized" in row else 0 for m in labels]
        values += [values[0]]
        labels += [labels[0]]

        fig = go.Figure(go.Scatterpolar(r=values, theta=labels, fill='toself', name=player))
        fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Sube el archivo para ver el radar.")

# --- Defensas Centrales ---
with tab3:
    if uploaded_file_cbs:
        df_cbs = pd.read_excel(uploaded_file_cbs)
        df_cbs = df_cbs.rename(columns={v: k for k, v in column_map.items()})

        minutos = st.slider("Minutos jugados", int(df_cbs['Minutos jugados'].min()), int(df_cbs['Minutos jugados'].max()), (int(df_cbs['Minutos jugados'].min()), int(df_cbs['Minutos jugados'].max())), key="cb_min")
        altura = st.slider("Altura", int(df_cbs['Altura'].min()), int(df_cbs['Altura'].max()), (int(df_cbs['Altura'].min()), int(df_cbs['Altura'].max())), key="cb_alt")
        edad = st.slider("Edad", int(df_cbs['Edad'].min()), int(df_cbs['Edad'].max()), (int(df_cbs['Edad'].min()), int(df_cbs['Edad'].max())), key="cb_edad")

        if st.button("Filtrar y Calcular (Centrales)"):
            filtros = {'Minutos jugados': minutos, 'Altura': altura, 'Edad': edad}
            df_filtrado = filter_players(df_cbs, filtros)

            if df_filtrado.empty:
                st.warning("No se encontraron jugadores con esos filtros.")
            else:
                df_score_cbs_all = calculate_all_scores(df_filtrado, roles_metrics_cbs)
                st.dataframe(style_score_table(df_score_cbs_all), use_container_width=True)
    else:
        st.info("Sube el archivo de defensas centrales.")
