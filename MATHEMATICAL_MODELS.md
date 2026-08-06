# Modelagem Matemática / Modelado Matemático
## 🧮 Projeto Colaborativo Internacional Brasil-México

Este documento apresenta a especificação matemática rigorosa das equações de Cálculo Diferencial, Integral e EDOs implementadas no projeto.

---

### 1. CÁLCULO INTEGRAL: ACUMULAÇÃO TÉRMICA (GDD)
### 1. CÁLCULO INTEGRAL: ACUMULACIÓN TÉRMICA (GDD)

* **🇧🇷 Português**:
  A energia térmica acumulada necessária para o desenvolvimento das culturas é modelada como a **integral definida** da temperatura diária $T(t)$ que excede a temperatura base limitante ($T_{\text{base}}$) ao longo do ciclo vegetativo $[t_0, t_f]$:
  $$GDD = \int_{t_0}^{t_f} \max(0, T(t) - T_{\text{base}}) \, dt$$
  A resolução numérica é obtida no código através da **Regra de Simpson** aplicada ao vetor de temperaturas das estações meteorológicas (INMET/SMN).

* **🇲🇽 Español**:
  La energía térmica acumulada necesaria para el desarrollo de los cultivos se modela como la **integral definida** de la temperatura diaria $T(t)$ que supera la temperatura base limitante ($T_{\text{base}}$) a lo largo del ciclo vegetativo $[t_0, t_f]$:
  $$GDD = \int_{t_0}^{t_f} \max(0, T(t) - T_{\text{base}}) \, dt$$
  La resolución numérica se obtiene en el código a través de la **Regla de Simpson** aplicada al vector de temperaturas de las estaciones meteorológicas (INMET/SMN).

---

### 2. CÁLCULO DIFERENCIAL: OTIMIZAÇÃO DE RENDIMENTO
### 2. CÁLCULO DIFERENCIAL: OPTIMIZACIÓN DE RENDIMIENTO

* **🇧🇷 Português**:
  Ajustamos a produtividade real ($Y$) em relação ao índice de estresse hídrico ($SPEI$) através de um modelo polinomial quadrático:
  $$Y(SPEI) = a \cdot SPEI^2 + b \cdot SPEI + c$$
  A maximização é resolvida encontrando a primeira derivada e igualando a zero para obter o ponto crítico $SPEI^*$:
  $$\frac{dY}{dSPEI} = 2a \cdot SPEI + b = 0 \implies SPEI^* = -\frac{b}{2a}$$
  O teste da segunda derivada confirma que a concavidade é voltada para baixo (Máximo Local), pois o coeficiente quadrático da sensibilidade climática é negativo ($a < 0$):
  $$\frac{d^2Y}{dSPEI^2} = 2a < 0$$

* **🇲🇽 Español**:
  Ajustamos la productividad real ($Y$) en relación con el índice de estrés hídrico ($SPEI$) a través de un modelo polinomial cuadrático:
  $$Y(SPEI) = a \cdot SPEI^2 + b \cdot SPEI + c$$
  La maximización se resuelve hallando la primera derivada e igualando a cero para obtener el punto crítico $SPEI^*$:
  $$\frac{dY}{dSPEI} = 2a \cdot SPEI + b = 0 \implies SPEI^* = -\frac{b}{2a}$$
  La prueba de la segunda derivada confirma que la concavidad es hacia abajo (Máximo Local), ya que el coeficiente cuadrático de la sensibilidad climática es negativo ($a < 0$):
  $$\frac{d^2Y}{dSPEI^2} = 2a < 0$$

---

### 3. EQUAÇÕES DIFERENCIAIS (EDO DE CRESCIMENTO LOGÍSTICO)
### 3. ECUACIONES DIFERENCIALES (EDO DE CRECIMIENTO LOGÍSTICO)

* **🇧🇷 Português**:
  A taxa instantânea de crescimento da biomassa da planta ($Y$) no tempo ($t$) é descrita pela equação logística de Verhulst, modificada pelas restrições de choques climáticos ($SPEI$):
  $$\frac{dY}{dt} = r(SPEI) \cdot Y \cdot \left(1 - \frac{Y}{K(SPEI)}\right)$$
  Onde a taxa de crescimento $r(SPEI)$ e o teto produtivo $K(SPEI)$ sofrem decréscimo sob secas severas. A EDO é resolvida numericamente no simulador usando o **Método de Euler**:
  $$Y_{t+1} = Y_t + \left(\frac{dY}{dt}\right) \cdot dt$$

* **🇲🇽 Español**:
  La tasa instantánea de crecimiento de la biomasa de la planta ($Y$) en el tiempo ($t$) se describe mediante la ecuación logística de Verhulst, modificada por las restricciones de choques climáticos ($SPEI$):
  $$\frac{dY}{dt} = r(SPEI) \cdot Y \cdot \left(1 - \frac{Y}{K(SPEI)}\right)$$
  Donde la tasa de crecimiento $r(SPEI)$ y el límite productivo $K(SPEI)$ disminuyen bajo sequías severas. La EDO se resuelve numéricamente en el simulador utilizando el **Método de Euler**:
  $$Y_{t+1} = Y_t + \left(\frac{dY}{dt}\right) \cdot dt$$

---

### 4. INTEGRAL DE FLUXO: VOLUME DE IRRIGAÇÃO
### 4. INTEGRAL DE FLUJO: VOLUMEN DE RIEGO

* **🇧🇷 Português**:
  Para os cultivos irrigados no México (Distritos de Riego de Sinaloa/Sonora), o volume total acumulado de água ($Vol$) é modelado como a integral temporal da taxa de vazão instantânea de entrada ($Q(t)$):
  $$Vol = \int_{t_0}^{t_f} Q(t) \, dt$$

* **🇲🇽 Español**:
  Para los cultivos de riego en México (Distritos de Riego de Sinaloa/Sonora), el volumen total acumulado de agua ($Vol$) se modela como la integral temporal de la tasa de caudal instantáneo de entrada ($Q(t)$):
  $$Vol = \int_{t_0}^{t_f} Q(t) \, dt$$
