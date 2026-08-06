# Arquitetura e Estrutura / Arquitectura y Estructura
## 📁 Projeto Colaborativo Internacional Brasil-México

Especificação técnica de diretórios, banco de dados e engenharia de software implementada neste repositório.

---

### 1. ÁRVORE DE DIRETÓRIOS / ÁRBOL DE DIRECTORIOS

```text
serene-bohr/
├── data/
│   ├── raw/                 # Dados brutos das APIs (IBGE, SIAP, NASA) / Datos brutos
│   └── processed/           # Tabelas tratadas e consolidadas (.parquet / .csv) / Datos procesados
├── src/
│   ├── data_etl/
│   │   ├── api_fetcher.py   # Ingestão agrícola e meteorológica / Ingestión de datos
│   │   └── integrator.py    # Integração de GDD (Regra de Simpson) / Integración de GDD
│   ├── models/
│   │   ├── optimization.py  # Derivadas de otimização de rendimento / Optimización de rendimiento
│   │   └── ode_solver.py    # Resolução de EDO de Verhulst (Euler) / Solución de EDO
│   └── dashboard/
│       └── app.py           # Interface web Streamlit (Bilíngue) / Panel web interactivo
├── README.md                # Apresentação do repositório / Presentación
├── MATHEMATICAL_MODELS.md   # Modelagem matemática detalhada / Modelado matemático
├── ESTRUTURA_DO_PROJETO.md  # Arquitetura do software / Arquitectura de software
└── requirements.txt         # Pacotes Python e dependências / Dependencias
```

---

### 2. ESQUEMA DO BANCO DE DADOS HÍBRIDO (PARQUET)
### 2. ESQUEMA DE LA BASE DE DATOS HÍBRIDA (PARQUET)

A base final unificada (`data/processed/painel_agro_climatico_consolidado.parquet`) possui a seguinte estrutura de colunas:

| Coluna / Columna | Tipo | Descrição / Descripción (PT) | Descripción (ES) |
| :--- | :--- | :--- | :--- |
| `pais` | `VARCHAR` | Identificador do País ('Brasil' ou 'Mexico') | Identificador del País |
| `ano` | `INTEGER` | Ano da Safra Agrícola (2000–2024) | Año de la Cosecha |
| `codigo_municipio` | `VARCHAR` | Código geográfico regional | Código geográfico regional |
| `nome_municipio` | `VARCHAR` | Nome do Município | Nombre del Municipio |
| `uf_estado` | `VARCHAR` | Estado / Entidade Federativa | Estado / Entidad Federativa |
| `cultura` | `VARCHAR` | Cultura agrícola analisada | Cultivo analizado |
| `area_colhida_ha` | `DOUBLE` | Área colhida em hectares | Área cosechada en hectáreas |
| `producao_toneladas`| `DOUBLE` | Produção total em toneladas | Producción total en toneladas |
| `produtividade_kg_ha`| `DOUBLE` | Rendimento físico agrícola ($kg/ha$) | Rendimiento físico agrícola ($kg/ha$) |
| `spei_3m` | `DOUBLE` | Índice de Seca SPEI (3 meses) | Índice de Sequía SPEI (3 meses) |
| `dias_estresse_termico_hdd`| `INTEGER`| Dias de estresse térmico ($T_{max} > 35^\circ C$) | Días de estrés térmico ($T_{max} > 35^\circ C$) |
| `ndvi_anomalia` | `DOUBLE` | Anomalia padronizada de NDVI MODIS | Anomalía estandarizada de NDVI MODIS |
| `precipitacao_acumulada_mm`| `DOUBLE`| Precipitação sazonal acumulada (mm) | Precipitación estacional acumulada (mm) |
