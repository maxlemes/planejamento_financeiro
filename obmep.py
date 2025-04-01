import pandas as pd
import requests

edicoes = [
    "2005",
    "2006",
    "2007",
    "2008",
    "2009",
    "2010",
    "2011",
    "2012",
    "2013",
    "2014",
    "2015",
    "2016",
    "2017",
    "2018",
    "2019",
    "16aobmep",
    "17obmep",
    "18obmep",
    "19obmep",
]
medalhas = ["Bronze", "Ouro", "Prata"]
colunas = ["Classificacao", "Nome", "Escola", "Tipo", "Municipio", "UF", "Medalha"]

todos_dfs = []

for edicao in edicoes:
    for medalha in medalhas:
        url = f"https://premiacao.obmep.org.br/{edicao}/verRelatorioPremiados{medalha}.do.htm"
        tabelas = pd.read_html(requests.get(url).content)
        for nivel, tabela in enumerate(tabelas[:3], start=1):
            df_temp = tabela.iloc[:, :7].copy()
            df_temp.columns = colunas
            df_temp["Nivel"] = nivel
            df_temp["Ano"] = edicao
            df_temp["Medalha"] = medalha
            todos_dfs.append(df_temp)

df_final = pd.concat(todos_dfs, ignore_index=True)

# Salvar em Excel
df_final.to_excel("premiados_obmep.xlsx", index=False)

print("Arquivo salvo com sucesso: premiados_obmep.xlsx")
