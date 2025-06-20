import streamlit as st
import pandas as pd
import io

# Tu diccionario roles_metrics igual que antes
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
    # ... (aquí añades todos los roles que tenías antes)
}

# Mapeo de columnas si hace falta
column_map = {
    'Minutos jugados': 'Minutes played',
    'Altura': 'Height',
    'Edad': 'Age'
}

@st.cache_data
def load_and_process(file) -> pd.DataFrame:
    df = pd.read_excel(file)

    # Renombrar columnas si están en otro idioma
    df = df.rename(columns={v: k for k, v in column_map.items()})

    # Normalizar las métricas por rol UNA vez
    # Primero normalizamos las columnas relevantes para todos los roles
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

    # Precalcular puntajes por rol usando columnas normalizadas para acelerar cálculo
    for role_name, data in roles_metrics.items():
        metrics = data["Metrics"]
        weights = data["Weights"]
        df[role_name] = 0
        for metric, weight in zip(metrics, weights):
            norm_col = metric + " Normalized"
            if norm_col in df.columns:
                df[role_name] += df[norm_col] * weight

        # Normalizar puntaje rol
        min_val, max_val = df[role_name].min(), df[role_name].max()
        if max_val > min_val:
            df[role_name + " Normalized"] = (df[role_name] - min_val) / (max_val - min_val) * 100
        else:
            df[role_name + " Normalized"] = 0

    # Calcular mejor rol combinado (primero + segundo mejor normalizado)
    def best_role(row):
        first_group = sorted(list(roles_metrics.keys())[:6], key=lambda role: row[f"{role} Normalized"], reverse=True)[0]
        second_group = sorted(list(roles_metrics.keys())[6:], key=lambda role: row[f"{role} Normalized"], reverse=True)[0]
        return f"{first_group} + {second_group}"

    df["Best Role Combined"] = df.apply(best_role, axis=1)

    return df

def filter_players(df, minutos, altura, edad):
    return df[
        (df['Minutos jugados'] >= minutos[0]) & (df['Minutos jugados'] <= minutos[1]) &
        (df['Altura'] >= altura[0]) & (df['Altura'] <= altura[1]) &
        (df['Edad'] >= edad[0]) & (df['Edad'] <= edad[1])
    ]

def calculate_score(df, role):
    # Muestra sólo columnas clave con el puntaje calculado para ese rol
    cols = ["Player", "Team", "Position"]
    if role in df.columns:
        cols.append(role)
    if role + " Normalized" in df.columns:
        cols.append(role + " Normalized")
    cols.append("Best Role Combined")

    return df[cols].sort_values(by=role, ascending=False)

def to_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    return output.getvalue()

# --- Streamlit app ---

st.title("Scouting Roles - Evaluación de Jugadores")

uploaded_file = st.file_uploader("Sube archivo Excel con datos de jugadores (.xlsx)", type=["xlsx"])

if uploaded_file is not None:
    df = load_and_process(uploaded_file)

    st.sidebar.header("Filtros")

    minutos = st.sidebar.slider(
        "Minutos jugados",
        int(df['Minutos jugados'].min()),
        int(df['Minutos jugados'].max()),
        (int(df['Minutos jugados'].min()), int(df['Minutos jugados'].max()))
    )

    altura = st.sidebar.slider(
        "Altura (cm)",
        int(df['Altura'].min()),
        int(df['Altura'].max()),
        (int(df['Altura'].min()), int(df['Altura'].max()))
    )

    edad = st.sidebar.slider(
        "Edad",
        int(df['Edad'].min()),
        int(df['Edad'].max()),
        (int(df['Edad'].min()), int(df['Edad'].max()))
    )

    role = st.sidebar.selectbox("Selecciona un rol", list(roles_metrics.keys()))

    df_filtered = filter_players(df, minutos, altura, edad)

    df_scores = calculate_score(df_filtered, role)

    st.subheader(f"Jugadores filtrados con puntaje para rol: {role}")
    st.dataframe(df_scores.head(20))

    excel_data = to_excel(df_scores)

    st.download_button(
        label="Exportar resultados a Excel",
        data=excel_data,
        file_name="jugadores_puntajes.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
