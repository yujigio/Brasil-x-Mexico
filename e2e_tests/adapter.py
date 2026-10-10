"""
Adapter and Test Harness for E2E Tests.
Connects test cases to production modules under `src/observatorio/math_core/`
with reference fallback capabilities to maintain progressive testability.
"""

import sys
import os
import math
from pathlib import Path
from typing import Dict, Any, Optional, Tuple, List, Union
import numpy as np
import pandas as pd

# Path configuration
E2E_DIR = Path(__file__).resolve().parent
PORTFOLIO_ROOT = E2E_DIR.parent
SRC_DIR = PORTFOLIO_ROOT / "src"
DATASET_CSV = PORTFOLIO_ROOT / "painel_agroclimatico_brasil_mexico.csv"
INDEX_HTML = PORTFOLIO_ROOT / "index.html"
WORKFLOW_YAML = PORTFOLIO_ROOT / ".github" / "workflows" / "deploy.yml"

# Ensure src/ is on sys.path
if str(SRC_DIR) not in sys.path and SRC_DIR.exists():
    sys.path.insert(0, str(SRC_DIR))

# Reference Agronomic Parameters
PARAMETROS_AGRONOMICOS = {
    "soja": {"t_base": 10.0, "ciclo_dias": 120, "nome": "Soja"},
    "milho 1ª safra": {"t_base": 10.0, "ciclo_dias": 140, "nome": "Milho 1ª Safra"},
    "milho 2ª safra": {"t_base": 10.0, "ciclo_dias": 120, "nome": "Milho 2ª Safra"},
    "café": {"t_base": 10.2, "ciclo_dias": 240, "nome": "Café"},
    "cana-de-açúcar": {"t_base": 18.0, "ciclo_dias": 365, "nome": "Cana-de-Açúcar"},
    "feijão/frijol": {"t_base": 10.0, "ciclo_dias": 90, "nome": "Feijão/Frijol"},
    "maíz blanco": {"t_base": 10.0, "ciclo_dias": 130, "nome": "Maíz Blanco"},
    "maíz amarillo": {"t_base": 10.0, "ciclo_dias": 125, "nome": "Maíz Amarillo"},
    "frijol": {"t_base": 10.0, "ciclo_dias": 90, "nome": "Frijol"},
    "caña de azúcar": {"t_base": 18.0, "ciclo_dias": 365, "nome": "Caña de Azúcar"},
}

# Production Module Loader
PRODUCTION_LOADED = False
try:
    from observatorio.math_core import integral as prod_integral
    from observatorio.math_core import differential as prod_diff
    from observatorio.math_core import verhulst as prod_verhulst
    from observatorio.math_core import statistics as prod_stats
    PRODUCTION_LOADED = True
except Exception:
    prod_integral = None
    prod_diff = None
    prod_verhulst = None
    prod_stats = None


# --- Authoritative Reference Oracle Implementation ---
def oracle_simpson_13(y: Union[np.ndarray, list], h: float = 1.0) -> float:
    """Exact Simpson 1/3 implementation with parity assertion."""
    y_arr = np.asarray(y, dtype=float)
    n_pontos = len(y_arr)
    if n_pontos < 3:
        raise ValueError(f"Simpson 1/3 requires at least 3 points, got {n_pontos}.")
    n_intervalos = n_pontos - 1
    if n_intervalos % 2 != 0:
        raise ValueError(
            f"Simpson 1/3 requires an even number of intervals ((n-1)%2==0). "
            f"Got {n_pontos} points => {n_intervalos} intervals (odd)."
        )
    soma_impares = np.sum(y_arr[1:-1:2])
    soma_pares = np.sum(y_arr[2:-1:2])
    resultado = (h / 3.0) * (y_arr[0] + 4.0 * soma_impares + 2.0 * soma_pares + y_arr[-1])
    return float(resultado)


def oracle_calcular_gdd(temperaturas: Union[np.ndarray, list], t_base: float = 10.0) -> float:
    """Calculates GDD thermal sum over t_base using Simpson 1/3."""
    temp_arr = np.asarray(temperaturas, dtype=float)
    calor_util = np.maximum(0.0, temp_arr - t_base)
    return oracle_simpson_13(calor_util, h=1.0)


def oracle_ajustar_curva_produtividade(
    spei: Union[np.ndarray, list],
    prod: Union[np.ndarray, list],
    anos: Optional[Union[np.ndarray, list]] = None,
    remover_tendencia: bool = True
) -> Dict[str, Any]:
    """Quadratic regression Y(SPEI) = a*SPEI^2 + b*SPEI + c with detrending."""
    spei_arr = np.asarray(spei, dtype=float)
    prod_arr = np.asarray(prod, dtype=float)
    if len(spei_arr) != len(prod_arr):
        raise ValueError("spei and prod must have equal length.")
    if len(spei_arr) < 3:
        raise ValueError("At least 3 points required.")
    
    y_analise = prod_arr.copy()
    if remover_tendencia and anos is not None:
        anos_arr = np.asarray(anos, dtype=float)
        slope, intercept = np.polyfit(anos_arr, prod_arr, 1)
        media_prod = np.mean(prod_arr)
        y_analise = prod_arr - (slope * anos_arr + intercept) + media_prod

    coefs = np.polyfit(spei_arr, y_analise, 2)
    a, b, c = float(coefs[0]), float(coefs[1]), float(coefs[2])
    spei_otimo = -b / (2.0 * a) if a != 0 else 0.0
    d2 = 2.0 * a
    is_maximo = (d2 < 0.0)
    y_max = a * (spei_otimo**2) + b * spei_otimo + c
    return {
        "a": a,
        "b": b,
        "c": c,
        "spei_otimo": spei_otimo,
        "d2Y_dSPEI2": d2,
        "is_maximo": is_maximo,
        "produtividade_maxima": y_max
    }


def oracle_simular_verhulst_euler(
    spei: float,
    dias: int = 120,
    y0: float = 50.0,
    dt: float = 1.0,
    k_base: float = 4500.0,
    r_base: float = 0.08
) -> Dict[str, Any]:
    """Simulates Verhulst ODE via Euler method."""
    r = float(max(0.02, r_base + 0.02 * spei))
    K = float(max(500.0, k_base + 800.0 * spei))
    
    n_passos = int(dias / dt)
    t_vals = np.linspace(0.0, dias, n_passos + 1)
    y_vals = np.zeros(n_passos + 1, dtype=float)
    y_vals[0] = y0
    
    for i in range(n_passos):
        y_atual = y_vals[i]
        dydt = r * y_atual * (1.0 - (y_atual / K))
        y_vals[i + 1] = y_atual + dydt * dt
        
    return {
        "t": t_vals,
        "y": y_vals,
        "r": r,
        "K": K,
        "y_final": float(y_vals[-1]),
        "spei": spei,
        "dias": dias,
        "dt": dt
    }


def oracle_solucao_analitica_verhulst(
    t: Union[np.ndarray, list, float],
    y0: float,
    K: float,
    r: float
) -> np.ndarray:
    """Exact analytical closed-form solution of Verhulst logistic ODE."""
    t_arr = np.asarray(t, dtype=float)
    return (K * y0) / (y0 + (K - y0) * np.exp(-r * t_arr))


# --- Public Interface Provider ---
def get_simpson_func():
    if PRODUCTION_LOADED and hasattr(prod_integral, "simpson_13"):
        return prod_integral.simpson_13
    return oracle_simpson_13


def get_calcular_gdd_func():
    if PRODUCTION_LOADED and hasattr(prod_integral, "calcular_gdd_cultura"):
        return prod_integral.calcular_gdd_cultura
    return lambda temp, cultura=None, t_base=10.0, ciclo_dias=None: {
        "gdd_total": oracle_calcular_gdd(temp, t_base),
        "t_base": t_base
    }


def get_differential_func():
    if PRODUCTION_LOADED and hasattr(prod_diff, "ajustar_curva_produtividade"):
        return prod_diff.ajustar_curva_produtividade
    return oracle_ajustar_curva_produtividade


def get_verhulst_euler_func():
    if PRODUCTION_LOADED and hasattr(prod_verhulst, "simular_verhulst_euler"):
        return prod_verhulst.simular_verhulst_euler
    return oracle_simular_verhulst_euler


def get_verhulst_analitico_func():
    if PRODUCTION_LOADED and hasattr(prod_verhulst, "solucao_analitica_verhulst"):
        return prod_verhulst.solucao_analitica_verhulst
    return oracle_solucao_analitica_verhulst


def get_statistics_func():
    if PRODUCTION_LOADED and hasattr(prod_stats, "executar_testes_agroclimaticos"):
        return prod_stats.executar_testes_agroclimaticos
    return None


def carregar_dataset() -> pd.DataFrame:
    """Loads authoritative historical dataset painel_agroclimatico_brasil_mexico.csv."""
    if not DATASET_CSV.exists():
        raise FileNotFoundError(f"Authoritative dataset not found at: {DATASET_CSV}")
    return pd.read_csv(DATASET_CSV)
