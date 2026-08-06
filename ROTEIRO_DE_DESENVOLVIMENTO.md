# Roteiro de Desenvolvimento Individual e Fluxo em Nuvem

Este guia consolida **todos os passos necessários** para que qualquer integrante do grupo execute o projeto inteiro sozinho pelo navegador, incluindo dicas de segurança para laboratórios públicos e computadores que apagam arquivos ao desligar.

---

## ☁️ 1. O Ecossistema 100% na Nuvem (Sem Instalar Nada)
Para garantir a acessibilidade de todos (inclusive de quem não possui computador em casa), o projeto será desenvolvido inteiramente pelo navegador usando as seguintes ferramentas gratuitas:

* **GitHub Codespaces**: Sua máquina virtual na nuvem. Fornece um terminal Linux e o editor VS Code completo direto no browser. Salva o código automaticamente em seu repositório GitHub.
* **Google Colab**: Ideal para testar e validar os cálculos matemáticos (regra de Simpson, derivadas e EDO) de forma interativa antes de colocá-los no código final.
* **Streamlit Community Cloud**: Servidor de hospedagem gratuito que lê seu repositório no GitHub e coloca seu dashboard online para o professor acessar.

---

## 📅 2. As 9 Etapas de Desenvolvimento do Projeto

### 🛠️ FASE A: Configuração e Coleta
* **PASSO 1: Setup da Máquina Virtual**
  - Crie um repositório no seu GitHub e inicie um **Codespaces** nele.
  - No terminal do Codespaces, instale os pacotes: `pip install pandas numpy scipy streamlit plotly statsmodels` e salve a lista de dependências rodando: `pip freeze > requirements.txt`.
* **PASSO 2: Coleta de Dados**
  - **Brasil (IBGE)**: Baixe os dados de produtividade (PAM - Tabela 5457) de soja, milho e café via portal SIDRA.
  - **México (SIAP)**: Baixe os dados correspondentes de milho, feijão e café no portal do SIAP.
  - **Clima**: Baixe dados diários de chuva e temperatura dos municípios via API **NASA POWER** / **Copernicus ERA5** ou institutos locais (**INMET** / **CPTEC/INPE** no Brasil e **SMN** / **CONAGUA** no México).

### 🧼 FASE B: Tratamento e Modelagem Espacial (ETL)
* **PASSO 3: Tratamento de Dados no Pandas**
  - Padronize as produtividades para $kg/ha$ (converta as tabelas do México de $t/ha$ multiplicando por 1000).
  - Alinhe a sazonalidade: o período de cultivo de verão do Brasil (Out-Mar) deve ser comparado ao do México (Mai-Nov).
  - Faça a interseção espacial das grades de clima com os municípios (Zonal Statistics) e cruze as tabelas agrícolas e climáticas usando `Ano` e `Código do Município`.

### 🧮 FASE C: Modelagem Matemática de Cálculo
* **PASSO 4: Cálculo Integral (Acumulação Agrometeorológica)**
  - Implemente a integral de graus-dia (GDD) no arquivo `integrator.py` usando a **Regra de Simpson** para aproximar a área sob a curva de temperatura de 120 dias do ciclo:
    GDD = Integral de t_0 a t_f de max(0, T(t) - T_base) dt
* **PASSO 5: Cálculo Diferencial (Otimização de Rendimento)**
  - Ajuste uma curva quadrática Y(SPEI) = a * SPEI^2 + b * SPEI + c aos dados.
  - Obtenha a primeira derivada, iguale a zero e resolva para achar o SPEI ideal: dY/dSPEI = 2a * SPEI + b = 0 => SPEI* = -b / (2a).
  - Verifique se a segunda derivada é negativa (d2Y/dSPEI2 = 2a < 0), confirmando que o ponto crítico é um **Máximo Local**.
* **PASSO 6: Equações Diferenciais Ordinárias (EDO de Crescimento)**
  - Simule o acúmulo de biomassa diária resolvendo numericamente a EDO logística de Verhulst via **Método de Euler** em um loop por 120 passos:
    dY/dt = r(SPEI) * Y * (1 - Y / K(SPEI)) => Y_t+1 = Y_t + (dY/dt) * dt

### 🖥️ FASE D: Interface, Validação e Deploy
* **PASSO 7: Dashboard Streamlit**
  - Monte a interface em `app.py` integrando os gráficos históricos e sliders onde o usuário altera o SPEI e vê a curva resultante da EDO (crescimento da biomassa) se achatar na tela em tempo real.
* **PASSO 8: Testes Unitários**
  - Crie testes básicos com a biblioteca `pytest` na pasta `tests/` para validar se os algoritmos de Simpson, Euler e a derivada calculam os valores corretos.
* **PASSO 9: Relatório e Deploy**
  - Redija o artigo descrevendo o modelo matemático de cálculo aplicado e publique o dashboard no Streamlit Cloud.

---

## 🔒 3. Dicas de Segurança e Sobrevivência para o Laboratório

Se você utilizar computadores públicos da faculdade que apagam todos os arquivos do disco C: ao reiniciar (sistemas como Deep Freeze):

1. **Faça Tudo pelo Codespaces**: Como os arquivos e a execução rodam inteiramente na nuvem do GitHub, reiniciar o computador da faculdade não apagará nada. Basta logar no GitHub em qualquer PC e abrir seu Codespace novamente.
2. **Commit Local Seguro (Sem Configuração Global)**: Para evitar que o Git da máquina salve seu e-mail de forma permanente, configure suas informações apenas dentro da pasta do projeto atual usando a flag --local:
   git config --local user.name "Seu Nome Completo"
   git config --local user.email "seu_email_do_github@email.com"
3. **Evite Deixar Senhas Gravadas**: Se for usar o terminal do PC local, force o Git a não salvar senhas rodando:
   git config --global credential.helper ""
   Sempre que der push, faça a autenticação utilizando um Personal Access Token (PAT) temporário do GitHub. Ao fechar o terminal, a máquina esquecerá a credencial.
4. **Deslogue de Tudo**: Antes de sair do laboratório, clique em "Sign Out" no site do GitHub no navegador da faculdade.
