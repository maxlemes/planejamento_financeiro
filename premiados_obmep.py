import pandas as pd
import requests

estados_siglas = {
    "Acre": "AC",
    "Alagoas": "AL",
    "Amapá": "AP",
    "Amazonas": "AM",
    "Bahia": "BA",
    "Ceará": "CE",
    "Distrito Federal": "DF",
    "Espírito Santo": "ES",
    "Goiás": "GO",
    "Maranhão": "MA",
    "Mato Grosso": "MT",
    "Mato Grosso do Sul": "MS",
    "Minas Gerais": "MG",
    "Pará": "PA",
    "Paraíba": "PB",
    "Paraná": "PR",
    "Pernambuco": "PE",
    "Piauí": "PI",
    "Rio de Janeiro": "RJ",
    "Rio Grande do Norte": "RN",
    "Rio Grande do Sul": "RS",
    "Rondônia": "RO",
    "Roraima": "RR",
    "Santa Catarina": "SC",
    "São Paulo": "SP",
    "Sergipe": "SE",
    "Tocantins": "TO",
}

url = f"https://pt.wikipedia.org/wiki/Lista_de_unidades_federativas_do_Brasil_por_popula%C3%A7%C3%A3o"
tabela = pd.read_html(requests.get(url).content)
df_pop = tabela[1]
df_pop = df_pop.iloc[:, 0:2]
df_pop.columns = ["Estado", "Populacao"]

df_pop["Populacao"] = (
    df_pop["Populacao"].str.replace("\xa0", "").str.replace(" ", "").astype(int)
)


# Criar nova coluna com siglas
df_pop["UF"] = df_pop["Estado"].map(estados_siglas)


# Ler o arquivo Excel
arquivo = "premiados_obmep.xlsx"
df = pd.read_excel(arquivo, sheet_name="Sheet1")  # Especifique a planilha
df.loc[df["Ano"] == "16aobmep", "Ano"] = "2021"
df.loc[df["Ano"] == "17obmep", "Ano"] = "2022"
df.loc[df["Ano"] == "18obmep", "Ano"] = "2023"
df.loc[df["Ano"] == "19obmep", "Ano"] = "2024"


#  1. Contar medalhas por Edição, UF e Nível
resultado = df.groupby(["Ano", "UF", "Nivel"]).size().unstack(fill_value=0)

# 2. Reorganizar para melhor visualização
resultado = resultado.reset_index().rename_axis(None, axis=1)
# print(resultado["Ano"].unique())  # Primeiras linhas
resultado.columns = ["Ano", "UF", "Nivel 1", "Nivel 2", "Nivel 3"]

df_join = pd.merge(left=resultado, right=df_pop, on="UF", how="inner")
print(df_join.head())

resultado = df_join


# 3. Salvar em Excel (uma aba por edição)
with pd.ExcelWriter("medalhas_por_Ano.xlsx") as writer:
    for ano in df["Ano"].unique():
        df_edicao = resultado[resultado["Ano"] == ano]
        df_edicao["Total"] = df_edicao[["Nivel 1", "Nivel 2", "Nivel 3"]].sum(axis=1)
        df_edicao["Populacao"] = df_edicao["Populacao"]
        df_edicao["X Medal"] = df_edicao["Total"] / df_edicao["Populacao"]
        df_edicao = df_edicao.sort_values(by="Total", ascending=False)
        df_edicao.to_excel(writer, sheet_name=f"Ano {ano}", index=False)
        print(df_edicao.head())


# Mostrar os dados
print(df_edicao.head())  # Primeiras linhas
