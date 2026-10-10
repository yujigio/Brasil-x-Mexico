# 🌎 Observatório Agroclimático & Ambiental: Brasil vs. México (2000–2024)
## Modelagem de Cálculo Integral, Diferencial e EDOs sob Anomalias Meteorológicas Bilaterais

[![Deploy Observatorio Agroclimatico to GitHub Pages](https://github.com/yujigio/Brasil-x-Mexico/actions/workflows/deploy.yml/badge.svg)](https://github.com/yujigio/Brasil-x-Mexico/actions/workflows/deploy.yml)
[![Live Demo - Domínio Oficial](https://img.shields.io/badge/Live%20Demo-agroclima.yujisuheishi.com.br-10b981.svg)](https://agroclima.yujisuheishi.com.br)
[![Bilingual PT/ES](https://img.shields.io/badge/Language-Bilingual%20(PT%20%7C%20ES)-blue.svg)](#)
[![Python Version](https://img.shields.io/badge/Python-3.11%20%7C%203.12-3776AB.svg?logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-amber.svg)](LICENSE)
[![Academic Collaboration](https://img.shields.io/badge/Academic-Fatec%20Ourinhos%20%26%20An%C3%A1huac%20Puebla-purple.svg)](#)

> **Projeto Colaborativo Internacional "Cálculo intercultural: construyendo conexiones Brasil y México"**  
> Parceria acadêmica entre a **Faculdade de Tecnologia de Ourinhos (Fatec Ourinhos — Brasil 🇧🇷)** e a **Universidad Anáhuac Puebla (México 🇲🇽)**.  
> **Autor & Pesquisador:** Yuji Gio  
> **Repositório Oficial:** [github.com/yujigio/Brasil-x-Mexico](https://github.com/yujigio/Brasil-x-Mexico)  
> **Domínio Próprio de Produção:** [agroclima.yujisuheishi.com.br](https://agroclima.yujisuheishi.com.br)  
> **Espelho Alternativo:** [yujigio.github.io/Brasil-x-Mexico](https://yujigio.github.io/Brasil-x-Mexico)

---

## 🌐 Demonstração Online do Produto Web
O projeto integra uma **Single Page Application (SPA)** científica interativa de padrão internacional, com design *Glassmorphism*, renderização de fórmulas matemáticas em KaTeX, mapas geoespaciais comparativos via Leaflet.js, gráficos reativos via Chart.js, alternância fluida entre temas (Dark e Light Mode) e internacionalização dinâmica $100\%$ em tempo real (Português 🇧🇷 e Espanhol 🇲🇽):  
👉 **[Acesse o Observatório no Domínio Oficial: agroclima.yujisuheishi.com.br](https://agroclima.yujisuheishi.com.br)**

---

## 🇧🇷 Visão Geral do Projeto (Português)
Este repositório consolida o projeto de pesquisa e desenvolvimento aplicado de **Cálculo Intercultural** e **Ciência de Dados**. O objetivo central é investigar e modelar matematicamente as relações causais entre anomalias climáticas extremas (secas severas La Niña, ondas de calor El Niño e variações extremas de precipitação) e o rendimento físico ($kg/ha$) de culturas agrícolas estratégicas no Brasil e no México entre **2000 e 2024**.

A pesquisa baseou-se na auditoria minuciosa de **15 GB de dados brutos** consolidados a partir de bases governamentais e de sensoriamento remoto:
- **Agronomia:** IBGE PAM (Brasil) e SIAP/SADER (México).
- **Meteorologia & Clima:** INMET, CONAGUA e NASA POWER (Agroclimatologia diária).
- **Emissões & Meio Ambiente:** SEEG (13ª edição, Observatório do Clima) e INECC (Inventário Nacional de Emissões do México).
- **Saúde Pública & Epidemiologia:** DATASUS (SUS — Brasil) e IMSS/Secretaría de Salud (México).

---

## 🇲🇽 Descripción del Proyecto (Español)
Este repositorio consolida el proyecto de investigación y desarrollo de la cátedra de **Cálculo Intercultural** y **Ciencia de Datos**, modelando matemáticamente el impacto de las anomalías meteorológicas extremas sobre el rendimiento físico agrícola ($kg/ha$) en Brasil y México durante el período **2000–2024**.

Se auditaron 15 GB de microdatos oficiales comparando las matrices energéticas, el inventario de emisiones de gases de efecto invernadero (SEEG vs. INECC), los costos hospitalarios en salud pública por material particulado ($PM_{2.5}$) y la resiliencia productiva entre los cultivos de temporal en Brasil y los distritos de riego en México.

---

## 🧮 Arquitetura do Pacote Matemático (`src/observatorio/math_core/`)

O núcleo analítico do projeto foi modularizado em código Python de alta performance e rigor matemático:

### 1. `integral.py` — Cálculo Integral & Acumulação Térmica ($GDD$)
- **Formulação Teórica:** Acumulação de Graus-Dia de Desenvolvimento ($GDD$) acima da temperatura basal fenológica:
  $$GDD = \int_{t_0}^{t_f} \max\left(0, T(t) - T_{\text{base}}\right) \, dt$$
- **Algoritmo Numérico:** Regra de Simpson 1/3 pura com asserção estrita de paridade no número de intervalos discretos ($n$ par) e convergência de quarta ordem $O(h^4)$:
  $$\int_{t_0}^{t_n} f(t) \, dt \approx \frac{\Delta t}{3} \left[ f(t_0) + 4 \sum_{i=1,3,5}^{n-1} f(t_i) + 2 \sum_{i=2,4,6}^{n-2} f(t_i) + f(t_n) \right]$$
- **Validação de Precisão:** Validado analiticamente com erro relativo $< 0{,}00034\%$ contra integrais exatas de $\sin(x)$, $\exp(x)$ e polinômios de grau $\le 3$.
- **Culturas Calibradas:** Soja ($T_{\text{base}} = 10^\circ\text{C}$), Milho 1ª e 2ª Safra ($10^\circ\text{C}$), Café ($12^\circ\text{C}$), Cana-de-Açúcar ($14^\circ\text{C}$) e Feijão/Frijol ($10^\circ\text{C}$).

### 2. `differential.py` — Cálculo Diferencial & Otimização de Produtividade vs. SPEI
- **Formulação Teórica:** Curva polinomial de rendimento com detrending tecnológico secular para isolar o componente estritamente climático:
  $$Y(SPEI) = a \cdot SPEI^2 + b \cdot SPEI + c$$
- **Dedução do Ponto Crítico:** Pela 1ª derivada ordinária igualada a zero:
  $$\frac{dY}{dSPEI} = 2a \cdot SPEI + b = 0 \implies SPEI^* = -\frac{b}{2a} \approx +0{,}38$$
- **Prova de Máximo Global:** Pelo teste da 2ª derivada negativa:
  $$\frac{d^2Y}{dSPEI^2} = 2a < 0 \quad (\text{com } a < 0 \implies \text{Concavidade estritamente negativa})$$

### 3. `verhulst.py` — Equações Diferenciais Ordinárias (EDOs) de Crescimento Vegetativo
- **Formulação Teórica:** Dinâmica diária de biomassa aérea via EDO Logística de Pierre-François Verhulst (1838) sob forçante climática:
  $$\frac{dY}{dt} = r(SPEI) \cdot Y(t) \cdot \left(1 - \frac{Y(t)}{K(SPEI)}\right)$$
- **Discretização Numérica:** Resolvida dia a dia pelo Método de Euler com passo $\Delta t = 1{,}0\text{ dia}$ ao longo de 120 dias de safra:
  $$Y_{t+1} = Y_t + \left[ r(SPEI) \cdot Y_t \cdot \left(1 - \frac{Y_t}{K(SPEI)}\right) \right] \cdot \Delta t$$
- **Estabilidade Numérica:** Varredura computacional contínua em 601 pontos no domínio $SPEI \in [-3{,}0, +3{,}0]$, garantindo não-divergência ($r \cdot \Delta t \le 0{,}14 \ll 2{,}0$), ausência de NaNs/Infs e estrita positividade da biomassa.
- **Cenários Padronizados:** Seca Severa ($SPEI = -2{,}5$), Clima Normal ($SPEI = 0{,}0$) e Excesso Hídrico ($SPEI = +2{,}5$).

### 4. `statistics.py` — Inferência Estatística Formal (ANOVA & Testes t)
- **Normalização de Rendimento:** Índice Relativo de Produtividade ($YieldIndex = Y / \bar{Y}_{\text{cultura}}$).
- **ANOVA One-Way:**
  - Brasil: $F(1, 123) = 27{,}61$, $p = 6{,}34 \times 10^{-7}$ (significativo a $p < 0{,}001$).
  - México: $F(2, 122) = 38{,}25$, $p = 1{,}27 \times 10^{-13}$ (significativo a $p < 0{,}001$).
- **Testes t de Student (Normal vs. Seca Severa):**
  - Brasil (Sequeiro): queda média de rendimento de $-12{,}18\%$ ($t = 5{,}2542, p = 6{,}34 \times 10^{-7}$).
  - México (Irrigado): queda média de rendimento de $-12{,}62\%$ ($t = 7{,}5354, p = 1{,}09 \times 10^{-11}$).
- **Sensibilidade Climática ($d\text{Index}/d\text{SPEI}$):**
  - Média Brasil: $0{,}0574$; Média México: $0{,}0669$; Teste t comparativo entre países: $t = -0{,}6497, p = 0{,}5341$.
  - Conclusão: a dependência de reservatórios hídricos no México faz com que secas severas prolongadas gerem perdas relativas comparáveis às do sequeiro brasileiro.

---

## 📁 Estrutura de Diretórios e Layout do Repositório

```text
brasil-mexico-portfolio/
├── .github/
│   └── workflows/
│       └── deploy.yml                                     # Pipeline de CI/CD (QA automatizado e deploy no GitHub Pages)
├── assets/
│   ├── apresentacao_brasil_mexico_pt.pdf                  # Slides oficiais da defesa acadêmica do projeto
│   └── relatorio_contaminacion_brasil.pdf                 # Relatório técnico ambiental (SEEG, INECC, PM2.5)
├── e2e_tests/
│   ├── __init__.py
│   ├── adapter.py                                         # Adaptador unificado para execução e inspeção E2E
│   ├── run_e2e_tests.py                                   # Executor da suíte E2E em 4 camadas (Tiers 1 a 4)
│   ├── test_tier1_features.py                             # Tier 1: Verificação de contratos e componentes funcionais
│   ├── test_tier2_boundaries.py                           # Tier 2: Casos de borda, paridade ímpar e estabilidade extrema
│   ├── test_tier3_combinations.py                         # Tier 3: Acoplamento cruzado entre SPEI, GDD e Euler
│   └── test_tier4_scenarios.py                            # Tier 4: Cenários reais (La Niña 2021/2022, alinhamento documental)
├── src/
│   └── observatorio/
│       ├── __init__.py
│       └── math_core/
│           ├── __init__.py                                # Ponto de entrada do pacote matemático
│           ├── differential.py                            # Modelagem quadrática, detrending e pontos críticos
│           ├── integral.py                                # Integração Simpson 1/3 e Graus-Dia de Desenvolvimento
│           ├── statistics.py                              # ANOVA One-Way, testes t e sensibilidade climática
│           └── verhulst.py                                # EDO logística de Verhulst e simulação dinâmica de Euler
├── tests/
│   ├── __init__.py
│   ├── run_tests.py                                       # Executor autônomo de testes unitários (zero dependências)
│   └── test_portfolio_models.py                           # Suíte de 12 testes unitários e matemáticos
├── index.html                                             # Aplicação Web SPA Interativa Bilíngue (Glassmorphism)
├── observatorio_agroclimatico_brasil_mexico.ipynb         # Jupyter Notebook científico autossuficiente (250 observações)
├── painel_agroclimatico_brasil_mexico.csv                 # Chassi Comum de Dados (250 linhas, 0 nulos, 0 duplicatas)
├── README.md                                              # Documentação técnica e apresentação do repositório
├── RELATORIO_ACADEMICO_BRASIL_MEXICO.md                   # Artigo científico completo (normas ABNT NBR 6022 e APA 7th)
└── requirements.txt                                       # Especificação de dependências do ambiente Python
```

---

## 🧪 Instruções de Execução & Suíte de Testes Automatizados

O repositório disponibiliza uma esteira abrangente de garantia de qualidade, com testes unitários matemáticos e testes de ponta a ponta (E2E).

### 1. Instalação do Ambiente Virtual
```bash
# Clonar o repositório
git clone https://github.com/yujigio/Brasil-x-Mexico.git
cd Brasil-x-Mexico

# Instalar dependências
pip install -r requirements.txt
```

### 2. Execução dos Testes Unitários Matemáticos (12 Testes)
A suíte unitária pode ser executada com o executor nativo (sem dependências externas) ou via `pytest`:
```bash
# Execução direta via runner autônomo (Python Standard Library unittest):
python tests/run_tests.py

# Ou execução via pytest:
pytest -v --durations=0 tests/test_portfolio_models.py
```

**Cobertura dos Testes Unitários:**
- `test_01`: Exatidão exata da Regra de Simpson 1/3 para polinômios de grau $\le 3$.
- `test_02`: Convergência trigonométrica para $\sin(x)$ com erro $< 0{,}01\%$.
- `test_03`: Convergência exponencial para $\exp(x)$ com erro $< 0{,}01\%$.
- `test_04`: Confirmação da ordem de convergência teórica $O(h^4) \approx 4{,}00$.
- `test_05`: Acumulação térmica de Graus-Dia de Desenvolvimento ($GDD$).
- `test_06`: Concavidade negativa ($2a < 0$) e dedução do $SPEI^*$ em todas as culturas.
- `test_07`: Estabilidade numérica de Euler no domínio completo $[-3{,}0, +3{,}0]$.
- `test_08`: Monotonicidade e limites teóricos $[Y_0, K]$ na EDO de Verhulst.
- `test_09`: Unicidade estrita da chave primária composta `(pais, ano, cultura)`.
- `test_10`: Completude dos dados (250 linhas, 0 nulos nas 8 colunas).
- `test_11`: Limites físicos e consistência agronômica de produtividade, chuva e SPEI.
- `test_12`: Validação estatística formal da ANOVA e testes t.

### 3. Execução dos Testes de Ponta a Ponta (E2E — 60 Testes em 4 Tiers)
```bash
python e2e_tests/run_e2e_tests.py
```
- **Tier 1 (Features & Contracts):** 41 testes validando contratos de API, fórmulas KaTeX, layout, downloads e pipeline CI/CD.
- **Tier 2 (Boundaries & Edge Cases):** 8 testes checando fronteiras extremas de SPEI ($-3{,}0$ e $+3{,}0$), exceções de paridade de Simpson e limites de $T_{\text{base}}$.
- **Tier 3 (Cross-Module Combinations):** 6 testes validando o acoplamento dinâmico entre $SPEI$, modelos diferenciais, capacidade de suporte $K$ e simulação de Verhulst.
- **Tier 4 (Real-World Scenarios):** 5 testes reproduzindo a seca histórica da La Niña de 2021/2022, o pipeline completo de dados até a inferência e o alinhamento com o relatório acadêmico.

### 4. Execução da Aplicação Web Localmente
```bash
# Iniciar servidor estático local
python -m http.server 8000
```
Acesse no navegador: `http://localhost:8000`

### 5. Execução do Jupyter Notebook
```bash
jupyter notebook observatorio_agroclimatico_brasil_mexico.ipynb
```

---

## 🚀 Pipeline de Integração e Entrega Contínua (CI/CD)

O pipeline automatizado do GitHub Actions está configurado em `.github/workflows/deploy.yml` com arquitetura em dois estágios:

```
[Push em main/master ou Workflow Dispatch]
                   │
                   ▼
       [Job 1: Test & Data Audit]
  ├── Checkout & Configuração Python 3.11
  ├── Instalação de dependências (pip)
  ├── Execução de python tests/run_tests.py (12 testes unitários)
  ├── Execução de python e2e_tests/run_e2e_tests.py (60 testes E2E)
  └── Asserção de integridade física dos artefatos (HTML, CSV, IPYNB, PDFs)
                   │
                   ▼ (Somente se Job 1 passar com 100% de sucesso)
       [Job 2: GitHub Pages Deploy]
  ├── actions/configure-pages@v5
  ├── actions/upload-pages-artifact@v3 (path: .)
  └── actions/deploy-pages@v4
```

---

## 📑 Citação Acadêmica e Bibliografia Oficial

### Formato ABNT (NBR 6023:2018):
```text
FATEC OURINHOS; UNIVERSIDAD ANÁHUAC PUEBLA. Observatório Agroclimático Brasil vs México: Aplicação de Cálculo Integral, Diferencial e EDOs sob Anomalias Climáticas. Repositório Acadêmico Internacional, 2024–2026. Disponível em: https://github.com/yujigio/Brasil-x-Mexico. Acesso em: 10 out. 2026.
```

### Formato APA (7th Edition):
```text
Fatec Ourinhos, & Universidad Anáhuac Puebla. (2024–2026). Agroclimatic Observatory Brazil vs Mexico: Mathematical modeling and environmental big data (Version 2.0) [Software and repository]. GitHub. https://github.com/yujigio/Brasil-x-Mexico
```

Para a bibliografia acadêmica completa com referências formais aos trabalhos originais de **Vicente-Serrano et al. (2010)**, **Verhulst (1838)**, **McMaster & Wilhelm (1997)**, **SEEG (2024)**, **INECC (2024)**, **IPCC AR6 (2021)**, **IBGE PAM (2024)**, **SIAP (2024)** e **NASA POWER (2024)**, consulte a Seção 7 de [RELATORIO_ACADEMICO_BRASIL_MEXICO.md](RELATORIO_ACADEMICO_BRASIL_MEXICO.md).

---

## ⚖️ Licença & Autoria
Distribuído sob a licença **MIT**. Consulte `LICENSE` para obter mais informações.  
**Autor & Pesquisador Principal:** [Yuji Gio](https://github.com/yujigio)  
*Projeto acadêmico de portfólio desenvolvido para colaboração internacional e publicação científica.*
