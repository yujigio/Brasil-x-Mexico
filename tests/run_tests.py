#!/usr/bin/env python3
"""
Test Runner Dedicado (Zero Dependências Externas)
Executa a suíte de 12 testes unitários do Observatório Agroclimático Brasil vs. México
utilizando exclusivamente a biblioteca padrão `unittest`.
"""

import os
import sys
import unittest
from pathlib import Path

# Configuração robusta de sys.path para execução a partir de qualquer diretório
RUNNER_DIR = Path(__file__).resolve().parent
PROJECT_DIR = RUNNER_DIR.parent

if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))
if str(RUNNER_DIR) not in sys.path:
    sys.path.insert(0, str(RUNNER_DIR))

from test_portfolio_models import TestPortfolioModels


def main() -> int:
    """Executa a suíte de testes com TextTestRunner verboso e reporta status."""
    print("=" * 80)
    print(" OBSERVATÓRIO AGROCLIMÁTICO BRASIL VS. MÉXICO — SUÍTE DE TESTES UNITÁRIOS")
    print("=" * 80)
    print(f"Diretório do Projeto: {PROJECT_DIR}")
    print(f"Arquivo de Testes:    {RUNNER_DIR / 'test_portfolio_models.py'}")
    print(f"Python Executável:    {sys.executable}")
    print(f"Versão Python:        {sys.version.split()[0]}")
    print("-" * 80)

    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestPortfolioModels)

    runner = unittest.TextTestRunner(verbosity=2)
    resultado = runner.run(suite)

    print("-" * 80)
    print(f"Total de Testes Executados: {resultado.testsRun}")
    print(f"Falhas:                     {len(resultado.failures)}")
    print(f"Erros:                      {len(resultado.errors)}")
    print(f"Taxa de Aprovação:          {((resultado.testsRun - len(resultado.failures) - len(resultado.errors)) / resultado.testsRun * 100):.1f}%" if resultado.testsRun > 0 else "0%")
    print("=" * 80)

    if resultado.wasSuccessful():
        print(">>> STATUS: APROVADO COM 100% DE SUCESSO (12/12 TESTES PASSARAM) <<<")
        return 0
    else:
        print(">>> STATUS: REPROVADO — CORRIJA OS ERROS/FALHAS ACIMA <<<")
        return 1


if __name__ == "__main__":
    sys.exit(main())
