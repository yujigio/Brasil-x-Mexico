"""
Suíte de Testes Automatizados e Auditoria de Dados: Observatório Agroclimático Brasil vs. México
Validação matemática rigorosa, estabilidade numérica e integridade relacional.

Contém 12 testes unitários padrão unittest.TestCase:
- test_01: Simpson exactness on degree <= 3 polynomial (abs err < 1e-12).
- test_02: Simpson trigonometric convergence on sin(x) (< 0.01% error).
- test_03: Simpson exponential convergence on exp(x) (< 0.01% error).
- test_04: Simpson fourth-order convergence O(h^4) ratio approx 16.0.
- test_05: Biological GDD thermal accumulation (< 0.01% error).
- test_06: Differential calculus: local maximum proof (2a < 0) and SPEI* critical point for 100% of crops in Brazil and Mexico with detrending.
- test_07: Euler Verhulst stability scan: 0 NaNs, 0 Infs, non-negative biomass across 61 points in [-3.0, +3.0].
- test_08: Euler Verhulst monotonicity and bounds [Y0, K].
- test_09: Relational integrity: composite primary key (pais, ano, cultura) uniqueness (0 duplicates).
- test_10: Data completeness: exactly 250 records, 0 nulls across all 8 columns in painel_agroclimatico_brasil_mexico.csv.
- test_11: Value range assertions: physical boundaries for yield, rain, temperature, and SPEI.
- test_12: Statistical hypothesis testing: ANOVA and t-tests on standardized yields with p < 0.001.
"""

import os
import sys
from pathlib import Path
import unittest

import numpy as np
import pandas as pd

# Resolução dinâmica de caminhos para suportar execução de qualquer diretório de trabalho
TESTS_DIR = Path(__file__).resolve().parent
PROJECT_DIR = TESTS_DIR.parent
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

# Importação do núcleo matemático em produção
from src.observatorio.math_core.integral import (
    simpson_13,
    calcular_gdd_cultura,
    validar_precisao_simpson,
)
from src.observatorio.math_core.differential import (
    ajustar_curva_produtividade,
    calibrar_painel_culturas,
)
from src.observatorio.math_core.verhulst import (
    simular_verhulst_euler,
    solucao_analitica_verhulst,
    obter_cenarios_padrao,
    testar_estabilidade_dominio_spei,
)
from src.observatorio.math_core.statistics import (
    executar_testes_agroclimaticos,
)


def _obter_caminho_csv() -> Path:
    """Localiza o arquivo painel_agroclimatico_brasil_mexico.csv de forma resiliente."""
    candidatos = [
        PROJECT_DIR / "painel_agroclimatico_brasil_mexico.csv",
        Path.cwd() / "painel_agroclimatico_brasil_mexico.csv",
        Path.cwd() / "brasil-mexico-portfolio" / "painel_agroclimatico_brasil_mexico.csv",
    ]
    for c in candidatos:
        if c.is_file():
            return c
    raise FileNotFoundError(
        f"Arquivo painel_agroclimatico_brasil_mexico.csv não encontrado nos caminhos: {candidatos}"
    )


class TestPortfolioModels(unittest.TestCase):
    """Suíte oficial de 12 testes unitários cobrindo o núcleo analítico e integridade de dados."""

    @classmethod
    def setUpClass(cls):
        """Carrega os dados autoritativos do painel agroclimático uma única vez."""
        cls.csv_path = _obter_caminho_csv()
        cls.df = pd.read_csv(cls.csv_path)

    def test_01_simpson_exactness_degree_le_3(self):
        """
        Teste 01: Exatidão da Regra de Simpson 1/3 para polinômios de grau <= 3.
        Teorema: Simpson 1/3 é exato (erro = 0, limitado apenas por precisão de ponto flutuante)
        para qualquer polinômio até terceiro grau, pois o erro é proporcional à 4ª derivada f^(4)(xi) = 0.
        Verifica polinômio cúbico f(x) = 4x^3 - 3x^2 + 2x - 5 em [0, 2]:
        Integral analítica = [x^4 - x^3 + x^2 - 5x]_0^2 = 16 - 8 + 4 - 10 = 2.0.
        Critério de aceitação: erro absoluto < 1e-12.
        """
        # Malha com 4 subintervalos (5 nós, n par)
        x = np.linspace(0.0, 2.0, 5)
        h = 2.0 / 4.0
        y = 4.0 * x**3 - 3.0 * x**2 + 2.0 * x - 5.0
        integral_num = simpson_13(y, h=h)
        integral_exata = 2.0
        erro_abs = abs(integral_num - integral_exata)

        self.assertLess(
            erro_abs,
            1e-12,
            f"Simpson 1/3 falhou na exatidão cúbica. Erro absoluto: {erro_abs:.2e} >= 1e-12"
        )

        # Teste adicional com polinômio quadrático f(x) = 5x^2 - 4x + 7 em [1, 3]
        # Integral = [5/3 x^3 - 2x^2 + 7x]_1^3 = (45 - 18 + 21) - (5/3 - 2 + 7) = 48 - 20/3 = 124/3
        x_quad = np.linspace(1.0, 3.0, 7)
        h_quad = (3.0 - 1.0) / 6.0
        y_quad = 5.0 * x_quad**2 - 4.0 * x_quad + 7.0
        integral_num_quad = simpson_13(y_quad, h=h_quad)
        integral_exata_quad = 124.0 / 3.0
        erro_abs_quad = abs(integral_num_quad - integral_exata_quad)

        self.assertLess(
            erro_abs_quad,
            1e-12,
            f"Simpson 1/3 falhou na exatidão quadrática. Erro absoluto: {erro_abs_quad:.2e} >= 1e-12"
        )

    def test_02_simpson_trigonometric_convergence_sin(self):
        """
        Teste 02: Convergência da Regra de Simpson 1/3 para a função trigonométrica sin(x).
        Integral analítica: Integral_0^pi sin(x) dx = [-cos(x)]_0^pi = 2.0.
        Critério de aceitação: erro relativo < 0.01% (< 1e-4).
        """
        n_subintervalos = 20  # 21 pontos
        x = np.linspace(0.0, np.pi, n_subintervalos + 1)
        h = np.pi / float(n_subintervalos)
        y = np.sin(x)

        integral_num = simpson_13(y, h=h)
        integral_exata = 2.0
        erro_rel_pct = abs(integral_num - integral_exata) / integral_exata * 100.0

        self.assertLess(
            erro_rel_pct,
            0.01,
            f"Erro relativo em sin(x) ({erro_rel_pct:.6f}%) excedeu o limiar de 0.01%"
        )

    def test_03_simpson_exponential_convergence_exp(self):
        """
        Teste 03: Convergência da Regra de Simpson 1/3 para a função exponencial exp(x).
        Integral analítica: Integral_0^1 exp(x) dx = exp(1) - 1 = e - 1 = 1.718281828459...
        Critério de aceitação: erro relativo < 0.01% (< 1e-4).
        """
        n_subintervalos = 10  # 11 pontos
        x = np.linspace(0.0, 1.0, n_subintervalos + 1)
        h = 1.0 / float(n_subintervalos)
        y = np.exp(x)

        integral_num = simpson_13(y, h=h)
        integral_exata = float(np.e - 1.0)
        erro_rel_pct = abs(integral_num - integral_exata) / integral_exata * 100.0

        self.assertLess(
            erro_rel_pct,
            0.01,
            f"Erro relativo em exp(x) ({erro_rel_pct:.6f}%) excedeu o limiar de 0.01%"
        )

    def test_04_simpson_fourth_order_convergence_ratio(self):
        """
        Teste 04: Confirmação da ordem teórica de convergência O(h^4) da Regra de Simpson 1/3.
        Ao reduzir o passo h pela metade (h -> h/2, dobrando o número de subintervalos de N1 para N2 = 2*N1),
        o erro de truncamento global decresce por um fator de (h / (h/2))^4 = 2^4 = 16.0.
        Para exp(x) em [0, 1] com N1 = 10 e N2 = 20:
        Razão = E(h1) / E(h2) approx 16.0.
        Critério de aceitação: razão entre 15.5 e 16.5 (tolerância delta = 0.5 ao redor de 16.0).
        """
        integral_exata = float(np.e - 1.0)

        n1 = 10
        x1 = np.linspace(0.0, 1.0, n1 + 1)
        h1 = 1.0 / float(n1)
        err1 = abs(simpson_13(np.exp(x1), h=h1) - integral_exata)

        n2 = 20
        x2 = np.linspace(0.0, 1.0, n2 + 1)
        h2 = 1.0 / float(n2)
        err2 = abs(simpson_13(np.exp(x2), h=h2) - integral_exata)

        self.assertGreater(err2, 0.0, "Erro n2 não pode ser zero.")
        razao = err1 / err2

        self.assertAlmostEqual(
            razao,
            16.0,
            delta=0.5,
            msg=f"Razão de convergência observada {razao:.4f} diverge de 16.0 (esperado para O(h^4))."
        )

    def test_05_biological_gdd_thermal_accumulation(self):
        """
        Teste 05: Acumulação térmica biológica de Graus-Dia de Desenvolvimento (GDD).
        Integral analítica: GDD = Integral_0^120 max(0, T(t) - T_base) dt.
        Cenário senoidal canônico: T(t) = 28 + 6 * sin(2*pi*t / 120), T_base = 10.0°C.
        Como T(t) >= 22.0°C > T_base, calor_util = 18 + 6 * sin(2*pi*t / 120).
        Integral exata em [0, 120]: 18 * 120 + 0 = 2160.0 °C.dia.
        Critério de aceitação: erro relativo < 0.01% (< 1e-4).
        """
        t = np.linspace(0.0, 120.0, 121)
        temperaturas = 28.0 + 6.0 * np.sin(2.0 * np.pi * t / 120.0)

        res_gdd = calcular_gdd_cultura(
            temperaturas=temperaturas,
            cultura="Soja",
            t_base=10.0,
            ciclo_dias=120,
            h=1.0,
        )

        gdd_obtido = float(res_gdd["gdd"])
        gdd_analitico = 2160.0
        erro_rel_gdd = abs(gdd_obtido - gdd_analitico) / gdd_analitico * 100.0

        self.assertLess(
            erro_rel_gdd,
            0.01,
            f"Erro relativo no cálculo fenológico de GDD ({erro_rel_gdd:.6f}%) excedeu 0.01%"
        )

        # Validação complementar via função interna de testes do math_core
        val_prec = validar_precisao_simpson()
        self.assertTrue(val_prec["sucesso"], "A rotina validar_precisao_simpson() falhou.")
        self.assertLess(val_prec["bioclimatico_gdd"]["erro_relativo_pct"], 0.01)

    def test_06_differential_local_maximum_and_spei_optimal(self):
        """
        Teste 06: Cálculo Diferencial - prova de concavidade negativa (2a < 0, máximo local)
        e ponto crítico SPEI* = -b/(2a) para 100% dos cultivos de Brasil e México com detrending.
        Verifica:
        - 10 cultivos calibrados no total (5 no Brasil, 5 no México).
        - Coeficiente quadrático a < 0 para todos os cultivos.
        - Segunda derivada d2Y/dSPEI2 = 2a < 0 para todos os cultivos.
        - is_maximo == True para 100% dos cultivos.
        - SPEI* analiticamente consistente com -b/(2a).
        """
        cal = calibrar_painel_culturas(self.df, remover_tendencia=True)

        self.assertEqual(
            len(cal),
            10,
            f"Esperado 10 cultivos calibrados (5 BR + 5 MX), obtido {len(cal)}"
        )

        # 100% dos cultivos devem satisfazer a condição de concavidade negativa (2a < 0)
        self.assertTrue(
            (cal["a"] < 0.0).all(),
            f"Cultivos com a >= 0 detectados: {cal[cal['a'] >= 0.0][['pais', 'cultura', 'a']]}"
        )
        self.assertTrue(
            (cal["d2Y_dSPEI2"] < 0.0).all(),
            "Segunda derivada não-negativa encontrada em cultivos calibrados."
        )
        self.assertTrue(
            cal["is_maximo"].all(),
            "Nem todos os cultivos foram classificados com máximo local."
        )

        # Checagem de precisão analítica de SPEI* = -b / (2a)
        for _, row in cal.iterrows():
            a = row["a"]
            b = row["b"]
            spei_otimo_calculado = -b / (2.0 * a)
            self.assertAlmostEqual(
                row["spei_otimo"],
                spei_otimo_calculado,
                places=3,
                msg=f"Discrepância na dedução analítica de SPEI* para {row['pais']} - {row['cultura']}"
            )

    def test_07_euler_verhulst_stability_scan(self):
        """
        Teste 07: Varredura de estabilidade numérica do Método de Euler para a EDO de Verhulst.
        Equação: dY/dt = r(SPEI) * Y * (1 - Y/K(SPEI)), dt = 1.0 dia, t in [0, 120].
        Varre 61 pontos equidistantes no domínio de forçante agroclimática SPEI in [-3.0, +3.0].
        Critérios de aceitação:
        - 0 valores NaN em toda a trajetória.
        - 0 valores Inf em toda a trajetória.
        - Biomassa estritamente não-negativa Y(t) >= 0 para todo t em [0, 120].
        - Rotina oficial testar_estabilidade_dominio_spei((-3.0, 3.0), passos=61) retorna True.
        """
        pontos_spei = np.linspace(-3.0, 3.0, 61)

        for s in pontos_spei:
            sim = simular_verhulst_euler(spei=float(s), dias=120, y0=50.0, dt=1.0)
            y = sim["y"]

            # Ausência de NaNs e Infs
            self.assertEqual(
                int(np.isnan(y).sum()),
                0,
                f"NaN detectado na simulação de Euler para SPEI = {s:.2f}"
            )
            self.assertEqual(
                int(np.isinf(y).sum()),
                0,
                f"Inf detectado na simulação de Euler para SPEI = {s:.2f}"
            )

            # Não-negatividade da biomassa
            self.assertTrue(
                bool((y >= 0.0).all()),
                f"Biomassa negativa detectada para SPEI = {s:.2f}"
            )

        # Validação complementar pelo módulo em produção
        estavel = testar_estabilidade_dominio_spei((-3.0, 3.0), passos=61)
        self.assertTrue(estavel, "testar_estabilidade_dominio_spei retornou False para passos=61.")

    def test_08_euler_verhulst_monotonicity_and_bounds(self):
        """
        Teste 08: Monotonicidade e limites teóricos [Y0, K] na EDO logística de Verhulst.
        Propriedade biofísica: Se Y0 < K(SPEI), dY/dt > 0 para todo Y in [Y0, K).
        Portanto, a trajetória Y(t) é monotonicamente não-decrescente e permanece limitada
        no intervalo [Y0, K] (com folga numérica de Euler <= 1.05 * K).
        Avalia os 3 cenários canônicos: Seca Severa (-2.5), Clima Normal (0.0) e Excesso Hídrico (+2.5).
        """
        cenarios = obter_cenarios_padrao()
        self.assertEqual(len(cenarios), 3, "Esperado exatamente 3 cenários padrão.")

        for nome, sim in cenarios.items():
            y = sim["y"]
            y0 = float(y[0])
            K = float(sim["K"])

            # Valor inicial coincide com y0 = 50.0
            self.assertAlmostEqual(y0, 50.0, places=2)

            # Monotonicidade não-decrescente: Y_{t+1} - Y_t >= -1e-6
            deltas = np.diff(y)
            self.assertTrue(
                bool((deltas >= -1e-6).all()),
                f"Violação de monotonicidade no cenário '{nome}': deltas negativos encontrados."
            )

            # Limite inferior: Y(t) >= Y0
            self.assertTrue(
                bool((y >= y0 - 1e-6).all()),
                f"Trajetória violou limite inferior Y0 no cenário '{nome}'."
            )

            # Limite superior: Y(t) <= 1.05 * K
            self.assertTrue(
                bool((y <= K * 1.05).all()),
                f"Trajetória explodiu além de 1.05 * K no cenário '{nome}'."
            )

            # Biomassa final menor ou igual à capacidade de suporte K
            self.assertLessEqual(
                sim["y_final"],
                K * 1.05,
                f"Biomassa final superou K no cenário '{nome}'."
            )

    def test_09_relational_composite_pk_uniqueness(self):
        """
        Teste 09: Integridade Relacional - unicidade estrita da chave primária composta
        (pais, ano, cultura) em painel_agroclimatico_brasil_mexico.csv.
        Critério de aceitação: estritamente 0 linhas duplicadas no subconjunto de chaves.
        """
        duplicadas = self.df.duplicated(subset=["pais", "ano", "cultura"]).sum()
        self.assertEqual(
            int(duplicadas),
            0,
            f"Violação de integridade relacional: {duplicadas} chaves primárias duplicadas (pais, ano, cultura)."
        )

    def test_10_dataset_completeness_and_schema(self):
        """
        Teste 10: Completude dos Dados e Validação de Esquema Relacional.
        Critérios de aceitação:
        - Exatamente 250 registros históricos (25 anos x 5 culturas x 2 países).
        - Exatamente 8 colunas canônicas esperadas presentes no painel.
        - Estritamente 0 valores nulos (NaN/None) em todas as colunas.
        """
        self.assertEqual(
            len(self.df),
            250,
            f"Contagem incorreta de registros: esperado 250, encontrado {len(self.df)}"
        )

        colunas_esperadas = [
            "pais",
            "ano",
            "cultura",
            "produtividade_kg_ha",
            "precipitacao_mm",
            "spei_3m",
            "temp_media",
            "status_clima",
        ]
        for col in colunas_esperadas:
            self.assertIn(
                col,
                self.df.columns,
                f"Coluna mandatória ausente no painel: '{col}'"
            )

        nulos_totais = int(self.df[colunas_esperadas].isnull().sum().sum())
        self.assertEqual(
            nulos_totais,
            0,
            f"Dados incompletos: {nulos_totais} valores nulos encontrados no painel."
        )

    def test_11_dataset_value_ranges_physical_boundaries(self):
        """
        Teste 11: Asserção de limites físicos e consistência agronômica dos dados.
        Limites biofísicos validados:
        - Produtividade agrícola: 100 kg/ha <= Y <= 150.000 kg/ha.
        - Precipitação anual: 100 mm <= P <= 4.000 mm.
        - Temperatura média: 10.0 °C <= T <= 45.0 °C.
        - Índice SPEI-3m: -4.0 <= SPEI <= +4.0.
        - Séries temporais: Anos estritamente no intervalo [2000, 2024].
        - Domínio de países: Conjunto discreto {'Brasil', 'Mexico'}.
        - Domínio de classes climáticas: {'Normal', 'Seca Moderada', 'Seca Severa'}.
        """
        # Produtividade (kg/ha)
        self.assertTrue(
            bool((self.df["produtividade_kg_ha"] >= 100.0).all()),
            "Produtividade com valores fisicamente improváveis (< 100 kg/ha)."
        )
        self.assertTrue(
            bool((self.df["produtividade_kg_ha"] <= 150000.0).all()),
            "Produtividade com valores excessivos (> 150.000 kg/ha)."
        )

        # Precipitação (mm)
        self.assertTrue(
            bool((self.df["precipitacao_mm"] >= 100.0).all()),
            "Precipitação abaixo de limites plausíveis (< 100 mm)."
        )
        self.assertTrue(
            bool((self.df["precipitacao_mm"] <= 4000.0).all()),
            "Precipitação acima de limites plausíveis (> 4.000 mm)."
        )

        # Temperatura (°C)
        self.assertTrue(
            bool((self.df["temp_media"] >= 10.0).all()),
            "Temperatura média abaixo de 10.0 °C."
        )
        self.assertTrue(
            bool((self.df["temp_media"] <= 45.0).all()),
            "Temperatura média acima de 45.0 °C."
        )

        # SPEI-3m
        self.assertTrue(
            bool((self.df["spei_3m"] >= -4.0).all()),
            "SPEI-3m abaixo de limites climatológicos (< -4.0)."
        )
        self.assertTrue(
            bool((self.df["spei_3m"] <= 4.0).all()),
            "SPEI-3m acima de limites climatológicos (> 4.0)."
        )

        # Anos
        self.assertEqual(int(self.df["ano"].min()), 2000)
        self.assertEqual(int(self.df["ano"].max()), 2024)

        # Países
        paises_unicos = set(self.df["pais"].unique())
        self.assertEqual(paises_unicos, {"Brasil", "Mexico"})

        # Status do clima
        classes_clima = set(self.df["status_clima"].unique())
        self.assertTrue(classes_clima.issubset({"Normal", "Seca Moderada", "Seca Severa"}))

    def test_12_statistical_hypothesis_testing(self):
        """
        Teste 12: Inferência Estatística Formal - ANOVA One-Way e Testes t de Student.
        Valida que o impacto da seca severa sobre os índices relativos de produtividade:
        - É altamente significativo via ANOVA One-Way (p < 0.001) para o Brasil.
        - É altamente significativo via ANOVA One-Way (p < 0.001) para o México.
        - Teste t de Student comparando safras em Clima Normal vs. Seca Severa
          produz valor-p < 0.001 com queda percentual de rendimento estritamente positiva (> 0).
        """
        resultados = executar_testes_agroclimaticos(self.df)

        # ANOVA One-Way Brasil
        p_anova_br = resultados["anova_brasil"]["p_value"]
        self.assertLess(
            p_anova_br,
            0.001,
            f"ANOVA Brasil valor-p ({p_anova_br:.2e}) não atingiu significância p < 0.001"
        )
        self.assertTrue(resultados["anova_brasil"]["significativo"])

        # ANOVA One-Way México
        p_anova_mx = resultados["anova_mexico"]["p_value"]
        self.assertLess(
            p_anova_mx,
            0.001,
            f"ANOVA México valor-p ({p_anova_mx:.2e}) não atingiu significância p < 0.001"
        )
        self.assertTrue(resultados["anova_mexico"]["significativo"])

        # Teste t Brasil: Normal vs Seca Severa
        p_t_br = resultados["ttest_impacto_seca_brasil"]["p_value"]
        queda_br = resultados["ttest_impacto_seca_brasil"]["queda_media_pct"]
        self.assertLess(
            p_t_br,
            0.001,
            f"Teste t Brasil valor-p ({p_t_br:.2e}) não atingiu significância p < 0.001"
        )
        self.assertGreater(
            queda_br,
            0.0,
            "Queda de produtividade na seca severa do Brasil deve ser positiva."
        )

        # Teste t México: Normal vs Seca Severa
        p_t_mx = resultados["ttest_impacto_seca_mexico"]["p_value"]
        queda_mx = resultados["ttest_impacto_seca_mexico"]["queda_media_pct"]
        self.assertLess(
            p_t_mx,
            0.001,
            f"Teste t México valor-p ({p_t_mx:.2e}) não atingiu significância p < 0.001"
        )
        self.assertGreater(
            queda_mx,
            0.0,
            "Queda de produtividade na seca severa do México deve ser positiva."
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
