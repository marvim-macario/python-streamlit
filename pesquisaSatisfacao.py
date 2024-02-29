import streamlit as st
import pandas as pd
import plotly.express as px
import pyodbc
import plotly.io as pio     

df = pd.read_excel("dados_pesquisa.xlsx")


# Conectar ao banco de dados
# conn = pyodbc.connect('DRIVER={SQL Server};SERVER=10.236.2.56;DATABASE=CAD;UID=qlik_integra;PWD=qlik_integra')

# Query SQL
# query = "SELECT * FROM pmerj_ocorrencias.vw_qlik_pesq_satisfacao"

# Executar a consulta e carregar os dados no pandas
# df = pd.read_sql(query, conn)

# Fechar a conexão com o banco de dados
# conn.close()

# Configurações da página
st.set_page_config(layout='wide', page_title="Pesquisa de Satisfação")

# Função count protocolos
def contar_protocolos(df):
    return df['protocolo'].nunique()

# Função média das avaliações
def calcular_media_avaliacoes(df):
    return round(df['nota_resposta'].mean(), 2)

# Função para calcular a média das avaliações para uma pergunta específica
def calcular_media_por_pergunta(df, cod_pergunta):
    df_filtered = df[df['cod_pergunta'] == cod_pergunta]
    return round(df_filtered['nota_resposta'].mean(), 2)

# Função para calcular a média da nota de resposta por dia
def calcular_media_por_dia(df):
    media_por_dia = df.groupby('dia')['nota_resposta'].mean().reset_index()
    return media_por_dia.round(2)  # Arredonda para duas casas decimais




# filtros - Carregar os dados
units = list(df['BPM'].unique())
mun_list = list(df['mun'].unique())
bairro_list = list(df['bairro'].unique())
ano_list = list(df['ano'].unique())
mes_list = list(df['mes'].unique())
dia_list = list(df['dia'].unique())

# Selects lado a lado
col1, col2, col3, col4, col5, col6 = st.columns(6)
with col1:
    selected_unit = st.multiselect("", units, placeholder="Unidade")
with col2:
    selected_mun = st.multiselect("", mun_list, placeholder="Município")
with col3:
    selected_bairro = st.multiselect("", bairro_list, placeholder="Bairro")
with col4:
    selected_ano = st.multiselect("", ano_list, placeholder="Ano")
with col5:
    selected_mes = st.multiselect("", mes_list, placeholder="Mês")
with col6:
    selected_dia = st.multiselect("", dia_list, placeholder="Dia")

# Filtrar seleções
filtered_df = df
if selected_unit:
    filtered_df = filtered_df[filtered_df['BPM'].isin(selected_unit)]
if selected_mun:
    filtered_df = filtered_df[filtered_df['mun'].isin(selected_mun)]
if selected_bairro:
    filtered_df = filtered_df[filtered_df['bairro'].isin(selected_bairro)]
if selected_ano:
    filtered_df = filtered_df[filtered_df['ano'].isin(selected_ano)]
if selected_mes:
    filtered_df = filtered_df[filtered_df['mes'].isin(selected_mes)]
if selected_dia:
    filtered_df = filtered_df[filtered_df['dia'].isin(selected_dia)]



# Valores dos CARDS
av_mobile = contar_protocolos(filtered_df)
media_avaliacoes = calcular_media_avaliacoes(filtered_df)
media_atendimento_telefonico = calcular_media_por_pergunta(filtered_df, 'P0001')
media_chegada_local = calcular_media_por_pergunta(filtered_df, 'P0002')
media_resolucao_problema = calcular_media_por_pergunta(filtered_df, 'P0003')
media_servico_pm = calcular_media_por_pergunta(filtered_df, 'P0004')



#GRAFICO DE BARRAS HORIZONTAIS
def update_chart(df, title):
    bar_fig = px.bar(df.groupby('nota_resposta').size().reset_index(name='count'), 
                     height=350,
                     x='count', 
                     y='nota_resposta', 
                     orientation='h', 
                     labels={'count': 'Count', 'nota_resposta': 'Nota de Resposta'},
                     title=title,
                     barmode='stack',
                     hover_data={'count': True, 'nota_resposta': False},
                    )

    bar_fig.update_traces(marker=dict(line=dict(color='#FEBF0F', width=2),  # Cor e largura da linha da borda
                                       color='#F6E6BA',
                                       opacity=0.9,
                                       ),
                          selector=dict(type='bar'),
                          width=0.5,  
                          text=df.groupby('nota_resposta').size().values,
                          textposition='outside'  
                          )
    
    bar_fig.update_layout(xaxis_title=None, yaxis_title=None, plot_bgcolor='rgba(255,255,255,0.7)', paper_bgcolor='#FFFFFF',
                          margin=dict(l=30, r=10, t=70, b=50),  
                          title=dict(text=f'<b>{title}</b>', font=dict(size=21, family="Roboto"), x=0.02, y=0.95),  
                          yaxis=dict(tickfont=dict(size=14), automargin=True, showgrid=False, showline=False, fixedrange=True),  # Removendo a linha do grid
                          xaxis=dict(showticklabels=False, showline=False, fixedrange=True),
                          bargap=0.15,
                          uniformtext_minsize=10,
                          uniformtext_mode='hide',
                          showlegend=False,
                         )

    return bar_fig

#INCLUIR NO HTML
updated_bar_fig1 = update_chart(filtered_df, 'Total de Avaliações')




# Calcular a média da nota de resposta por dia
media_por_dia = calcular_media_por_dia(filtered_df)



#GRÁFICO DE LINHA NOTA POR DIA
def update_line_chart(df, title):
    
    line_fig = px.line(df, x='dia', y='nota_resposta', 
                       height=350,
                       labels={'nota_resposta': 'Média da Nota de Resposta', 'dia': 'Data'},
                       title=title,
                       )
    
    line_fig.update_layout(xaxis_title=None, yaxis_title=None, plot_bgcolor='rgba(255,255,255,0.7)', paper_bgcolor='#FFFFFF',
                           title=dict(text=f'<b>{title}</b>', font=dict(size=21, family="Roboto"), x=0.02, y=0.95),  
                           yaxis=dict(tickfont=dict(size=12)),  
                           xaxis=dict(tickfont=dict(size=12), showline=False),  # Removendo a linha do eixo x
                           )
    
    # Modificando a forma das linhas para suavizadas (onduladas)
    for trace in line_fig.data:
        trace.update(line=dict(width=5), line_color='#1E88E5', name='')
    
    # Adicionando marcadores aos valores e exibindo os valores em cada ponto
    line_fig.update_traces(mode='lines+markers', marker=dict(size=8, color='#1E88E5', line=dict(width=1, color='black')), text=df['nota_resposta'])
    
    # Formatando os valores do eixo y para duas casas decimais
    line_fig.update_yaxes(tickvals=list(range(int(min(df['nota_resposta'])), int(max(df['nota_resposta']))+1)), tickformat=".2f")
    
    # Removendo dropdown e range slider
    line_fig.update_layout(updatemenus=[], xaxis_rangeslider_visible=False)
    
    return line_fig

#HTML do gráfico de linhas
updated_line_fig = update_line_chart(media_por_dia, 'Média Avaliação por Dia')
line_chart_html = pio.to_html(updated_line_fig, full_html=False)



# FUNÇÕES PARA AS TABELAS
# Filtrar o DataFrame para incluir apenas as linhas por pergunta"
filtered_df_p0001 = filtered_df[filtered_df['cod_pergunta'] == 'P0001']

filtered_df_p0002 = filtered_df[filtered_df['cod_pergunta'] == 'P0002']

filtered_df_p0003 = filtered_df[filtered_df['cod_pergunta'] == 'P0003']

filtered_df_p0004 = filtered_df[filtered_df['cod_pergunta'] == 'P0004']


# ATENDENTES
table_data_atendentes = filtered_df_p0001.groupby('atendente').agg({'protocolo': 'nunique', 'nota_resposta': 'mean'}).reset_index()
table_data_atendentes.columns = ['Atendente', 'Count Distinct Protocolo', 'Média Nota Resposta']
table_data_atendentes['Média Nota Resposta'] = table_data_atendentes['Média Nota Resposta'].round(2)
table_data_atendentes = table_data_atendentes.sort_values(by='Média Nota Resposta', ascending=False)

# Criar uma tabela com os resultados para atendentes
table_html_atendentes = """
<div id="atendentes_table" class="table-container" style="max-height: 400px; overflow-y: auto; display: block;">
    <table id="table_atendentes" class="scrollable-table" style="font-family: 'Roboto', sans-serif; border-collapse: collapse; width: 100%;">
        <thead>
            <tr class="sticky-row" style="background-color: #EEEEEE;">
                <th style="padding: 10px; border: 1px solid #DDDDDD;">Atendente</th>
                <th style="padding: 10px; border: 1px solid #DDDDDD;">
                    <button onclick="sortTable(1, 'atendentes')" style="background-color: #E3E9EF; border: none; border-radius: 5px; padding: 5px 10px; cursor: pointer;">Quantidade</button>
                    <span id="arrow1_atendentes" style="margin-left: 5px;"></span>
                </th>
                <th style="padding: 10px; border: 1px solid #DDDDDD;">
                    <button onclick="sortTable(2, 'atendentes')" style="background-color: #E3E9EF; border: none; border-radius: 5px; padding: 5px 10px; cursor: pointer;">Atendimento Telefônico</button>
                    <span id="arrow2_atendentes" style="margin-left: 5px;"></span>
                </th>
            </tr>
        </thead>
        <tbody>
"""

# Adicionar os dados da tabela para atendentes_table
for index, row in table_data_atendentes.iterrows():
    table_html_atendentes += f"""
            <tr>
                <td style="padding: 10px; border: 1px solid #DDDDDD;">{row['Atendente']}</td>
                <td style="padding: 10px; border: 1px solid #DDDDDD;">{row['Count Distinct Protocolo']}</td>
                <td style="padding: 10px; border: 1px solid #DDDDDD;">{row['Média Nota Resposta']}</td>
            </tr>
"""

table_html_atendentes += """
        </tbody>
    </table>
</div>
"""

table_html_atendentes += """
<style>
    .sticky-row th {
        position: sticky;
        top: 0;
        z-index: 2;
        background-color: #EEEEEE;
    }
</style>
"""


# DESPACHADORES #P0002
table_data_despachadores = filtered_df_p0002.groupby('despachador').agg({'protocolo': 'nunique', 'nota_resposta': 'mean'}).reset_index()
table_data_despachadores.columns = ['Despachador', 'Count Distinct Protocolo', 'Média Nota Resposta']
table_data_despachadores['Média Nota Resposta'] = table_data_despachadores['Média Nota Resposta'].round(2)
table_data_despachadores = table_data_despachadores.sort_values(by='Média Nota Resposta', ascending=False)

# Adicionar a média da nota de resposta para a pergunta P0003
table_data_despachadores_p0003 = filtered_df_p0003.groupby('despachador')['nota_resposta'].mean().reset_index()
table_data_despachadores_p0003.columns = ['Despachador', 'Média Nota Resposta P0003']
table_data_despachadores = table_data_despachadores.merge(table_data_despachadores_p0003, on='Despachador', how='left').round(2)
table_data_despachadores['Média Nota Resposta P0003'] = table_data_despachadores['Média Nota Resposta P0003'].fillna(0)

# Criar uma tabela com os resultados para despachadores
table_html_despachadores = """
<div id="despachadores_table" class="table-container" style="max-height: 400px; overflow-y: auto; display: none;">
    <table id="table_despachadores" class="scrollable-table" style="font-family: 'Roboto', sans-serif; border-collapse: collapse; width: 100%;">
        <thead>
            <tr class="sticky-row" style="background-color: #EEEEEE;">
                <th style="padding: 10px; border: 1px solid #DDDDDD;">Despachador</th>
                <th style="padding: 10px; border: 1px solid #DDDDDD;">
                    <button onclick="sortTable(1, 'despachadores')" style="background-color: #E3E9EF; border: none; border-radius: 5px; padding: 5px 10px; cursor: pointer;">Quantidade</button>
                    <span id="arrow1_despachadores" style="margin-left: 5px;"></span>
                </th>
                <th style="padding: 10px; border: 1px solid #DDDDDD;">
                    <button onclick="sortTable(2, 'despachadores')" style="background-color: #E3E9EF; border: none; border-radius: 5px; padding: 5px 10px; cursor: pointer;">Chegada ao Local</button>
                    <span id="arrow2_despachadores" style="margin-left: 5px;"></span>
                </th>
                <th style="padding: 10px; border: 1px solid #DDDDDD;">
                <button onclick="sortTable(3, 'despachadores')" style="background-color: #E3E9EF; border: none; border-radius: 5px; padding: 5px 10px; cursor: pointer;">Resolução do Problema</button>
                <span id="arrow3_despachadores" style="margin-left: 5px;"></span>
            </th>
            </tr>
        </thead>
        <tbody>
"""

# Adicionar os dados da tabela para despachadores_table
for index, row in table_data_despachadores.iterrows():
    table_html_despachadores += f"""
            <tr>
                <td style="padding: 10px; border: 1px solid #DDDDDD;">{row['Despachador']}</td>
                <td style="padding: 10px; border: 1px solid #DDDDDD;">{row['Count Distinct Protocolo']}</td>
                <td style="padding: 10px; border: 1px solid #DDDDDD;">{row['Média Nota Resposta']}</td>
                <td style="padding: 10px; border: 1px solid #DDDDDD;">{row['Média Nota Resposta P0003']}</td>
            </tr>
"""

table_html_despachadores += """
        </tbody>
    </table>
</div>
"""

table_html_despachadores += """
<style>
    .sticky-row th {
        position: sticky;
        top: 0;
        z-index: 2;
        background-color: #EEEEEE;
    }
</style>
"""

# Adicionar os botões para selecionar as tabelas de atendentes e despachadores
buttons_html = """
<div style="margin-bottom: 30px;">
    <button id="btn_atendentes" onclick="showTable('atendentes_table')" style="background-color: #1E88E5; color: white; font-size: 16px; font-family: 'Roboto', sans-serif; border: none; border-radius: 5px; padding: 5px 10px; cursor: pointer;">Atendentes</button>
    <button id="btn_despachadores" onclick="showTable('despachadores_table')" style="background-color: #1E88E5; color: white; font-size: 16px; font-family: 'Roboto', sans-serif; border: none; border-radius: 5px; padding: 5px 10px; cursor: pointer;">Despachadores</button>
</div>
"""

# Adicionar o código JavaScript para ordenar as tabelas e exibir apenas a tabela clicada
script_html = """
<script>
var order1_atendentes = 'asc';
var order2_atendentes = 'asc';
var order1_despachadores = 'asc';
var order2_despachadores = 'asc';
var order3_despachadores = 'asc';

function sortTable(columnIndex, tableName) {
    var table, rows, switching, i, x, y, shouldSwitch;
    table = document.getElementById('table_' + tableName);
    switching = true;
    while (switching) {
        switching = false;
        rows = table.rows;
        for (i = 1; i < (rows.length - 1); i++) {
            shouldSwitch = false;
            x = rows[i].getElementsByTagName("td")[columnIndex];
            y = rows[i + 1].getElementsByTagName("td")[columnIndex];
            if (columnIndex === 1 || columnIndex === 2 || columnIndex === 3) {
                if ((columnIndex === 1 && ((tableName === 'atendentes' && order1_atendentes === 'asc') || (tableName === 'despachadores' && order1_despachadores === 'asc') && parseInt(x.innerHTML) > parseInt(y.innerHTML)) || 
                    (columnIndex === 1 && ((tableName === 'atendentes' && order1_atendentes === 'desc') || (tableName === 'despachadores' && order1_despachadores === 'desc') && parseInt(x.innerHTML) < parseInt(y.innerHTML)))) || 
                    (columnIndex === 2 && ((tableName === 'atendentes' && order2_atendentes === 'asc') || (tableName === 'despachadores' && order2_despachadores === 'asc') && parseInt(x.innerHTML) > parseInt(y.innerHTML)) || 
                    (columnIndex === 2 && ((tableName === 'atendentes' && order2_atendentes === 'desc') || (tableName === 'despachadores' && order2_despachadores === 'desc') && parseInt(x.innerHTML) < parseInt(y.innerHTML)))) ||
                    (columnIndex === 3 && ((tableName === 'atendentes' && order3_atendentes === 'asc') || (tableName === 'despachadores' && order3_despachadores === 'asc') && parseInt(x.innerHTML) > parseInt(y.innerHTML)) || 
                    (columnIndex === 3 && ((tableName === 'atendentes' && order3_atendentes === 'desc') || (tableName === 'despachadores' && order3_despachadores === 'desc') && parseInt(x.innerHTML) < parseInt(y.innerHTML))))) {
                    shouldSwitch = true;
                    break;
                }
            }
        }
        if (shouldSwitch) {
            rows[i].parentNode.insertBefore(rows[i + 1], rows[i]);
            switching = true;
        }
    }
    toggleArrow(columnIndex, tableName);
}


function toggleArrow(columnIndex, tableName) {
    var arrow;
    if (tableName === 'atendentes') {
        arrow = document.getElementById('arrow' + columnIndex + '_atendentes');
        if (columnIndex === 1) {
            order1_atendentes = order1_atendentes === 'asc' ? 'desc' : 'asc';
            arrow.innerHTML = order1_atendentes === 'asc' ? '&#x25B2;' : '&#x25BC;';
        } else if (columnIndex === 2) {
            order2_atendentes = order2_atendentes === 'asc' ? 'desc' : 'asc';
            arrow.innerHTML = order2_atendentes === 'asc' ? '&#x25B2;' : '&#x25BC;';
        } else if (columnIndex === 3) {
            order3_atendentes = order3_atendentes === 'asc' ? 'desc' : 'asc';
            arrow.innerHTML = order3_atendentes === 'asc' ? '&#x25B2;' : '&#x25BC;';
        }
    } else if (tableName === 'despachadores') {
        arrow = document.getElementById('arrow' + columnIndex + '_despachadores');
        if (columnIndex === 1) {
            order1_despachadores = order1_despachadores === 'asc' ? 'desc' : 'asc';
            arrow.innerHTML = order1_despachadores === 'asc' ? '&#x25B2;' : '&#x25BC;';
        } else if (columnIndex === 2) {
            order2_despachadores = order2_despachadores === 'asc' ? 'desc' : 'asc';
            arrow.innerHTML = order2_despachadores === 'asc' ? '&#x25B2;' : '&#x25BC;';
        } else if (columnIndex === 3) {
            order3_despachadores = order3_despachadores === 'asc' ? 'desc' : 'asc';
            arrow.innerHTML = order3_despachadores === 'asc' ? '&#x25B2;' : '&#x25BC;';
        }
    }
}


function showTable(tableName) {
    var tables = document.querySelectorAll('.table-container');
    tables.forEach(function(table) {
        table.style.display = 'none';
    });
    var selectedTable = document.getElementById(tableName);
    if (selectedTable) {
        selectedTable.style.display = 'block';
    }
    
    // Adiciona opacidade ao botão correspondente à tabela selecionada
    var buttons = document.querySelectorAll('[id^="btn_"]');
    buttons.forEach(function(button) {
        button.style.opacity = 1; // Resetar a opacidade de todos os botões
    });
    var selectedButton = document.getElementById('btn_' + tableName);
    if (selectedButton) {
        selectedButton.style.opacity = 0.5; // Aplicar opacidade ao botão selecionado
    }
}
</script>
"""

# Combinar todos os elementos HTML
table_html = buttons_html + table_html_atendentes + table_html_despachadores + script_html








#CSS - HTML
html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{
            background-color: #EAF2FF;
            font-family: 'Roboto', sans-serif;
            margin: 0;
            padding: 10px;
        }}

        .card {{
            display: grid;
            grid-template-columns: 1fr 4fr; /* Divide o cartão em duas colunas */
            background-color: #FFFFFF;
            border-radius: 10px;
            box-shadow: 0px 3px 6px rgba(0, 0, 0, 0.2);
            padding: 20px;
            text-align: left;
            align-items: center;
            margin: 10px;
        }}

        .card img {{
                display: block; /* Define a imagem como um bloco para poder aplicar margem */
                margin: 0 auto; /* Centraliza a imagem horizontalmente */
                width: 56px;
                height: 56px;
                border-radius: 10px 0 0 10px; /* Arredonda a borda superior esquerda da imagem */
                    }}

        .card div {{
            padding-left: 10px;
        }}

        .card p {{
            font-size: 16px; /* Alterado para 16px */
            margin: 5px 0;
            text-align: left;
        }}

        .card p2 {{
            font-size: 28px; /* Alterado para 16px */
            margin: 5px 0;
            text-align: left;
            font-weight: bold;
        }}

        .grid-container {{
            display: grid;
            grid-template-columns: repeat(6, 1fr); /* Alterei para 6 colunas */
            justify-items: space-between; /* Alinha os itens nas extremidades */
            align-items: center; /* Alinha os itens verticalmente */
            
        }}

        .grid-item {{
            width: 100%; /* Ajustei para 100% */
            background-color: #FFFFFF;
            border-radius: 10px;
            box-shadow: 0px 3px 6px rgba(0, 0, 0, 0.2);
            padding: 10px;
            text-align: left;
            align-items: left;
        }}

        .grid-container-graficos {{
            display: grid;
            gap: 40px;
            grid-template-columns: 1fr 1fr 1fr; /* Alterei para 1fr e 2fr */
            
            justify-items: center;
            align-items: center; /* Alinha os itens verticalmente */
            margin-right: 20px;
            margin-left: 20px;
            margin-top: 1px;
            height: 400px;
        }}

        .grid-container-graficos2 {{
            display: grid;
            grid-template-columns: 1fr;
            
                        
            justify-items: center;
            align-items: center; /* Alinha os itens verticalmente */
            margin-right: 20px;
            margin-left: 20px;
            margin-top: 1px;
            height: 400px;

        }}
        .grid-container-graficos3 {{
            display: grid;
            grid-template-columns: 1fr;
            
                       
            justify-items: center;
            align-items: center; /* Alinha os itens verticalmente */
            margin-right: 20px;
            margin-left: 20px;
            margin-top: 1px;
            height: 400px;

        }}
    </style>
</head>



<body>
    <div class="grid-container">
        <div class="card">
            <img src="https://i.ibb.co/FbcM1pL/cel.png">
            <div>
                <p class="bold-text">Avaliações Mobile</p>
                <p2 class="bold-text">{av_mobile}</p2>
            </div>
        </div>
        <div class="card">
            <img src="https://i.ibb.co/R6STXnW/estrela.png">
            <div>
                <p class="bold-text">Média Avaliações</p>
                <p2 class="bold-text">{media_avaliacoes}</p2>
            </div>
        </div>
        <div class="card">
            <img src="https://i.ibb.co/z87Zw5S/tel.png">
            <div>
                <p class="bold-text">Atend. telefônico</p>
                <p2 class="bold-text">{media_atendimento_telefonico}</p2>
            </div>
        </div>
        <div class="card">
            <img src="https://i.ibb.co/w0B8nSY/chegada.png">
            <div>
                <p class="bold-text">Chegada ao Local</p>
                <p2 class="bold-text">{media_chegada_local}</p2>
            </div>
        </div>
        <div class="card">
            <img src="https://i.ibb.co/9T6QZBK/servico-Prestado.png">
            <div>
                <p class="bold-text">Resolução Problema</p>
                <p2 class="bold-text">{media_resolucao_problema}</p2>
            </div>
        </div>
        <div class="card">
            <img src="https://i.ibb.co/RQC981c/servico-Pm.png">
            <div>
                <p class="bold-text">Serviço da PM</p>
                <p2 class="bold-text">{media_servico_pm}</p2>
            </div>
        </div>

    </div>
    
    <div class="grid-container-graficos">
        <div class="grid-item">
            {updated_bar_fig1.to_html(include_plotlyjs='cdn')}
        </div>
        <div class="grid-item">
            {updated_bar_fig1.to_html(include_plotlyjs='cdn')}

        </div>
        <div class="grid-item">
                    {updated_bar_fig1.to_html(include_plotlyjs='cdn')}
        </div>
    </div>

    <div class="grid-container-graficos2">  
        <div class="grid-item">  
        {line_chart_html}
        </div>
    </div>

    <div class="grid-container-graficos3">  
        <div class="grid-item">  
        {table_html}

        </div>
    </div>


</body>
</html>
"""

st.components.v1.html(html_content, height=1000)  ;
                                                                          


