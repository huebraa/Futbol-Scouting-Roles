import streamlit as st
import pandas as pd
import numpy as np
import io

# --- Tus columnas en inglés según tu Excel ---
MINUTOS_COL = "Minutes Played"
ALTURA_COL = "Height"
EDAD_COL = "Age"

# --- Tus roles y métricas ---
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

@st.cache_data
def load_data(file):
    df = pd.read_excel(file)
    # Renombrar columnas para consistencia (si quieres)
    # Aquí no renombramos para no romper nada, depende de tus columnas originales
    return df

def normalize_column(df, col):
    min_val, max_val = df[col].min(), df[col].max()
    if max_val > min_val:
        return (df[col] - min_val) / (max_val - min_val) * 100
    else:
        return 0

def calculate_all_roles(df):
    # Para evitar repetir cálculos, vamos a crear todas las columnas normalizadas que se usan
    norm_cache = {}
    for role, data in roles_metrics.items():
        df[role] = 0.0
        for metric, weight in zip(data["Metrics"], data["Weights"]):
            if metric in df.columns:
                if metric not in norm_cache:
                    norm_cache[metric] = normalize_column(df, metric)
                df[role] += norm_cache[metric] * weight

    # Normalizar scores de cada rol
    for role in roles_metrics.keys():
        df[f"{role} Normalizado"] = normalize_column(df, role)

    return df

def filter_players(df, minutos, altura, edad):
    df = df[(df['Minutos jugados'] >= minutos[0]) & (df['Minutos jugados'] <= minutos[1])]
    df = df[(df['Altura'] >= altura[0]) & (df['Altura'] <= altura[1])]
    df = df[(df['Edad'] >= edad[0]) & (df['Edad'] <= edad[1])]
    return df

def to_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    processed_data = output.getvalue()
    return processed_data

st.title("Scouting Roles - Visualización completa y ordenable")

uploaded_file = st.file_uploader("Sube tu archivo Excel (.xlsx)", type=["xlsx"])

if uploaded_file is not None:
    df = load_data(uploaded_file)

    # Mostrar primeras filas
    st.write("Datos cargados:")
    st.dataframe(df.head())

    # Filtros
    st.sidebar.header("Filtros")
    minutos = st.sidebar.slider("Minutos jugados", int(df['Minutos jugados'].min()), int(df['Minutos jugados'].max()), (int(df['Minutos jugados'].min()), int(df['Minutos jugados'].max())))
    altura = st.sidebar.slider("Altura", int(df['Altura'].min()), int(df['Altura'].max()), (int(df['Altura'].min()), int(df['Altura'].max())))
    edad = st.sidebar.slider("Edad", int(df['Edad'].min()), int(df['Edad'].max()), (int(df['Edad'].min()), int(df['Edad'].max())))

    df_filtered = filter_players(df, minutos, altura, edad)
    df_filtered = calculate_all_roles(df_filtered)

    # Columnas de puntajes normalizados para mostrar y ordenar
    role_cols = [f"{role} Normalizado" for role in roles_metrics.keys()]

    # DataFrame para mostrar
    display_cols = ['Player', 'Team', 'Position'] + role_cols

    st.subheader("Tabla de roles (ordenable por cualquiera de las columnas)")

    df_show = df_filtered[display_cols].copy()

    st.dataframe(df_show, use_container_width=True)  # Streamlit permite ordenar al hacer clic en encabezados

    # Descargar Excel
    excel_data = to_excel(df_show)
    st.download_button("Descargar Excel con todos los roles", data=excel_data, file_name="roles_puntajes.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
