import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
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

    taxa_mensal = (1 + taxa_anual / 100) ** (1/12) - 1
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
        rendimento_mensal = saldo_acumulado * ((1 + taxa_anual / 100) ** (1/12) - 1)
        renda_passiva.append(rendimento_mensal * 12)  # Renda passiva anual

    df = pd.DataFrame({"Ano": anos, "Renda Passiva Anual": renda_passiva})
    return df

def calcular_renda_passiva_mensal(aporte_mensal, taxa_anual, anos):
    renda_mensal = []
    for ano in anos:
        saldo_acumulado = calcular_fv(aporte_mensal, taxa_anual, ano)
        rendimento_mensal = saldo_acumulado * ((1 + taxa_anual / 100) ** (1/12) - 1)
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
    aporte_1 = ganho*12*aporte/100

    dados = [{
        "Prazo (Anos)": 1,
        "Valor Aportado": aporte_1,
        "Saldo Acumulado": aporte_1,
        "Renda Passiva Mensal": 0
    }]

    anos = list(range(2, 31)) # começa do segundo ano
    aporte_liq = ganho*aporte*(1-0.275)/100

    for ano in anos:
        valor_aportado = aporte_1 + (ano-1) * aporte_liq  # Calcula o valor total aportado
        saldo_acumulado = aporte_1 + calcular_fv(aporte_1*(1+taxa_anual/100)+aporte_liq, taxa_anual, ano-1)
        rendimento_anual = saldo_acumulado*taxa_anual/100
        rendimento_mensal = saldo_acumulado * ((1 + taxa_anual / 100) ** (1/12) - 1)
        dados.append({
            "Prazo (Anos)": ano,
            "Valor Aportado": valor_aportado,
            "Saldo Acumulado": saldo_acumulado,
            "Renda Passiva Anual": rendimento_anual,
            "Renda Passiva Mensal": rendimento_mensal
        })

    df = pd.DataFrame(dados)

    if aporte >= 1:
        for col in ["Valor Aportado", "Saldo Acumulado","Renda Passiva Anual", "Renda Passiva Mensal"]:
            df[col] = df[col].apply(lambda x: f"R$ {x:,.2f}")
    else:
        df["Renda Passiva Mensal"] = df["Renda Passiva Mensal"].apply(lambda x: f"{x:.2%}")

    return df

def calcular_tabela_comparativa_renda(taxa_anual):
    anos = [5, 10, 15, 20, 25, 30]
    dados = {"Anos": anos}
    for aporte in [0.1, 0.15, 0.2, 0.25, 0.3]:
        renda_mensal = calcular_renda_passiva_mensal(aporte, taxa_anual, anos)["Renda Passiva Mensal"]
        dados[f"Aporte {aporte * 100}%"] = renda_mensal.apply(lambda x: f"{x:.2%}")
    df = pd.DataFrame(dados)

    return df


def calcular_tabela_comparativa_patrimonio(taxa_anual):
    anos = [5, 10, 15, 20, 25, 30]
    dados = {"Ano": anos}
    for aporte in [0.1, 0.15, 0.2, 0.25, 0.3]:
        patrimonio = [calcular_fv(aporte, taxa_anual, ano) for ano in anos]
        dados[f"Aporte {aporte * 100}%"] = patrimonio
    df = pd.DataFrame(dados)
    for col in df.columns[1:]:
        df[col] = df[col].apply(lambda x: f"{int(x)}")
    return df

def calcular_aporte(ganho_mensal, aporte):
    dados = []

    ganho_anual = 13*ganho_mensal
    aporte_total = ganho_anual*aporte/100
    aporte_mensal = aporte_total/12

    dados.append({
        "Ganho Anual":  ganho_anual,
        "Aporte Anual": aporte_total,
        "Aporte Mensal Equivalente": aporte_mensal
    })

    df = pd.DataFrame(dados)

    for col in df.columns:
        df[col] = df[col].apply(lambda x: f"R$ {x:,.2f}")

    return df

def main():
    st.title("Calculadora de Poupança e Renda")

    # aporte_mensal = st.number_input("Aporte Mensal", min_value=1, value=1000, step=100)
    # taxa_anual = st.number_input("Taxa de Juros Anual (%)", min_value=1, value=10)

    col1, col2, col3 = st.columns(3)  # Divide a tela em duas colunas

    with col1:
        ganho_mensal = st.number_input("Salário (R$) ", min_value=1, value=5000, step=100)

    with col2:
        aporte = st.number_input("Aporte (%)", min_value=1, value=12, step=1)

    with col3:
        taxa_anual = st.number_input("Taxa de Juros Anual (%)", min_value=1, value=10)



    if st.button("Calcular"):
        # Adiciona um espaço entre os frames
        st.markdown(" ")  # Você pode adicionar mais espaços para aumentar o espaço
        st.markdown(
            """
            <div style="border-top: 2px double orange; margin-top: 20px; margin-bottom: 20px;"></div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("")  # Você pode adicionar mais espaços para aumentar o espaço

        tabela = calcular_aporte(ganho_mensal, aporte)
        html = tabela.to_html(index=False)
        # Analisa e modifica o HTML
        soup = BeautifulSoup(html, "html.parser")
        
        for cell in soup.find_all("th"):
            cell["style"] = "text-align: center;"

        # Exibe o HTML modificado
        st.write(str(soup), unsafe_allow_html=True)
        # html = f'<div style="font-size: 16px;">{html}</div>'  # Aumenta o tamanho da fonte
        # st.write(tabela.to_html(index=False), unsafe_allow_html=True)

        # Adiciona um espaço entre os frames
        st.markdown(
            """
            <div style="border-top: 2px double orange; margin-top: 20px; margin-bottom: 20px;"></div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("")  # Você pode adicionar mais espaços para aumentar o espaço

        tabela = calcular_tabela_prev(ganho_mensal, aporte, taxa_anual)
        renda_passiva_df = calcular_renda_passiva_anual(aporte, taxa_anual)
        anos = list(range(2, 31))

        renda_mensal_df = calcular_renda_passiva_mensal(aporte, taxa_anual, anos)

        df_tab = tabela[tabela['Prazo (Anos)'].isin([5,10,15,20,25,30])]

        # Remove o índice ao exibir a tabela
        html = df_tab.to_html(index=False)
        html = f'<div style="font-size: 16px;">{html}</div>'  # Aumenta o tamanho da fonte
        st.write(df_tab.to_html(index=False), unsafe_allow_html=True)

                # Adiciona um espaço entre as tabelas
        st.markdown(" ")  # Você pode adicionar mais espaços para aumentar o espaço
               # Adiciona uma linha dupla usando CSS
        st.markdown(
            """
            <div style="border-top: 2px double orange; margin-top: 20px; margin-bottom: 20px;"></div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("")  # Você pode adicionar mais espaços para aumentar o espaço

    # Gráfico de barras
        fig = go.Figure(
                data=[
                    go.Bar(
                        name="Valor Aportado",
                        x=tabela["Prazo (Anos)"],
                        y=[float(val[2:].replace(",", "")) for val in tabela["Valor Aportado"]],
                        hovertemplate="Ano: %{x}<br>Valor Aportado: R$ %{y:,.2f}<extra></extra>",  # Tag informativa
                    ),
                    go.Bar(
                        name="Rendimento",
                        x=tabela["Prazo (Anos)"],
                        y=[
                            float(val[2:].replace(",", "")) - float(val2[2:].replace(",", ""))
                            for val, val2 in zip(tabela["Saldo Acumulado"], tabela["Valor Aportado"])
                        ],
                    hovertemplate="Ano: %{x}<br>Rendimento: R$ %{y:,.2f}<extra></extra>",  # Tag informativa
                    ),
                ]
            )

        fig.update_layout(
            barmode='stack', title='Saldo Acumulado', xaxis_title='Prazo (Anos)', yaxis_title='Valor (R$)'
        )
        st.plotly_chart(fig)

                # Adiciona um espaço entre as tabelas
        st.markdown(" ")  # Você pode adicionar mais espaços para aumentar o espaço
               # Adiciona uma linha dupla usando CSS
        st.markdown(
            """
            <div style="border-top: 2px double orange; margin-top: 20px; margin-bottom: 20px;"></div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("")  # Você pode adicionar mais espaços para aumentar o espaço

    # Gráfico de renda passiva mensal
        fig_renda_mensal = go.Figure(
            data=go.Scatter(
                x=renda_mensal_df["Ano"],
                y=renda_mensal_df["Renda Passiva Mensal"],
                mode="lines",
                hovertemplate="Ano: %{x}<br>Renda Mensal: R$ %{y:,.2f}<extra></extra>",  # Tag informativa
            )
        )
        
        fig_renda_mensal.update_layout(
            title='Renda Passiva Mensal', xaxis_title='Ano', yaxis_title='Renda Mensal (R$)'
        )
        
        st.plotly_chart(fig_renda_mensal)

                # Adiciona um espaço entre as tabelas
        st.markdown(" ")  # Você pode adicionar mais espaços para aumentar o espaço
               # Adiciona uma linha dupla usando CSS
        st.markdown(
            """
            <div style="border-top: 2px double orange; margin-top: 20px; margin-bottom: 20px;"></div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("")  # Você pode adicionar mais espaços para aumentar o espaço

        tabela_comparativa = calcular_tabela_comparativa_renda(taxa_anual)
    
        st.write("Aporte Mensal (% do ganho) x Renda Passiva Mensal (% do salário)", tabela_comparativa.to_html(index=False), unsafe_allow_html=True)

        # Adiciona um espaço entre as tabelas
        st.markdown(" ")  # Você pode adicionar mais espaços para aumentar o espaço
               # Adiciona uma linha dupla usando CSS
        st.markdown(
            """
            <div style="border-top: 2px double orange; margin-top: 20px; margin-bottom: 20px;"></div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("")  # Você pode adicionar mais espaços para aumentar o espaço


        tabela_comparativa_patrimonio = calcular_tabela_comparativa_patrimonio(taxa_anual)
        st.write("Aporte Mensal (% do salário) x Patrimônio (em salários)", tabela_comparativa_patrimonio.to_html(index=False), unsafe_allow_html=True)

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

                # Adiciona um espaço entre as tabelas
        st.markdown(" ")  # Você pode adicionar mais espaços para aumentar o espaço
               # Adiciona uma linha dupla usando CSS
        st.markdown(
            """
            <div style="border-top: 2px double orange; margin-top: 20px; margin-bottom: 20px;"></div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("")  # Você pode adicionar mais espaços para aumentar o espaço



if __name__ == "__main__":
    main()