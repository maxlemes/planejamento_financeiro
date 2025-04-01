import pandas as pd
import requests

todos_dfs = []

url = f"https://pt.wikipedia.org/wiki/Lista_de_unidades_federativas_do_Brasil_por_popula%C3%A7%C3%A3o"
tabela = pd.read_html(requests.get(url).content)
df = tabela[1]
df = df.iloc[:, 0:2]
df.columns = ["UF", "Populacao"]
print(df)
