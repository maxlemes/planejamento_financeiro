# Calculadora de Poupança e Renda

## Descrição

A Calculadora de Poupança e Renda é uma aplicação desenvolvida em Python que permite aos usuários realizar simulações sobre investimentos e previdência, ajudando a entender a melhor forma de alocar a renda mensal em fundos de aposentadoria e outras modalidades de investimento. A plataforma calcula o Imposto de Renda (IRPF) em função dos aportes mensais, rendimentos e saldo acumulado ao longo dos anos, considerando diferentes estratégias de investimento (conservadora, moderada e agressiva).

## Funcionalidades

- Cálculo simulado de Imposto de Renda com e sem PGBL (Plano Gerador de Benefício Livre).
- Tabelas de simulação de valores aportados e rendimentos acumulados ao longo de 30 anos.
- A visualização de gráficos interativos para melhor entender a distribuição do patrimônio entre previdência e investimentos ao longo do tempo.
- Heatmaps que mostram a relação entre aporte percentual e rendimento passivo mensal.
- Cálculo do usufruto em meses e anos com base no saldo acumulado e na renda mensal.
- Interface amigável utilizando Streamlit, com design atrativo e responsivo.

## Requisitos

Para executar a aplicação, você precisará do seguinte:

- Python 3.x
- Bibliotecas: `matplotlib`, `numpy`, `pandas`, `plotly`, `seaborn`, `streamlit`, `beautifulsoup4`

## Instalação

1. Clone o repositório:
   ```bash
   git clone <URL_DO_REPOSITORIO>
   cd <DIRETORIO_DO_REPOSITORIO>
   ```

2. Crie um ambiente virtual e ative-o:
   ```bash
   python -m venv env
   source env/bin/activate  # Para Linux
   env\Scripts\activate  # Para Windows
   ```

3. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

## Uso

Para iniciar a aplicação, execute o seguinte comando no terminal:

```bash
streamlit run app.py
```

Substitua `app.py` pelo nome do arquivo que contém o código da aplicação.

## Contribuição

Contribuições são bem-vindas! Se você quiser contribuir, siga estes passos:

1. Fork o repositório.
2. Crie uma branch para sua nova funcionalidade (`git checkout -b feature/nova-funcionalidade`).
3. Commit suas alterações (`git commit -m 'Adiciona nova funcionalidade'`).
4. Push para a branch (`git push origin feature/nova-funcionalidade`).
5. Abra um Pull Request.

## Licença

Este projeto é licenciado sob a MIT License. Consulte o arquivo `LICENSE` para obter mais detalhes.

## Contato

Para qualquer dúvida ou sugestão, entre em contato pelo e-mail: [seu-email@example.com].

---

Sinta-se à vontade para usar, modificar e distribuir esta aplicação. Boas simulações!