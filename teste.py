import pandas as pd 
from dash import Dash, html, Input, Output,callback, dcc
import dash 
casos = pd.read_csv('caso_full.csv', sep = ',')
import plotly.express as px

casos.head()
casos['data'] = pd.to_datetime(casos['date'])
casos['ano'] = casos['data'].dt.year
casos['mes'] = casos['data'].dt.month
casos = casos[['city', 'epidemiological_week', 'state', 'new_confirmed', 'new_deaths', 'ano','mes']]
casos.head()
casos.info()
estados_regioes = {
    'AC': 'Norte',
    'AL': 'Nordeste',
    'AM': 'Norte',
    'AP': 'Norte',
    'BA': 'Nordeste',
    'CE': 'Nordeste',
    'DF': 'Centro-Oeste',
    'ES': 'Sudeste',
    'GO': 'Centro-Oeste',
    'MA': 'Nordeste',
    'MG': 'Sudeste',
    'MS': 'Centro-Oeste',
    'MT': 'Centro-Oeste',
    'PA': 'Norte',
    'PB': 'Nordeste',
    'PE': 'Nordeste',
    'PI': 'Nordeste',
    'PR': 'Sul',
    'RJ': 'Sudeste',
    'RN': 'Nordeste',
    'RO': 'Norte',
    'RR': 'Norte',
    'RS': 'Sul',
    'SC': 'Sul',
    'SE': 'Nordeste',
    'SP': 'Sudeste',
    'TO': 'Norte'
}

casos['regiao'] = casos['state'].map(estados_regioes)
casos.head()
total_ano = casos[['state','new_deaths','ano','new_confirmed', 'regiao']].groupby(['state','ano','regiao']).sum().reset_index()
total_mes = casos[['state','mes','new_deaths','new_confirmed','ano','regiao']].groupby(['state','mes','ano','regiao']).sum().reset_index()

total_ano
px.histogram(total_ano,
             x='regiao',
             y='new_deaths',
             color = 'ano',
             hover_name='new_confirmed')
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px

app = dash.Dash(__name__)

# Supondo que você já tenha os DataFrames total_ano e total_estado carregados.

app.layout = html.Div([

    html.Div(children=[
        # Criando botão de filtro para os gráficos
        dcc.Dropdown(
            id='filtro_ano',
            options=[{'label': ano, 'value': ano} for ano in total_ano['ano'].unique()],
            value=2022
        ),
        dcc.Dropdown(
            id='filtro_estados',
            options=[{'label': estado, 'value': estado} for estado in total_ano['state'].unique()],
            value=None,
            placeholder='Escolha um estado para focar.'
        ),
    ]),

    html.Div(children=[
        dcc.Graph(id='grafico_calor'),
        dcc.Graph(id='grafico_hist')

    ], style={'display': 'flex'}),
    html.Div(children =[ 
        dcc.Graph(id = 'grafico_barras'),
        dcc.Graph(id = 'grafico_rosca')
        
    ], style = {'display': 'flex'})

])

@app.callback(
    [Output('grafico_calor', 'figure'),
     Output('grafico_hist', 'figure'),
     Output('grafico_barras', 'figure'),
     Output('grafico_rosca', 'figure')],
    [Input('filtro_estados', 'value'),
     Input('filtro_ano', 'value')]
)


# Atualizando os CallsBacks

def atualiza_charts(estado, ano):
    # Filtrando os dados com base no estado e ano selecionados para o mapa
    estado_df = total_ano[(total_ano['ano'] == ano) & (total_ano['state'] == estado)] if estado else total_ano[total_ano['ano'] == ano]

    # Criando o mapa geografico do Brasil
    fig_mapa = px.choropleth(estado_df,
                             geojson='https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/brazil-states.geojson',
                             locations='state',
                             featureidkey='properties.sigla',
                             color='new_confirmed',
                             hover_name='state',
                             hover_data=['new_confirmed', 'new_deaths'],
                             color_continuous_scale='Blues',
                             title="Mapa Coroplético dos Casos por Estado no Brasil")



    fig_mapa.update_geos(
        scope="south america",  # Limitar o escopo ao Brasil
        projection_type="mercator",  # Usar projeção Mercator
        center={"lat": -14.2350, "lon": -51.9253},  # Centralizar no Brasil
        lataxis_range=[-35, 5],  # Ajustar as latitudes para focar no Brasil
        lonaxis_range=[-75, -30]  # Ajustar as longitudes para focar no Brasil
    )

    
    # Filtrando os dados apenas pelo ano selecionado para o gráfico de linhas
    filtro_ano = total_ano[total_ano['ano'] == ano]

    # Histrograma dos casos por região e ano
    fig_hist = px.histogram(filtro_ano,
                x='regiao',
                y='new_deaths',
                hover_name='new_confirmed',
                color = 'state')
                

    # Criando o gráfico de barras por ano entre estados
    fig_barras = px.bar(data_frame= estado_df,
       x = 'new_deaths',
       y = 'state',
       color = 'regiao',
       title = 'Indices de mortes entre estados',
       orientation='h'
       
       )
    
    fig_pie = px.pie(
        filtro_ano,
        values = 'new_confirmed',
       names= 'regiao',
       color_discrete_sequence=px.colors.sequential.RdBu,
       labels = {'regiao': 'regiao'}
       )
    

    fig_pie.update_traces(textinfo='label+percent')


    return fig_mapa, fig_hist,fig_barras,fig_pie

if __name__ == '__main__':
    app.run_server(debug=True)
