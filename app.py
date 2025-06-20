import streamlit as st
import pandas as pd
import numpy as np
import io

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
    # etc...
}

column_map = {
    'Minutos jugados': 'Minutes played',
    'Altura': 'Height',
    'Edad': 'Age'
}

@st.cache_data
def load_data(file):
    df = pd.read_excel(file)
    df.rename(columns={v: k for k, v in column_map.items()}, inplace=True)
    return df

@st.cache_data
def normalize_df(df):
    # Normalizar métricas solo una vez
    all_metrics = set()
    for role in roles_metrics.values():
        all_metrics.update(role["Metrics"])
    all_metrics = list(all_metrics)

    for metric in all_metrics:
        if metric in df.columns:
            min_val, max_val = df[metric].min(), df[metric].max()
            if max_val > min_val:
                df[metric + " Normalized"] = (df[metric] - min_val) / (max_val - min_val) * 100
            else:
                df[metric + " Normalized"] = 0
    return df

def calculate_score(df, role):
    metrics = roles_metrics[role]["Metrics"]
    weights = roles_metrics[role]["Weights"]
    score = pd.Series(0, index=df.index, dtype=float)
    for metric, weight in zip(metrics, weights):
        norm_col = metric + " Normalized"
        if norm_col in df.columns:
            score += df[norm_col] * weight
    return score

def filter_players(df, minutos, altura, edad):
    return df[
        (df['Minutos jugados'] >= minutos[0]) & (df['Minutos jugados'] <= minutos[1]) &
        (df['Altura'] >= altura[0]) & (df['Altura'] <= altura[1]) &
        (df['Edad'] >= edad[0]) & (df['Edad'] <= edad[1])
    ]

def to_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    return output.getvalue()

st.title("Scouting Roles Optimizado")

uploaded_file = st.file_uploader("Sube tu Excel", type=["xlsx"])
if uploaded_file is not None:
    df = load_data(uploaded_file)
    df = normalize_df(df)

    st.sidebar.header("Filtros")
    minutos = st.sidebar.slider("Minutos jugados", int(df['Minutos jugados'].min()), int(df['Minutos jugados'].max()), (int(df['Minutos jugados'].min()), int(df['Minutos jugados'].max())))
    altura = st.sidebar.slider("Altura", int(df['Altura'].min()), int(df['Altura'].max()), (int(df['Altura'].min()), int(df['Altura'].max())))
    edad = st.sidebar.slider("Edad", int(df['Edad'].min()), int(df['Edad'].max()), (int(df['Edad'].min()), int(df['Edad'].max())))

    role = st.sidebar.selectbox("Selecciona rol", list(roles_metrics.keys()))

    df_filtered = filter_players(df, minutos, altura, edad)
    df_filtered[role + " Score"] = calculate_score(df_filtered, role)
    df_filtered = df_filtered.sort_values(by=role + " Score", ascending=False)

    st.subheader(f"Top jugadores para el rol: {role}")
    st.dataframe(df_filtered.head(20))

    excel_data = to_excel(df_filtered)
    st.download_button("Exportar a Excel", data=excel_data, file_name="scouting_scores.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
