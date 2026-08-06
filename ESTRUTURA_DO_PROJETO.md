# Estrutura do Repositório Sugerida (Desenvolvimento Individual)

Para organizar o desenvolvimento do seu projeto completo, crie as pastas e arquivos abaixo seguindo a hierarquia padrão:

```text
projeto-calculo-individual/
├── data/
│   ├── raw/                 # Onde você colocará as tabelas brutas baixadas do IBGE/INEGI
│   └── processed/           # Onde você salvará as tabelas tratadas e combinadas no Pandas
├── src/
│   ├── data_etl/
│   │   ├── api_fetcher.py   # Seu script para carregar e unificar os dados agrícolas e climáticos
│   │   └── integrator.py    # Sua função de cálculo de GDD (Integral via Simpson)
│   ├── models/
│   │   ├── optimization.py  # Sua função de otimização (Derivadas de 1ª e 2ª ordem)
│   │   └── ode_solver.py    # Seu script do loop de crescimento vegetal (EDO via Euler)
│   └── dashboard/
│       └── app.py           # Seu aplicativo Streamlit interativo unificando tudo
├── README.md                # Apresentação do seu repositório GitHub
├── PROJETO_DE_PESQUISA.md    # Seu roteiro conceitual e referências de escrita
└── ROTEIRO_DE_DESENVOLVIMENTO_INDIVIDUAL.md # Seu workbook passo a passo
```

---

## 🛠️ Passos Recomendados para Iniciar o Desenvolvimento

1. **Criação da Árvore de Diretórios**:
   Abra o terminal na pasta do projeto e crie as pastas de código e dados com:
   ```bash
   mkdir -p data/raw data/processed src/data_etl src/models src/dashboard
   ```

2. **Criação dos Arquivos de Script**:
   Crie os arquivos vazios (comentados) em cada pasta para mapear o seu desenvolvimento:
   * Em `src/data_etl/integrator.py`, adicione o comentário:
     ```python
     # TODO: Implementar a Regra de Simpson para integrar dados de temperatura (GDD)
     ```
   * Em `src/models/optimization.py`, adicione:
     ```python
     # TODO: Implementar cálculo de SPEI ótimo resolvendo a derivada dY/dSPEI = 0
     ```
   * Em `src/models/ode_solver.py`, adicione:
     ```python
     # TODO: Implementar o Método de Euler para resolver a EDO dY/dt
     ```
   * Em `src/dashboard/app.py`, adicione:
     ```python
     # TODO: Montar o Streamlit contendo filtros, gráficos da EDO e simulador
     ```
