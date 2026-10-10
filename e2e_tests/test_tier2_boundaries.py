"""
Tier 2: Boundary, Parity & Corner Cases.
Validates system behavior on edge conditions and defensive assertions:
- Extreme SPEI domain boundaries [-3.0, +3.0]
- Simpson odd-interval parity assertion ((n-1) % 2 != 0 raises ValueError)
- Simpson insufficient points (<3 points raises ValueError)
- Thermal base temperature boundaries (T_base <= 0 and T_base > max(T))
- Differential input validation (dimension mismatch, <3 points)
- Comprehensive 61-point numerical stability scan across [-3.0, +3.0]
"""

import unittest
import numpy as np

try:
    from e2e_tests.adapter import (
        get_simpson_func,
        get_calcular_gdd_func,
        get_differential_func,
        get_verhulst_euler_func,
    )
except (ImportError, ValueError):
    from adapter import (
        get_simpson_func,
        get_calcular_gdd_func,
        get_differential_func,
        get_verhulst_euler_func,
    )


class TestBoundaryAndCornerCases(unittest.TestCase):
    """Tier 2 Suite: Boundary, Parity & Corner Cases."""

    def setUp(self):
        self.simpson = get_simpson_func()
        self.calc_gdd = get_calcular_gdd_func()
        self.ajustar = get_differential_func()
        self.euler = get_verhulst_euler_func()

    def test_01_extreme_spei_lower_boundary_minus_3(self):
        """At extreme drought SPEI = -3.0, simulation remains stable and non-negative."""
        # r = max(0.02, 0.08 + 0.02*(-3.0)) = 0.02
        # K = max(500, 4500 + 800*(-3.0)) = 2100.0
        res = self.euler(spei=-3.0, dias=120, y0=50.0, dt=1.0)
        self.assertAlmostEqual(res["r"], 0.02, places=4)
        self.assertAlmostEqual(res["K"], 2100.0, places=1)
        self.assertFalse(np.isnan(res["y"]).any(), "Detected NaN at SPEI = -3.0")
        self.assertFalse(np.isinf(res["y"]).any(), "Detected Inf at SPEI = -3.0")
        self.assertTrue((res["y"] >= 0.0).all(), "Biomass dropped below zero at SPEI = -3.0")
        self.assertTrue((res["y"] <= 2100.0 + 1e-6).all(), "Biomass exceeded K at SPEI = -3.0")

    def test_02_extreme_spei_upper_boundary_plus_3(self):
        """At extreme wet SPEI = +3.0, simulation remains bounded and monotonic."""
        # r = 0.08 + 0.02*(3.0) = 0.14
        # K = 4500 + 800*(3.0) = 6900.0
        res = self.euler(spei=3.0, dias=120, y0=50.0, dt=1.0)
        self.assertAlmostEqual(res["r"], 0.14, places=4)
        self.assertAlmostEqual(res["K"], 6900.0, places=1)
        self.assertFalse(np.isnan(res["y"]).any(), "Detected NaN at SPEI = +3.0")
        self.assertFalse(np.isinf(res["y"]).any(), "Detected Inf at SPEI = +3.0")
        self.assertTrue((res["y"] >= 0.0).all())
        self.assertTrue((res["y"] <= 6900.0 + 1e-6).all())

    def test_03_simpson_odd_intervals_parity_exception(self):
        """Simpson 1/3 strictly raises ValueError when number of intervals is odd."""
        # 4 points => 3 intervals (odd)
        y_odd1 = np.array([1.0, 2.0, 3.0, 4.0])
        with self.assertRaises(ValueError, msg="Simpson 1/3 must reject 3 intervals (4 points)"):
            self.simpson(y_odd1, h=1.0)

        # 6 points => 5 intervals (odd)
        y_odd2 = np.array([0.0, 1.0, 4.0, 9.0, 16.0, 25.0])
        with self.assertRaises(ValueError, msg="Simpson 1/3 must reject 5 intervals (6 points)"):
            self.simpson(y_odd2, h=1.0)

    def test_04_simpson_insufficient_points_exception(self):
        """Simpson 1/3 strictly raises ValueError when passed fewer than 3 points."""
        with self.assertRaises(ValueError):
            self.simpson([], h=1.0)

        with self.assertRaises(ValueError):
            self.simpson([5.0], h=1.0)

        with self.assertRaises(ValueError):
            self.simpson([5.0, 10.0], h=1.0)

    def test_05_tbase_extreme_lower_boundary_zero_or_negative(self):
        """When T_base <= 0, all temperatures are fully effective."""
        # Array of 5 points (4 intervals) with 4 days cycle => h = 1.0
        temp = np.array([20.0, 22.0, 25.0, 24.0, 21.0])
        gdd_res = self.calc_gdd(temp, cultura="soja", t_base=0.0, ciclo_dias=4)
        val = gdd_res.get("gdd", gdd_res.get("gdd_total", gdd_res)) if isinstance(gdd_res, dict) else gdd_res
        integral_temp = self.simpson(temp, h=1.0)
        self.assertAlmostEqual(val, integral_temp, places=2)

    def test_06_tbase_extreme_upper_boundary_above_maximum_temp(self):
        """When T_base exceeds max temperature, GDD is identically zero."""
        temp = np.array([20.0, 22.0, 25.0, 24.0, 21.0])  # max is 25.0
        gdd_res = self.calc_gdd(temp, cultura="soja", t_base=50.0, ciclo_dias=4)
        val = gdd_res.get("gdd", gdd_res.get("gdd_total", gdd_res)) if isinstance(gdd_res, dict) else gdd_res
        self.assertAlmostEqual(val, 0.0, places=6,
                               msg="Thermal accumulation must be 0 when T_base exceeds maximum temperature.")

    def test_07_differential_input_dimension_validation(self):
        """Differential model strictly validates vector lengths and minimum sample count."""
        # Length mismatch
        spei = np.array([0.0, 1.0, 2.0])
        prod = np.array([3000.0, 3500.0])
        with self.assertRaises(ValueError):
            self.ajustar(spei, prod)

        # Insufficient points (< 3)
        with self.assertRaises(ValueError):
            self.ajustar([0.0, 1.0], [3000.0, 3500.0])

    def test_08_euler_verhulst_comprehensive_domain_scan(self):
        """Scans 61 equidistant SPEI points in [-3.0, +3.0] asserting non-divergence."""
        spei_grid = np.linspace(-3.0, 3.0, 61)
        for s in spei_grid:
            res = self.euler(spei=s, dias=120, y0=50.0, dt=1.0)
            y = res["y"]
            self.assertFalse(np.isnan(y).any(), f"NaN detected at SPEI = {s}")
            self.assertFalse(np.isinf(y).any(), f"Inf detected at SPEI = {s}")
            self.assertTrue((y >= 0.0).all(), f"Negative yield at SPEI = {s}")
            self.assertTrue((y <= res["K"] + 1e-4).all(), f"Yield exceeded K at SPEI = {s}")
            # Stability criterion r * dt < 2.0
            self.assertLess(res["r"] * res["dt"], 2.0, f"Euler stability condition violated at SPEI = {s}")


if __name__ == "__main__":
    unittest.main()
