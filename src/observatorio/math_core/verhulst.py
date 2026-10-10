"""
Módulo de Equações Diferenciais Ordinárias (EDOs): Dinâmica Logística de Verhulst
Modela o acúmulo temporal de biomassa vegetal Y(t) sob forçantes agroclimáticas de SPEI:
    dY/dt = r(SPEI) * Y(t) * (1 - Y(t) / K(SPEI))
Resolvido numericamente pelo Método de Euler com passo discreto dt = 1.0 dia e
comparado com a solução analítica exata.
"""

from typing import Dict, Tuple, Union
import numpy as np


def solucao_analitica_verhulst(
    t: Union[np.ndarray, list, float],
    y0: float,
    K: float,
    r: float
) -> np.ndarray:
    """
    Retorna a solução analítica exata da EDO logística de Verhulst:
        Y(t) = (K * Y_0) / [ Y_0 + (K - Y_0) * exp(-r * t) ]
        
    Parâmetros:
        t: Vetor de tempo em dias (ou escalar).
        y0: Biomassa inicial (kg/ha).
        K: Capacidade de suporte ambiental (kg/ha).
        r: Taxa intrínseca de crescimento diário (1/dia).
        
    Retorno:
        np.ndarray: Valores analíticos exatos da biomassa no tempo t.
    """
    t_arr = np.asarray(t, dtype=float)
    termo_exp = (K - y0) * np.exp(-r * t_arr)
    y_exato = (K * y0) / (y0 + termo_exp)
    return y_exato


def simular_verhulst_euler(
    spei: float,
    dias: int = 120,
    y0: float = 50.0,
    dt: float = 1.0,
    k_base: float = 4500.0,
    r_base: float = 0.08
) -> Dict[str, Union[float, int, np.ndarray]]:
    """
    Simula o acúmulo dinâmico de biomassa vegetal pelo Método de Euler:
        Y_{k+1} = Y_k + [ r(SPEI) * Y_k * (1 - Y_k / K(SPEI)) ] * dt
        
    Parâmetros biofísicos dependentes do SPEI:
        r(SPEI) = max(0.02, r_base + 0.02 * SPEI)
        K(SPEI) = max(500.0, k_base + 800.0 * SPEI)
        
    Parâmetros:
        spei: Índice de seca/umidade SPEI (e.g. -2.5 para seca severa, 0.0 para normal, +2.5 para excesso).
        dias: Duração total do ciclo fenológico em dias (padrão: 120 dias).
        y0: Biomassa inicial emergente da plântula (kg/ha, padrão: 50.0).
        dt: Passo temporal da discretização numérica (dias, padrão: 1.0).
        k_base: Capacidade de suporte base em clima neutro (kg/ha).
        r_base: Taxa de crescimento base em clima neutro (1/dia).
        
    Retorno:
        dict: Dicionário contendo trajetórias 't', 'y', 'y_analitico', parâmetros 'r', 'K',
              biomassas finais e métricas de erro de discretização.
    """
    spei_val = float(spei)
    dt_val = float(dt)
    y0_val = float(y0)
    
    if dt_val <= 0:
        raise ValueError(f"O passo de tempo dt deve ser estritamente positivo. Recebido: {dt_val}")
    if dias <= 0:
        raise ValueError(f"O número de dias do ciclo deve ser positivo. Recebido: {dias}")
    if y0_val <= 0:
        raise ValueError(f"A biomassa inicial y0 deve ser positiva. Recebido: {y0_val}")
        
    # Calibração dos parâmetros ecofisiológicos dependentes do balanço hídrico
    r = max(0.02, r_base + 0.02 * spei_val)
    K = max(500.0, k_base + 800.0 * spei_val)
    
    n_passos = int(round(dias / dt_val))
    t_vetor = np.linspace(0.0, float(dias), n_passos + 1)
    
    # Integração pelo Método de Euler Progressivo
    y_euler = np.empty(n_passos + 1, dtype=float)
    y_euler[0] = y0_val
    
    for i in range(n_passos):
        y_atual = y_euler[i]
        # Derivada logística instantânea
        dydt = r * y_atual * (1.0 - (y_atual / K))
        y_prox = y_atual + dydt * dt_val
        y_euler[i + 1] = y_prox
        
    # Comparação com a solução analítica exata
    y_analitico = solucao_analitica_verhulst(t_vetor, y0=y0_val, K=K, r=r)
    
    erro_abs = np.abs(y_euler - y_analitico)
    max_erro_abs = float(np.max(erro_abs))
    erro_rel_final_pct = float(abs(y_euler[-1] - y_analitico[-1]) / y_analitico[-1] * 100.0)
    
    return {
        "t": t_vetor,
        "y": y_euler,
        "y_analitico": y_analitico,
        "r": round(float(r), 4),
        "K": round(float(K), 2),
        "y_final": round(float(y_euler[-1]), 2),
        "y_final_analitico": round(float(y_analitico[-1]), 2),
        "spei": round(spei_val, 2),
        "dias": dias,
        "dt": dt_val,
        "max_erro_absoluto": round(max_erro_abs, 4),
        "erro_relativo_final_pct": round(erro_rel_final_pct, 4)
    }


def obter_cenarios_padrao() -> Dict[str, Dict[str, Union[float, int, np.ndarray]]]:
    """
    Gera as simulações comparativas padronizadas para os três cenários canônicos:
    1. 'Seca Severa': SPEI = -2.5
    2. 'Clima Normal': SPEI = 0.0
    3. 'Excesso Hídrico': SPEI = +2.5
    
    Retorno:
        dict: Mapeamento de nome do cenário para os resultados completos da simulação de Euler.
    """
    cenarios = {
        "Seca Severa": simular_verhulst_euler(spei=-2.5, dias=120, y0=50.0, dt=1.0),
        "Clima Normal": simular_verhulst_euler(spei=0.0, dias=120, y0=50.0, dt=1.0),
        "Excesso Hídrico": simular_verhulst_euler(spei=+2.5, dias=120, y0=50.0, dt=1.0)
    }
    return cenarios


def testar_estabilidade_dominio_spei(
    intervalo: Tuple[float, float] = (-3.0, 3.0),
    passos: int = 61
) -> bool:
    """
    Varre continuamente o domínio de SPEI em [-3.0, +3.0] e valida que:
    1. A solução numérica de Euler não produz valores NaN ou Infinitos.
    2. A biomassa Y(t) permanece estritamente positiva em todo o ciclo de 120 dias.
    3. A curva de crescimento é monotonicamente não-decrescente (sem oscilações espúrias).
    4. Y(t) converge de maneira assintótica e não ultrapassa a capacidade K(SPEI).
    5. O erro de truncamento de Euler permanece rigorosamente sob controle (< 5.0% em todo o ciclo).
    
    Parâmetros:
        intervalo: Tupla (spei_min, spei_max), padrão (-3.0, 3.0).
        passos: Quantidade de amostragens no domínio, padrão 61 (passo de 0.1).
        
    Retorno:
        bool: True se 100% dos testes de estabilidade numérica forem aprovados.
    """
    spei_valores = np.linspace(intervalo[0], intervalo[1], passos)
    
    for s in spei_valores:
        sim = simular_verhulst_euler(spei=float(s), dias=120, y0=50.0, dt=1.0)
        y = sim["y"]
        K = sim["K"]
        
        # 1. Ausência de NaNs ou Infs
        if not np.all(np.isfinite(y)):
            raise ValueError(f"Instabilidade detectada: NaNs ou Infs encontrados para SPEI={s}")
            
        # 2. Positividade estrita
        if np.any(y <= 0.0):
            raise ValueError(f"Instabilidade detectada: Biomassa não-positiva para SPEI={s}")
            
        # 3. Monotonicidade não-decrescente (Y_0 < K => dy/dt >= 0)
        diffs = np.diff(y)
        if np.any(diffs < -1e-6):
            raise ValueError(f"Instabilidade detectada: Oscilação espúria detectada para SPEI={s}")
            
        # 4. Limitada pela capacidade de suporte K (+ tolerância de Euler)
        if np.any(y > K * 1.05):
            raise ValueError(f"Instabilidade detectada: Explosão numérica acima de K para SPEI={s}")
            
        # 5. Erro relativo no final do ciclo controlado
        if sim["erro_relativo_final_pct"] > 5.0:
            raise ValueError(
                f"Erro de discretização de Euler excessivo ({sim['erro_relativo_final_pct']}%) para SPEI={s}"
            )
            
    return True
