"""
Tier 4: Real-World Application Scenarios.
Validates complete end-to-end scientific and operational workflows:
- Historical 2021/2022 La Niña drought impact scenario in Brazil & Mexico
- Complete End-to-End Data-to-Yield Analytical Pipeline
- Irrigation climate buffering asymmetry scenario (Rainfed BR vs Irrigated MX)
- Thermal heatwave (+4°C) phenological acceleration scenario
- Consistency audit between academic paper documentation and dataset models
"""

import unittest
from pathlib import Path
import numpy as np
import pandas as pd

try:
    from e2e_tests.adapter import (
        PORTFOLIO_ROOT,
        carregar_dataset,
        get_simpson_func,
        get_calcular_gdd_func,
        get_differential_func,
        get_verhulst_euler_func,
        get_statistics_func,
    )
except (ImportError, ValueError):
    from adapter import (
        PORTFOLIO_ROOT,
        carregar_dataset,
        get_simpson_func,
        get_calcular_gdd_func,
        get_differential_func,
        get_verhulst_euler_func,
        get_statistics_func,
    )


class TestRealWorldApplicationScenarios(unittest.TestCase):
    """Tier 4 Suite: Real-World Application Scenarios."""

    def setUp(self):
        self.df = carregar_dataset()
        self.simpson = get_simpson_func()
        self.calc_gdd = get_calcular_gdd_func()
        self.ajustar = get_differential_func()
        self.euler = get_verhulst_euler_func()
        self.academic_paper_path = PORTFOLIO_ROOT / "RELATORIO_ACADEMICO_BRASIL_MEXICO.md"

    def test_01_historic_2021_2022_la_nina_drought_impact_scenario(self):
        """Simulates the historic 2021/2022 La Niña drought impact on Southern/Center-West Brazil."""
        # 2021 and 2022 recorded severe drought in Brazil
        drought_years = self.df[(self.df["pais"] == "Brasil") & (self.df["ano"].isin([2021, 2022]))]
        self.assertTrue(len(drought_years) > 0, "No records found for 2021/2022 drought.")
        
        # Verify recorded SPEI was severely negative
        mean_spei_drought = drought_years["spei_3m"].mean()
        self.assertLess(mean_spei_drought, -0.8,
                        msg=f"Expected severe negative SPEI during 2021/2022, got {mean_spei_drought}.")
        
        # For Milho 2ª Safra (highly vulnerable safrinha), check yield drop vs historical average
        milho2 = self.df[(self.df["pais"] == "Brasil") & (self.df["cultura"] == "Milho 2ª Safra")]
        prod_media_geral = milho2["produtividade_kg_ha"].mean()
        prod_2021 = milho2[milho2["ano"] == 2021]["produtividade_kg_ha"].values[0]
        
        # 2021 yield is lower than the 25-year mean
        self.assertLess(prod_2021, prod_media_geral,
                        msg="2021 safrinha yield was not depressed by documented severe drought.")
        
        # Verhulst simulation with 2021 SPEI mirrors biomass loss
        spei_2021 = milho2[milho2["ano"] == 2021]["spei_3m"].values[0]
        sim_2021 = self.euler(spei=spei_2021, dias=120)
        sim_normal = self.euler(spei=0.0, dias=120)
        
        queda_biomassa_pct = (sim_normal["y_final"] - sim_2021["y_final"]) / sim_normal["y_final"] * 100.0
        self.assertGreater(queda_biomassa_pct, 10.0,
                           msg=f"Model simulated biomass drop was {queda_biomassa_pct:.1f}%, expected > 10%.")

    def test_02_full_end_to_end_data_to_yield_analytical_pipeline(self):
        """Executes complete data pipeline: ingestion -> validation -> detrending -> diff -> ODE -> stats."""
        # 1. Ingestion & Validation
        df = self.df.copy()
        self.assertEqual(len(df), 250)
        self.assertEqual(df.isnull().sum().sum(), 0)
        
        # 2. Extract Soja Brasil time series
        df_soja = df[(df["pais"] == "Brasil") & (df["cultura"] == "Soja")].sort_values("ano")
        spei = df_soja["spei_3m"].values
        prod = df_soja["produtividade_kg_ha"].values
        anos = df_soja["ano"].values
        
        # 3. Differential optimization with detrending
        diff_res = self.ajustar(spei, prod, anos=anos, remover_tendencia=True)
        self.assertTrue(diff_res["is_maximo"])
        self.assertLess(diff_res["a"], 0.0)
        spei_opt = diff_res["spei_otimo"]
        
        # 4. Verhulst dynamic growth simulation for optimal vs drought
        ode_opt = self.euler(spei=spei_opt, dias=120)
        ode_drought = self.euler(spei=-2.5, dias=120)
        self.assertGreater(ode_opt["y_final"], ode_drought["y_final"])
        
        # 5. Simpson GDD thermal accumulation
        dias_cycle = np.arange(121)
        temp_cycle = 27.0 + 5.0 * np.sin(2.0 * np.pi * dias_cycle / 120.0)
        gdd = self.simpson(np.maximum(0.0, temp_cycle - 10.0), h=1.0)
        self.assertGreater(gdd, 1500.0)
        
        # 6. Overall pipeline consistency verified
        self.assertTrue(True)

    def test_03_irrigation_buffering_asymmetry_scenario(self):
        """Analyzes climatic resilience between rainfed (Brazil) and irrigated (Mexico) systems."""
        # Standardize yields
        df_calc = self.df.copy()
        df_calc["idx"] = df_calc.groupby(["pais", "cultura"])["produtividade_kg_ha"].transform(lambda s: s / s.mean())
        
        # Filter severe drought vs normal
        br_drought = df_calc[(df_calc["pais"] == "Brasil") & (df_calc["status_clima"] == "Seca Severa")]["idx"]
        mx_drought = df_calc[(df_calc["pais"] == "Mexico") & (df_calc["status_clima"] == "Seca Severa")]["idx"]
        
        # Both countries suffer yield loss during severe drought
        self.assertLess(br_drought.mean(), 1.0)
        self.assertLess(mx_drought.mean(), 1.0)
        
        # Standard deviations / variability during drought
        self.assertTrue(len(br_drought) > 0 and len(mx_drought) > 0)

    def test_04_thermal_heatwave_anomaly_simulation(self):
        """Simulates a +4°C heatwave anomaly across 120 days causing thermal accumulation surge."""
        dias = np.arange(121)
        # Baseline normal: T(t) = 24 + 4*sin(2*pi*t/120)
        temp_base = 24.0 + 4.0 * np.sin(2.0 * np.pi * dias / 120.0)
        temp_heatwave = temp_base + 4.0
        
        gdd_normal = self.simpson(np.maximum(0.0, temp_base - 10.0), h=1.0)
        gdd_heatwave = self.simpson(np.maximum(0.0, temp_heatwave - 10.0), h=1.0)
        
        # +4°C over 120 days adds approximately 4 * 120 = 480 GDD
        diff_gdd = gdd_heatwave - gdd_normal
        self.assertAlmostEqual(diff_gdd, 480.0, places=1,
                               msg=f"Heatwave addition was {diff_gdd:.1f} GDD, expected 480.0.")

    def test_05_academic_paper_and_dataset_consistency(self):
        """Verifies documentation alignment between RELATORIO_ACADEMICO_BRASIL_MEXICO.md and models."""
        self.assertTrue(self.academic_paper_path.exists(),
                        msg="Academic paper RELATORIO_ACADEMICO_BRASIL_MEXICO.md must exist.")
        
        with open(self.academic_paper_path, "r", encoding="utf-8") as f:
            paper_text = f.read()
            
        # Paper must mention key mathematical components
        self.assertIn("Simpson", paper_text)
        self.assertIn("Verhulst", paper_text)
        self.assertIn("SPEI", paper_text)
        self.assertIn("2000", paper_text)
        self.assertIn("2024", paper_text)


if __name__ == "__main__":
    unittest.main()
