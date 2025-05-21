# =====================
# 🔷 INICIALIZACIÓN DEL DASHBOARD
# =====================
# Dashboard final con Plotly Dash
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, dcc, html, dash_table, Input, Output
import dash_bootstrap_components as dbc
import base64
import io


# Inicialización de la app
dashboard = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = dashboard.server

# Carga de datos

# =====================
# 🔷 CARGA Y PREPARACIÓN DE DATOS
# =====================
df = pd.read_csv(r"1747382241186.csv")

# Procesar la columna de fecha
df["START_DATE"] = pd.to_datetime(df["START_DATE"], errors="coerce")
df = df[df["START_DATE"].notna()]  # ✅ Filtrar filas sin fecha válida
df["fecha"] = df["START_DATE"].dt.date
valid_fecha_unicas = sorted(df["fecha"].unique())



# Convertir correctamente a booleano
df["interaction_user"] = df["interaction_user"].astype(str).str.lower() == "true"
df["STATUS"] = df["STATUS"].astype(str)
df["tipo_interaccion"] = df.apply(lambda row: (
    "Encuestas contestadas" if row["interaction_user"] == True
    else "Llamadas conectadas" if row["STATUS"] == "completed"
    else "Llamadas no contestadas"
), axis=1)

# Tabla 1: Resumen llamadas y encuestas
# Agrupar por tipo de interaccion

# =====================
# 🔷 TABLA 1: RESUMEN DE INTERACCIONES
# =====================
tabla_resumen_df = df.groupby("tipo_interaccion").size().reset_index(name="conteo")

# Agregar fila de total
total_llamadas = tabla_resumen_df["conteo"].sum()
fila_total = pd.DataFrame([{"tipo_interaccion": "Total llamadas", "conteo": total_llamadas}])

# Concatenar la fila al final

# =====================
# 🔷 TABLA 1: RESUMEN DE INTERACCIONES
# =====================
tabla_resumen_df = pd.concat([tabla_resumen_df, fila_total], ignore_index=True)

tabla_resumen = dash_table.DataTable(
    id="tabla1_resumen",
    #columns=[{"name": col, "id": col} for col in tabla_resumen_df.columns],
    columns=[
    {"name": "Descripción", "id": "tipo_interaccion"},
    {"name": "# Registros", "id": "conteo"}
],
    data=tabla_resumen_df.to_dict("records"),
    sort_action="native",  # Para ordenar columnas
    #style_table={"overflowX": "auto"} # es para ver la tabla ancha
    style_table={
        "width": "480px",
        "margin": "0 auto",
        "border": "1px solid #ccc",
        "borderRadius": "8px",
        "overflowX": "auto",

    },
    style_cell={
        "textAlign": "center",
        "padding": "10px",
        "fontFamily": "Arial",
        "fontSize": "14px",
        "border": "none",
    },
    style_data={
        "backgroundColor": "white",
        "borderBottom": "1px solid #dee2e6"
    },
    style_header={
        "backgroundColor": "#4285F4",  # Azul tipo Google
        "color": "white",
        "fontWeight": "bold",
        "border": "none",
        "whiteSpace": "pre-line",  # 👈 esto respeta el \n como salto de línea
    },
    style_data_conditional=[
    {
        "if": {"filter_query": '{tipo_interaccion} = "Total llamadas"'},
        "fontWeight": "bold",
        "backgroundColor": "#f0f8ff"  # opcional: color suave de fondo
    }
],
    style_as_list_view=True  # Elimina bordes tipo Excel
)


# Gráfica 3 y 4 + Tablas de preferencia política

# =====================
# 🔷 GRÁFICAS Y TABLAS DE PREFERENCIA POLÍTICA
# =====================
orden_partidos = [
    "Morena", "PAN", "PRI", "PT", "PVEM", "Movimiento Ciudadano",
    "Ninguno", "Prefiere no decir", "Sin información"
]
colores_partidos = [
    "#a8dadc", "#457b9d", "#e63946", "#ffb703", "#90be6d",
    "#f4a261", "#bdbdbd", "#e0aaff", "#cfd8dc"
]
df_validas = df[df["interaction_user"] == True].copy()
df_validas["partido1_preferencia"] = df_validas["partido1_preferencia"].astype(str)
df_validas["partido1_apoyo"] = df_validas["partido1_apoyo"].astype(str)
df_validas["partido2_preferencia"] = df_validas["partido2_preferencia"].astype(str)
df_validas["partido2_apoyo"] = df_validas["partido2_apoyo"].astype(str)
conteo_cruzado_1 = pd.crosstab(df_validas["partido1_apoyo"], df_validas["partido1_preferencia"]).reset_index()
conteo_cruzado_2 = pd.crosstab(df_validas["partido2_apoyo"], df_validas["partido2_preferencia"]).reset_index()


# Grafica partido preferencial

# ▶️ Gráfica partido1: cálculo y orden de partidos
df_preferencia1 = pd.DataFrame({
    "partido": orden_partidos,
    "total": [df_validas["partido1_preferencia"].value_counts().get(p, 0) for p in orden_partidos]
}).sort_values("total", ascending=False)

# Extrae los partidos con valor > 0 y ordenados
partidos_con_valor = df_preferencia1[df_preferencia1["total"] > 0]["partido"].tolist()

# Filtramos columnas
columnas_visibles = ["partido1_apoyo"] + partidos_con_valor
tabla1_partido1_df = conteo_cruzado_1[columnas_visibles]


# ▶️ Generación de gráfica de barras para partido1
fig_partido1 = px.bar(
    #pd.DataFrame([{"partido": p, "total": df_validas["partido1_preferencia"].value_counts().get(p, 0)} for p in orden_partidos]),

# ▶️ Gráfica partido1: cálculo y orden de partidos
    df_preferencia1,
    x="partido", y="total", color="partido",
    color_discrete_sequence=colores_partidos, text="total"
)
fig_partido1.update_traces(text=None)
fig_partido1.update_layout(title="Preferencia de Partido Político",
    xaxis_title="Respuesta", yaxis_title="Total",
    plot_bgcolor="white", paper_bgcolor="white", showlegend=False, font=dict(size=14))

# Grafica segundo partido preferencial
df_preferencia2 = pd.DataFrame({
    "partido": orden_partidos,
    "total": [df_validas["partido2_preferencia"].value_counts().get(p, 0) for p in orden_partidos]
}).sort_values("total", ascending=False)



# ▶️ Generación de gráfica de barras para partido2
fig_partido2 = px.bar(
    df_preferencia2,
    x="partido", y="total", color="partido",
    color_discrete_sequence=colores_partidos, text="total"
)
fig_partido2.update_traces(text=None)
fig_partido2.update_layout(title="Segunda Preferencia de Partido Político",
    xaxis_title="Partido", yaxis_title="Total",
    plot_bgcolor="white", paper_bgcolor="white", showlegend=False, font=dict(size=14))

# Gráfica 7: Semáforo de calificación al gobierno
mapa_calif = {"Muy malo": 0, "Malo": 1, "Neutral": 2, "Bueno": 3, "Muy bueno": 4}
labels = list(mapa_calif.keys())
calif_counts = df[df["interaction_user"] == True]["gobierno_calificacion"].value_counts().reindex(labels, fill_value=0)
total = sum(calif_counts.values)

# Agregar categoría invisible para crear semicírculo superior (frontal)
labels.append("")
valores = [calif_counts[k] for k in mapa_calif.keys()] + [total]
colores = ["red", "orange", "yellow", "limegreen", "green", "white"]


# =====================
# 🔷 GRÁFICA SEMÁFORO DE CALIFICACIÓN AL GOBIERNO
# =====================
fig_semaforo = px.pie(
    df_dona := pd.DataFrame({
        "Calificación": ["Muy malo", "Malo", "Neutral", "Bueno", "Muy bueno"],
        "Total": [calif_counts[k] for k in ["Muy malo", "Malo", "Neutral", "Bueno", "Muy bueno"]]
    }),
    names="Calificación",
    values="Total",
    hole=0.6,
    color="Calificación",
    color_discrete_sequence=["#e63946", "#f4a261", "#ffe066", "#90be6d", "#2a9d8f"]
)

fig_semaforo.update_traces(
    textinfo="percent+label",
    textposition="inside",
    insidetextorientation="radial"
)

fig_semaforo.update_layout(
    title="Calificación al Gobierno",
    title_x=0.5,
    showlegend=False,
    margin=dict(t=40, b=40, l=40, r=40),
    font=dict(size=14),
    plot_bgcolor="white",
    paper_bgcolor="white",
    height=450,
    width=450
)

# Layout completo del dashboard

# =====================
# 🔷 LAYOUT COMPLETO DEL DASHBOARD
# =====================
dashboard.layout = dbc.Container([
    # Header
    dbc.Row([
        dbc.Col(html.Img(src="/assets/directo_telecom.png", height="78px"), width="auto"),
        dbc.Col(
            html.Div(html.H1("Encuestas Heraldo — Partidos Políticos", className="text-center"),
                     style={"display": "flex", "alignItems": "center", "justifyContent": "center", "height": "100%"}),
            width=True
        ),
        dbc.Col(html.Img(src="/assets/heraldo.jpg", height="70"), width="auto")
    ], align="center", justify="between", className="my-4"),

    # Filtro de fecha (ahora arriba)
    dcc.DatePickerRange(
      id="filtro_fecha_rango",
      start_date=df["fecha"].min(),
      end_date=df["fecha"].max(),
      display_format="DD/MM/YYYY",
      style={"width": "350px", "margin": "0 auto 20px"},
      minimum_nights=0,
    ),



    # Tabla resumen y botón de descarga
    html.Div([
        html.Button("Descargar CSV", id="btn_csv", className="me-4", style={"marginBottom": "10px"}),
        dcc.Download(id="download_csv"),
        tabla_resumen
    ]),

    html.Div(style={"height": "50px"}),  # espacio visual

    # Primera fila: Gráfica partido1 + Tabla
    dbc.Row([
        dbc.Col(
            dcc.Graph(id="grafica4_partido1", figure=fig_partido1),
            style={"display": "flex", "alignItems": "center", "height": "100%"}, 
            width=7
        ),
        dbc.Col(
            dash_table.DataTable(
            id="tabla1_partido1",
            columns=[{"name": "Razón de apoyo", "id": "partido1_apoyo"}]
                     + [{"name": col, "id": col} for col in conteo_cruzado_1.columns if col != "partido1_apoyo"],
            data=conteo_cruzado_1.to_dict("records"),
            style_table={"overflowX": "auto"},
            style_cell={"textAlign": "center", "padding": "5px"},
            style_header={"backgroundColor": "#f4f4f4", "fontWeight": "bold", "whiteSpace": "pre-line",}
          )
        , style={"display": "flex", "alignItems": "start", "marginTop": "50px"}, width=5
        )
    ]),

    # Segunda fila: Gráfica partido2 + Tabla
    dbc.Row([dbc.Col(html.Div(dcc.Graph(id="grafica5_partido2", figure=fig_partido2),
            style={"display": "flex", "alignItems": "center", "height": "100%", "marginTop": "50px"}), width=7),
            dbc.Col(html.Div(dash_table.DataTable(
            id="tabla2_partido2",
            columns=[{"name": "Razón de apoyo", "id": "partido2_apoyo"}] 
            + [{"name": col, "id": col} for col in conteo_cruzado_2.columns 
               if col != "partido2_apoyo"],
            data=conteo_cruzado_2.to_dict("records"),
            style_table={"overflowX": "auto"},
            style_cell={"textAlign": "center", "padding": "5px"},
            style_header={"backgroundColor": "#f4f4f4", "fontWeight": "bold", "whiteSpace": "pre-line", }
        ), style={"display": "flex", "alignItems": "center", "height": "100%", "marginLeft": "-180px"}), width=5),
    ]),
    # Gráfica semáforo
    dbc.Row([
        dbc.Col(dcc.Graph(id="grafica7_semaforo", figure=fig_semaforo),
                style={"display": "flex", "justifyContent": "center", "alignItems": "center", "marginTop": "80px"},
                width=12)
    ])
], fluid=True)


# Activar botón de descarga de la tabla

# =====================
# 🔷 CALLBACKS
# =====================
@dashboard.callback(
    Output("grafica4_partido1", "figure"),
    Output("grafica5_partido2", "figure"),
    Output("grafica7_semaforo", "figure"),
    Output("tabla1_partido1", "data"),
    Output("tabla2_partido2", "data"),
    Output("tabla1_resumen", "data"),
    Input("filtro_fecha_rango", "start_date"),
    Input("filtro_fecha_rango", "end_date"),
)
def actualizar_con_rango(start_date, end_date):
    # Filtrar el DataFrame por el rango de fechas
    if not start_date or not end_date:
        return dash.no_update, dash.no_update, dash.no_update, [], [], []
    
    fecha_inicio = pd.to_datetime(start_date).date()
    fecha_fin = pd.to_datetime(end_date).date()
    
    df_filtrado = df[(df["fecha"] >= fecha_inicio) & (df["fecha"] <= fecha_fin)]
    if df_filtrado.empty:
        return dash.no_update, dash.no_update, dash.no_update, [], [], []
    df_validas = df_filtrado[df_filtrado["interaction_user"] == True].copy()
    
    # Tabla resumen
    resumen_df = df_filtrado.groupby("tipo_interaccion").size().reset_index(name="conteo")
    total_llamadas = resumen_df["conteo"].sum()
    resumen_df = pd.concat([resumen_df, pd.DataFrame([{
        "tipo_interaccion": "Total llamadas",
        "conteo": total_llamadas
    }])], ignore_index=True)

    # Gráfica partido1
    df_preferencia1 = pd.DataFrame({
        "partido": orden_partidos,
        "total": [df_validas["partido1_preferencia"].value_counts().get(p, 0) for p in orden_partidos]
    }).sort_values("total", ascending=False)

    fig_partido1 = px.bar(
        df_preferencia1, x="partido", y="total", color="partido",
        color_discrete_sequence=colores_partidos
    )
    fig_partido1.update_traces(text=None)
    fig_partido1.update_layout(
        title="Preferencia de Partido Político",
        xaxis_title="Respuesta", yaxis_title="Total",
        plot_bgcolor="white", paper_bgcolor="white",
        showlegend=False, font=dict(size=14)
    )

    # Gráfica partido2
    df_preferencia2 = pd.DataFrame({
        "partido": orden_partidos,
        "total": [df_validas["partido2_preferencia"].value_counts().get(p, 0) for p in orden_partidos]
    }).sort_values("total", ascending=False)

    fig_partido2 = px.bar(
        df_preferencia2, x="partido", y="total", color="partido",
        color_discrete_sequence=colores_partidos
    )
    fig_partido2.update_traces(text=None)
    fig_partido2.update_layout(
        title="Segunda Preferencia de Partido Político",
        xaxis_title="Partido", yaxis_title="Total",
        plot_bgcolor="white", paper_bgcolor="white",
        showlegend=False, font=dict(size=14)
    )

    # Tablas cruzadas
    conteo_cruzado_1 = pd.crosstab(df_validas["partido1_apoyo"], df_validas["partido1_preferencia"]).reset_index()
    conteo_cruzado_2 = pd.crosstab(df_validas["partido2_apoyo"], df_validas["partido2_preferencia"]).reset_index()

    tabla1_data = conteo_cruzado_1.to_dict("records")
    tabla2_data = conteo_cruzado_2.to_dict("records")
    resumen_data = resumen_df.to_dict("records")

    # Gráfica semáforo
    calif_counts = df_validas["gobierno_calificacion"].value_counts().reindex(
        ["Muy malo", "Malo", "Neutral", "Bueno", "Muy bueno"], fill_value=0
    )
    df_dona = pd.DataFrame({
        "Calificación": calif_counts.index,
        "Total": calif_counts.values
    })

    fig_semaforo = px.pie(
        df_dona, names="Calificación", values="Total", hole=0.6,
        color="Calificación",
        color_discrete_sequence=["#e63946", "#f4a261", "#ffe066", "#90be6d", "#2a9d8f"]
    )
    fig_semaforo.update_traces(
        textinfo="percent+label",
        textposition="inside",
        insidetextorientation="radial"
    )
    fig_semaforo.update_layout(
        title="Calificación al Gobierno",
        title_x=0.5,
        showlegend=False,
        margin=dict(t=40, b=40, l=40, r=40),
        font=dict(size=14),
        plot_bgcolor="white",
        paper_bgcolor="white",
        height=450,
        width=450
    )

    return fig_partido1, fig_partido2, fig_semaforo, tabla1_data, tabla2_data, resumen_data

@dashboard.callback(
    Output("download_csv", "data"),
    Input("btn_csv", "n_clicks"),
    prevent_initial_call=True
)
def descargar_csv(n_clicks):
    return dcc.send_data_frame(tabla_resumen_df.to_csv, "tabla_resumen.csv", index=False)




# =====================
# 🔷 EJECUCIÓN LOCAL
# =====================
if __name__ == "__main__":
    dashboard.run(host="0.0.0.0", port=8050)

    
    
#### Correr http://127.0.0.1:8050/