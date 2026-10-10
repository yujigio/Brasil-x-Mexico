"""
Núcleo Matemático e Modelagem Bioclimática
Contém módulos para:
- integral: Regra Composta de Simpson 1/3 e cálculo fenológico de GDD.
- differential: Otimização quadrática Y(SPEI), detrending secular e pontos críticos.
- verhulst: EDO logística de biomassa resolvida pelo método de Euler e solução analítica.
- statistics: Testes de hipóteses ANOVA e t de Student para sensibilidade climática.
"""

from .integral import simpson_13, calcular_gdd_cultura, validar_precisao_simpson
from .differential import ajustar_curva_produtividade, calibrar_painel_culturas
from .verhulst import (
    simular_verhulst_euler,
    solucao_analitica_verhulst,
    obter_cenarios_padrao,
    testar_estabilidade_dominio_spei,
)
from .statistics import executar_testes_agroclimaticos

__all__ = [
    "simpson_13",
    "calcular_gdd_cultura",
    "validar_precisao_simpson",
    "ajustar_curva_produtividade",
    "calibrar_painel_culturas",
    "simular_verhulst_euler",
    "solucao_analitica_verhulst",
    "obter_cenarios_padrao",
    "testar_estabilidade_dominio_spei",
    "executar_testes_agroclimaticos",
]
