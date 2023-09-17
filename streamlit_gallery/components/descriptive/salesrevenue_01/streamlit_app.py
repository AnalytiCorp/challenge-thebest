import pandas as pd
import streamlit as st
from streamlit_echarts import st_pyecharts, st_echarts
from pyecharts import options as opts
from pyecharts.charts import Pie, Bar

# Função para carregar os dados
@st.cache_data
def data_base():
    # Carregando os dados do arquivo XLSX
    path = "base/dados_ficticios.xlsx"
    df_clientes = pd.read_excel(path, sheet_name='Clientes')
    df_produtos = pd.read_excel(path, sheet_name='Produtos')
    df_transacoes = pd.read_excel(path, sheet_name='Transações')

    # Criando um dataframe único combinando as tabelas relevantes
    df_final = df_transacoes.merge(df_clientes, on='ID_Consumidor').merge(df_produtos, on='ID_produto')
    df_final_2022 = df_final[df_final['Data_compra'].dt.year == 2022]
        
    return df_final, df_final_2022, df_transacoes, df_produtos, df_clientes

def dre():
    df_final, df_final_2022, df_transacoes, df_produtos, df_clientes = data_base()

    # Cálculos para a Demonstração de Resultado do Exercício (DRE)
    receita_bruta = df_final['Valor'].sum()
    receita_liquida = 0.9 * receita_bruta
    df_final['Custo_total'] = df_final['Quantidade'] * df_final['ID_produto'].map(df_produtos.set_index('ID_produto')['Custo'])
    custos_vendas = df_final['Custo_total'].sum()
    margem_bruta = receita_liquida - custos_vendas
    despesas_operacionais = 0.15 * receita_liquida
    lucro_operacional = margem_bruta - despesas_operacionais
    impostos = 0.1 * lucro_operacional
    lucro_liquido = lucro_operacional - impostos

    # Estruturando os dados da DRE
    dre = {
        'Receita Bruta': receita_bruta,
        'Receita Líquida': receita_liquida,
        'Custos de Vendas': custos_vendas,
        'Margem Bruta': margem_bruta,
        'Despesas Operacionais': despesas_operacionais,
        'Lucro Operacional': lucro_operacional,
        'Impostos': impostos,
        'Lucro Líquido': lucro_liquido
    }
    
    return dre

def tendencias_tempo():
    df_final, df_final_2022, df_transacoes, df_produtos, df_clientes = data_base()
    
    # 1.a. Tendências de vendas ao longo do tempo
    df_vendas_tempo = df_final_2022.groupby('Data_compra').agg({'Quantidade': 'sum'}).sort_index()

    # Amortização dos dados usando média móvel
    df_vendas_tempo['Média_móvel'] = df_vendas_tempo['Quantidade'].rolling(window=7).mean()

    # Substituir NaN por 0 nos dados de média móvel
    df_vendas_tempo['Média_móvel'].fillna(0, inplace=True)

    # Preparando os dados para o gráfico de linhas
    datas = df_vendas_tempo.index.strftime('%Y-%m-%d').tolist()
    vendas_diarias = df_vendas_tempo['Quantidade'].tolist()
    media_movel = df_vendas_tempo['Média_móvel'].tolist()

    option = {
        "xAxis": {
            "type": "category",
            "data": datas,
            "axisLabel": {"fontSize": 12, "color": "black"}
        },
        "yAxis": {"type": "value"},
        "axisLabel": {"fontSize": 12, "color": "black"},
        "series": [
            {"data": vendas_diarias, "type": "line", "name": "Vendas Diárias", "itemStyle": {"color": "green"}},
            {"data": media_movel, "type": "line", "name": "Média Móvel - 7 dias", "lineStyle": {"type": "dashed"}, "itemStyle": {"color": "orange"}}
        ],
        "tooltip": {
            "trigger": "axis",
        },
        "legend": {
            "data": ["Vendas Diárias", "Média Móvel - 7 dias"],
        }
    }

    return option

def pie_chart(dre):
    # Criando o gráfico de pizza
    dre_data = list(dre.items())
    pie_chart = (
        Pie()
        .add("", dre_data, radius=["40%", "75%"], 
             label_opts=opts.LabelOpts(
                 position="outside",
                 formatter="{b}: {d}%",
             ),
             center=["65%", "60%"],
             
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(title="Gráfico de Pizza da DRE"),
            legend_opts=opts.LegendOpts(
                orient="vertical",
                pos_top="15%",
                pos_left="0%",
            )
        )
    )
    
    return pie_chart

def receita():
    df_final, df_final_2022, df_transacoes, df_produtos, df_clientes = data_base()

    # 1.b. Comparar a receita entre diferentes produtos, categorias ou regiões
    df_receita_produto = df_final_2022.groupby('Nome_produto').agg({'Valor': 'sum'}).sort_values(by='Valor', ascending=False)
    df_receita_categoria = df_final_2022.groupby('Categoria').agg({'Valor': 'sum'}).sort_values(by='Valor', ascending=False)
    df_receita_bairro = df_final_2022.groupby('Bairro').agg({'Valor': 'sum'}).sort_values(by='Valor', ascending=False)

    # Selecionando os 5 produtos mais vendidos
    top_5_produtos = df_receita_produto.head(5)

    # Preparando os dados para o gráfico de barras
    produtos = top_5_produtos.index.tolist()
    receita_produtos = top_5_produtos['Valor'].tolist()

    categorias = df_receita_categoria.index.tolist()
    receita_categorias = df_receita_categoria['Valor'].tolist()

    bairros = df_receita_bairro.index.tolist()
    receita_bairros = df_receita_bairro['Valor'].tolist()
        
    c_p = (
        Bar()
        .add_xaxis(produtos)
        .add_yaxis("Receita por Produto", receita_produtos, itemstyle_opts=opts.ItemStyleOpts(color="orange"),)
        .set_global_opts(
            title_opts=opts.TitleOpts(title="Vendas por Produto"),
            yaxis_opts=opts.AxisOpts(name="Receita"),
            xaxis_opts=opts.AxisOpts(name="Produtos"),
        )
    )
    
    c_c = (
        Bar()
        .add_xaxis(categorias)
        .add_yaxis("Receita por Categoria", receita_categorias, itemstyle_opts=opts.ItemStyleOpts(color="green"),)
        .set_global_opts(
            title_opts=opts.TitleOpts(title="Vendas por Categoria"),
            yaxis_opts=opts.AxisOpts(name="Receita"),
            xaxis_opts=opts.AxisOpts(name="Categorias"),
        )
    )
    
    c_b = (
        Bar()
        .add_xaxis(bairros)
        .add_yaxis("Receita por Bairro", receita_bairros, itemstyle_opts=opts.ItemStyleOpts(color="orange"),)
        .set_global_opts(
            title_opts=opts.TitleOpts(title="Vendas por Bairro"),
            yaxis_opts=opts.AxisOpts(name="Receita"),
            xaxis_opts=opts.AxisOpts(name="Bairros"),
        )
    )
    
    return c_p, c_c, c_b

def main():
    # Título principal do aplicativo
    st.title("Análise de Vendas e Demonstração de DRE")

    # DRE
    st.header("Demonstração de Resultado do Exercício (DRE)")
    st.write("A Demonstração de Resultado do Exercício (DRE) é um relatório contábil elaborado em conjunto com o balanço patrimonial, que descreve os resultados das operações de uma empresa durante um período de tempo específico.")
    var_dre = dre()
    st.write(var_dre)

    # Gráfico de pizza da DRE
    st.header("Análise Visual da DRE")
    st.write("O gráfico abaixo apresenta uma representação visual dos diferentes componentes da Demonstração de Resultado do Exercício. Cada fatia do gráfico corresponde a uma parte da DRE, facilitando a compreensão da estrutura de receitas e despesas da empresa.")
    var_pie_chart = pie_chart(var_dre)
    st.write(st_pyecharts(var_pie_chart))
    
    # Tendências de vendas
    st.header("Tendências de Vendas ao Longo do Tempo")
    st.write("O gráfico a seguir mostra as vendas diárias ao longo do tempo no ano de 2022. A linha verde representa as vendas diárias, enquanto a linha laranja (tracejada) representa a média móvel de 7 dias, que ajuda a identificar tendências ao suavizar variações diárias.")
    option = tendencias_tempo()
    st.write(st_echarts(option, height=500))
    
    # Receita por diferentes categorias
    st.header("Análise da Receita")
    st.write("Abaixo, você encontrará três gráficos de barras que mostram a receita gerada por diferentes produtos, categorias e regiões (bairros). Essa análise ajuda a identificar quais são os produtos mais vendidos, as categorias mais populares e as regiões com maior volume de vendas.")
    
    produtos, categorias, bairros = receita()
    
    st.subheader("Receita por Produto")
    st.write("Este gráfico mostra a receita gerada pelos cinco produtos mais vendidos.")
    st.write(st_pyecharts(produtos))
    
    st.subheader("Receita por Categoria")
    st.write("Este gráfico apresenta a receita gerada por cada categoria de produto.")
    st.write(st_pyecharts(categorias))
    
    st.subheader("Receita por Bairro")
    st.write("O gráfico a seguir descreve a receita obtida em diferentes bairros.")
    st.write(st_pyecharts(bairros))
    
    

if __name__ == "__main__":
    main()
