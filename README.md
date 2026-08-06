# 🌾 Observatório Agro-Climático: Brasil vs. México
## 🌎 Observatorio Agroclimático: Brasil vs. México

[![Streamlit App](https://img.shields.io/badge/Streamlit-Dashboard-FF4B4B.svg)](src/dashboard/app.py)
[![Bilingual](https://img.shields.io/badge/Language-Bilingual--PT--ES-blue.svg)](#)
[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)

---

### 🇧🇷 [PORTUGUÊS] Apresentação do Projeto
Este repositório serve como a **vitrine de desenvolvimento** do projeto acadêmico da disciplina de **Cálculo** do **Projeto Colaborativo Internacional "Cálculo intercultural: construyendo conexiones Brasil y México"** (parceria Fatec Ourinhos & Universidad Anáhuac Puebla).

O sistema analisa, compara e simula o rendimento físico agrícola ($kg/ha$) entre Brasil e México (2000–2024) sob o impacto de anomalias meteorológicas (secas severas, ondas de calor e anomalias de precipitação), utilizando modelos matemáticos de Cálculo Integral, Diferencial e Equações Diferenciais Ordinárias (EDOs).

#### Culturas Analisadas
* **Brasil (Sequeiro e Safra Dupla)**: Soja, Milho (1ª e 2ª safra), Café e Cana-de-Açúcar.
* **México (Dualidade Irrigação e Temporal)**: Milho Branco, Milho Amarelo, Feijão, Café e Cana-de-Açúcar.

---

### 🇲🇽 [ESPAÑOL] Presentación del Proyecto
Este repositorio sirve como la **vitrina de desarrollo** del proyecto académico de la asignatura de **Cálculo** dentro do **Proyecto Colaborativo Internacional "Cálculo intercultural: construyendo conexiones Brasil y México"** (alianza Fatec Ourinhos & Universidad Anáhuac Puebla).

El sistema analiza, compara y simula el rendimiento físico agrícola ($kg/ha$) entre Brasil y México (2000–2024) bajo el impacto de anomalías meteorológicas (sequías severas, olas de calor y anomalías de precipitación), utilizando modelos matemáticos de Cálculo Integral, Diferencial y Ecuaciones Diferenciales Ordinarias (EDOs).

#### Cultivos Analizados
* **Brasil (Secano y Doble Cosecha)**: Soya, Maíz (1ª y 2ª cosecha), Café y Caña de Azúcar.
* **México (Dualidad Riego y Temporal)**: Maíz Blanco, Maíz Amarillo, Frijol, Café y Caña de Azúcar.

---

## 🛠️ Arquitetura e Estrutura / Arquitectura y Estructura

* 🧮 [MATHEMATICAL_MODELS.md](MATHEMATICAL_MODELS.md): Especificação matemática bilíngue contendo as deduções e resoluções numéricas de Cálculo (Simpson, Euler, Derivadas e Fluxo de Irrigação).
* 📁 [ESTRUTURA_DO_PROJETO.md](ESTRUTURA_DO_PROJETO.md): Arquitetura de software, esquema do banco de dados híbrido e organização de diretórios.
* ⚙️ [requirements.txt](requirements.txt): Bibliotecas Python de processamento científico e dashboard.

---

## 🚀 Execução / Ejecución

### 1. Iniciar o Ambiente / Iniciar el Entorno
O projeto é executado na nuvem via **GitHub Codespaces** ou localmente:
```bash
pip install -r requirements.txt
```

### 2. Dashboard Streamlit
Inicie a interface visual interativa / Iniciar la interfaz visual interactiva:
```bash
streamlit run src/dashboard/app.py
```
