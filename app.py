import streamlit as st
import pandas as pd
import io

# --- Mapeo de columnas ---
column_map = {
    'Minutos jugados': 'Minutes played',
    'Altura': 'Height',
    'Edad': 'Age'
}

# --- Roles y métricas ---
roles_metrics = {
    "Box Crashers": {
        "Metrics": ["xG per 90", "xA", "Successful dribbles, %", "Dribbles per 90", "Touches in box per 90", "Progressive runs per 90"],
        "Weights": [0.25, 0.2, 0.1, 0.15, 0.2, 0.1]
    },
    "Creator": {
        "Metrics": ["Key passes per 90", "xG per 90", "xA", "Passes to final third per 90", "Progressive passes per 90", "Long passes per 90"],
        "Weights": [0.3, 0.25, 0.2, 0.1, 0.1, 0.05]
    },
    "Orchestrator": {
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

# --- Descripciones de roles ---
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

# --- Funciones ---
def filter_players(df, filter_params):
    for column, value in filter_params.items():
        if column in df.columns:
            if isinstance(value, tuple):
                df = df[(df[column] >= value[0]) & (df[column] <= value[1])]
            else:
                df = df[df[column] == value]
    return df

def calculate_score(df, role):
    metrics = roles_metrics[role]["Metrics"]
    weights = roles_metrics[role]["Weights"]

    df = df.copy()
    df["Puntaje"] = 0.0
    for metric, weight in zip(metrics, weights):
        if metric in df.columns:
            min_val, max_val = df[metric].min(), df[metric].max()
            if max_val > min_val:
                df[metric] = (df[metric] - min_val) / (max_val - min_val) * 100
            df["Puntaje"] += df[metric] * weight

    df["Puntaje Normalizado"] = (df["Puntaje"] - df["Puntaje"].min()) / (df["Puntaje"].max() - df["Puntaje"].min()) * 100
    return df[["Player", "Team", "Position", "Puntaje", "Puntaje Normalizado"]].sort_values(by="Puntaje", ascending=False)

def calculate_roles(df):
    df = df.copy()
    for role in roles_metrics.keys():
        df[role] = 0.0
        metrics = roles_metrics[role]["Metrics"]
        weights = roles_metrics[role]["Weights"]

        for metric, weight in zip(metrics, weights):
            if metric in df.columns:
                min_val, max_val = df[metric].min(), df[metric].max()
                if max_val > min_val:
                    df[metric] = (df[metric] - min_val) / (max_val - min_val) * 100
                df[role] += df[metric] * weight

    for role in roles_metrics.keys():
        df[f"{role} Normalized"] = (df[role] - df[role].min()) / (df[role].max() - df[role].min()) * 100

    def best_role(row):
        main_roles = sorted(roles_metrics.keys(), key=lambda r: row[f"{r} Normalized"], reverse=True)
        return f"{main_roles[0]} + {main_roles[1]}"

    df["Best Role Combined"] = df.apply(best_role, axis=1)
    columns = ["Player", "Team", "Position", "Best Role Combined"] + [f"{r} Normalized" for r in roles_metrics.keys()]
    return df[columns]

def to_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    return output.getvalue()

# --- Interfaz Streamlit ---
st.title("🔎 Análisis de Roles de Mediocampistas")

uploaded_file = st.file_uploader("📂 Sube tu archivo Excel", type=["xlsx"])

if uploaded_file is not None:
    df_raw = pd.read_excel(uploaded_file)
    df_raw = df_raw.rename(columns={v: k for k, v in column_map.items()})
    st.success("Archivo cargado correctamente ✅")

    st.subheader("🎛️ Filtros")
    minutos = st.slider("Minutos jugados", int(df_raw['Minutos jugados'].min()), int(df_raw['Minutos jugados'].max()), value=(500, 2000))
    altura = st.slider("Altura (cm)", int(df_raw['Altura'].min()), int(df_raw['Altura'].max()))
    edad = st.slider("Edad", int(df_raw['Edad'].min()), int(df_raw['Edad'].max()))

    selected_role = st.selectbox("🎯 Selecciona un rol para evaluar puntaje", list(roles_metrics.keys()))
    mostrar_info = st.checkbox("Mostrar descripción del rol", value=True)

    if mostrar_info and selected_role in role_descriptions:
        info = role_descriptions[selected_role]
        st.markdown(f"### 🧩 Perfil: **{info['Nombre']}**")
        st.markdown(f"**Descripción:** {info['Descripción']}")
        st.markdown(f"**Posición típica:** `{info['Posición']}`")

    if st.button("📊 Filtrar y calcular puntajes"):
        filtros = {'Minutos jugados': minutos, 'Altura': altura, 'Edad': edad}
        df_filtered = filter_players(df_raw, filtros)

        if df_filtered.empty:
            st.warning("⚠️ No se encontraron jugadores con esos filtros.")
        else:
            df_score = calculate_score(df_filtered, selected_role)
            df_roles = calculate_roles(df_filtered)
            df_final = pd.merge(df_score, df_roles, on=["Player", "Team", "Position"])
            st.subheader("📈 Resultados")
            st.dataframe(df_final.head(20))

            excel_data = to_excel(df_final)
            st.download_button("⬇️ Exportar a Excel", data=excel_data, file_name="jugadores_roles.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
