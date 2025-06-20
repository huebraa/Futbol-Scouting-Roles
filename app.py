import streamlit as st
import pandas as pd
import numpy as np
import io

# --- Tu mapeo de columnas ---
column_map = {
    'Minutos jugados': 'Minutes played',
    'Altura': 'Height',
    'Edad': 'Age'
}

# --- Tus roles y métricas, sin cambiar ---
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
    "Orchestrator": {
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
    "Possession Enabler": {
        "Metrics": ["Short / medium passes per 90", "Accurate short / medium passes, %","Accurate forward passes, %","Passes per 90", "Accurate through passes, %"],
        "Weights": [0.3, 0.25, 0.15, 0.15, 0.15]
    },
    "Defensive Mid": {
        "Metrics": ["Defensive duels won, %", "Aerial duels won, %", "PAdj Sliding tackles", "PAdj Interceptions",
                    "Successful defensive actions per 90"],
        "Weights": [0.4, 0.1, 0.2, 0.2, 0.1]
    },
    "Number 6": {
        "Metrics": ["Defensive duels won, %", "Accurate short / medium passes, %","Short / medium passes per 90", "Offensive duels won, %"  ],
        "Weights": [0.3, 0.25, 0.225, 0.225]
    },
    "Deep-Lying Playmaker": {
        "Metrics": ["Passes to final third per 90", "Deep completions per 90", "Progressive passes per 90", "Shot assists per 90","xA", "Second assists per 90", "Third assists per 90",
                    "Defensive duels won, %","Key passes per 90"],
        "Weights": [0.125, 0.125, 0.25, 0.15, 0.05, 0.05, 0.05, 0.1, 0.1]
    },
    "Progressive Midfielder": {
        "Metrics": ["Progressive runs per 90", "Progressive passes per 90", "Passes to final third per 90", "Received passes per 90", "Offensive duels won, %", "Accelerations per 90"],
        "Weights": [0.225, 0.225, 0.2, 0.15, 0.1, 0.1]
    },
    "Box-to-Box Midfielder": {
        "Metrics": ["Defensive duels won, %", "Offensive duels won, %", "Progressive runs per 90", "Passes to final third per 90", "PAdj Sliding tackles", "PAdj Interceptions"],
        "Weights": [0.275, 0.275, 0.25, 0.1, 0.05, 0.05]
    },
    "Advanced Playmaker": {
        "Metrics": ["Shot assists per 90", "Key passes per 90", "Smart passes per 90", "Offensive duels won, %", "Successful dribbles, %", "xA", "Non-penalty goals per 90", "xG per 90"],
        "Weights": [0.2, 0.15, 0.15, 0.15, 0.1, 0.1, 0.1, 0.05]
    },
    "Wide CAM": {
        "Metrics": ["Shot assists per 90", "xA", "Successful dribbles, %", "Crosses per 90", "Deep completed crosses per 90", "Accelerations per 90", "Touches in box per 90"],
        "Weights": [0.1, 0.1, 0.2, 0.2, 0.2, 0.15, 0.05]
    }
}

# -- Función para cargar datos con cache --
@st.cache_data
def load_data(file):
    df = pd.read_excel(file)
    # Renombrar columnas para que coincidan con tus filtros
    df.rename(columns={v: k for k, v in column_map.items()}, inplace=True)
    return df

# -- Función para normalizar métricas (para uso interno) --
def normalize_column(df, col):
    min_val, max_val = df[col].min(), df[col].max()
    if max_val > min_val:
        return (df[col] - min_val) / (max_val - min_val) * 100
    else:
        return 0

# -- Calcular puntaje para un rol específico --
def calculate_score(df, role):
    metrics = roles_metrics[role]["Metrics"]
    weights = roles_metrics[role]["Weights"]

    df["Puntaje"] = 0.0
    for metric, weight in zip(metrics, weights):
        if metric in df.columns:
            df[metric + " Normalizado"] = normalize_column(df, metric)
            df["Puntaje"] += df[metric + " Normalizado"] * weight

    df["Puntaje Normalizado"] = normalize_column(df, "Puntaje")

    return df[["Player", "Team", "Position", "Puntaje", "Puntaje Normalizado"]].sort_values(by="Puntaje", ascending=False)

# -- Calcular todos los roles y normalizarlos --
def calculate_roles(df):
    for role in roles_metrics.keys():
        df[role] = 0.0
        metrics = roles_metrics[role]["Metrics"]
        weights = roles_metrics[role]["Weights"]

        for metric, weight in zip(metrics, weights):
            if metric in df.columns:
                norm_col = metric + " Normalizado"
                if norm_col not in df.columns:
                    df[norm_col] = normalize_column(df, metric)
                df[role] += df[norm_col] * weight

    for role in roles_metrics.keys():
        df[f"{role} Normalized"] = normalize_column(df, role)

    def best_role(row):
        first_group = sorted(list(roles_metrics.keys())[:6], key=lambda role: row[f"{role} Normalized"], reverse=True)[0]
        second_group = sorted(list(roles_metrics.keys())[6:], key=lambda role: row[f"{role} Normalized"], reverse=True)[0]
        return f"{first_group} + {second_group}"

    df["Best Role Combined"] = df.apply(best_role, axis=1)

    columns_to_keep = ["Player", "Team", "Position", "Best Role Combined"] + [f"{role} Normalized" for role in roles_metrics.keys()]
    return df[columns_to_keep]

# -- Función para filtrar según rango --
def filter_players(df, filter_params):
    for column, value in filter_params.items():
        if column in df.columns:
            if isinstance(value, tuple):
                min_value, max_value = value
                df = df[(df[column] >= min_value) & (df[column] <= max_value)]
            else:
                df = df[df[column] == value]
    return df

# -- Convertir DataFrame a Excel en memoria para descarga --
def to_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    processed_data = output.getvalue()
    return processed_data

# === STREAMLIT APP ===
st.title("Scouting Roles con Optimización y Todas Funciones")

uploaded_file = st.file_uploader("Sube tu archivo Excel (.xlsx)", type=["xlsx"])

if uploaded_file is not None:
    df_raw = load_data(uploaded_file)

    # Mostrar datos cargados
    st.write("Datos cargados:")
    st.dataframe(df_raw.head())

    # Filtros
    st.sidebar.header("Filtros")
    minutos = st.sidebar.slider("Minutos jugados", int(df_raw['Minutos jugados'].min()), int(df_raw['Minutos jugados'].max()), (int(df_raw['Minutos jugados'].min()), int(df_raw['Minutos jugados'].max())))
    altura = st.sidebar.slider("Altura", int(df_raw['Altura'].min()), int(df_raw['Altura'].max()), (int(df_raw['Altura'].min()), int(df_raw['Altura'].max())))
    edad = st.sidebar.slider("Edad", int(df_raw['Edad'].min()), int(df_raw['Edad'].max()), (int(df_raw['Edad'].min()), int(df_raw['Edad'].max())))

    # Aplicar filtro
    filter_params = {
        'Minutos jugados': minutos,
        'Altura': altura,
        'Edad': edad
    }
    df_filtered = filter_players(df_raw, filter_params)

    # Selección de rol individual o todos los roles
    modo = st.sidebar.radio("Modo de visualización:", ["Un solo rol", "Todos los roles"])

    if modo == "Un solo rol":
        rol_seleccionado = st.sidebar.selectbox("Selecciona un rol", list(roles_metrics.keys()))
        df_scores = calculate_score(df_filtered.copy(), rol_seleccionado)
        st.subheader(f"Puntajes para el rol: {rol_seleccionado}")
        st.dataframe(df_scores.head(20))

        excel_data = to_excel(df_scores)
        st.download_button("Descargar Excel", data=excel_data, file_name=f"Puntajes_{rol_seleccionado}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    else:  # Todos los roles
        df_roles = calculate_roles(df_filtered.copy())
        st.subheader("Puntajes para todos los roles")
        st.dataframe(df_roles.head(20))

        excel_data = to_excel(df_roles)
        st.download_button("Descargar Excel", data=excel_data, file_name="Puntajes_Todos_Roles.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
