"""
Tier 3: Cross-Feature Multi-Module Combinations.
Validates multi-module interactions and cross-feature workflows:
- Coupled SPEI perturbations driving both Yield regression & Verhulst ODE
- Multi-crop cross-country comparative sensitivity (Brazil rainfed vs Mexico irrigated)
- Combined thermal energy (Simpson GDD) and hydrological stress (SPEI)
- Correlation between detrended empirical yields and Verhulst dynamic carrying capacity
- End-to-end data extraction, detrending, differential optimization and ODE simulation
- Agronomic cycle length and thermal accumulation differentiation
"""

import unittest
import numpy as np
import pandas as pd

try:
    from e2e_tests.adapter import (
        carregar_dataset,
        get_simpson_func,
        get_calcular_gdd_func,
        get_differential_func,
        get_verhulst_euler_func,
        PARAMETROS_AGRONOMICOS,
    )
except (ImportError, ValueError):
    from adapter import (
        carregar_dataset,
        get_simpson_func,
        get_calcular_gdd_func,
        get_differential_func,
        get_verhulst_euler_func,
        PARAMETROS_AGRONOMICOS,
    )


class TestCrossFeatureCombinations(unittest.TestCase):
    """Tier 3 Suite: Cross-Feature Multi-Module Combinations."""

    def setUp(self):
        self.df = carregar_dataset()
        self.simpson = get_simpson_func()
        self.calc_gdd = get_calcular_gdd_func()
        self.ajustar = get_differential_func()
        self.euler = get_verhulst_euler_func()

    def test_01_coupled_spei_driving_yield_and_verhulst(self):
        """SPEI perturbation consistently drives both Differential Yield and Verhulst ODE."""
        # Baseline Normal: SPEI = 0.0
        # Severe Drought: SPEI = -2.2
        sub = self.df[(self.df["pais"] == "Brasil") & (self.df["cultura"] == "Soja")].sort_values("ano")
        diff_res = self.ajustar(sub["spei_3m"].values, sub["produtividade_kg_ha"].values, anos=sub["ano"].values)
        
        a, b, c = diff_res["a"], diff_res["b"], diff_res["c"]
        y_normal_diff = a * (0.0**2) + b * 0.0 + c
        y_drought_diff = a * ((-2.2)**2) + b * (-2.2) + c
        
        # Differential model indicates yield loss under drought
        self.assertLess(y_drought_diff, y_normal_diff)
        
        # Verhulst ODE simulation under same conditions
        sim_normal = self.euler(spei=0.0, dias=120)
        sim_drought = self.euler(spei=-2.2, dias=120)
        
        # Both models agree directionally on biomass suppression
        self.assertLess(sim_drought["y_final"], sim_normal["y_final"])
        self.assertLess(sim_drought["r"], sim_normal["r"])
        self.assertLess(sim_drought["K"], sim_normal["K"])

    def test_02_multi_crop_cross_country_comparative_sensitivity(self):
        """Compares climate response between rainfed Brazil crops and irrigated Mexico crops."""
        # Soja (BR) vs Frijol (MX)
        soja = self.df[(self.df["pais"] == "Brasil") & (self.df["cultura"] == "Soja")].sort_values("ano")
        frijol = self.df[(self.df["pais"] == "Mexico") & (self.df["cultura"] == "Frijol")].sort_values("ano")
        
        res_soja = self.ajustar(soja["spei_3m"].values, soja["produtividade_kg_ha"].values, anos=soja["ano"].values)
        res_frijol = self.ajustar(frijol["spei_3m"].values, frijol["produtividade_kg_ha"].values, anos=frijol["ano"].values)
        
        # Both crops exhibit negative quadratic concavity (local maximum)
        self.assertTrue(res_soja["is_maximo"])
        self.assertTrue(res_frijol["is_maximo"])
        self.assertLess(res_soja["a"], 0.0)
        self.assertLess(res_frijol["a"], 0.0)
        
        # Severe drought (SPEI = -2.5) causes productivity decline relative to normal (SPEI = 0.0)
        y_norm_soja = res_soja["a"]*(0.0**2) + res_soja["b"]*0.0 + res_soja["c"]
        y_dry_soja = res_soja["a"]*((-2.5)**2) + res_soja["b"]*(-2.5) + res_soja["c"]
        self.assertLess(y_dry_soja, y_norm_soja)
        
        y_norm_frijol = res_frijol["a"]*(0.0**2) + res_frijol["b"]*0.0 + res_frijol["c"]
        y_dry_frijol = res_frijol["a"]*((-2.5)**2) + res_frijol["b"]*(-2.5) + res_frijol["c"]
        self.assertLess(y_dry_frijol, y_norm_frijol)

    def test_03_thermal_gdd_and_water_deficit_compound_stress(self):
        """Simulates combined thermal energy accumulation and hydrological water deficit."""
        dias = np.arange(121)
        # Heatwave anomaly: +3°C above typical baseline
        temp_baseline = 25.0 + 5.0 * np.sin(2.0 * np.pi * dias / 120.0)
        temp_heatwave = temp_baseline + 3.0
        
        gdd_base = self.simpson(np.maximum(0.0, temp_baseline - 10.0), h=1.0)
        gdd_heat = self.simpson(np.maximum(0.0, temp_heatwave - 10.0), h=1.0)
        
        # Heatwave accelerates thermal sum accumulation
        self.assertGreater(gdd_heat, gdd_base)
        
        # Severe hydrological deficit (SPEI = -2.5) limits biomass despite higher heat
        ode_dry = self.euler(spei=-2.5, dias=120)
        ode_normal = self.euler(spei=0.0, dias=120)
        self.assertLess(ode_dry["y_final"], ode_normal["y_final"])

    def test_04_detrended_historical_yield_vs_dynamic_carrying_capacity(self):
        """Verifies positive correlation between detrended yields and Verhulst carrying capacity K(SPEI)."""
        df_milho = self.df[(self.df["pais"] == "Brasil") & (self.df["cultura"] == "Milho 1ª Safra")].sort_values("ano")
        spei_vals = df_milho["spei_3m"].values
        prod_vals = df_milho["produtividade_kg_ha"].values
        anos = df_milho["ano"].values
        
        # Linear detrending
        slope, intercept = np.polyfit(anos, prod_vals, 1)
        prod_detrended = prod_vals - (slope * anos + intercept) + np.mean(prod_vals)
        
        # Compute Verhulst carrying capacity K for each historical year
        k_vals = np.array([max(500.0, 4500.0 + 800.0 * s) for s in spei_vals])
        
        # Correlation between detrended yield and capacity K must be strongly positive
        corr = np.corrcoef(prod_detrended, k_vals)[0, 1]
        self.assertGreater(corr, 0.40,
                           msg=f"Correlation between detrended yield and carrying capacity was {corr:.3f}, expected > 0.40.")

    def test_05_end_to_end_data_feeding_pipeline(self):
        """Extracts historical slice, fits differential model, and feeds SPEI* to Euler simulator."""
        sub = self.df[(self.df["pais"] == "Brasil") & (self.df["cultura"] == "Milho 2ª Safra")].sort_values("ano")
        diff_res = self.ajustar(sub["spei_3m"].values, sub["produtividade_kg_ha"].values, anos=sub["ano"].values)
        
        spei_opt = diff_res["spei_otimo"]
        # Simulate growth at empirically optimal SPEI
        sim_opt = self.euler(spei=spei_opt, dias=120)
        
        # Simulate growth under drought condition (SPEI = -2.0)
        sim_dry = self.euler(spei=-2.0, dias=120)
        
        # Optimal SPEI simulation produces higher biomass than drought
        self.assertGreater(sim_opt["y_final"], sim_dry["y_final"])
        self.assertGreater(sim_opt["K"], sim_dry["K"])

    def test_06_multi_crop_cycle_duration_and_gdd_saturation(self):
        """Shorter cycle crops accumulate proportionally less GDD than longer cycle crops."""
        # 90 days for Feijão vs 120 days for Soja vs 140 days for Milho 1ª Safra
        dias_90 = np.arange(91)
        dias_120 = np.arange(121)
        
        # Uniform thermal regime T = 25°C, T_base = 10.0°C => 15 GDD / day
        temp_90 = np.full(91, 25.0)
        temp_120 = np.full(121, 25.0)
        
        gdd_90 = self.simpson(np.maximum(0.0, temp_90 - 10.0), h=1.0)
        gdd_120 = self.simpson(np.maximum(0.0, temp_120 - 10.0), h=1.0)
        
        self.assertAlmostEqual(gdd_90, 90.0 * 15.0, places=1)
        self.assertAlmostEqual(gdd_120, 120.0 * 15.0, places=1)
        self.assertLess(gdd_90, gdd_120)


if __name__ == "__main__":
    unittest.main()
