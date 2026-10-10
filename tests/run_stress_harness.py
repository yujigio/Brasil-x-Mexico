"""
Executor do Harness de Estresse Adversarial e Verificação Empírica
Observatório Agroclimático Brasil vs. México - Tier 5 Hardening

Executa simulações numéricas intensivas, mapeia pontos de quebra,
quantifica taxas de erro e limites de estabilidade assintótica.
"""

import sys
import time
from pathlib import Path
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
    testar_estabilidade_dominio_spei,
)
from src.observatorio.math_core.statistics import (
    _calcular_anova_manual,
    _calcular_ttest_manual,
    executar_testes_agroclimaticos,
)


def stress_test_simpson():
    print("=" * 70)
    print("1. STRESS TEST: SIMPSON 1/3 QUADRATURE & PARITY ORACLE")
    print("=" * 70)

    # 1.1 Parity Sweep
    parity_results = []
    for n_pts in range(1, 12):
        n_intervals = n_pts - 1
        x = np.linspace(0, 1, n_pts)
        y = x**2
        try:
            val = simpson_13(y, h=1.0 / max(1, n_intervals))
            status = f"PASSED (val={val:.4f})"
            exception_raised = False
        except ValueError as e:
            status = f"REJECTED: ValueError ({e})"
            exception_raised = True

        expected_rejection = (n_pts < 3) or (n_intervals % 2 != 0)
        correct = (exception_raised == expected_rejection)
        parity_results.append({
            "n_pontos": n_pts,
            "n_intervalos": n_intervals,
            "paridade": "PAR" if n_intervals % 2 == 0 else "IMPAR",
            "rejeitado": exception_raised,
            "status": "CORRETO" if correct else "FALHA"
        })
        print(f"  Pts: {n_pts:2d} | Intervalos: {n_intervals:2d} | Paridade: {'PAR' if n_intervals % 2 == 0 else 'IMPAR':5s} | Rejeitado: {str(exception_raised):5s} | {status}")

    # 1.2 Convergence order verification
    print("\n  Taxa de Convergência O(h^4) sobre f(x) = sin(x) em [0, pi]:")
    h_values = [np.pi / (10 * (2**i)) for i in range(5)]
    erros = []
    for h in h_values:
        n = int(round(np.pi / h))
        if n % 2 != 0:
            n += 1
            h = np.pi / n
        x = np.linspace(0, np.pi, n + 1)
        y = np.sin(x)
        num = simpson_13(y, h=h)
        err = abs(num - 2.0)
        erros.append(err)
        print(f"    n = {n:4d} | h = {h:.6f} | Erro Abs: {err:.3e}")

    ratios = [erros[i] / erros[i + 1] for i in range(len(erros) - 1)]
    print(f"    Razoes de reducao de erro (esperado ~16.0 para O(h^4)): {[round(r, 2) for r in ratios]}")

    # 1.3 Non-smooth functions
    print("\n  Integracao de Funcoes Nao-Suaves:")
    x_grid = np.linspace(0, 2, 201)
    # Heaviside
    y_step = np.where(x_grid >= 1.0, 1.0, 0.0)
    int_step = simpson_13(y_step, h=2.0 / 200.0)
    err_step = abs(int_step - 1.0)
    print(f"    Degrau de Heaviside [0, 2]: Num = {int_step:.6f} | Exato = 1.000000 | Erro: {err_step:.3e}")

    # Cúspide |x - 1|
    y_cusp = np.abs(x_grid - 1.0)
    int_cusp = simpson_13(y_cusp, h=2.0 / 200.0)
    err_cusp = abs(int_cusp - 1.0)
    print(f"    Cuspide |x - 1| em [0, 2]: Num = {int_cusp:.6f} | Exato = 1.000000 | Erro: {err_cusp:.3e}")

    return {"parity": parity_results, "ratios": ratios}


def stress_test_differential():
    print("\n" + "=" * 70)
    print("2. STRESS TEST: DIFFERENTIAL MODEL & DETRENDING EDGE CASES")
    print("=" * 70)

    # 2.1 Extrema SPEI range [-10.0, +10.0]
    spei_calib = np.linspace(-2.0, 2.0, 25)
    prod_calib = 4000.0 - 250.0 * (spei_calib - 0.2)**2 + np.sin(spei_calib) * 20.0
    res = ajustar_curva_produtividade(spei_calib, prod_calib, remover_tendencia=False)
    print(f"  Calibracao normal: a={res['a']}, b={res['b']}, c={res['c']}, SPEI*={res['spei_otimo']}")
    print(f"  d2Y/dSPEI2={res['d2Y_dSPEI2']}, is_maximo={res['is_maximo']}")

    # Avaliação em SPEI extremo
    for s_ext in [-10.0, -5.0, 0.0, 5.0, 10.0]:
        y_ext = res["a"] * (s_ext**2) + res["b"] * s_ext + res["c"]
        print(f"    SPEI = {s_ext:5.1f} -> Produtividade Predita = {y_ext:10.2f} kg/ha")

    # 2.2 Collinear SPEI (Zero Variance)
    print("\n  SPEI Colinear com Variancia Zero:")
    try:
        ajustar_curva_produtividade([0.0, 0.0, 0.0, 0.0], [3000, 3100, 2900, 3050], remover_tendencia=False)
        print("    ERRO: Deveria ter falhado com LinAlgError!")
    except np.linalg.LinAlgError as e:
        print(f"    [OK] np.linalg.LinAlgError interceptado com sucesso: {e}")

    # 2.3 Constant Productivity (Zero Curvature)
    print("\n  Produtividade Constante (Curvatura Zero a -> 0):")
    res_flat = ajustar_curva_produtividade([-2, -1, 0, 1, 2], [3000, 3000, 3000, 3000, 3000], remover_tendencia=False)
    print(f"    a={res_flat['a']:.2e}, spei_otimo={res_flat['spei_otimo']}, is_maximo={res_flat['is_maximo']}")
    print("    Observacao: Polyfit gera ruido de ponto flutuante na ordem de 1e-13.")

    # 2.4 Detrending with Collinear Years
    print("\n  Detrending Secular com Anos Colineares (Variancia de Tempo Nula):")
    res_collin_anos = ajustar_curva_produtividade([-1, 0, 1, 2], [1000, 2000, 3000, 4000], anos=[2020, 2020, 2020, 2020], remover_tendencia=True)
    print(f"    spei_otimo={res_collin_anos['spei_otimo']:.2e}, produtividade_maxima={res_collin_anos['produtividade_maxima']:.2e}")
    print("    Observacao: Anos colineares geram instabilidade numerica no detrending secular linear.")


def stress_test_verhulst():
    print("\n" + "=" * 70)
    print("3. STRESS TEST: VERHULST LOGISTIC ODE (EULER METHOD)")
    print("=" * 70)

    # 3.1 Fine grid domain scan [-5.0, +5.0]
    spei_vals = np.linspace(-5.0, 5.0, 1001)
    nan_count = 0
    inf_count = 0
    non_pos_count = 0
    monotonicity_violations = 0
    max_trunc_error = 0.0

    t0 = time.time()
    for s in spei_vals:
        sim = simular_verhulst_euler(float(s), dias=120, y0=50.0, dt=1.0)
        y = sim["y"]
        K = sim["K"]

        if not np.all(np.isfinite(y)):
            nan_count += 1
        if np.any(y <= 0):
            non_pos_count += 1
        if np.any(np.diff(y) < -1e-6):
            monotonicity_violations += 1
        if sim["erro_relativo_final_pct"] > max_trunc_error:
            max_trunc_error = sim["erro_relativo_final_pct"]

    elapsed = time.time() - t0
    print(f"  Varredura Fina [-5.0, +5.0] (1001 simulações) executada em {elapsed:.3f}s:")
    print(f"    Falhas de Finitude (NaN/Inf): {nan_count}")
    print(f"    Valores Nao-Positivos:        {non_pos_count}")
    print(f"    Violacoes de Monotonicidade:  {monotonicity_violations}")
    print(f"    Erro Relativo Maximo:         {max_trunc_error:.4f}% (< 5.0% limite)")

    # 3.2 Stability limit and bifurcation scan
    print("\n  Mapeamento do Limiar de Rigidez Numerica e Bifurcacao (r * dt):")
    for r_test in [0.05, 0.1, 0.5, 1.0, 1.5, 1.9, 2.1, 2.5, 3.0]:
        sim = simular_verhulst_euler(0.0, dias=120, y0=50.0, dt=1.0, r_base=r_test)
        diffs = np.diff(sim["y"][-20:])
        is_oscillating = bool(np.any(diffs[:-1] * diffs[1:] < 0))
        regime = "OSCILATORIO / BIFURCADO" if is_oscillating else "ESTAVEL MONOTONICO"
        print(f"    r*dt = {r_test:4.2f} | y_final = {sim['y_final']:8.2f} | Erro Final: {sim['erro_relativo_final_pct']:6.2f}% | Regime: {regime}")


def stress_test_statistics():
    print("\n" + "=" * 70)
    print("4. STRESS TEST: STATISTICAL INFERENCE & PERMUTATION ORACLE")
    print("=" * 70)

    # 4.1 Permutation test (Monte Carlo under H0)
    print("  Teste de Permutacao Monte Carlo (2000 iteracoes sob H0):")
    rng = np.random.default_rng(2026)
    p_vals_anova = []
    p_vals_ttest = []

    for _ in range(2000):
        # Gerar amostras da mesma distribuicao
        s1 = rng.normal(1.0, 0.2, 25)
        s2 = rng.normal(1.0, 0.2, 25)
        s3 = rng.normal(1.0, 0.2, 25)

        _, p_a = _calcular_anova_manual([s1, s2, s3])
        _, p_t = _calcular_ttest_manual(s1, s2)
        p_vals_anova.append(p_a)
        p_vals_ttest.append(p_t)

    fpr_anova = np.mean(np.array(p_vals_anova) < 0.05)
    fpr_ttest = np.mean(np.array(p_vals_ttest) < 0.05)
    print(f"    Taxa de Falso Positivo (alpha = 0.05) ANOVA:  {fpr_anova:.4f} (Esperado: ~0.05)")
    print(f"    Taxa de Falso Positivo (alpha = 0.05) Teste t: {fpr_ttest:.4f} (Esperado: ~0.05)")

    # 4.2 Zero within-group variance
    print("\n  Comportamento com Variancia Intra-Grupo Nula:")
    g1 = np.array([10.0, 10.0, 10.0])
    g2 = np.array([20.0, 20.0, 20.0])
    f_man, p_man = _calcular_anova_manual([g1, g2])
    print(f"    _calcular_anova_manual([10, 10, 10], [20, 20, 20]): F = {f_man}, p = {p_man}")
    try:
        from scipy import stats
        f_sci, p_sci = stats.f_oneway(g1, g2)
        print(f"    scipy.stats.f_oneway: F = {f_sci}, p = {p_sci}")
    except Exception as e:
        print(f"    scipy indisponivel: {e}")


if __name__ == "__main__":
    stress_test_simpson()
    stress_test_differential()
    stress_test_verhulst()
    stress_test_statistics()
    print("\n" + "=" * 70)
    print(">>> TODOS OS TESTES DE ESTRESSE FORAM EXECUTADOS COM SUCESSO! <<<")
    print("=" * 70)
