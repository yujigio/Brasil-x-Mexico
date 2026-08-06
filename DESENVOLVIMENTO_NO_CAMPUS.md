# Guia de Desenvolvimento 100% no Campus (Inclusão Digital)

Este guia apresenta alternativas práticas para realizar todo o projeto utilizando **apenas a infraestrutura física da faculdade** (laboratórios) e **ferramentas em nuvem que rodam direto no navegador**, garantindo que integrantes que não possuem computador próprio consigam entregar 100% do trabalho.

---

## ☁️ 1. Programação sem Instalar Nada: IDEs na Nuvem (Browser)
Se as máquinas do laboratório da faculdade tiverem bloqueio para instalação de softwares (Python, VS Code, Git), existem três caminhos gratuitos que rodam direto no navegador:

### A. Google Colab (Recomendado para as etapas de Matemática/Cálculo)
* **Como usar**: Basta logar com uma conta Google.
* **Vantagens**: Já vem com Python, Pandas, Numpy, Scipy e bibliotecas gráficas instaladas por padrão. Não consome processamento da máquina local.
* **Aplicação no Projeto**: Perfeito para testar a Regra de Simpson (Integral), resolver o Método de Euler (EDO) e ajustar a curva quadrática (Otimização). Os códigos e gráficos ficam salvos automaticamente no Google Drive do aluno.

### B. GitHub Codespaces (Recomendado para o Dashboard e Git)
* **Como usar**: Diretamente pelo site do GitHub do aluno.
* **Vantagens**: O GitHub fornece gratuitamente 60 horas mensais de um computador virtual. Ele abre o VS Code completo dentro do navegador.
* **Aplicação no Projeto**: O aluno pode programar o Dashboard Streamlit no Codespaces e clicar em "Preview" para testar o aplicativo rodando em tempo real na nuvem. Também permite fazer Commits e Push para o Git sem precisar configurar nada na máquina do laboratório.

---

## 💾 2. Gerenciamento e Transporte de Arquivos sem Depender de Máquina Fixa
Como os computadores da faculdade costumam reiniciar e apagar arquivos locais ao final do dia, o aluno precisa salvar seu progresso na nuvem:

* **Google Drive / OneDrive Institucional**: Todo estudante da Fatec/Anáhuac geralmente possui uma conta institucional com espaço em nuvem gratuito. Use o Drive para guardar os arquivos CSV baixados na etapa de coleta.
* **GitHub**: Fazer commits constantes ao fim de cada sessão no laboratório garante que o código nunca seja perdido ao desligar o computador do campus.

---

## ⏱️ 3. Planejamento do Tempo no Campus (Sprints de Laboratório)
Propõe-se dividir as 30 horas estimadas do projeto em blocos que caibam no tempo de permanência no campus (ex: antes/depois da aula, janelas de horário ou laboratório livre):

* **Sessão 1: Coleta rápida de dados** (1h30 no campus):
  * Fazer o download dos dados históricos do IBGE (SIDRA) e do SIAP México usando a internet do campus. Salvar os CSVs no Google Drive.
* **Sessão 2 e 3: Tratamento de dados e Cálculo no Google Colab** (3h no campus):
  * Importar os arquivos do Google Drive diretamente no Colab e implementar os algoritmos de Simpson, Euler e derivadas.
* **Sessão 3 e 4: Montagem do Dashboard e Deploy** (3h no campus):
  * Abrir o GitHub Codespaces no navegador do laboratório, montar o arquivo `app.py` do Streamlit e publicar na nuvem da Streamlit Cloud.

---

## 👥 4. Grupos de Estudo e Programação Pareada no Campus
* **Estudo na Biblioteca**: Os alunos podem se reunir na biblioteca do campus para resolver as equações de derivadas e integrais no papel e lápis primeiro.
* **Programação em Par (Pair Programming)**: Mesmo que o trabalho seja individual, os alunos que possuem notebooks próprios podem levá-los para o campus e sentar lado a lado com quem não tem computador, compartilhando ideias e tirando dúvidas de lógica em tempo real nos laboratórios de informática.
