# Roteiro de Desenvolvimento Individual Completo: 9 Etapas de Execução

Este guia consolida **todos os passos necessários** para que qualquer integrante do grupo execute o projeto inteiro sozinho. Siga a sequência abaixo para construir uma aplicação completa e pronta para portfólio.

---

## 🛠️ PASSO 1: Configuração do Ambiente 100% na Nuvem (Setup)
Não é necessário instalar nenhum programa no computador do laboratório. Faremos tudo pelo navegador.

- [ ] **1.1. Criar Conta no GitHub**: Garantir que você tenha uma conta ativa no GitHub.
- [ ] **1.2. Criar o Repositório**: Criar um repositório no seu perfil do GitHub para hospedar o projeto de Cálculo.
- [ ] **1.3. Iniciar o GitHub Codespaces**:
     * No seu repositório do GitHub, clique no botão verde **"Code"**.
     * Vá na aba **"Codespaces"** e clique em **"Create codespace on main"**.
     * O navegador abrirá o editor VS Code na nuvem pronto para uso.
- [ ] **1.4. Instalar Dependências na Máquina Virtual**:
     * Abra o terminal do Codespaces e instale as bibliotecas necessárias com:
       `pip install pandas numpy scipy streamlit plotly statsmodels`
     * Salve as dependências no arquivo de controle do repositório:
       `pip freeze > requirements.txt`

---

## 📅 PASSO 2: Coleta de Dados (Data Ingestion)
Coletar as séries históricas (2000–2024) das fontes de dados oficiais do Brasil e do México.

- [ ] **2.1. Dados Agrícolas do Brasil (IBGE)**: Consultar a API do IBGE SIDRA (Tabela 5457 - Pesquisa Agrícola Municipal) para obter: área colhida (ha), produção (t) e rendimento médio (kg/ha) para Soja, Milho e Café.
- [ ] **2.2. Dados Agrícolas do México (SIAP)**: Fazer o download dos dados históricos municipais no portal do SIAP/Datos Abiertos para obter área, produção e rendimento de Milho, Feijão e Café.
- [ ] **2.3. Dados Climáticos (Globais ou Locais)**: Coletar temperatura máxima diária ($T_{max}$), precipitação diária e evapotranspiração potencial para os municípios.
     * **Fontes Globais**: API Copernicus CDS (ERA5-Land) ou API do NASA POWER.
     * **Fontes do Brasil**: Institutos nacionais de meteorologia, como as estações automáticas/históricas do **INMET** (Instituto Nacional de Meteorologia) ou bases do **CPTEC/INPE** (Centro de Previsão de Tempo e Estudos Climáticos).
     * **Fontes do México**: Estações do **SMN** (Servicio Meteorológico Nacional) ou portais da **CONAGUA**.
- [ ] **2.4. Dados de Satélite (NDVI)**: Extrair a série histórica de NDVI (Índice de Vegetação) das regiões agrícolas através do Google Earth Engine (MODIS MOD13Q1).

---

## 🧼 PASSO 3: Tratamento de Dados e Modelagem Espacial (ETL)
Limpar, normalizar e cruzar todas as fontes de dados em um banco unificado.

- [ ] **3.1. Padronização de Unidades**: Converter todas as produtividades para $kg/ha$ (o México fornece em $t/ha$, multiplique por 1000).
- [ ] **3.2. Harmonização Geográfica**: Alinhar os códigos de municípios do IBGE (7 dígitos) e INEGI (5 dígitos) e limpar caracteres especiais nos nomes das cidades.
- [ ] **3.3. Interseção Espacial (Zonal Statistics)**: Para dados climáticos baixados em formato de grade (raster NetCDF), calcular a média de temperatura e chuva ponderada apenas pelas áreas de cultivo de cada município.
- [ ] **3.4. Cruzamento Final (Merge)**: Juntar as bases agrícola e climática em um dataframe único usando `Ano` e `Código do Município` como chaves.
- [ ] **3.5. Limpeza de Nulos e Outliers**: Remover ou interpolar valores nulos ou inconsistentes (ex: produtividade zerada em anos sem colheita registrada).

---

## 🌡️ PASSO 4: Cálculo Integral (Acumulação Agrometeorológica)
Aplicar o Cálculo Integral para estimar a energia térmica acumulada que a planta recebeu.

- [ ] **4.1. Definir a Integral de Calor (GDD)**: Modelar o GDD como a área sob a curva de temperatura que excede o limite basal da planta:
     $$GDD = \int_{t_0}^{t_f} \max(0, T(t) - T_{\text{base}}) \, dt$$
- [ ] **4.2. Implementar Integração Numérica**: Programar o algoritmo da **Regra de Simpson** no Python para calcular numericamente o valor da integral a partir das temperaturas diárias.
- [ ] **4.3. Calcular Estresse Térmico (HDD)**: Adaptar a integral para calcular os dias em que a planta sofreu estresse por calor extremo (dias em que $T_{max} > 35^\circ C$ na floração).

---

## 📈 PASSO 5: Cálculo Diferencial (Otimização de Rendimento)
Encontrar matematicamente o ponto ideal de umidade do solo que gera a maior produtividade.

- [ ] **5.1. Ajustar Modelo Quadrático**: Ajustar uma curva polinomial de segundo grau relacionando a produtividade ($Y$) com o índice de seca ($SPEI$):
     $$Y(SPEI) = a \cdot SPEI^2 + b \cdot SPEI + c$$
- [ ] **5.2. Derivar e Encontrar Ponto Crítico**: Calcular a primeira derivada $\frac{dY}{dSPEI}$, igualar a zero e resolver para $SPEI$:
     $$\frac{dY}{dSPEI} = 2a \cdot SPEI + b = 0 \implies SPEI^* = -\frac{b}{2a}$$
- [ ] **5.3. Testar a Concavidade**: Calcular a segunda derivada $\frac{d^2Y}{dSPEI^2} = 2a$. Se $a < 0$, comprovar que o ponto crítico é um **Máximo Local** (estabilidade hídrica ideal).

---

## 🌿 PASSO 6: Equações Diferenciais (EDO de Crescimento)
Modelar e simular a taxa instantânea de crescimento da biomassa da planta ao longo dos dias.

- [ ] **6.1. Definir a EDO de Crescimento**: Escrever a equação diferencial de crescimento logístico (Verhulst) com restrição climática:
     $$\frac{dY}{dt} = r(SPEI) \cdot Y \cdot \left(1 - \frac{Y}{K(SPEI)}\right)$$
- [ ] **6.2. Implementar o Método de Euler**: Criar um loop numérico em Python para resolver a EDO dia a dia atualizando a biomassa:
     $$Y_{t+1} = Y_t + \left(\frac{dY}{dt}\right) \cdot dt$$
- [ ] **6.3. Acoplar Estresse Climático**: Alterar a taxa de crescimento $r$ e o limite $K$ baseando-se no índice $SPEI$ do ano (secas severas reduzem $r$ e $K$).

---

## 🖥️ PASSO 7: Desenvolvimento do Dashboard Interativo
Criar a interface visual para apresentar o projeto e permitir interações matemáticas.

- [ ] **7.1. Estruturar Interface (Streamlit)**: Criar o layout do app com abas dedicadas para "Análise Histórica", "Visualização Climática" e "Modelagem Matemática (Cálculo)".
- [ ] **7.2. Gráficos Interativos**: Plotar gráficos usando `plotly.express` para mostrar a evolução da produtividade e anomalias de chuva.
- [ ] **7.3. Simulador da EDO**: Criar sliders de controle do clima ($SPEI$) conectados ao modelo EDO para que o usuário veja a curva de crescimento vegetal se achatar conforme a seca se intensifica.

---

## 🧪 PASSO 8: Testes Unitários e Validação de Código
Garantir a integridade científica do código implementado.

- [ ] **8.1. Testes de Integração**: Escrever testes no `pytest` para verificar se a função da Regra de Simpson calcula a área de teste corretamente.
- [ ] **8.2. Testes da EDO**: Escrever testes para certificar que a resolução de Euler converge para a capacidade de suporte $K$ em condições normais.
- [ ] **8.3. Teste do Ponto Crítico**: Validar se o SPEI ótimo calculado maximiza de fato o valor da produtividade na curva de otimização.

---

## 🎓 PASSO 9: Escrita do Relatório, Deploy e Portfólio
Finalizar as entregas acadêmicas e publicar o projeto no seu GitHub.

- [ ] **9.1. Redigir Relatório Científico**: Escrever a introdução, metodologia matemática de cálculo, discussões sobre as políticas agrícolas Brasil/México e conclusões.
- [ ] **9.2. Publicar o Dashboard**: Fazer o deploy do app Streamlit na nuvem (Streamlit Community Cloud).
- [ ] **9.3. Documentar o GitHub**: Garantir que o `README.md` tenha badges, imagens do dashboard e instruções claras de instalação para valorizar o seu portfólio.
