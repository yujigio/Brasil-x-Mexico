# Roteiro e Tópicos para o Projeto de Pesquisa (Cálculo)

Este documento apresenta o **esqueleto conceitual** e os tópicos que o grupo deve pesquisar e redigir para compor o artigo final.

---

## 1. INTRODUÇÃO E CONTEXTUALIZAÇÃO (A ser redigido pelo grupo)
* **Tópicos de Pesquisa**:
  * O que é o projeto colaborativo Brasil-México?
  * Dinâmica do Agronegócio no Brasil (foco em sequeiro e Cerrado/Sul).
  * Dinâmica do Agronegócio no México (foco em irrigação e regiões áridas do Norte vs. temporal no Sul).
  * O que são anomalias climáticas (secas severas, El Niño, La Niña, ondas de calor) e por que elas afetam a produtividade?

---

## 2. APLICAÇÃO DE CÁLCULO DIFERENCIAL E INTEGRAL
Esta é a seção central da matéria. O grupo deve pesquisar e demonstrar como aplicar os seguintes tópicos matemáticos:

### A. Cálculo Integral: Acumulação de Calor (GDD/HDD)
* **Conceito**: Como medir o calor acumulado que uma planta recebe ao longo dos dias?
* **Fórmula de Pesquisa**:
  $$GDD = \int_{t_0}^{t_f} (T(t) - T_{\text{base}}) \, dt \quad \text{se } T(t) > T_{\text{base}}$$
* **O que pesquisar**:
  * O que significa a integral definida neste contexto? (Representa a área sob a curva de temperatura ao longo do tempo).
  * O que é a Regra de Simpson e como ela serve para fazer essa integração de forma numérica no computador?

### B. Cálculo Diferencial: Otimização e Taxas de Variação
* **Conceito**: Como determinar o ponto de equilíbrio de água no solo ($SPEI$) que dá a maior produtividade possível?
* **Fórmula de Pesquisa**:
  $$Y(SPEI) = a \cdot SPEI^2 + b \cdot SPEI + c$$
* **O que pesquisar**:
  * Como encontrar o ponto crítico igualando a primeira derivada a zero: $\frac{dY}{dSPEI} = 0$.
  * Como usar a segunda derivada $\frac{d^2Y}{dSPEI^2}$ para provar se o ponto encontrado é de máximo ou de mínimo.

### C. Equações Diferenciais Ordinárias (EDO): Modelo de Crescimento
* **Conceito**: Como a taxa de crescimento vegetal varia a cada dia dependendo do clima?
* **Equação de Crescimento Logístico (Verhulst)**:
  $$\frac{dY}{dt} = r \cdot Y \cdot \left(1 - \frac{Y}{K}\right)$$
* **O que pesquisar**:
  * O que significa cada termo desta EDO ($\frac{dY}{dt}$, taxa de crescimento $r$, capacidade de carga $K$)?
  * Como o clima (seca/calor) altera a taxa de crescimento $r$ e o limite $K$?
  * O que é o Método de Euler e como ele resolve essa EDO passo a passo no computador?

---

## 3. FONTES DE DADOS A SEREM CONSULTADAS
* **Dados Agrícolas (Brasil)**: Pesquisar a tabela de Pesquisa Agrícola Municipal (PAM) do IBGE SIDRA.
* **Dados Agrícolas (México)**: Pesquisar o banco de dados do SIAP (Servicio de Información Agroalimentaria y Pesquera).
* **Dados Climáticos (Globais e Nacionais)**:
  * **Globais**: APIs do Copernicus ERA5 e NASA POWER.
  * **Brasil (Locais)**: Portais e bancos históricos de estações automáticas do **INMET** (Instituto Nacional de Meteorologia) e previsões/estudos do **CPTEC/INPE**.
  * **México (Locais)**: Dados do **SMN** (Servicio Meteorológico Nacional) e da **CONAGUA**.
