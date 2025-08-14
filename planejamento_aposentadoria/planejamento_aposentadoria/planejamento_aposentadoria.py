import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import seaborn as sns
import streamlit as st
from bs4 import BeautifulSoup

# Configuração da página
st.set_page_config(layout="wide")  # Isso define a largura para ocupar a tela inteira


def calcular_ir(salario_mensal, aporte):
    # Cálculo do renda mensal considerando o salário bruto
    previdencia = (
        salario_mensal * (aporte / 100) if aporte < 12 else salario_mensal * 0.12
    )

    # Faixas do INSS (baseado em valores de 2025)
    faixas_inss = [(1518.00, 0.075), (2793.88, 0.09), (4190.83, 0.12), (8157.41, 0.14)]
    teto_inss = 8157.41  # Teto do INSS

    # Cálculo da contribuição mensal ao INSS
    salario_base = min(salario_mensal, teto_inss)
    inss_mensal = 0
    faixa_anterior = 0

    for faixa, aliquota in faixas_inss:
        if salario_base > faixa:
            inss_mensal += (faixa - faixa_anterior) * aliquota
        else:
            inss_mensal += (salario_base - faixa_anterior) * aliquota
            break
        faixa_anterior = faixa

    # Renda tributável
    renda_tributavel = salario_mensal - inss_mensal - previdencia
    renda_sem = salario_mensal - inss_mensal

    # Faixas do IR (2025)
    faixas_ir = [
        (2259.20, 0.0, 0),
        (2826.65, 0.075, 169.44),
        (3751.05, 0.15, 381.44),
        (4664.68, 0.225, 662.77),
        (float("inf"), 0.275, 896.00),
    ]

    def irpf(renda, faixas_ir):
        """Calcula o IRPF com base na renda e nas faixas de IR fornecidas."""

        ir = 0
        for limite, aliquota, deducao in faixas_ir:
            if renda < limite:
                ir = (renda * aliquota) - deducao
                break
            else:
                ir = (limite * aliquota) - deducao

        return ir

    ir_mensal = irpf(renda_tributavel, faixas_ir)
    ir_sem = irpf(renda_sem, faixas_ir)

    dados = {
        "Descrição": [
            "Renda Anual",
            "Desconto INSS",
            "PGBL",
            "Renda Tributável",
            "IRPF",
        ],
        "Sem PGBL": [
            salario_mensal * 13.5,
            inss_mensal * 13.5,
            0,  # Sem PGBL
            renda_sem * 13.5,
            ir_sem * 13.5,
        ],
        "Com PGBL": [
            salario_mensal * 13.5,
            inss_mensal * 13.5,
            previdencia * 13.5,
            renda_tributavel * 13.5,
            ir_mensal * 13.5,
        ],
    }

    df = pd.DataFrame(dados)

    return df


def tabela_prev(renda_mensal, aporte, taxa_anual, dirpf):
    """
    Calcula a tabela de poupança e renda passiva a cada 5 anos.

    Args:
        aporte_mensal (float): O valor do aporte mensal.
        taxa_anual (float): A taxa de juros anual (em porcentagem).
        prazo_anos (int): O prazo em anos.

    Returns:
        pandas.DataFrame: A tabela de poupança e renda passiva a cada 5 anos.
    """

    # Valor aportado no 1o mes
    taxa_aporte = aporte / 100
    renda_anual = renda_mensal * 13.5

    aporte_total = renda_anual * taxa_aporte

    aporte_1 = aporte_total if taxa_aporte < 0.12 else 0.12 * renda_anual

    dados = [
        {
            "Anos": 1,
            "Valor Aportado": aporte_1,
            "Saldo Acumulado": aporte_1,
            "Renda Passiva Anual": 0,
            "Renda Passiva Mensal": 0,
        }
    ]

    aporte_liq = aporte_1 - dirpf

    anos = list(range(2, 31))  # começa do segundo ano

    saldo_acumulado = aporte_1
    for ano in anos:
        valor_aportado = (
            aporte_1 + (ano - 1) * aporte_liq
        )  # Calcula o valor total aportado
        saldo_acumulado = aporte_1 + saldo_acumulado * (1 + taxa_anual / 100)
        if ano <= 10:
            rendimento_anual = 0
            rendimento_mensal = 0
        else:
            rendimento_anual = saldo_acumulado * taxa_anual / 100
            rendimento_mensal = rendimento_anual / 12
        dados.append(
            {
                "Anos": ano,
                "Valor Aportado": valor_aportado,
                "Saldo Acumulado": saldo_acumulado,
                "Renda Passiva Anual": rendimento_anual,
                "Renda Passiva Mensal": rendimento_mensal,
            }
        )

    df = pd.DataFrame(dados)

    return df


def tabela_inv(renda_mensal, aporte, taxa_anual, dirpf=0):
    """
    Calcula a tabela de poupança e renda passiva a cada 5 anos.

    Args:
        aporte_mensal (float): O valor do aporte mensal.
        taxa_anual (float): A taxa de juros anual (em porcentagem).
        prazo_anos (int): O prazo em anos.

    Returns:
        pandas.DataFrame: A tabela de poupança e renda passiva a cada 5 anos.
    """

    # Valor aportado no 1o mes
    taxa_aporte = aporte / 100
    renda_anual = renda_mensal * 13.5
    taxa_prev = aporte / 100 if aporte < 12 else 0.12

    if dirpf == 0:
        aporte_1 = renda_anual * taxa_aporte
    else:
        aporte_1 = renda_anual * (taxa_aporte - taxa_prev)

    dados = [
        {
            "Anos": 1,
            "Valor Aportado": aporte_1,
            "Saldo Acumulado": aporte_1,
            "Renda Passiva Anual": 0,
            "Renda Passiva Mensal": 0,
        }
    ]

    anos = list(range(2, 31))  # começa do segundo ano

    aporte_inv = aporte_1 + dirpf
    saldo_acumulado = aporte_1

    for ano in anos:
        valor_aportado = (
            aporte_1 + (ano - 1) * aporte_inv
        )  # Calcula o valor total aportado
        saldo_acumulado = aporte_inv + saldo_acumulado * (1 + taxa_anual / 100)

        rendimento_anual = saldo_acumulado * taxa_anual / 100
        rendimento_mensal = rendimento_anual / 12

        dados.append(
            {
                "Anos": ano,
                "Valor Aportado": valor_aportado,
                "Saldo Acumulado": saldo_acumulado,
                "Renda Passiva Anual": rendimento_anual,
                "Renda Passiva Mensal": rendimento_mensal,
            }
        )

    df = pd.DataFrame(dados)

    return df


def tabela_comparativa_renda(taxa_anual, anos, aportes, dirpf):
    dados = {"Anos": anos}

    for aporte in aportes:

        df_prev = tabela_prev(1, aporte, taxa_anual, dirpf)

        df_inv = tabela_inv(1, aporte, taxa_anual, dirpf)

        df_total = (
            df_prev.iloc[:, 1:] + df_inv.iloc[:, 1:]
        )  # Soma apenas da segunda coluna em diante
        df_total.insert(
            0, df_prev.columns[0], df_inv.iloc[:, 0]
        )  # Mantém a primeira coluna original

        df_total = df_total[df_total["Anos"].isin(anos)]

        dados[f"Aporte {aporte}%"] = df_total["Renda Passiva Mensal"]

    df = pd.DataFrame(dados)

    return df


def tabela_comparativa_patrimonio(taxa_anual, anos, aportes, dirpf):
    dados = {"Anos": anos}

    for aporte in aportes:

        df_prev = tabela_prev(1, aporte, taxa_anual, dirpf)

        df_inv = tabela_inv(1, aporte, taxa_anual, dirpf)

        df_total = (
            df_prev.iloc[:, 1:] + df_inv.iloc[:, 1:]
        )  # Soma apenas da segunda coluna em diante
        df_total.insert(
            0, df_prev.columns[0], df_inv.iloc[:, 0]
        )  # Mantém a primeira coluna original

        df_total = df_total[df_total["Anos"].isin(anos)]

        dados[f"Aporte {aporte}%"] = df_total["Saldo Acumulado"]

    df = pd.DataFrame(dados)

    return df


def calcular_aporte(renda_mensal, aporte):
    dados = []

    renda_anual = 13.5 * renda_mensal
    aporte_total = renda_anual * aporte / 100
    aporte_prev = aporte_total if aporte < 12 else renda_anual * 0.12

    df = calcular_ir(renda_mensal, aporte)

    irpf_com_previdencia = df.loc[df["Descrição"] == "IRPF", "Com PGBL"].values[
        0
    ]
    irpf_sem_previdencia = df.loc[df["Descrição"] == "IRPF", "Sem PGBL"].values[
        0
    ]

    diff_irpf = float(irpf_sem_previdencia) - float(irpf_com_previdencia)

    aporte_inv = aporte_total - aporte_prev

    dados.append(
        {
            "Ano": 1,
            "Aporte PGBL": aporte_prev,
            "Aporte Investimentos": aporte_inv,
            "Total": aporte_total,
        }
    )

    aporte_prev = aporte_prev - diff_irpf
    aporte_inv = aporte_total - aporte_prev

    dados.append(
        {
            "Ano": 2,
            "Aporte PGBL": aporte_prev,
            "Aporte Investimentos": aporte_inv,
            "Total": aporte_total,
        }
    )

    df = pd.DataFrame(dados)

    return df


def adicionar_linha():
    """Adiciona um espaço entre os frames no Streamlit com uma linha dupla laranja."""
    st.markdown(
        """
        <div style="border-top: 2px double orange; margin-top: 20px; margin-bottom: 20px;"></div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(" ")


def formatar_reais(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def tabela_html(df, tipo=None):
    """Converte um DataFrame numa tabela em html"""
    if tipo == 1:
        for col in df.columns[1:]:
            df[col] = df[col].apply(lambda x: f"{x:.2%}")
    elif tipo == 2:
        for col in df.columns[1:]:
            df[col] = df[col].apply(lambda x: f"{int(x)}")
    else:
        for col in df.columns[1:]:
            df[col] = df[col].apply(formatar_reais)

    html = df.to_html(index=False)
    # Analisa e modifica o HTML
    soup = BeautifulSoup(html, "html.parser")

    for cell in soup.find_all("th"):
        cell["style"] = "text-align: center;"

    # Exibe o HTML modificado
    return soup


def usufruto(renda_mensal, taxa_anual, df):

    def anos_usufruto(valor, renda_mensal, taxa_mensal):
        n = 0
        valor = valor - renda_mensal
        max_iteracoes = 1500  # Limite de iterações
        iteracoes = 0
        while valor > 0 and iteracoes < max_iteracoes:
            valor = valor * (1 + taxa_mensal) - renda_mensal
            n += 1
            iteracoes += 1
        if iteracoes == max_iteracoes:
            print("Aviso: loop atingiu o limite de iterações.")
        return n

    taxa_mensal = (1 + taxa_anual / 100) ** (1 / 12) - 1

    df = df[["Anos", "Saldo Acumulado"]]
    df["Meses de Usufruto"] = df["Saldo Acumulado"].apply(
        anos_usufruto, args=(renda_mensal, taxa_mensal)
    )
    df["Anos de Usufruto"] = df["Meses de Usufruto"].apply(lambda x: x / 12)

    return df


def criar_heatmap(dataframe, tipo):
    """Cria um heatmap onde a primeira coluna é o índice (y) e as colunas restantes são os valores (x)."""
    dataframe = dataframe.set_index(
        dataframe.columns[0]
    )  # Define a primeira coluna como índice
    if tipo == 1:
        tipo_fmt = ".1%"
        tipo_vmin = -2
    elif tipo == 2:
        dataframe = dataframe.round().astype(int)
        tipo_fmt = "d"
        tipo_vmin = -200
    plt.figure(figsize=(10, 8))
    sns.heatmap(
        dataframe,
        annot=True,
        cmap="Blues",
        fmt=tipo_fmt,
        vmin=tipo_vmin,
        vmax=dataframe.max().max(),
    )
    st.pyplot(plt)


def main():
    st.markdown("""
        <style>
            /* Carregar a fonte do Google Fonts */
            @import url('https://fonts.googleapis.com/css2?family=Roboto+Mono&display=swap');
            
            /* Aplicar a fonte globalmente em todo o corpo da página */
            * {
                font-size: 20px;  /* Tamanho maior para os títulos */
            }
            
            /* Definir tamanho da fonte para o corpo do texto */
            body {
                font-size: 16px;  /* Ajuste o tamanho conforme necessário */
            }

            /* Ajuste do tamanho para títulos */
            h1, h2, h3, h4, h5, h6 {
                font-size: 28px;  /* Tamanho maior para os títulos */
            }

            /* Ajustar as tabelas */
            .stDataFrame {
                font-size: 22px; /* Tamanho da fonte para os dados da tabela */
            }

            /* Ajustes para caixa de texto ou elementos específicos */
            .st-bv {
                font-size: 24px; /* Ajuste o tamanho conforme necessário */
            }
        </style>
    """, unsafe_allow_html=True)
    
    # --- Definindo o Cabeçalho -----------------------------------------------------------------------

    st.title("Calculadora de Poupança e Renda")

    adicionar_linha()

    st.write("Defina os parâmetro iniciais")

    # Adicione aqui a lógica para a estratégia agressiva

    col1, col2, col3 = st.columns(3)  # Divide a tela em colunas

    with col1:
        renda_mensal = st.number_input(
            "Renda Mensal (R$) ", min_value=1, value=6000, step=100
        )

    with col2:
        aporte = st.number_input("Aporte (%)", min_value=0, value=12, step=1)

    with col3:
        taxa_anual = st.number_input("Taxa de Juros Anual (%)", min_value=1, value=10)

    adicionar_linha()

    st.write("Escolha sua estratégia")

    # Botões de estratégia
    estrat1, estrat2, estrat3 = st.columns(3)

    with estrat1:
        botao_conservador = st.button("Estratégia Conservadora")

    with estrat2:
        botao_moderado = st.button("Estratégia Moderada")

    with estrat3:
        botao_agressivo = st.button("Estratégia Agressiva")

    # adicionar_linha()
    st.write("")


    # Lógica dos botões (fora das colunas)
    if botao_conservador:
        st.write(
            "<h3 style='text-align: center;'><font color='orange'>Estratégia Conservadora</font></h3>",
            unsafe_allow_html=True,
        )

        # --- Calcula o IRPF ------------------------------------------------------------------------
        # adicionar_linha()
        st.write("")

        aporte_mensal = renda_mensal * aporte / 100
        aporte_anual = aporte_mensal * 13.5
        taxa_aporte = aporte / 100

        dados = [
            {
                "Renda Mensal": renda_mensal,
                "Aporte Mensal": aporte_mensal,
                "Aporte Anual": aporte_anual,
            }
        ]

        df = pd.DataFrame(dados)
        df["Renda Mensal"] = df["Renda Mensal"].apply(formatar_reais)

        # converte em uma tabela html e publica
        tabela = tabela_html(df)
        st.markdown("<h3>Valor dos Aportes</h3>", unsafe_allow_html=True)
        st.write(str(tabela), unsafe_allow_html=True)

        # --- Calcula as tabelas com os aportes em previdência e investimentos ----------------------
        adicionar_linha()

        df_inv = tabela_inv(renda_mensal, aporte, taxa_anual)

        df = df_inv[df_inv["Anos"].isin([5, 10, 15, 20, 25, 30])]

        # converte em uma tabela html e publica
        tabela = tabela_html(df)
        st.markdown("<h3>Resultado</h3>", unsafe_allow_html=True)
        st.write(str(tabela), unsafe_allow_html=True)

        # ---  Gráfico de barras com o patrimônio dividido entre previdência e investimentos ----------
        adicionar_linha()

        df = df_inv
        blues_palette = sns.color_palette("Blues")

        fig = go.Figure(
            data=[
                go.Bar(
                    name="Valor Aportado",
                    x=df["Anos"],
                    y=df["Valor Aportado"],
                    marker=dict(color="orange"),  # Define a cor da barra
                    hovertemplate="Ano: %{x}<br>Valor Aportado: R$ %{y:,.2f}<extra></extra>",
                ),
                go.Bar(
                    name="Rendimentos",
                    x=df["Anos"],
                    y=df["Saldo Acumulado"] - df["Valor Aportado"],
                    marker=dict(color="blue"),  # Define a cor da barra
                    hovertemplate="Ano: %{x}<br>Rendimentos: R$ %{y:,.2f}<extra></extra>",
                ),
            ]
        )
        st.markdown("<h3>Patrimônio Acumulado</h3>", unsafe_allow_html=True)
        fig.update_layout(
            barmode="stack",
            # title="Saldo Acumulado",
            xaxis_title="Prazo (Anos)",
            yaxis_title="Valor (R$)",
        )
        st.plotly_chart(fig)

        # --- Tabela de sensibilidade --------------------------------------------------------------------
        adicionar_linha()

        anos = [5, 10, 15, 20, 25, 30]
        aportes = [5, 10, 15, 20]
        dados = {"Anos": anos}

        for aporte in aportes:

            df_inv = tabela_inv(1, aporte, taxa_anual)

            df_inv = df_inv[df_inv["Anos"].isin(anos)]

            dados[f"Aporte {aporte}%"] = df_inv["Renda Passiva Mensal"]

        df = pd.DataFrame(dados)
        st.markdown(
            "<h3>Aporte Mensal (%) x Renda Passiva Mensal (%)</h3>",
            unsafe_allow_html=True,
        )
        criar_heatmap(df, tipo=1)

        # # converte em uma tabela html e publica
        # tabela = tabela_html(df, tipo=1)
        # st.write("Aporte Mensal (% do renda) x Renda Passiva Mensal (% do salário)",
        #     str(tabela), unsafe_allow_html=True)

        # --- Tabela de sensibilidade --------------------------------------------------------------------
        adicionar_linha()

        anos = [5, 10, 15, 20, 25, 30]
        aportes = [10, 12, 15, 20, 25, 30]
        dados = {"Anos": anos}

        for aporte in aportes:

            df_inv = tabela_inv(renda_mensal=1, aporte=aporte, taxa_anual=taxa_anual)

            df_inv = df_inv[df_inv["Anos"].isin(anos)]

            dados[f"Aporte {aporte}%"] = df_inv["Saldo Acumulado"]

        df = pd.DataFrame(dados)
        st.markdown("<h3>Aporte Mensal (%) x Patrimônio</h3>", unsafe_allow_html=True)
        criar_heatmap(df, tipo=2)

        # # converte em uma tabela html e publica
        # tabela = tabela_html(df, tipo = 2)
        # st.markdown("<h3>Aporte Mensal (%) x Patrimônio</h3>", unsafe_allow_html=True)
        # st.write(str(tabela), unsafe_allow_html=True)

        #  # --- Fase de usufruto -----------------------------------------------------------------------
        # adicionar_linha()

        # df_inv = tabela_inv(renda_mensal, 100*taxa_aporte, taxa_anual)

        # df = usufruto(renda_mensal, taxa_anual, df_inv)
        # df = df[df["Anos"].isin([5, 10, 15, 16, 17, 18, 19, 20])]
        # df["Saldo Acumulado"] = df["Saldo Acumulado"].apply(formatar_reais)

        # for col in df.columns[2:]:
        #     df[col] = df[col].apply(lambda x: f"{int(x)}")

        # html = df.to_html(index=False)

        # # Analisa e modifica o HTML
        # soup = BeautifulSoup(html, "html.parser")

        # for cell in soup.find_all("th"):
        #     cell["style"] = "text-align: center;"

        # # converte em uma tabela html e publica
        # st.write(str(soup), unsafe_allow_html=True)

        # Adiciona estilo CSS para centralizar os dados das tabelas ----------------------------------
        adicionar_linha()
        st.markdown(
            """
            <style>
                table {
                    width: 100%;
                }
                table thead th, table td {
                    text-align: center;
                }
            </style>
            """,
            unsafe_allow_html=True,
        )

    if botao_moderado:
        st.write(
            "<h3 style='text-align: center;'><font color='orange'>Estratégia Moderada</font></h3>",
            unsafe_allow_html=True,
        )

        # --- Calcula o IRPF ------------------------------------------------------------------------
        # adicionar_linha()
        st.write("")
        taxa_aporte = aporte / 100

        df = calcular_ir(renda_mensal, aporte)

        irpf_com_previdencia = df.loc[
            df["Descrição"] == "IRPF", "Com PGBL"
        ].values[0]
        irpf_sem_previdencia = df.loc[
            df["Descrição"] == "IRPF", "Sem PGBL"
        ].values[0]

        dirpf = float(irpf_sem_previdencia) - float(irpf_com_previdencia)
        diff_irpf = formatar_reais(dirpf)

        # converte em uma tabela html e publica
        tabela = tabela_html(df)
        st.markdown(
            f"<h3>Cálculo do IRPF para renda mensal de {formatar_reais(renda_mensal)}.</h3>",
            unsafe_allow_html=True,
        )
        st.write(
            str(tabela), f"A diferença de IRPF é {diff_irpf}.", unsafe_allow_html=True
        )

        # --- Calcula o renda anual, Aporte Anual e Aporte mensal -----------------------------------
        adicionar_linha()

        renda_anual = renda_mensal * 13.5
        aporte_total = renda_anual * taxa_aporte
        aporte_prev = aporte_total if aporte < 12 else renda_anual * 0.12
        diff_irpf = float(irpf_sem_previdencia) - float(irpf_com_previdencia)

        aporte_liq = aporte_prev - diff_irpf

        dados = [
            {
                "Renda Anual": renda_anual,
                "Aporte 1o Ano": aporte_prev,
                "Aporte 2o Ano": aporte_liq,
            }
        ]

        df = pd.DataFrame(dados)
        df["Renda Anual"] = df["Renda Anual"].apply(formatar_reais)

        # converte em uma tabela html e publica
        tabela = tabela_html(df)
        st.markdown("<h3>Valor dos Aportes</h3>", unsafe_allow_html=True)
        st.write(str(tabela), unsafe_allow_html=True)

        # --- Calcula as tabelas com os aportes em previdência e investimentos ----------------------
        adicionar_linha()

        df_prev = tabela_prev(renda_mensal, aporte, taxa_anual, dirpf)

        df = df_prev[df_prev["Anos"].isin([5, 10, 15, 20, 25, 30])]

        # converte em uma tabela html e publica
        tabela = tabela_html(df)
        st.markdown("<h3>Resultado</h3>", unsafe_allow_html=True)
        st.write(str(tabela), unsafe_allow_html=True)

        # ---  Gráfico de barras com o patrimônio dividido entre previdência e investimentos ----------
        adicionar_linha()

        df = df_prev

        fig = go.Figure(
            data=[
                go.Bar(
                    name="Valor Aportado",
                    x=df["Anos"],
                    y=df["Valor Aportado"],
                    marker=dict(color="orange"),  # Define a cor da barra
                    hovertemplate="Ano: %{x}<br>Valor Aportado: R$ %{y:,.2f}<extra></extra>",
                ),
                go.Bar(
                    name="Rendimentos",
                    x=df["Anos"],
                    y=df["Saldo Acumulado"] - df["Valor Aportado"],
                    marker=dict(color="blue"),  # Define a cor da barra
                    hovertemplate="Ano: %{x}<br>Rendimentos: R$ %{y:,.2f}<extra></extra>",
                ),
            ]
        )
        st.markdown("<h3>Patrimônio Acumulado</h3>", unsafe_allow_html=True)
        fig.update_layout(
            barmode="stack",
            # title="Saldo Acumulado",
            xaxis_title="Prazo (Anos)",
            yaxis_title="Valor (R$)",
        )
        st.plotly_chart(fig)

        # --- Tabela de sensibilidade --------------------------------------------------------------------
        adicionar_linha()

        anos = [11, 12, 15, 20, 25, 30]
        aportes = [5, 8, 10, 12]
        dados = {"Anos": anos}

        for aporte in aportes:

            df_inv = tabela_prev(1, aporte, taxa_anual, dirpf)

            df_inv = df_inv[df_inv["Anos"].isin(anos)]

            dados[f"Aporte {aporte}%"] = df_inv["Renda Passiva Mensal"]

        df = pd.DataFrame(dados)
        st.markdown(
            "<h3>Aporte Mensal (%) x Renda Passiva Mensal (%)</h3>",
            unsafe_allow_html=True,
        )
        criar_heatmap(df, tipo=1)

        # # converte em uma tabela html e publica
        # tabela = tabela_html(df, tipo=1)
        # st.markdown("<h3>Aporte Mensal (%) x Renda Passiva Mensal (%)</h3>", unsafe_allow_html=True)
        # st.write(str(tabela), unsafe_allow_html=True)

        # --- Tabela de sensibilidade --------------------------------------------------------------------
        adicionar_linha()

        anos = [11, 12, 15, 20, 25, 30]
        aportes = [5, 8, 10, 12]
        dados = {"Anos": anos}

        for aporte in aportes:

            df_inv = tabela_prev(1, aporte, taxa_anual, dirpf)

            df_inv = df_inv[df_inv["Anos"].isin(anos)]

            dados[f"Aporte {aporte}%"] = df_inv["Saldo Acumulado"]

        df = pd.DataFrame(dados)
        st.markdown(
            "<h3>Aporte Mensal (%) x Patrimônio (em renda mensal)</h3>",
            unsafe_allow_html=True,
        )
        criar_heatmap(df, tipo=2)

        # converte em uma tabela html e publica
        # tabela = tabela_html(df, tipo = 2)
        # st.markdown("<h3>Aporte Mensal (%) x Patrimônio (em renda mensal)</h3>", unsafe_allow_html=True)
        # st.write(str(tabela), unsafe_allow_html=True)

        # Adiciona estilo CSS para centralizar os dados das tabelas ----------------------------------
        adicionar_linha()
        st.markdown(
            """
            <style>
                table {
                    width: 100%;
                }
                table thead th, table td {
                    text-align: center;
                }
            </style>
            """,
            unsafe_allow_html=True,
        )

    if botao_agressivo:
        st.write(
            "<h3 style='text-align: center;'><font color='orange'>Estratégia Agressiva</font></h3>",
            unsafe_allow_html=True,
        )

        # --- Calcula o IRPF ------------------------------------------------------------------------
        # adicionar_linha()
        st.write("")

        df = calcular_ir(renda_mensal, aporte)

        irpf_com_previdencia = df.loc[
            df["Descrição"] == "IRPF", "Com PGBL"
        ].values[0]
        irpf_sem_previdencia = df.loc[
            df["Descrição"] == "IRPF", "Sem PGBL"
        ].values[0]

        dirpf = float(irpf_sem_previdencia) - float(irpf_com_previdencia)
        diff_irpf = formatar_reais(dirpf)

        # converte em uma tabela html e publica
        tabela = tabela_html(df)
        st.markdown(
            f"<h3>Cálculo do IRPF para renda mensal de {formatar_reais(renda_mensal)}.</h3>",
            unsafe_allow_html=True,
        )
        st.write(
            str(tabela), f"A diferença de IRPF é {diff_irpf}.", unsafe_allow_html=True
        )

        # --- Calcula o renda anual, Aporte Anual e Aporte mensal -----------------------------------
        adicionar_linha()

        df = calcular_aporte(renda_mensal, aporte)

        # converte em uma tabela html e publica
        tabela = tabela_html(df)
        st.markdown("<h3>Valor dos Aportes</h3>", unsafe_allow_html=True)
        st.write(str(tabela), unsafe_allow_html=True)

        # --- Calcula as tabelas com os aportes em previdência e investimentos ----------------------
        adicionar_linha()

        st.markdown("<h3>Aportes em PGBL</h3>", unsafe_allow_html=True)
        df_prev = tabela_prev(renda_mensal, aporte, taxa_anual, dirpf)

        df = df_prev[df_prev["Anos"].isin([5, 10, 15, 20, 25, 30])]

        # converte em uma tabela html e publica
        tabela = tabela_html(df)
        st.write(str(tabela), unsafe_allow_html=True)

        st.markdown("<h3>Aportes em outros investimentos</h3>", unsafe_allow_html=True)
        df_inv = tabela_inv(renda_mensal, aporte, taxa_anual, dirpf)

        df = df_inv[df_inv["Anos"].isin([5, 10, 15, 20, 25, 30])]

        # converte em uma tabela html e publica
        tabela = tabela_html(df)
        st.write(str(tabela), unsafe_allow_html=True)

        # --- Exibe a tabela com os valores agregados ------------------------------------------------
        adicionar_linha()

        # juntando os dados df_prev e df_inv
        df_total = (
            df_prev.iloc[:, 1:] + df_inv.iloc[:, 1:]
        )  # Soma apenas da segunda coluna em diante
        df_total.insert(
            0, df_prev.columns[0], df_inv.iloc[:, 0]
        )  # Mantém a primeira coluna original

        df = df_total[df_total["Anos"].isin([5, 10, 15, 20, 25, 30])]

        # converte em uma tabela html e publica
        tabela = tabela_html(df)

        st.markdown("<h3>Resultado</h3>", unsafe_allow_html=True)
        st.write(str(tabela), unsafe_allow_html=True)

        # ---  Gráfico de barras com o patrimônio dividido entre previdência e investimentos ----------
        adicionar_linha()

        fig = go.Figure(
            data=[
                go.Bar(
                    name="PGBL",
                    x=df_prev["Anos"],
                    y=df_prev["Saldo Acumulado"],
                    marker=dict(color="orange"),  # Define a cor da barra
                    hovertemplate="Ano: %{x}<br>Previdência: R$ %{y:,.2f}<extra></extra>",
                ),
                go.Bar(
                    name="Investimentos",
                    x=df_inv["Anos"],
                    y=df_inv["Saldo Acumulado"],
                    marker=dict(color="blue"),  # Define a cor da barra
                    hovertemplate="Ano: %{x}<br>Investimentos: R$ %{y:,.2f}<extra></extra>",
                ),
            ]
        )
        st.markdown("<h3>Patrimônio Acumulado</h3>", unsafe_allow_html=True)
        fig.update_layout(
            barmode="stack",
            # title="Saldo Acumulado",
            xaxis_title="Prazo (Anos)",
            yaxis_title="Valor (R$)",
        )
        st.plotly_chart(fig)

        # --- Tabela de sensibilidade --------------------------------------------------------------------
        adicionar_linha()

        anos = [5, 10, 15, 20, 25, 30]
        aportes = [10, 12, 15, 20, 25, 30]

        df = tabela_comparativa_renda(taxa_anual, anos, aportes, dirpf / renda_mensal)

        st.markdown(
            "<h3>Aporte Mensal (%) x Renda Passiva Mensal (%)</h3>",
            unsafe_allow_html=True,
        )
        criar_heatmap(df, tipo=1)

        # converte em uma tabela html e publica
        # tabela = tabela_html(df, tipo = 1)
        # st.write("Aporte Mensal (% do renda) x Renda Passiva Mensal (% do salário)",
        #     str(tabela), unsafe_allow_html=True)

        # --- Tabela de sensibilidade --------------------------------------------------------------------
        adicionar_linha()

        anos = [5, 10, 15, 20, 25, 30]
        aportes = [10, 12, 15, 20,  25, 30]

        df = tabela_comparativa_patrimonio(
            taxa_anual, anos, aportes, dirpf / renda_mensal
        )

        st.markdown(
            "<h3>Aporte Mensal (%) x Patrimônio (em renda mensal)</h3>",
            unsafe_allow_html=True,
        )
        criar_heatmap(df, tipo=2)

        # converte em uma tabela html e publica
        # tabela = tabela_html(df, tipo = 2)
        # st.write("Aporte Mensal (% do salário) x Patrimônio (em salários mensais)",
        #     str(tabela), unsafe_allow_html=True)

        # --- Fase de usufruto -----------------------------------------------------------------------
        adicionar_linha()

        df = usufruto(renda_mensal, taxa_anual, df_total)
        df = df[df["Anos"].isin([5, 10, 15, 16, 17, 18, 19, 20])]
        df["Saldo Acumulado"] = df["Saldo Acumulado"].apply(formatar_reais)

        for col in df.columns[2:]:
            df[col] = df[col].apply(lambda x: f"{int(x)}")

        html = df.to_html(index=False)

        # Analisa e modifica o HTML
        soup = BeautifulSoup(html, "html.parser")

        for cell in soup.find_all("th"):
            cell["style"] = "text-align: center;"

        # converte em uma tabela html e publica
        st.markdown("<h3>Usufruto em meses ou anos</h3>", unsafe_allow_html=True)
        st.write(str(soup), unsafe_allow_html=True)
        
        # Centraliza os cabeçalhos
        for cell in soup.find_all("th"):
            cell["style"] = "text-align: center; font-size: 12px;"

        # Aplica estilos na tabela
        table_style = """
            <style>
                .custom-table {
                    font-size: 12px;
                    width: 100%;
                    max-width: 100%;
                    overflow-x: auto;
                    display: block;
                }
                .custom-table table {
                    width: 100%;
                    border-collapse: collapse;
                }
                .custom-table th, .custom-table td {
                    padding: 5px;
                    text-align: center;
                }
            </style>
        """

        # Publica a tabela com estilos no Streamlit
        st.markdown("<h3>Usufruto em meses ou anos</h3>", unsafe_allow_html=True)
        st.markdown(table_style + f'<div class="custom-table">{soup}</div>', unsafe_allow_html=True)


        # Adiciona estilo CSS para centralizar os dados das tabelas ----------------------------------
        adicionar_linha()
        st.markdown(
            """
            <style>
                table {
                    width: 100%;
                }
                table thead th, table td {
                    text-align: center;
                }
            </style>
            """,
            unsafe_allow_html=True,
        )


if __name__ == "__main__":
    main()
