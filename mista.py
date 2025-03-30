import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from bs4 import BeautifulSoup


def calcular_fv(aporte_mensal, taxa_anual, prazo_anos):
    """
    Calcula o valor futuro de uma anuidade.

    Args:
        aporte_mensal (float): O valor do aporte mensal.
        taxa_anual (float): A taxa de juros anual (em porcentagem).
        prazo_anos (int): O prazo em anos.

    Returns:
        float: O valor futuro da anuidade.
    """

    taxa_mensal = (1 + taxa_anual / 100) ** (1 / 12) - 1
    prazo_meses = prazo_anos * 12
    return aporte_mensal * (((1 + taxa_mensal) ** prazo_meses - 1) / taxa_mensal)


def calcular_renda_passiva_anual(aporte_mensal, taxa_anual):
    """
    Calcula a renda passiva anual até 30 anos.

    Args:
        aporte_mensal (float): O valor do aporte mensal.
        taxa_anual (float): A taxa de juros anual (em porcentagem).

    Returns:
        pandas.DataFrame: A tabela com a renda passiva anual.
    """

    anos = list(range(1, 31))
    renda_passiva = []
    for ano in anos:
        saldo_acumulado = calcular_fv(aporte_mensal, taxa_anual, ano)
        rendimento_mensal = saldo_acumulado * ((1 + taxa_anual / 100) ** (1 / 12) - 1)
        renda_passiva.append(rendimento_mensal * 12)  # Renda passiva anual

    df = pd.DataFrame({"Ano": anos, "Renda Passiva Anual": renda_passiva})
    return df


def calcular_renda_passiva_mensal(aporte_mensal, taxa_anual, anos):
    renda_mensal = []
    for ano in anos:
        saldo_acumulado = calcular_fv(aporte_mensal, taxa_anual, ano)
        rendimento_mensal = saldo_acumulado * ((1 + taxa_anual / 100) ** (1 / 12) - 1)
        renda_mensal.append(rendimento_mensal)  # Renda passiva mensal
    return pd.DataFrame({"Ano": anos, "Renda Passiva Mensal": renda_mensal})


def calcular_saldo_anual(aporte_mensal, taxa_anual):
    """
    Calcula o saldo acumulado anual até 30 anos.

    Args:
        aporte_mensal (float): O valor do aporte mensal.
        taxa_anual (float): A taxa de juros anual (em porcentagem).

    Returns:
        pandas.DataFrame: A tabela com o saldo acumulado anual.
    """

    anos = list(range(1, 31))
    saldo_acumulado = []
    for ano in anos:
        saldo_acumulado.append(calcular_fv(aporte_mensal, taxa_anual, ano))

    df = pd.DataFrame({"Ano": anos, "Saldo Acumulado": saldo_acumulado})
    return df


def calcular_tabela_prev(ganho, aporte, taxa_anual):
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
    aporte_1 = ganho * 13 * aporte / 100

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
    aporte_liq = aporte_1 * (1 - 0.275)
    saldo_acumulado = aporte_1
    for ano in anos:
        valor_aportado = (
            aporte_1 + (ano - 1) * aporte_liq
        )  # Calcula o valor total aportado
        saldo_acumulado = aporte_1 + saldo_acumulado * (1 + taxa_anual / 100)
        if ano < 10:
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

    if aporte >= 1:
        for col in [
            "Valor Aportado",
            "Saldo Acumulado",
            "Renda Passiva Anual",
            "Renda Passiva Mensal",
        ]:
            df[col] = df[col].apply(lambda x: f"R$ {x:,.2f}")
    else:
        df["Renda Passiva Mensal"] = df["Renda Passiva Mensal"].apply(
            lambda x: f"{x:.2%}"
        )

    return df


def calcular_tabela_inv(ganho_mensal, aporte, taxa_anual):
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
    aporte_1 = ganho_mensal * 13 * (aporte / 100 - 0.12)

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
    aporte_liq = ganho_mensal * 13 * (aporte / 100 - 0.12 * (1 - 0.275))
    saldo_acumulado = aporte_1
    for ano in anos:
        valor_aportado = (
            aporte_1 + (ano - 1) * aporte_liq
        )  # Calcula o valor total aportado
        saldo_acumulado = aporte_liq + saldo_acumulado * (1 + taxa_anual / 100)
        if ano < 0:
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

    if aporte >= 1:
        for col in [
            "Valor Aportado",
            "Saldo Acumulado",
            "Renda Passiva Anual",
            "Renda Passiva Mensal",
        ]:
            df[col] = df[col].apply(lambda x: f"R$ {x:,.2f}")
    else:
        df["Renda Passiva Mensal"] = df["Renda Passiva Mensal"].apply(
            lambda x: f"{x:.2%}"
        )

    return df


def calcular_tabela_comparativa_renda(taxa_anual):
    anos = [5, 10, 15, 20, 25, 30]
    dados = {"Anos": anos}
    for aporte in [0.1, 0.12, 0.15, 0.20]:
        df_prev = calcular_tabela_prev(1, 12, taxa_anual)
        df_inv = calcular_tabela_inv(1, 12, taxa_anual)

        df_prev = df_prev[["Anos", "Renda Passiva Mensal"]].apply(converter_reais)
        df_inv = df_inv[["Anos", "Renda Passiva Mensal"]].apply(converter_reais)

        df_total = (
            df_prev.iloc[:, 1:] + df_inv.iloc[:, 1:]
        )  # Soma apenas da segunda coluna em diante
        df_total.insert(
            0, df_prev.columns[0], df_inv.iloc[:, 0]
        )  # Mantém a primeira coluna original

        df_total = df_total[df_total["Anos"].isin([5, 10, 15, 20, 25, 30])]

        dados[f"Aporte {aporte * 100}%"] = df_total.apply(lambda x: f"{x:.2%}")

    df = pd.DataFrame(dados)

    return df


def calcular_tabela_comparativa_patrimonio(taxa_anual):
    anos = [5, 10, 15, 20, 25, 30]
    dados = {"Anos": anos}
    for aporte in [0.08, 0.10, 0.12]:
        patrimonio = [calcular_fv(aporte, taxa_anual, ano) for ano in anos]
        dados[f"Aporte {aporte * 100}%"] = patrimonio
    df = pd.DataFrame(dados)
    for col in df.columns[1:]:
        df[col] = df[col].apply(lambda x: f"{int(x)}")
    return df


def calcular_aporte(ganho_mensal, aporte):
    dados = []

    ganho_anual = 13 * ganho_mensal
    aporte_total = ganho_anual * aporte / 100
    aporte_prev = ganho_anual * 0.12
    aporte_inv = aporte_total - aporte_prev
    aporte_mensal = aporte_total * (1 - 0.275)

    dados.append(
        {
            "Ano": 1,
            "Aporte Previdência": aporte_prev,
            "Aporte Investimentos": aporte_inv,
            "Total": aporte_total,
        }
    )
    dados.append(
        {
            "Ano": 2,
            "Aporte Previdência": aporte_prev * (1 - 0.275),
            "Aporte Investimentos": aporte_total - aporte_prev * (1 - 0.275),
            "Total": aporte_total,
        }
    )

    df = pd.DataFrame(dados)

    for col in df.columns[1:]:
        df[col] = df[col].apply(lambda x: f"R$ {x:,.2f}")

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


def converter_reais(valor):
    if isinstance(valor, str):  # Verifica se é string
        return float(valor.replace("R$", "").replace(",", "").strip())
    return valor  # Retorna o valor original se não for string


def formatar_reais(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def main():
    st.title("Calculadora de Poupança e Renda")

    col1, col2, col3 = st.columns(3)  # Divide a tela em duas colunas

    with col1:
        ganho_mensal = st.number_input(
            "Salário (R$) ", min_value=1, value=5000, step=100
        )

    with col2:
        aporte = st.number_input("Aporte (%)", min_value=1, value=15, step=1)

    with col3:
        taxa_anual = st.number_input("Taxa de Juros Anual (%)", min_value=1, value=10)

    if st.button("Calcular"):
        adicionar_linha()  # -------------------------------------------------------------------------

        # --- Calcula o Ganho anual, Aporte Anual e Aporte mensal

        tabela = calcular_aporte(ganho_mensal, aporte)
        html = tabela.to_html(index=False)
        # Analisa e modifica o HTML
        soup = BeautifulSoup(html, "html.parser")

        for cell in soup.find_all("th"):
            cell["style"] = "text-align: center;"

        # Exibe o HTML modificado
        st.write(str(soup), unsafe_allow_html=True)

        adicionar_linha()  # -------------------------------------------------------------------------

        # --- Calcula a tabela com os valores aportados e o saldo acumulado

        st.write("Previdência")
        tabela = calcular_tabela_prev(ganho_mensal, 12, taxa_anual)
        df_prev = tabela

        tabela = tabela[tabela["Anos"].isin([5, 10, 15, 20, 25, 30])]

        # Remove o índice ao exibir a tabela
        html = tabela.to_html(index=False)
        html = (
            f'<div style="font-size: 16px;">{html}</div>'  # Aumenta o tamanho da fonte
        )

        # Analisa e modifica o HTML
        soup = BeautifulSoup(html, "html.parser")

        for cell in soup.find_all("th"):
            cell["style"] = "text-align: center;"

        # Exibe o HTML modificado
        st.write(str(soup), unsafe_allow_html=True)

        # adicionar_linha() #-------------------------------------------------------------------------

        st.write("Investimentos")
        tabela = calcular_tabela_inv(ganho_mensal, aporte, taxa_anual)
        df_inv = tabela

        tabela = tabela[tabela["Anos"].isin([5, 10, 15, 20, 25, 30])]

        # Remove o índice ao exibir a tabela
        html = tabela.to_html(index=False)
        html = (
            f'<div style="font-size: 16px;">{html}</div>'  # Aumenta o tamanho da fonte
        )

        # Analisa e modifica o HTML
        soup = BeautifulSoup(html, "html.parser")

        for cell in soup.find_all("th"):
            cell["style"] = "text-align: center;"

        # Exibe o HTML modificado
        st.write(str(soup), unsafe_allow_html=True)

        adicionar_linha()  # -------------------------------------------------------------------------

        for col in df_prev.columns[1:]:
            df_prev[col] = df_prev[col].apply(converter_reais)
            df_inv[col] = df_inv[col].apply(converter_reais)

        df_total = (
            df_prev.iloc[:, 1:] + df_inv.iloc[:, 1:]
        )  # Soma apenas da segunda coluna em diante
        df_total.insert(
            0, df_prev.columns[0], df_inv.iloc[:, 0]
        )  # Mantém a primeira coluna original

        tabela = df_total[df_total["Anos"].isin([5, 10, 15, 20, 25, 30])]

        for col in tabela.columns[1:]:
            tabela[col] = tabela[col].apply(formatar_reais)

        # Remove o índice ao exibir a tabela
        html = tabela.to_html(index=False)
        html = (
            f'<div style="font-size: 16px;">{html}</div>'  # Aumenta o tamanho da fonte
        )

        # Analisa e modifica o HTML
        soup = BeautifulSoup(html, "html.parser")

        for cell in soup.find_all("th"):
            cell["style"] = "text-align: center;"

        # Exibe o HTML modificado
        st.write(str(soup), unsafe_allow_html=True)

        adicionar_linha()  # -------------------------------------------------------------------------

        # ---  Gráfico de barras com o valor aportado e o rendimento

        fig = go.Figure(
            data=[
                go.Bar(
                    name="Previdência",
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

        fig.update_layout(
            barmode="stack",
            title="Saldo Acumulado",
            xaxis_title="Prazo (Anos)",
            yaxis_title="Valor (R$)",
        )
        st.plotly_chart(fig)

        adicionar_linha()  # -------------------------------------------------------------------------

        tabela_comparativa = calcular_tabela_comparativa_renda(taxa_anual)

        # Remove o índice ao exibir a tabela
        html = tabela_comparativa.to_html(index=False)
        html = (
            f'<div style="font-size: 16px;">{html}</div>'  # Aumenta o tamanho da fonte
        )

        # Analisa e modifica o HTML
        soup = BeautifulSoup(html, "html.parser")

        for cell in soup.find_all("th"):
            cell["style"] = "text-align: center;"

        # Exibe o HTML modificado
        st.write(
            "Aporte Mensal (% do ganho) x Renda Passiva Mensal (% do salário)",
            str(soup),
            unsafe_allow_html=True,
        )

        adicionar_linha()  # -------------------------------------------------------------------------

        tabela_comparativa_patrimonio = calcular_tabela_comparativa_patrimonio(
            taxa_anual
        )

        # Remove o índice ao exibir a tabela
        html = tabela_comparativa_patrimonio.to_html(index=False)
        html = (
            f'<div style="font-size: 16px;">{html}</div>'  # Aumenta o tamanho da fonte
        )

        # Analisa e modifica o HTML
        soup = BeautifulSoup(html, "html.parser")

        for cell in soup.find_all("th"):
            cell["style"] = "text-align: center;"

        # Exibe o HTML modificado
        st.write(
            "Aporte Mensal (% do salário) x Patrimônio (em salários)",
            str(soup),
            unsafe_allow_html=True,
        )

        # Adiciona estilo CSS para centralizar os dados das tabelas
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

        adicionar_linha()  # -------------------------------------------------------------------------


if __name__ == "__main__":
    main()
