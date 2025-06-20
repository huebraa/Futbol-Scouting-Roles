}
}

# Añade este diccionario al principio junto con los otros roles_metrics
roles_metrics_wingers = {
    "Inverted Winger": {
        "Metrics": ["Shots per 90", "xG per 90", "Touches in box per 90", "Successful dribbles, %", "Shot assists per 90", "Deep completed crosses per 90", "Accurate short / medium passes, %"],
        "Weights": [0.3, 0.15, 0.15, 0.15, 0.1, 0.1, 0.05]
    },
    "Traditional Winger": {
        "Metrics": ["Shot assists per 90", "Successful dribbles, %", "Deep completed crosses per 90", "Accelerations per 90", "xA", "Accurate crosses, %"],
        "Weights": [0.2, 0.175, 0.225, 0.2, 0.1, 0.1]
    },
    "Playmaking Winger": {
        "Metrics": ["Key passes per 90", "Shot assists per 90", "Passes to final third per 90", "Deep completions per 90", "Progressive passes per 90", "Smart passes per 90", "Second assists per 90", "Third assists per 90"],
        "Weights": [0.25, 0.1, 0.1, 0.1, 0.15, 0.2, 0.05, 0.05]
    },
    "Inside Forward": {
        "Metrics": ["Touches in box per 90", "xG per 90", "Progressive runs per 90", "Goals per 90", "Successful dribbles, %", "Goal conversion, %", "xA"],
        "Weights": [0.2, 0.2, 0.1, 0.15, 0.1, 0.1, 0.15]
    }
}


# --- Diccionario con nombres, descripción y número típico de posición ---
role_descriptions = {
"Box Crashers": {
@@ -165,8 +144,7 @@ def calculate_score_all_roles(df, roles_metrics):
uploaded_file_mid = st.sidebar.file_uploader("Sube archivo mediocampistas", type=["xlsx"], key="mid")
uploaded_file_cbs = st.sidebar.file_uploader("Sube archivo defensas centrales", type=["xlsx"], key="cbs")


tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["Mediocampistas", "Radar Mediocampistas", "Defensas Centrales", "Radar Defensas Centrales", "Extremos", "Radar Extremos"])
tab1, tab2, tab3, tab4 = st.tabs(["Mediocampistas", "Radar Mediocampistas", "Defensas Centrales", "Radar Defensas Centrales"])

# --- Mediocampistas ---
with tab1:
@@ -185,7 +163,7 @@ def calculate_score_all_roles(df, roles_metrics):

# Mostrar descripciones de roles
st.subheader("Roles y Descripciones")
        for role, desc in role_descriptions_mid.items():  # Asumo que tienes diccionario para cada grupo
        for role, desc in role_descriptions.items():
st.markdown(f"**{desc['Nombre']} ({role})**")
st.markdown(f"Posición típica: {desc['Posición']}")
st.markdown(f"{desc['Descripción']}\n")
@@ -204,6 +182,7 @@ def calculate_score_all_roles(df, roles_metrics):
st.dataframe(df_score, use_container_width=True)
else:
st.info("Por favor, sube el archivo de mediocampistas desde la barra lateral.")

# --- Radar Mediocampistas (modificado) ---
with tab2:
if uploaded_file_mid is not None:
@@ -330,81 +309,3 @@ def calculate_score_all_roles(df, roles_metrics):
st.info("Selecciona al menos un defensa central para visualizar el radar.")
else:
st.info("Por favor, sube el archivo de defensas centrales desde la barra lateral para usar el radar.")

# --- Extremos (Tabla y filtro) ---
with tab5:
    uploaded_file_wingers = st.sidebar.file_uploader("Sube archivo extremos", type=["xlsx"], key="wingers")
    if uploaded_file_wingers is not None:
        df_wingers = pd.read_excel(uploaded_file_wingers)
        df_wingers = df_wingers.rename(columns={v: k for k, v in column_map.items()})

        minutos_min_w, minutos_max_w = int(df_wingers['Minutos jugados'].min()), int(df_wingers['Minutos jugados'].max())
        altura_min_w, altura_max_w = max(0, int(df_wingers['Altura'].min())), int(df_wingers['Altura'].max())
        edad_min_w, edad_max_w = int(df_wingers['Edad'].min()), int(df_wingers['Edad'].max())

        st.header("Filtrar y visualizar tabla - Extremos")
        minutos_w = st.slider("Minutos jugados", min_value=minutos_min_w, max_value=minutos_max_w, value=(minutos_min_w, minutos_max_w), key="minutos_w")
        altura_w = st.slider("Altura (cm)", min_value=altura_min_w, max_value=altura_max_w, value=(altura_min_w, altura_max_w), key="altura_w")
        edad_w = st.slider("Edad", min_value=edad_min_w, max_value=edad_max_w, value=(edad_min_w, edad_max_w), key="edad_w")
        if st.button("Filtrar y Calcular Puntajes (Extremos)", key="button_extremos"):
            filter_params_w = {
                'Minutos jugados': minutos_w,
                'Altura': altura_w,
                'Edad': edad_w
            }
            df_filtered_w = filter_players(df_wingers, filter_params_w)
            if df_filtered_w.empty:
                st.warning("No se encontraron extremos con esos filtros.")
            else:
                df_score_w = calculate_score_all_roles(df_filtered_w, roles_metrics_wingers)
                st.dataframe(df_score_w, use_container_width=True)
    else:
        st.info("Por favor, sube el archivo de extremos desde la barra lateral.")

# --- Radar Extremos (Comparación múltiple) ---
with tab6:
    if uploaded_file_wingers is not None:
        df_radar_w = pd.read_excel(uploaded_file_wingers)
        df_radar_w = df_radar_w.rename(columns={v: k for k, v in column_map.items()})

        for r in roles_metrics_wingers.keys():
            for metric in roles_metrics_wingers[r]["Metrics"]:
                if metric in df_radar_w.columns:
                    norm_col = metric + " Normalized"
                    df_radar_w[norm_col] = normalize_series(df_radar_w[metric])

        selected_players_w = st.multiselect("Selecciona uno o más extremos", df_radar_w["Player"].unique())
        selected_role_w = st.selectbox("Selecciona un rol para el radar (Extremos)", list(roles_metrics_wingers.keys()))

        if selected_players_w:
            fig_w = go.Figure()
            for player in selected_players_w:
                player_row_w = df_radar_w[df_radar_w["Player"] == player]
                if not player_row_w.empty:
                    player_row_w = player_row_w.iloc[0]
                    metrics_w = roles_metrics_wingers[selected_role_w]["Metrics"]
                    values_w = []
                    labels_w = []
                    for metric in metrics_w:
                        norm_col = metric + " Normalized"
                        if norm_col in player_row_w:
                            values_w.append(player_row_w[norm_col])
                            labels_w.append(metric)
                    if values_w:
                        values_w += [values_w[0]]  # cerrar el círculo
                        labels_w += [labels_w[0]]
                        fig_w.add_trace(go.Scatterpolar(
                            r=values_w,
                            theta=labels_w,
                            fill='toself',
                            name=player
                        ))
            fig_w.update_layout(
                polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
                title=f"Radar de Extremos - Rol: {selected_role_w}"
            )
            st.plotly_chart(fig_w, use_container_width=True)
        else:
            st.warning("Selecciona al menos un extremo para mostrar el radar.")
    else:
        st.info("Por favor, sube el archivo de extremos desde la barra lateral para usar el radar.")
