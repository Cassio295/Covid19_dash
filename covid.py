## Introdução
import pandas as pd 
from dash import Dash, html, Input, Output,callback, dcc
import dash 
#Carregando os dados de casos de COVID-19
casos = pd.read_csv('caso_full.zip', sep = ',')
import plotly.express as px
import dash_bootstrap_components as dbc

# Configuração inicial dos dados, convertendo a coluna de datas para o formato datetime
casos['data'] = pd.to_datetime(casos['date'])
casos['ano'] = casos['data'].dt.year
casos['mes'] = casos['data'].dt.month
# Selecionar as colunas relevantes para a análise
casos = casos[['city', 'epidemiological_week', 'state', 'new_confirmed', 'new_deaths', 'ano','mes']]
casos.head()
# Verificando os tipos dos dados presentes dentro da tabela
casos.info()
# Diionário que mapeia os estados para suas respectivas regiões
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

# Adiciona a coluan'regiao' mapeando os estados para suas respectivas regiões
casos['regiao'] = casos['state'].map(estados_regioes)
# Cria DataFrames para agregar os dados por estado, ano, e cidade para as visualizações
total_ano = casos[['state','new_deaths','ano','new_confirmed', 'regiao']].groupby(['state','ano','regiao',]).sum().reset_index()
total_ano_cidades = casos[['state','new_deaths','ano','new_confirmed','city','mes']].groupby(['state','ano','city','mes']).sum().reset_index()

total_ano_cidades
# Instanciando a aplicação do Dash
app = dash.Dash(__name__)

# Definindo o Layout da aplicação
app.layout = html.Div(
    style={
        'backgroundColor': '#06141B',
        'maxWidth': '1200px',  # Largura máxima fixa
        'minWidth': '1000px',  # Largura mínima para evitar encolhimento excessivo
        'margin': '0 auto',  # Centraliza a página
        'padding': '20px',
        'overflow': 'hidden',  # Controla o conteúdo que pode ultrapassar o tamanho
    },
    className="container",
    children=[
        # Criando os elementos dos filtros para ano, estado e região
        html.Div([
            html.Div(
                dcc.Dropdown(
                    id='filtro_ano',
                    options=[{'label': ano, 'value': ano} for ano in total_ano['ano'].unique()],
                    value=2022,
                    style={'color': '#CCD0CF', 'backgroundColor': '#11212D',  
                           'borderColor': '#4A5C6A', 'text-align': 'center', 
                           'padding': '5px', 'height': '38px'}
                ), style={'flex': '1', 'margin-right': '5px'}  
            ),

            html.Div(
                dcc.Dropdown(
                    id='filtro_estados',
                    options=[{'label': estado, 'value': estado} for estado in total_ano['state'].unique()],
                    style={'color': '#CCD0CF', 'backgroundColor': '#11212D',  
                           'borderColor': '#4A5C6A', 'text-align': 'center',
                           'padding': '5px', 'height': '38px'}
                ), style={'flex': '1', 'margin-right': '5px'}  
            ),
            html.Div(
                dcc.Dropdown(
                    id ='filtro_regiao',
                    options = [{'label': regiao, 'value': regiao} for regiao in total_ano['regiao'].unique()],
                    placeholder= 'Região:',
                    style={'color': '#CCD0CF', 'backgroundColor': '#11212D',  
                           'borderColor': '#4A5C6A', 'text-align': 'center',
                           'padding': '5px', 'height': '38px'}
                ), style = {'flex': '1'}
            ),
        ], style={'display': 'flex', 'padding': '5px'}),  
        
        # Botão para baixar os dados filtrados
        html.Div([
                html.Button('Baixar os dados', id='dow_csv'),
                dcc.Download(id='download-dataframe-csv')
                ],
                style={'display': 'flex', 'justify-content': 'flex-end', 'margin-bottom': '10px'}
                ),

        # Cards para exibir métricas agregadas
        html.Div([
            dbc.Card([
                dbc.CardBody(html.H4(id='maior_caso', children='Maior Número de Casos')),
            ], style={'backgroundColor': '#CCD0CF', 'color': '#11212D', 'padding': '5px', 'border-radius': '5px'}),
            
            dbc.Card([
                dbc.CardBody(html.H4(id='maior_morte', children='Maior Número de Mortes')),
            ], style={'backgroundColor': '#CCD0CF', 'color': '#11212D', 'padding': '5px', 'border-radius': '5px'}),        
            
            dbc.Card([
                dbc.CardBody(html.H4(id='maior_regiao_casos', children='Maior Região com Número de Casos')),
            ], style={'backgroundColor': '#CCD0CF', 'color': '#11212D', 'padding': '5px', 'border-radius': '5px'}),
            
            dbc.Card([
                dbc.CardBody(html.H4(id='maior_regiao_mortes', children='Maior Região com Número de Mortes')),
            ], style={'backgroundColor': '#CCD0CF', 'color': '#11212D', 'padding': '5px', 'border-radius': '5px'}),
        ], style={'display': 'flex', 'justify-content': 'space-between', 'gap': '10px', 'margin-bottom': '10px'}),  # Flexbox para manter alinhamento e espaçamento

        # Gráficos principais
        html.Div([
            dcc.Graph(id='grafico_calor', style={'flex': '1', 'padding': '20px'}),
            dcc.Graph(id='grafico_hist', style={'flex': '1', 'padding': '20px'}),
        ], style={'display': 'flex', 'gap': '10px', 'margin-bottom': '10px'}),  # Flexbox para alinhar gráficos

        html.Div([
            dcc.Graph(id='grafico_barras', style={'flex': '1', 'padding': '20px'}),
            dcc.Graph(id='grafico_rosca', style={'flex': '1', 'padding': '20px'}),
        ], style={'display': 'flex', 'gap': '10px'}),  # Flexbox para alinhar gráficos

    ]
)
# Callback para atualizar os gráficos e métricas com base nos filtros aplicados
@app.callback(
    [Output('grafico_calor', 'figure'),   # Output do gráfico de mapa coroplético
     Output('grafico_hist', 'figure'),    # Output do gráfico de histograma
     Output('grafico_barras', 'figure'),  # Output do gráfico de barras
     Output('grafico_rosca', 'figure'),   # Output do gráfico de pizza
     Output('maior_caso', 'children'),    # Output da métrica do maior caso
     Output('maior_morte', 'children'),   # Output da métrica do maior número de mortes
     Output('maior_regiao_casos', 'children'), # Output da métrica da região com mais casos
     Output('maior_regiao_mortes', 'children')], # Output da métrica da região com mais mortes
    [Input('filtro_estados', 'value'),    # Input para o filtro de estados
     Input('filtro_ano', 'value'),
     Input('filtro_regiao','value')]        # Input para o filtro de anos
)

def atualiza_charts(estado, ano, regiao):
    # Filtrando os dados com base na região e ano para os gráficos    
    if regiao:
        regiao_df = total_ano[(total_ano['ano'] == ano) & (total_ano['regiao'] == regiao)]

        fig_pie = px.pie(
        regiao_df[regiao_df['regiao'] == regiao],
        values='new_confirmed',
        names='state',
        color_discrete_sequence=px.colors.sequential.RdBu,
        labels={'state': 'Estado'},
        title='Porcentagem de Casos Confirmados'
    )
        
        
    else:
        regiao_df = total_ano[total_ano['ano'] == ano]

    # Gráfico de Pizza para casos confirmados por região
        fig_pie = px.pie(
            total_ano,
            values='new_confirmed',
            names='regiao',
            color_discrete_sequence=px.colors.sequential.RdBu,
            labels={'state': 'Estado'},
            title='Porcentagem de Casos Confirmados'
        )

    # Mapa Coroplético dos casos de Covid por região
    fig_mapa = px.choropleth(
        regiao_df,
        geojson='https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/brazil-states.geojson',
        locations='state',
        featureidkey='properties.sigla',
        color='new_deaths',
        hover_name='state',
        hover_data=['new_confirmed', 'new_deaths'],
        color_continuous_scale='Blues',
        title="Mapa Coroplético dos Casos por Estado no Brasil"
    )

    # Histograma para comparação de mortes por estado dentro da região selecionada
    fig_hist = px.histogram(
        regiao_df,
        x='state',
        y='new_deaths',
        hover_name='new_confirmed',
        color='state',
        title='Historico de crescimento de mortes por estado'
    )

    # Gráfico de Barras para mortes no estado selecionado (ou todos se nenhum estado for selecionado)
    if estado:
        cidade_df = total_ano_cidades[(total_ano_cidades['ano'] == ano) & (total_ano_cidades['state'] == estado)]
        
        fig_hist = px.line(
            data_frame= cidade_df,
            x = 'city',
            y = 'new_confirmed',
            color = 'mes',
            title = 'Crescimento de Casos ao longo dos meses por cidade'
        ) 
 

  

    fig_barras = px.bar(
        regiao_df,
        x='new_confirmed',
        y='state',
        color='regiao',
        title='Índices de casos por Estado',
        orientation='h'
    )

    # Atualizando os layouts do mapas
    fig_mapa.update_geos(
        scope="south america",
        projection_type="mercator",
        center={"lat": -14.2350, "lon": -51.9253},
        lataxis_range=[-35, 5],
        lonaxis_range=[-75, -30],
        landcolor="#11212D",
        showocean=True,
        oceancolor="#253745",
        lakecolor="#253745"
    )

    fig_mapa.update_layout(
        paper_bgcolor='#06141B',
        font=dict(color='#CCD0CF'),
        plot_bgcolor='#CCD0CF'
    )

    fig_mapa.update_xaxes(
        title_font=dict(size=18, color='#CCD0CF')
    )

    fig_hist.update_layout(
        paper_bgcolor='#06141B',
        font=dict(color='#CCD0CF')
    )

    fig_barras.update_layout(
        paper_bgcolor='#06141B',
        font=dict(color='#CCD0CF')
    )

    fig_pie.update_traces(textinfo='label+percent')
    fig_pie.update_layout(
        paper_bgcolor='#06141B',
        font=dict(color='#CCD0CF')
    )

    # Calcular métricas de maior caso e maior morte
    maior_caso = regiao_df.groupby('state')['new_confirmed'].sum().idxmax()
    maior_caso_valor = regiao_df.groupby('state')['new_confirmed'].sum().max()

    maior_morte = regiao_df.groupby('state')['new_deaths'].sum().idxmax()
    maior_morte_valor = regiao_df.groupby('state')['new_deaths'].sum().max()

    # Calcular métricas da maior região em casos e mortes
    maior_regiao_casos = regiao_df.groupby('regiao')['new_confirmed'].sum().idxmax()
    maior_regiao_casos_valor = regiao_df.groupby('regiao')['new_confirmed'].sum().max()

    maior_regiao_mortes = regiao_df.groupby('regiao')['new_deaths'].sum().idxmax()
    maior_regiao_mortes_valor = regiao_df.groupby('regiao')['new_deaths'].sum().max()

    # Retorna as figuras dos gráficos e as métricas calculadas
    return (
        fig_mapa,
        fig_hist,
        fig_barras,
        fig_pie,
        f'Maior número de casos: {maior_caso} ({maior_caso_valor})',
        f'Maior número de mortes: {maior_morte} ({maior_morte_valor})',
        f'Maior região com número de casos: {maior_regiao_casos} ({maior_regiao_casos_valor})',
        f'Maior região com número de mortes: {maior_regiao_mortes} ({maior_regiao_mortes_valor})'
    )


# Filtrando os dados com base na região e ano para os gráficos
@app.callback(
    Output('download-dataframe-csv', 'data'),
    Input('dow_csv', 'n_clicks'),
    [dash.dependencies.State('filtro_estados', 'value'),
     dash.dependencies.State('filtro_ano', 'value'),
     dash.dependencies.State('filtro_regiao', 'value')]
)
def gerar_dados(n_clicks, estado, ano, regiao):
    if n_clicks is None:
        raise dash.exceptions.PreventUpdate

    filter_data = total_ano[(total_ano['ano'] == ano)] 
    if estado:
        filter_data = filter_data[filter_data['state'] == estado]
    if regiao:
        filter_data = filter_data[filter_data['regiao'] == regiao]
    
    return dcc.send_data_frame(filter_data.to_csv, 'dados_filtrados.csv')
    
    return None

# if __name__ == 'main':
#     app.run_server(debug = True)