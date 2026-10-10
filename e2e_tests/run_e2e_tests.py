#!/usr/bin/env python3
"""
Standalone E2E Test Runner for Observatório Agroclimático & Ambiental Brasil vs. México.
Runs with standard library Python without external dependencies, while also supporting pytest.
Robust cross-platform terminal encoding support for Windows, Linux, and macOS.
"""

import sys
import os
import time
import unittest
import argparse
from pathlib import Path

# Safe UTF-8 reconfiguration for Windows standard streams
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
if hasattr(sys.stderr, "reconfigure"):
    try:
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Add parent directory to sys.path
E2E_DIR = Path(__file__).resolve().parent
PORTFOLIO_ROOT = E2E_DIR.parent
if str(PORTFOLIO_ROOT) not in sys.path:
    sys.path.insert(0, str(PORTFOLIO_ROOT))
if str(PORTFOLIO_ROOT / "src") not in sys.path and (PORTFOLIO_ROOT / "src").exists():
    sys.path.insert(0, str(PORTFOLIO_ROOT / "src"))

# ANSI Color codes (with Windows terminal fallback)
HAS_COLOR = os.environ.get("TERM") != "dumb" and (
    sys.platform != "win32" or "WT_SESSION" in os.environ or "ANSICON" in os.environ or os.environ.get("COLORTERM") is not None or True
)

GREEN = "\033[92m" if HAS_COLOR else ""
RED = "\033[91m" if HAS_COLOR else ""
YELLOW = "\033[93m" if HAS_COLOR else ""
BLUE = "\033[94m" if HAS_COLOR else ""
CYAN = "\033[96m" if HAS_COLOR else ""
BOLD = "\033[1m" if HAS_COLOR else ""
DIM = "\033[2m" if HAS_COLOR else ""
RESET = "\033[0m" if HAS_COLOR else ""


def build_suite(tier: int = None):
    """Builds test suite for specified tier or all tiers."""
    from e2e_tests import (
        test_tier1_features,
        test_tier2_boundaries,
        test_tier3_combinations,
        test_tier4_scenarios,
    )

    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    tier_map = {
        1: [
            test_tier1_features.TestSimpsonGDDFeature,
            test_tier1_features.TestDifferentialOptimizationFeature,
            test_tier1_features.TestVerhulstEulerFeature,
            test_tier1_features.TestStatisticalHypothesisFeature,
            test_tier1_features.TestRelationalIntegrityFeature,
            test_tier1_features.TestHtmlAndKatexFeature,
            test_tier1_features.TestCiCdConfigurationFeature,
        ],
        2: [test_tier2_boundaries.TestBoundaryAndCornerCases],
        3: [test_tier3_combinations.TestCrossFeatureCombinations],
        4: [test_tier4_scenarios.TestRealWorldApplicationScenarios],
    }

    if tier in tier_map:
        for cls in tier_map[tier]:
            suite.addTests(loader.loadTestsFromTestCase(cls))
    else:
        for t, classes in tier_map.items():
            for cls in classes:
                suite.addTests(loader.loadTestsFromTestCase(cls))

    return suite


class CustomE2ETestResult(unittest.TextTestResult):
    """Custom test result collector for formatted reporting."""

    def __init__(self, stream, descriptions, verbosity):
        super().__init__(stream, descriptions, verbosity)
        self.verbosity = verbosity
        self.results = []

    def startTest(self, test):
        super().startTest(test)
        if self.verbosity > 1:
            cls_name = test.__class__.__name__
            method_name = test._testMethodName
            self.stream.write(f"  {CYAN}RUN{RESET}  [{cls_name}] {method_name} ... ")
            self.stream.flush()

    def addSuccess(self, test):
        super().addSuccess(test)
        if self.verbosity > 1:
            self.stream.writeln(f"{GREEN}PASS{RESET}")
        elif self.verbosity == 1:
            self.stream.write(f"{GREEN}.{RESET}")
            self.stream.flush()

    def addFailure(self, test, err):
        super().addFailure(test, err)
        if self.verbosity > 1:
            self.stream.writeln(f"{RED}FAIL{RESET}")
        elif self.verbosity == 1:
            self.stream.write(f"{RED}F{RESET}")
            self.stream.flush()

    def addError(self, test, err):
        super().addError(test, err)
        if self.verbosity > 1:
            self.stream.writeln(f"{RED}ERROR{RESET}")
        elif self.verbosity == 1:
            self.stream.write(f"{RED}E{RESET}")
            self.stream.flush()


def run_tests(tier=None, verbosity=2):
    """Executes the E2E test suite and displays a formatted summary."""
    print(f"\n{BOLD}{CYAN}======================================================================{RESET}")
    print(f"{BOLD}{CYAN}  OBSERVATORIO BRASIL vs. MEXICO -- E2E TEST RUNNER (TIERS 1-4){RESET}")
    print(f"{BOLD}{CYAN}======================================================================{RESET}")
    print(f"{DIM}Target Codebase: {PORTFOLIO_ROOT}{RESET}")
    print(f"{DIM}Python Version:  {sys.version.split()[0]} ({sys.executable}){RESET}\n")

    tiers_to_run = [tier] if tier else [1, 2, 3, 4]
    tier_titles = {
        1: "Tier 1: Core Feature Coverage (Simpson, Diff, ODE, Stats, Relational, Web, CI/CD)",
        2: "Tier 2: Boundary, Parity & Corner Cases (Extreme SPEI, T_base, Parity, Inputs)",
        3: "Tier 3: Cross-Feature Multi-Module Combinations (Coupled SPEI, Multi-Crop)",
        4: "Tier 4: Real-World Application Scenarios (2021/2022 Drought, Full Pipeline)",
    }

    total_run = 0
    total_failures = 0
    total_errors = 0
    start_time = time.time()
    tier_counts = {}

    for t in tiers_to_run:
        print(f"{BOLD}{BLUE}[>] Executing {tier_titles[t]}{RESET}")
        suite = build_suite(tier=t)
        tier_counts[t] = suite.countTestCases()
        
        runner = unittest.TextTestRunner(
            resultclass=CustomE2ETestResult,
            verbosity=verbosity,
            stream=sys.stdout
        )
        
        result = runner.run(suite)
        total_run += result.testsRun
        total_failures += len(result.failures)
        total_errors += len(result.errors)
        print()

    duration = time.time() - start_time

    # Summary Dashboard
    print(f"{BOLD}{CYAN}----------------------------------------------------------------------{RESET}")
    print(f"{BOLD}SUMMARY TEST RESULTS DASHBOARD{RESET}")
    print(f"{BOLD}{CYAN}----------------------------------------------------------------------{RESET}")
    for t in tiers_to_run:
        count = tier_counts.get(t, 0)
        print(f"  Tier {t}: {count:>3} tests configured")
    print(f"{BOLD}{CYAN}----------------------------------------------------------------------{RESET}")
    print(f"Total Tests Executed: {BOLD}{total_run}{RESET}")
    print(f"Total Failures:       {RED if total_failures else GREEN}{total_failures}{RESET}")
    print(f"Total Errors:         {RED if total_errors else GREEN}{total_errors}{RESET}")
    print(f"Execution Duration:   {duration:.3f} seconds")
    
    if total_failures == 0 and total_errors == 0:
        print(f"\n{BOLD}{GREEN}[+] 100% PASS RATE -- ALL E2E REQUIREMENTS SUCCESSFULLY VERIFIED!{RESET}\n")
        return 0
    else:
        print(f"\n{BOLD}{RED}[x] TEST SUITE FAILED -- {total_failures} failures, {total_errors} errors.{RESET}\n")
        return 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="E2E Test Runner for Brasil vs Mexico Portfolio")
    parser.add_argument("--tier", "-t", type=int, choices=[1, 2, 3, 4], default=None,
                        help="Run only specific tier (1, 2, 3, or 4)")
    parser.add_argument("--verbosity", "-v", type=int, choices=[1, 2], default=2,
                        help="Output verbosity level (1: compact, 2: detailed)")
    args = parser.parse_args()

    exit_code = run_tests(tier=args.tier, verbosity=args.verbosity)
    sys.exit(exit_code)
