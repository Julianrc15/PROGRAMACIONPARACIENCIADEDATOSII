import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
from sklearn.metrics import roc_curve, auc
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from jupyter_dash import JupyterDash

df_final = pd.read_csv("PROGRAMACIONPARACIENCIADEDATOSII\data\datos_dashboard.csv")

app = JupyterDash(__name__)

# Estilo del dropdown
dropdown_style = {
    'width': '100%',
}

# Definir el diseño del dashboard
app.layout = html.Div([
    html.H1("Dashboard de Análisis Rentabilidad fondos de Inversión Colombianos", style={'background-color': '#581845', 'color': '#DAF7A6'}),

    dcc.Dropdown(
        id='dropdown-categoria',
        options=[{'label': cat, 'value': cat} for cat in df_final['Categoría'].unique()],
        value='Renta fija',
        clearable=False,
        placeholder="Seleccionar categoría",
        style=dropdown_style
    ),

    dcc.Graph(id='rentabilidad-vs-volatilidad'),
    dcc.Graph(id='rentabilidad-diaria-histograma'),
    dcc.Graph(id='roc-curve'),
    dcc.Graph(id='rentabilidad-vs-volatilidad-bloxplot'),
    dcc.Graph(id='rentabilidad-vs-benchmark-bloxplot'),
    dcc.Graph(id='rentabilidad-vs-sharpe-ratio-bloxplot'),
    html.Hr(),  # Línea horizontal para separar las visualizaciones de la tabla
    html.H3("Datos economicos fondos de inversión Colombianos"),
    dash_table.DataTable(
        id='datatable-head',
        columns=[{"name": i, "id": i} for i in df_final.columns],
        data=[],
    )
])

# Definir las actualizaciones de la tabla de las primeras 5 filas del DataFrame
@app.callback(
    Output('datatable-head', 'data'),
    [Input('dropdown-categoria', 'value')]
)
def update_datatable(selected_categoria):
    filtered_df = df_final[df_final['Categoría'] == selected_categoria]
    return filtered_df.head().to_dict('records')

# Definir las actualizaciones de las visualizaciones basadas en la selección del usuario
@app.callback(
    [Output('rentabilidad-vs-volatilidad', 'figure'),
     Output('rentabilidad-diaria-histograma', 'figure'),
     Output('roc-curve', 'figure'),
     Output('rentabilidad-vs-volatilidad-bloxplot', 'figure'),
     Output('rentabilidad-vs-benchmark-bloxplot', 'figure'),
     Output('rentabilidad-vs-sharpe-ratio-bloxplot', 'figure')],
    [Input('dropdown-categoria', 'value')]
)
def update_plots(selected_categoria):
    filtered_df = df_final[df_final['Categoría'] == selected_categoria]

    # Crear un gráfico de dispersión de rentabilidad vs. volatilidad
    fig1 = px.scatter(filtered_df, x='Volatilidad', y='Rentabilidad diaria', 
                      color='Nombre del fondo', title='Rentabilidad vs. Volatilidad',
                      labels={'Volatilidad': 'Volatilidad', 'Rentabilidad diaria': 'Rentabilidad Diaria'})

    # Crear un histograma de rentabilidad diaria
    fig2 = px.histogram(filtered_df, x='Rentabilidad diaria', 
                        title='Histograma de Rentabilidad Diaria',
                        labels={'Rentabilidad diaria': 'Rentabilidad Diaria'},
                        nbins=20)

    # Calcular las tasas de verdaderos positivos (TPR) y las tasas de falsos positivos (FPR)
    fpr, tpr, thresholds = roc_curve(y_test, probs_class_1)

    # Calcular el área bajo la curva ROC (AUC)
    roc_auc = auc(fpr, tpr)

    # Graficar la curva ROC
    roc_curve_fig = go.Figure()
    roc_curve_fig.add_trace(go.Scatter(x=fpr, y=tpr,
                                        mode='lines',
                                        line=dict(color='darkorange', width=2),
                                        name='Curva ROC (AUC = %0.2f)' % roc_auc))
    roc_curve_fig.add_trace(go.Scatter(x=[0, 1], y=[0, 1],
                                        mode='lines',
                                        line=dict(color='navy', width=2, dash='dash'),
                                        showlegend=False))
    roc_curve_fig.update_layout(title='Curva ROC',
                                xaxis_title='Tasa de Falsos Positivos (FPR)',
                                yaxis_title='Tasa de Verdaderos Positivos (TPR)',
                                xaxis=dict(range=[0, 1]),
                                yaxis=dict(range=[0, 1]))

    # Crear boxplot de rentabilidad vs. Volatilidad
    fig3 = px.box(filtered_df, x='Volatilidad', y='Rentabilidad diaria', 
                  title='Rentabilidad vs. Volatilidad',
                  labels={'Volatilidad': 'Volatilidad', 'Rentabilidad diaria': 'Rentabilidad Diaria'})

    # Crear boxplot de rentabilidad vs. Benchmark
    fig4 = px.box(filtered_df, x='Benchmark', y='Rentabilidad diaria', 
                  title='Rentabilidad vs. Benchmark',
                  labels={'Benchmark': 'Benchmark', 'Rentabilidad diaria': 'Rentabilidad Diaria'})

    # Crear boxplot de rentabilidad vs. Sharpe Ratio
    fig5 = px.box(filtered_df, x='Sharpe Ratio', y='Rentabilidad diaria', 
                  title='Rentabilidad vs. Sharpe Ratio',
                  labels={'Sharpe Ratio': 'Sharpe Ratio', 'Rentabilidad diaria': 'Rentabilidad Diaria'})

    return fig1, fig2, roc_curve_fig, fig3, fig4, fig5

# Ejecutar la aplicación Dash
app.run_server(mode='inline')