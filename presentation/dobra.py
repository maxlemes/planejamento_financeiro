import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np
from matplotlib.colors import LinearSegmentedColormap

# --- Dados ---
rotulos_anos = ['Patrimônio Inicial', 'Ano 1', 'Ano 2', 'Ano 3', 'Ano 4']
valores_bem = [100 * (0.9)**i for i in range(len(rotulos_anos))]
valores_capital_investido = [100 * (1.1)**i for i in range(len(rotulos_anos))]

# --- Paletas ---
# Vermelho decrescente (bem desvalorizando)
cores_vermelho = ["#FADBD8", "#F1948A", "#EC7063", "#CB4335", "#922B21"]
cmap_vermelho = LinearSegmentedColormap.from_list("vermelho_suave", cores_vermelho, N=5)

# Verde crescente (capital investido)
cores_verde = ["#E6F4EA", "#A8E6A2", "#5CB85C", "#2E8B57", "#145A32"]
cmap_verde = LinearSegmentedColormap.from_list("verde_suave", cores_verde, N=5)

cores_bem = [mcolors.to_hex(cmap_vermelho(i)) for i in range(5)]
cores_inv = [mcolors.to_hex(cmap_verde(i)) for i in range(5)]

# Cor do Ano 0 (azul)
cor_ano0 = "#1f77b4"

# --- Plot ---
x = np.arange(len(rotulos_anos))
width = 0.35

fig, ax = plt.subplots(figsize=(16, 8))

# Ano 0 → uma barra só, azul
rect_ano0 = ax.bar(x[0], valores_bem[0], width=width, color=cor_ano0)

# Anos 1..4 → barras lado a lado
x_group = x[1:]
vals_bem_group = valores_bem[1:]
vals_cap_group = valores_capital_investido[1:]

rects_bem = ax.bar(x_group - width/2, vals_bem_group, width, color=cores_bem[1:])
rects_cap = ax.bar(x_group + width/2, vals_cap_group, width, color=cores_inv[1:])

# --- Títulos e legendas ---
ax.set_ylabel('% do Capital Inicial', fontsize=18)
ax.set_title('Comparativo: Depreciação vs. Investimentos', fontsize=26, fontweight='bold')
ax.set_xticks(x)
ax.set_xticklabels(rotulos_anos, fontsize=18, fontweight='bold')

# --- Rótulos nas barras ---
def autolabel(rects, fmt="{:.2f}%"):
    for rect in rects:
        height = rect.get_height()
        ax.annotate(fmt.format(height),
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 5),
                    textcoords="offset points",
                    ha='center', va='bottom',
                    fontsize=16, fontweight='bold')

autolabel(rect_ano0, fmt="{:.2f}%")
autolabel(rects_bem)
autolabel(rects_cap)

# --- Estética ---
for spine in ax.spines.values():
    spine.set_visible(False)

ax.yaxis.grid(True, linestyle='--', alpha=0.6)

fig.tight_layout()
plt.show()

fig.savefig('imagens/comparativo.png', dpi=300, transparent=True, bbox_inches="tight")