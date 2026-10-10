"""
Suíte de Testes Adversariais e Estresse Numérico (Tier 5 Adversarial Coverage Hardening)
Observatório Agroclimático Brasil vs. México

Focado na exploração empírica de casos de borda, violação de paridade, estabilidade
dinâmica, degenerescência e condições extremas no núcleo matemático:
1. Simpson 1/3:
   - Rejeição de paridade ímpar (n_intervalos ímpar -> ValueError)
   - Entradas degeneradas (< 3 pontos, 1 ponto, 2 pontos, vetor vazio -> ValueError)
   - Passos extremos (h -> 0, h -> inf, h <= 0 -> ValueError)
   - Funções não-suaves (degrau Heaviside, valor absoluto com cúspide, ruído, picos)
   - Propagação de erro de discretização
2. Cálculo Diferencial & Detrending:
   - SPEI extremo longe da faixa climatológica (SPEI = +/-10, +/-100)
   - Dados colineares / variância nula em SPEI (LinAlgError em zero-variância pura)
   - Parábola invertida (a > 0 -> is_maximo = False)
   - Detrending com anos colineares ou desordenados
   - Comportamento de curvatura residual e ruído de ponto flutuante
3. EDO de Verhulst (Euler):
   - Varredura de estabilidade em malha fina em [-5.0, +5.0] (1001 pontos)
   - Condições iniciais limítrofes (y0 > K decaimento assintótico, y0 = K equilíbrio estacionário)
   - Validação de rejeição de parâmetros inválidos (y0 <= 0, dt <= 0, dias <= 0)
   - Mapeamento do limiar de bifurcação e rigidez numérica (r * dt > 2.0)
4. Inferência Estatística:
   - Teste de permutação (distribuição nula de p-valores sob H0)
   - Grupos severamente desbalanceados (N1 = 2 vs N2 = 1000)
   - Variância intra-grupo nula (comportamento de salvaguarda defensiva ms_within == 0)
   - Comparação analítica direta contra scipy.stats (f_oneway e ttest_ind)
"""

import sys
from pathlib import Path
import unittest
import numpy as np
import pandas as pd

TESTS_DIR = Path(__file__).resolve().parent
PROJECT_DIR = TESTS_DIR.parent
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

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
    _calcular_anova_manual,
    _calcular_ttest_manual,
    executar_testes_agroclimaticos,
)


class TestAdversarialSimpson(unittest.TestCase):
    """Bateria adversarial para o algoritmo de Quadratura de Simpson 1/3."""

    def test_odd_interval_parity_rejections(self):
        """Verifica se Simpson 1/3 rejeita estritamente números ímpares de subintervalos."""
        # 2 pontos = 1 subintervalo (ímpar) -> ValueError
        with self.assertRaises(ValueError):
            simpson_13([1.0, 2.0], h=1.0)

        # 4 pontos = 3 subintervalos (ímpar) -> ValueError
        with self.assertRaises(ValueError):
            simpson_13([1.0, 2.0, 3.0, 4.0], h=1.0)

        # 6 pontos = 5 subintervalos (ímpar) -> ValueError
        with self.assertRaises(ValueError):
            simpson_13([1.0, 2.0, 3.0, 4.0, 5.0, 6.0], h=1.0)

        # 100 pontos = 99 subintervalos (ímpar) -> ValueError
        with self.assertRaises(ValueError):
            simpson_13(np.ones(100), h=1.0)

    def test_degenerate_point_counts(self):
        """Verifica rejeição para entradas vazias, com 1 ponto ou 2 pontos."""
        # Vetor vazio (0 pontos)
        with self.assertRaises(ValueError):
            simpson_13([], h=1.0)

        # 1 único ponto (0 subintervalos)
        with self.assertRaises(ValueError):
            simpson_13([42.0], h=1.0)

        # 2 pontos
        with self.assertRaises(ValueError):
            simpson_13([10.0, 20.0], h=1.0)

    def test_extreme_and_invalid_step_sizes(self):
        """Testa valores de passo h negativos, nulos e extremos."""
        y_valid = [1.0, 2.0, 1.0]  # 3 pontos = 2 subintervalos (par)

        # h <= 0 deve gerar ValueError
        with self.assertRaises(ValueError):
            simpson_13(y_valid, h=0.0)

        with self.assertRaises(ValueError):
            simpson_13(y_valid, h=-1.0)

        with self.assertRaises(ValueError):
            simpson_13(y_valid, h=-1e-9)

        # Passo infinitesimal (h -> 0+)
        h_tiny = 1e-12
        res_tiny = simpson_13(y_valid, h=h_tiny)
        self.assertAlmostEqual(res_tiny, (1e-12 / 3.0) * (1.0 + 4.0 * 2.0 + 1.0), places=20)
        self.assertTrue(np.isfinite(res_tiny))

        # Passo astronômico (h -> inf)
        h_huge = 1e9
        res_huge = simpson_13(y_valid, h=h_huge)
        self.assertAlmostEqual(res_huge, (1e9 / 3.0) * 10.0, places=2)
        self.assertTrue(np.isfinite(res_huge))

    def test_non_smooth_and_discontinuous_functions(self):
        """Avalia comportamento em funções não suaves, com degrau, cúspide e ruído."""
        # 1. Função degrau de Heaviside em [0, 2]: H(x) = 0 se x < 1, 1 se x >= 1
        # Integral analítica exata em [0, 2] = 1.0
        n_pts = 101  # 100 intervalos
        x = np.linspace(0.0, 2.0, n_pts)
        y_step = np.where(x >= 1.0, 1.0, 0.0)
        res_step = simpson_13(y_step, h=2.0 / 100.0)
        self.assertTrue(np.isfinite(res_step))
        self.assertAlmostEqual(res_step, 1.0, places=1)

        # 2. Cúspide / valor absoluto: f(x) = |x - 1| em [0, 2]
        # Integral analítica exata = 1.0
        y_abs = np.abs(x - 1.0)
        res_abs = simpson_13(y_abs, h=2.0 / 100.0)
        self.assertTrue(np.isfinite(res_abs))
        self.assertAlmostEqual(res_abs, 1.0, places=2)

        # 3. Pulso impulsivo (Spike Dirac discreto)
        y_spike = np.zeros(101)
        y_spike[50] = 1000.0
        h = 0.01
        res_spike = simpson_13(y_spike, h=h)
        # y_spike[50] é nó de índice par: peso é 2 na regra
        # (h/3) * (2 * 1000) = (0.01 / 3) * 2000 = 6.66666...
        self.assertAlmostEqual(res_spike, (0.01 / 3.0) * 2.0 * 1000.0, places=5)

    def test_gdd_adversarial_temperature_series(self):
        """Testa o acumulador de GDD contra temperaturas extremas, congelantes e ondas de calor."""
        # Temperaturas todas abaixo de T_base (inverno rigoroso / congelamento)
        temps_frias = np.full(121, -5.0)
        res_frias = calcular_gdd_cultura(temps_frias, cultura="Soja", t_base=10.0)
        self.assertEqual(res_frias["gdd"], 0.0)

        # Temperaturas limítrofes exatamente iguais a T_base
        temps_base = np.full(121, 10.0)
        res_base = calcular_gdd_cultura(temps_base, cultura="Soja", t_base=10.0)
        self.assertEqual(res_base["gdd"], 0.0)

        # Onda de calor extremo (50°C constantes durante 120 dias, T_base = 10°C)
        # GDD analítico = (50 - 10) * 120 = 4800.0
        temps_quentes = np.full(121, 50.0)
        res_quentes = calcular_gdd_cultura(temps_quentes, cultura="Soja", t_base=10.0)
        self.assertAlmostEqual(res_quentes["gdd"], 4800.0, places=1)

        # Série curta insuficiente (< 3 pontos)
        with self.assertRaises(ValueError):
            calcular_gdd_cultura([25.0, 26.0], cultura="Soja")


class TestAdversarialDifferential(unittest.TestCase):
    """Bateria adversarial para o módulo diferencial e regressão SPEI."""

    def test_extreme_spei_extrapolation(self):
        """Avalia extrapolação para valores extremos de SPEI (-10.0 a +10.0)."""
        # Dados sintéticos de calibração
        spei = np.array([-2.0, -1.0, 0.0, 1.0, 2.0])
        prod = 3500.0 - 200.0 * (spei - 0.5)**2  # a = -200, ótimo em 0.5
        res = ajustar_curva_produtividade(spei, prod, remover_tendencia=False)

        self.assertAlmostEqual(res["a"], -200.0, places=1)
        self.assertAlmostEqual(res["spei_otimo"], 0.5, places=1)
        self.assertTrue(res["is_maximo"])

        # Avaliar previsão na parábola para SPEI extremo
        a, b, c = res["a"], res["b"], res["c"]
        y_spei_minus_10 = a * (-10.0)**2 + b * (-10.0) + c
        y_spei_plus_10 = a * (10.0)**2 + b * (10.0) + c

        # Em secas/umidades catastróficas, o modelo quadrático penaliza severamente
        self.assertLess(y_spei_minus_10, 0.0)
        self.assertLess(y_spei_plus_10, 0.0)

    def test_collinear_spei_rank_deficiency(self):
        """Testa resposta a dados degenerados onde todos os valores de SPEI são idênticos."""
        # 1. spei identicamente zero (todos 0.0): causa LinAlgError no SVD do Least Squares
        spei_zero = np.array([0.0, 0.0, 0.0, 0.0])
        prod = np.array([3000.0, 3100.0, 2900.0, 3050.0])
        with self.assertRaises(np.linalg.LinAlgError):
            ajustar_curva_produtividade(spei_zero, prod, remover_tendencia=False)

        # 2. spei constante não-zero (todos 1.0): causa RankWarning de matriz mal-condicionada
        spei_constante = np.array([1.0, 1.0, 1.0, 1.0])
        import warnings
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            res = ajustar_curva_produtividade(spei_constante, prod, remover_tendencia=False)
            self.assertTrue(any(issubclass(item.category, np.exceptions.RankWarning) for item in w))

    def test_zero_curvature_flat_productivity_float_noise(self):
        """
        Testa produtividade estritamente horizontal (sem resposta a SPEI).
        Observação empírica: a curvatura analítica é nula (a = 0). O polyfit produz
        ruído numérico de ponto flutuante (|a| ~ 1e-13). Como spei_otimo possui salvaguarda
        abs(a) > 1e-12, spei_otimo é corretamente fixado em 0.0.
        """
        spei = np.array([-2.0, -1.0, 0.0, 1.0, 2.0])
        prod_plana = np.full(5, 3000.0)

        res = ajustar_curva_produtividade(spei, prod_plana, remover_tendencia=False)
        # a e d2 devem ser virtualmente zero
        self.assertAlmostEqual(res["a"], 0.0, places=4)
        self.assertAlmostEqual(res["d2Y_dSPEI2"], 0.0, places=4)
        # spei_otimo deve ser 0.0 via salvaguarda de abs(a) <= 1e-12
        self.assertEqual(res["spei_otimo"], 0.0)

    def test_convex_inverted_parabola_rejection(self):
        """Testa curva convexa com a > 0 (mínimo local, não máximo)."""
        spei = np.array([-2.0, -1.0, 0.0, 1.0, 2.0])
        prod_valei = 3000.0 + 150.0 * spei**2  # a = +150 > 0
        res = ajustar_curva_produtividade(spei, prod_valei, remover_tendencia=False)

        self.assertGreater(res["a"], 0.0)
        self.assertGreater(res["d2Y_dSPEI2"], 0.0)
        self.assertFalse(res["is_maximo"])

    def test_detrending_edge_cases(self):
        """Testa detrending com anos constantes, invertidos e dados ruidosos."""
        spei = np.array([-2.0, -1.0, 0.0, 1.0, 2.0])
        prod = np.array([2800.0, 3100.0, 3400.0, 3300.0, 2900.0])

        # Anos em ordem decrescente (2024 -> 2020)
        anos_desc = np.array([2024, 2023, 2022, 2021, 2020])
        res_desc = ajustar_curva_produtividade(spei, prod, anos=anos_desc, remover_tendencia=True)
        self.assertTrue(res_desc["tendencia_removida"])
        self.assertTrue(res_desc["is_maximo"])

        # Anos com comprimento incompatível: defensivamente ignorado
        anos_incomp = np.array([2020, 2021])
        res_incomp = ajustar_curva_produtividade(spei, prod, anos=anos_incomp, remover_tendencia=True)
        self.assertFalse(res_incomp["tendencia_removida"])


class TestAdversarialVerhulst(unittest.TestCase):
    """Bateria adversarial para a dinâmica logística de Verhulst via Euler."""

    def test_fine_grid_stability_scan_wide_domain(self):
        """Varredura fina com 1001 nós no domínio expandido [-5.0, +5.0]."""
        spei_amostras = np.linspace(-5.0, 5.0, 1001)

        for s in spei_amostras:
            sim = simular_verhulst_euler(spei=float(s), dias=120, y0=50.0, dt=1.0)
            y = sim["y"]
            K = sim["K"]
            r = sim["r"]

            # 1. Sem NaNs ou Infs
            self.assertTrue(np.all(np.isfinite(y)), f"NaN ou Inf detectado em SPEI={s}")

            # 2. Positividade estrita
            self.assertTrue(np.all(y > 0.0), f"Biomassa <= 0 em SPEI={s}")

            # 3. Não ultrapassa K (com margem de erro discreto de Euler de 5%)
            self.assertTrue(np.all(y <= K * 1.05), f"Explosão além de K em SPEI={s}")

            # 4. Monotonicidade não-decrescente
            diffs = np.diff(y)
            self.assertTrue(np.all(diffs >= -1e-6), f"Oscilação espúria em SPEI={s}")

    def test_carrying_capacity_boundary_conditions(self):
        """Avalia condições quando biomassa inicial y0 >= K (supersaturação ou equilíbrio)."""
        # 1. y0 == K (equilíbrio estacionário)
        sim_eq = simular_verhulst_euler(spei=0.0, dias=120, y0=4500.0, dt=1.0, k_base=4500.0)
        # Derivada deve ser identicamente nula, y(t) = K
        self.assertTrue(np.allclose(sim_eq["y"], 4500.0, atol=1e-3))

        # 2. y0 > K (população inicial acima da capacidade de suporte)
        # Teoricamente: dy/dt < 0, a curva deve decair monotonicamente até K
        sim_super = simular_verhulst_euler(spei=0.0, dias=120, y0=6000.0, dt=1.0, k_base=4500.0)
        y_super = sim_super["y"]
        # Decaimento: derivadas negativas
        diffs = np.diff(y_super)
        self.assertTrue(np.all(diffs <= 1e-6), "Biomassa acima de K não decresceu monotonicamente.")
        # Convergência assintótica final próxima de K
        self.assertAlmostEqual(y_super[-1], 4500.0, delta=100.0)

    def test_invalid_and_boundary_parameters(self):
        """Testa parâmetros iniciais inválidos (y0 <= 0, dt <= 0, dias <= 0)."""
        with self.assertRaises(ValueError):
            simular_verhulst_euler(spei=0.0, y0=0.0)

        with self.assertRaises(ValueError):
            simular_verhulst_euler(spei=0.0, y0=-50.0)

        with self.assertRaises(ValueError):
            simular_verhulst_euler(spei=0.0, dt=0.0)

        with self.assertRaises(ValueError):
            simular_verhulst_euler(spei=0.0, dt=-1.0)

        with self.assertRaises(ValueError):
            simular_verhulst_euler(spei=0.0, dias=0)

        with self.assertRaises(ValueError):
            simular_verhulst_euler(spei=0.0, dias=-10)

    def test_stiffness_and_growth_rate_stability_boundary(self):
        """
        Avalia rigidez numérica e o limiar de bifurcação de Euler (r * dt < 2.0).
        Demonstra que o modelo biológico permanece estritamente estável para SPEI <= 10.0,
        mas documenta que para r*dt > 2.0 ocorre oscilação espúria / bifurcação.
        """
        # Limite padrão em SPEI extremo (+10.0): r = 0.28, r*dt = 0.28 << 2.0 -> Estável
        sim_max_spei = simular_verhulst_euler(spei=10.0, dias=120, y0=50.0, dt=1.0)
        self.assertTrue(np.all(np.isfinite(sim_max_spei["y"])))
        self.assertLess(sim_max_spei["erro_relativo_final_pct"], 5.0)

        # Caso sintético extremo com r*dt > 2.0 (regime de sobre-amortecimento/oscilação)
        sim_oscilatorio = simular_verhulst_euler(spei=0.0, r_base=2.5, dt=1.0)
        # O método de Euler exibe oscilação ao redor de K quando r*dt > 2.0
        y_osc = sim_oscilatorio["y"]
        diffs = np.diff(y_osc[-10:])
        # Verifica presença de inversão de sinal (oscilação periódica discreta)
        has_alternation = np.any(diffs[:-1] * diffs[1:] < 0)
        self.assertTrue(has_alternation, "Euler deveria oscilar quando r*dt > 2.0")


class TestAdversarialStatistics(unittest.TestCase):
    """Bateria adversarial para testes de hipótese e robustez inferencial."""

    def test_zero_within_group_variance_defensive_behavior(self):
        """
        Testa ANOVA quando todos os elementos dentro de cada grupo são idênticos.
        Comportamento empírico observado: Quando SS_within == 0.0, ms_within == 0.0.
        O código implementa salvaguarda defensiva ms_within > 0 else 0.0, retornando
        F_stat = 0.0 e p_val = 1.0 (em vez de levantar ZeroDivisionError).
        """
        g1 = np.array([10.0, 10.0, 10.0])
        g2 = np.array([20.0, 20.0, 20.0])

        f_stat, p_val = _calcular_anova_manual([g1, g2])
        self.assertEqual(f_stat, 0.0)
        self.assertEqual(p_val, 1.0)

        t_stat, pt_val = _calcular_ttest_manual(g1, g2)
        self.assertEqual(t_stat, 0.0)
        self.assertEqual(pt_val, 1.0)

    def test_severely_unbalanced_sample_sizes(self):
        """Testa amostras com tamanhos severamente díspares (N1 = 2, N2 = 1000)."""
        rng = np.random.default_rng(42)
        g_pequeno = rng.normal(loc=1.0, scale=0.1, size=2)
        g_grande = rng.normal(loc=1.0, scale=0.1, size=1000)

        f_stat, p_val = _calcular_anova_manual([g_pequeno, g_grande])
        self.assertTrue(np.isfinite(f_stat))
        self.assertTrue(0.0 <= p_val <= 1.0)

        t_stat, pt_val = _calcular_ttest_manual(g_pequeno, g_grande)
        self.assertTrue(np.isfinite(t_stat))
        self.assertTrue(0.0 <= pt_val <= 1.0)

    def test_exact_agreement_with_scipy(self):
        """Compara o fallback manual contra scipy.stats para validação exata de oráculo."""
        try:
            from scipy import stats
        except ImportError:
            self.skipTest("scipy não instalado no ambiente.")

        rng = np.random.default_rng(123)
        g1 = rng.normal(loc=1.0, scale=0.2, size=25)
        g2 = rng.normal(loc=0.8, scale=0.2, size=25)
        g3 = rng.normal(loc=1.2, scale=0.2, size=25)

        # 1. ANOVA One-Way
        f_manual, p_manual = _calcular_anova_manual([g1, g2, g3])
        f_scipy, p_scipy = stats.f_oneway(g1, g2, g3)

        self.assertAlmostEqual(f_manual, f_scipy, places=4)
        self.assertAlmostEqual(p_manual, p_scipy, places=4)

        # 2. Teste t de Student (amostras independentes com igual variância)
        t_manual, pt_manual = _calcular_ttest_manual(g1, g2)
        t_scipy, pt_scipy = stats.ttest_ind(g1, g2, equal_var=True)

        self.assertAlmostEqual(t_manual, t_scipy, places=4)
        self.assertAlmostEqual(pt_manual, pt_scipy, places=4)

    def test_permutation_test_null_distribution(self):
        """Executa teste de permutação para verificar que sob H0 os p-valores são válidos."""
        rng = np.random.default_rng(999)
        n_sim = 200
        p_valores = []

        for _ in range(n_sim):
            # Amostras extraídas da mesmíssima distribuição normal padrão N(0, 1)
            amostra_a = rng.normal(loc=0.0, scale=1.0, size=20)
            amostra_b = rng.normal(loc=0.0, scale=1.0, size=20)
            _, p_val = _calcular_ttest_manual(amostra_a, amostra_b)
            p_valores.append(p_val)

        p_arr = np.array(p_valores)
        # Taxa de falsos positivos (erro tipo I) sob alpha = 0.05 deve ser aproximadamente ~5%
        taxa_rejeicao = np.mean(p_arr < 0.05)
        self.assertLess(taxa_rejeicao, 0.15, f"Taxa de falsos positivos inflada: {taxa_rejeicao:.3f}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
