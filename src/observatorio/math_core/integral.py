"""
Módulo de Cálculo Integral: Regra Composta de Simpson 1/3 e GDD
Implementação matemática pura para acumulação térmica de Graus-Dia de Desenvolvimento (GDD).
"""

from typing import Dict, Optional, Union
import numpy as np

# Parâmetros fenológicos e agronômicos de referência (Embrapa / SIAP / FAO)
PARAMETROS_CULTURAS = {
    "soja": {
        "nome_padrao": "Soja",
        "t_base": 10.0,
        "ciclo_dias": 120,
        "nome_cientifico": "Glycine max",
        "descricao": "Leguminosa de ciclo estival com sensibilidade fotoperiódica."
    },
    "milho 1ª safra": {
        "nome_padrao": "Milho 1ª Safra",
        "t_base": 10.0,
        "ciclo_dias": 140,
        "nome_cientifico": "Zea mays",
        "descricao": "Milho safra principal de verão com ciclo completo."
    },
    "milho 2ª safra": {
        "nome_padrao": "Milho 2ª Safra",
        "t_base": 10.0,
        "ciclo_dias": 120,
        "nome_cientifico": "Zea mays",
        "descricao": "Milho safrinha sucessivo com ciclo reduzido."
    },
    "café": {
        "nome_padrao": "Café",
        "t_base": 10.2,
        "ciclo_dias": 240,
        "nome_cientifico": "Coffea arabica",
        "descricao": "Cultura perene com período crítico de floração e granação."
    },
    "cana-de-açúcar": {
        "nome_padrao": "Cana-de-Açúcar",
        "t_base": 18.0,
        "ciclo_dias": 365,
        "nome_cientifico": "Saccharum officinarum",
        "descricao": "Cultura semiperene tropical com elevada exigência térmica de base."
    },
    "feijão/frijol": {
        "nome_padrao": "Feijão/Frijol",
        "t_base": 10.0,
        "ciclo_dias": 90,
        "nome_cientifico": "Phaseolus vulgaris",
        "descricao": "Ciclo curto intensivo com alta sensibilidade a anomalias térmicas."
    },
    "maíz blanco": {
        "nome_padrao": "Maíz Blanco",
        "t_base": 10.0,
        "ciclo_dias": 130,
        "nome_cientifico": "Zea mays",
        "descricao": "Grão básico mexicano para consumo humano (tortilla e nixtamalização)."
    },
    "maíz amarillo": {
        "nome_padrao": "Maíz Amarillo",
        "t_base": 10.0,
        "ciclo_dias": 130,
        "nome_cientifico": "Zea mays",
        "descricao": "Milho amarelo forrageiro e industrial."
    },
    "frijol": {
        "nome_padrao": "Frijol",
        "t_base": 10.0,
        "ciclo_dias": 90,
        "nome_cientifico": "Phaseolus vulgaris",
        "descricao": "Leguminosa básica da dieta mexicana (variedades pinto e negro)."
    },
    "caña de azúcar": {
        "nome_padrao": "Caña de Azúcar",
        "t_base": 18.0,
        "ciclo_dias": 365,
        "nome_cientifico": "Saccharum officinarum",
        "descricao": "Cana-de-açúcar mexicana de zonas irrigadas e tropicais."
    }
}


def _normalizar_chave_cultura(nome: str) -> str:
    """Normaliza strings de culturas removendo acentos e espaços extras."""
    n = nome.strip().lower()
    tabela = str.maketrans("áàâãéêíóôõúüçñ", "aaaaeeiooouucn")
    n_sem_acento = n.translate(tabela)
    
    # Mapeamento de sinônimos conhecidos
    if "soja" in n_sem_acento:
        return "soja"
    if "1" in n_sem_acento and ("milho" in n_sem_acento or "safra" in n_sem_acento):
        return "milho 1ª safra"
    if "2" in n_sem_acento or "safrinha" in n_sem_acento:
        return "milho 2ª safra"
    if "cafe" in n_sem_acento:
        return "café"
    if "cana" in n_sem_acento or "cana" in n or "azucar" in n_sem_acento:
        return "cana-de-açúcar"
    if "frijol" in n_sem_acento or "feijao" in n_sem_acento:
        return "feijão/frijol"
    if "blanco" in n_sem_acento:
        return "maíz blanco"
    if "amarillo" in n_sem_acento:
        return "maíz amarillo"
    
    # Busca direta no dicionário original
    for chave in PARAMETROS_CULTURAS:
        if chave.translate(tabela) == n_sem_acento:
            return chave
            
    return n_sem_acento


def simpson_13(y: Union[np.ndarray, list], h: float = 1.0) -> float:
    """
    Calcula a integral definida pela Regra Composta de Simpson 1/3.
    
    Fórmula:
        I = (h / 3) * [ y_0 + 4 * sum(y_impares) + 2 * sum(y_pares) + y_n ]
        
    Parâmetros:
        y: Vetor de ordenadas f(x_i) amostradas em pontos equidistantes.
        h: Espaçamento constante delta_x entre pontos consecutivos.
        
    Retorno:
        float: Valor da aproximação numérica da integral.
        
    Exceções:
        ValueError: Se o número de intervalos (n = len(y) - 1) não for par
                    ou se len(y) < 3.
    """
    y_arr = np.asarray(y, dtype=float)
    n_pontos = len(y_arr)
    
    if n_pontos < 3:
        raise ValueError(
            f"A Regra de Simpson 1/3 requer pelo menos 3 pontos (2 subintervalos). "
            f"Recebido: {n_pontos} pontos."
        )
        
    n_intervalos = n_pontos - 1
    if n_intervalos % 2 != 0:
        raise ValueError(
            f"Violação de paridade da Regra de Simpson 1/3: o número de subintervalos "
            f"(n = len(y) - 1 = {n_intervalos}) deve ser rigorosamente par "
            f"(número ímpar de pontos). Recebido: {n_pontos} pontos."
        )
        
    if h <= 0:
        raise ValueError(f"O passo de integração h deve ser estritamente positivo. Recebido: {h}")
        
    # Soma dos termos conforme a quadratura de Simpson 1/3
    soma_extremos = y_arr[0] + y_arr[-1]
    soma_impares = np.sum(y_arr[1:-1:2])
    soma_pares = np.sum(y_arr[2:-1:2])
    
    integral = (h / 3.0) * (soma_extremos + 4.0 * soma_impares + 2.0 * soma_pares)
    return float(integral)


def calcular_gdd_cultura(
    temperaturas: Union[np.ndarray, list],
    cultura: Optional[str] = "Soja",
    t_base: Optional[float] = None,
    ciclo_dias: Optional[int] = None,
    h: float = 1.0
) -> Dict[str, Union[str, float, int]]:
    """
    Calcula a acumulação de Graus-Dia de Desenvolvimento (GDD) via Simpson 1/3:
        GDD = Integral_0^T max(0, T(t) - T_base) dt
        
    Parâmetros:
        temperaturas: Vetor de temperaturas diárias ou interpoladas da cultura.
        cultura: Nome da cultura (e.g. 'Soja', 'Milho 1ª Safra', 'Café', 'Cana-de-Açúcar', 'Feijão/Frijol').
                 Padrão: 'Soja'.
        t_base: Temperatura base agronômica (°C). Se None, usa valor agronômico tabelado.
        ciclo_dias: Duração do ciclo vegetativo em dias. Se None, usa padrão da cultura.
        h: Passo temporal entre amostras sucessivas em dias (padrão: 1.0 dia).
        
    Retorno:
        dict: Dicionário contendo cultura, t_base, ciclo_dias, gdd, gdd_total, metodo e n_pontos.
    """
    chave = _normalizar_chave_cultura(cultura) if cultura else "soja"
    meta = PARAMETROS_CULTURAS.get(chave, {
        "nome_padrao": cultura if cultura else "Soja",
        "t_base": 10.0,
        "ciclo_dias": 120
    })
    
    t_base_efetivo = float(t_base) if t_base is not None else float(meta["t_base"])
    ciclo_efetivo = int(ciclo_dias) if ciclo_dias is not None else int(meta["ciclo_dias"])
    
    temps_arr = np.asarray(temperaturas, dtype=float)
    
    # Se fornecidas temperaturas completas além do ciclo, truncar até ciclo_efetivo + 1
    if len(temps_arr) > ciclo_efetivo + 1:
        temps_arr = temps_arr[: ciclo_efetivo + 1]
        
    # Verificar paridade para Simpson 1/3
    n = len(temps_arr) - 1
    if n < 2:
        raise ValueError(f"Série térmica insuficiente: {len(temps_arr)} pontos. Mínimo: 3 pontos.")
        
    # Se o número de intervalos for ímpar, ajustamos truncando 1 ponto para manter consistência par
    if n % 2 != 0:
        temps_arr = temps_arr[:-1]
        n = len(temps_arr) - 1
        
    # Calor útil diário: max(0, T - T_base)
    calor_util = np.maximum(0.0, temps_arr - t_base_efetivo)
    
    gdd_total = simpson_13(calor_util, h=h)
    
    return {
        "cultura": meta["nome_padrao"],
        "t_base": round(t_base_efetivo, 2),
        "ciclo_dias": ciclo_efetivo,
        "gdd": round(gdd_total, 2),
        "gdd_total": round(gdd_total, 2),
        "metodo": "Simpson 1/3",
        "n_pontos": len(calor_util)
    }


def validar_precisao_simpson() -> Dict[str, Union[float, bool, Dict[str, float]]]:
    """
    Executa bateria de testes analíticos comparando a aproximação de Simpson 1/3
    contra soluções exatas para validar erro relativo inferior a 0.01%:
    1. Polinômio Cúbico: Integral_0^2 (3x^3 - 2x^2 + 5x - 1) dx = 44/3
    2. Função Senoidal: Integral_0^pi sin(x) dx = 2.0
    3. Onda Bioclimática Térmica: T(t) = 28 + 6*sin(2*pi*t/120) - 10 no ciclo de 120 dias = 2160.0
    
    Retorno:
        dict: Resultados analíticos com erro relativo percentual (< 0.01%).
    """
    # Teste 1: Polinômio cúbico em [0, 2] com n = 10 subintervalos (11 pontos)
    # Por teoria, Simpson 1/3 é exato para polinômios de grau <= 3
    x_cub = np.linspace(0.0, 2.0, 11)
    y_cub = 3.0 * x_cub**3 - 2.0 * x_cub**2 + 5.0 * x_cub - 1.0
    h_cub = 2.0 / 10.0
    i_num_cub = simpson_13(y_cub, h=h_cub)
    i_exato_cub = 44.0 / 3.0  # 14.666666666666666
    erro_rel_cub = abs(i_num_cub - i_exato_cub) / abs(i_exato_cub) * 100.0
    
    # Teste 2: Seno em [0, pi] com n = 100 subintervalos (101 pontos)
    x_sen = np.linspace(0.0, np.pi, 101)
    y_sen = np.sin(x_sen)
    h_sen = np.pi / 100.0
    i_num_sen = simpson_13(y_sen, h=h_sen)
    i_exato_sen = 2.0
    erro_rel_sen = abs(i_num_sen - i_exato_sen) / abs(i_exato_sen) * 100.0
    
    # Teste 3: Curva bioclimática analítica em [0, 120] dias com n = 120 subintervalos
    # T(t) = 28 + 6*sin(2*pi*t/120), T_base = 10.0 => calor_util = 18 + 6*sin(2*pi*t/120)
    # Integral exata de 0 a 120: 18 * 120 + 0 = 2160.0
    t_dias = np.linspace(0.0, 120.0, 121)
    y_bio = 18.0 + 6.0 * np.sin(2.0 * np.pi * t_dias / 120.0)
    h_bio = 1.0
    i_num_bio = simpson_13(y_bio, h=h_bio)
    i_exato_bio = 2160.0
    erro_rel_bio = abs(i_num_bio - i_exato_bio) / abs(i_exato_bio) * 100.0
    
    tolerancia_max = 0.01  # 0.01%
    passou = (
        erro_rel_cub < tolerancia_max
        and erro_rel_sen < tolerancia_max
        and erro_rel_bio < tolerancia_max
    )
    
    return {
        "sucesso": passou,
        "tolerancia_limite_pct": tolerancia_max,
        "polinomio_cubico": {
            "numerico": round(i_num_cub, 8),
            "exato": round(i_exato_cub, 8),
            "erro_absoluto": abs(i_num_cub - i_exato_cub),
            "erro_relativo_pct": erro_rel_cub,
            "passou": erro_rel_cub < tolerancia_max
        },
        "trigonometrico_seno": {
            "numerico": round(i_num_sen, 8),
            "exato": round(i_exato_sen, 8),
            "erro_absoluto": abs(i_num_sen - i_exato_sen),
            "erro_relativo_pct": erro_rel_sen,
            "passou": erro_rel_sen < tolerancia_max
        },
        "bioclimatico_gdd": {
            "numerico": round(i_num_bio, 8),
            "exato": round(i_exato_bio, 8),
            "erro_absoluto": abs(i_num_bio - i_exato_bio),
            "erro_relativo_pct": erro_rel_bio,
            "passou": erro_rel_bio < tolerancia_max
        }
    }
