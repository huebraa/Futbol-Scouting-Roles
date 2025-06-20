import pandas as pd
import ipywidgets as widgets
from IPython.display import display, clear_output

# ======================
# Definición de Roles
# ======================
roles_cb = {
    "Ball playing CB": {
        "Metrics": ["Accurate long passes, %","Passes to final third per 90","Deep completions per 90","Progressive passes per 90",
                    "Passes per 90","Aerial duels won, %","Defensive duels won, %"],
        "Weights": [0.15, 0.2, 0.075, 0.15, 0.325, 0.05, 0.05]
    },
    "Defensive CB": {
        "Metrics": ["Defensive duels won, %", "Aerial duels won, %", "PAdj Sliding tackles", "PAdj Interceptions",
                    "Successful defensive actions per 90"],
        "Weights": [0.3, 0.2, 0.2, 0.2, 0.1]
    },
    "Wide CB": {
        "Metrics": ["Progressive passes per 90", "Progressive runs per 90", "Passes per 90", "Defensive duels won, %", "Accurate short / medium passes, %", "Accurate long passes, %"],
        "Weights": [0.125, 0.275, 0.2, 0.2, 0.15, 0.05]
    },
    "Spreader CB": {
        "Metrics": ["Progressive passes per 90", "Progressive runs per 90", "Defensive duels won, %", "Accurate forward passes, %",
                    "PAdj Interceptions", "Long passes per 90", "Accurate long passes, %"],
        "Weights": [0.15, 0.1, 0.05, 0.15, 0.05, 0.25, 0.2]
    },
    "Aggressor CB": {
        "Metrics": ["Defensive duels won, %", "Defensive duels per 90", "PAdj Sliding tackles", "PAdj Interceptions",
                    "Shots blocked per 90"],
        "Weights": [0.3, 0.25, 0.25, 0.15, 0.05]
    },
    "Anchor CB": {
        "Metrics": ["Shots blocked per 90", "PAdj Interceptions", "Aerial duels won, %", "Defensive duels won, %", "Accurate short / medium passes, %"],
        "Weights": [0.25, 0.25, 0.2, 0.2, 0.1]
    }
}

roles_dm = {
    "Deep Lying Playmaker": {
        "Metrics": ["Accurate short / medium passes, %", "Progressive passes per 90", "Passes per 90", "Passes to final third per 90", "Accurate forward passes, %"],
        "Weights": [0.2, 0.2, 0.2, 0.2, 0.2]
    },
    "Anchor Midfielder": {
        "Metrics": ["PAdj Interceptions", "PAdj Sliding tackles", "Shots blocked per 90", "Defensive duels per 90", "Accurate short / medium passes, %"],
        "Weights": [0.25, 0.25, 0.2, 0.2, 0.1]
    },
    "Box to Box": {
        "Metrics": ["Progressive runs per 90", "Passes to final third per 90", "Defensive duels per 90", "Progressive passes per 90", "Shots per 90"],
        "Weights": [0.25, 0.2, 0.2, 0.2, 0.15]
    }
}

# ======================
# Funciones auxiliares
# ======================
def normalize_column(df, col):
    min_val, max_val = df[col].min(), df[col].max()
    if max_val > min_val:
        return (df[col] - min_val) / (max_val - min_val) * 100
    else:
        return df[col]

def calculate_score(df, role, roles_dict):
    df_copy = df.copy()
    metrics = roles_dict[role]["Metrics"]
    weights = roles_dict[role]["Weights"]
    df_copy["Score"] = 0
    for m, w in zip(metrics, weights):
        if m in df_copy.columns:
            df_copy[m + "_norm"] = normalize_column(df_copy, m)
            df_copy["Score"] += df_copy[m + "_norm"] * w
    df_copy["Score"] = normalize_column(df_copy, "Score")
    return df_copy[["Player", "Team", "Position", "Score"] + [m + "_norm" for m in metrics]].sort_values(by="Score", ascending=False)

# ======================
# Interfaz Interactiva
# ======================
def interactive_sidebar_roles():
    file_upload = widgets.FileUpload(accept='.xlsx', multiple=False)
    display(file_upload)

    output = widgets.Output()
    display(output)

    def on_upload(change):
        if file_upload.value:
            with output:
                clear_output()
                content = list(file_upload.value.values())[0]['content']
                df = pd.read_excel(content)

                # Sliders
                minutos = widgets.IntRangeSlider(value=[0, 3000], min=0, max=4000, step=100, description="Minutos")
                altura = widgets.IntRangeSlider(value=[160, 200], min=150, max=210, step=1, description="Altura (cm)")
                edad = widgets.IntRangeSlider(value=[16, 35], min=16, max=40, step=1, description="Edad")

                # Dropdowns separados en HBox
                cb_dropdown = widgets.Dropdown(options=list(roles_cb.keys()), description="DC")
                dm_dropdown = widgets.Dropdown(options=list(roles_dm.keys()), description="MC")
                filter_button = widgets.Button(description="Filtrar y Evaluar")

                box = widgets.HBox([
                    widgets.VBox([widgets.Label("Defensas Centrales"), cb_dropdown]),
                    widgets.VBox([widgets.Label("Mediocentros"), dm_dropdown])
                ])

                display(minutos, altura, edad, box, filter_button)

                def on_click(b):
                    clear_output(wait=True)
                    display(file_upload, output)

                    df_filtered = df[(df['Minutos jugados'] >= minutos.value[0]) & (df['Minutos jugados'] <= minutos.value[1]) &
                                     (df['Altura'] >= altura.value[0]) & (df['Altura'] <= altura.value[1]) &
                                     (df['Edad'] >= edad.value[0]) & (df['Edad'] <= edad.value[1])]

                    result_cb = calculate_score(df_filtered, cb_dropdown.value, roles_cb)
                    result_dm = calculate_score(df_filtered, dm_dropdown.value, roles_dm)

                    print(f"\nTop Defensas Centrales - {cb_dropdown.value}")
                    display(result_cb.head(10))

                    print(f"\nTop Mediocentros - {dm_dropdown.value}")
                    display(result_dm.head(10))

                filter_button.on_click(on_click)

    file_upload.observe(on_upload, names='value')

# Ejecutar
interactive_sidebar_roles()
