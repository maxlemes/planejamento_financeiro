import plotly.graph_objects as go
import plotly.express as px

# --- PASSO 1: SEUS DADOS (sem alteração) ---
labels = [
    # Nível 1 (Rendas)
    'Salário', 'Investimentos', 'Outros', 
    
    # Nível 2 (Total)
    'RENDA TOTAL', 
    
    # Nível 3 (Despesas)
    'Moradia', 'Alimentação', 'Transporte', 'Educação', 'Saúde', 'Lazer', 'Investimentos'
]
source = [0, 1, 2,  3, 3, 3, 3, 3, 3, 3]
target = [3, 3, 3,  4, 5, 6, 7, 8, 9, 10]
value = [0.7, 0.2, 0.1,  0.25, 0.15, 0.15, .13, 0.12, 0.1, 0.1]

# --- PASSO 2: SELEÇÃO DAS CORES DA PALETA 'BLUES' ---

# 1. Escolhe a paleta de cores sequencial
# palette = px.colors.sequential.Blues
palette = px.colors.sequential.Greens_r

# 2. Seleciona 3 tons da paleta (índices de 0 a 9, do mais claro ao mais escuro)
item = 0
cor_renda_rgb = palette[item]   # Um tom bem escuro
cor_total_rgb = palette[item+1]   # Um tom médio 
cor_despesa_rgb = palette[item+2] # Um tom claro

# 3. Adiciona a transparência desejada a cada cor
cor_renda = cor_renda_rgb.replace('rgb', 'rgba').replace(')', ', 0.8)')
cor_total = cor_total_rgb.replace('rgb', 'rgba').replace(')', ', 0.9)')
cor_despesa = cor_despesa_rgb.replace('rgb', 'rgba').replace(')', ', 0.8)')


# --- O restante do código continua idêntico ---

# Atribui a cor correta para cada NÓ com base no seu nível
node_colors = []
central_node_index = labels.index('RENDA TOTAL')
for i, label in enumerate(labels):
    if i < central_node_index:
        node_colors.append(cor_renda)
    elif i == central_node_index:
        node_colors.append(cor_total)
    else:
        node_colors.append(cor_despesa)

# Atribui a cor sólida correta para cada LINK (com 50% de opacidade)
cor_renda_link = cor_renda.replace('0.8', '0.5')
cor_despesa_link = cor_despesa.replace('0.8', '0.5')
link_colors = []
for i in range(len(source)):
    if target[i] == central_node_index:
        link_colors.append(cor_renda_link)
    else:
        link_colors.append(cor_despesa_link)

# --- PASSO 3: PREPARAÇÃO DOS DADOS PARA EXIBIÇÃO ---
display_percentages = [v * 100 for v in value]
node_totals = {i: 0 for i in range(len(labels))}
for s, t, v in zip(source, target, value):
    node_totals[s] += v
    node_totals[t] += v
node_display_percentages = [total * 100 for i, total in sorted(node_totals.items())]

# --- PASSO 4: GERAR O GRÁFICO ---
fig = go.Figure(data=[go.Sankey(
    arrangement="snap",
    node=dict(pad=25, thickness=20, color=node_colors, line=dict(color='black', width=0.5), label=labels, customdata=node_display_percentages, hovertemplate='%{label}<br><b>%{customdata:.1f}%</b><extra></extra>'),
    link=dict(source=source, target=target, value=value, color=link_colors, customdata=display_percentages, hovertemplate='De %{source.label}<br />Para %{target.label}<br /><b>%{customdata:.1f}%</b><extra></extra>')
)])


# --- MUDANÇA ESTÁ AQUI ---
fig.update_layout(
    title_text="",
    font=dict(size=12, family="Arial, sans-serif"),
    height=600,
    
    # Adicione estas duas linhas para o fundo transparente
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)'
)

# --- PASSO 5: SALVAR O GRÁFICO ---
try:
    fig.write_image("orcamento_pessoal.png", scale=2)
    print("Sucesso! O gráfico foi salvo como 'orcamento_pessoal.png'.")
except Exception as e:
    print(f"Erro ao salvar a imagem: {e}")

# fig.show()