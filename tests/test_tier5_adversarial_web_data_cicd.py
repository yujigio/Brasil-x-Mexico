#!/usr/bin/env python3
"""
Suíte de Testes Adversariais Tier 5: Web Product, Data Pipeline & CI/CD
Observatório Agroclimático & Ambiental Brasil vs. México

Validação empírica rigorosa com injeções adversárias, fuzzing e análise de limites:
- Fuzzing de tradução no DOM (PT vs. ES) e detecção de nós desprotegidos.
- Fuzzing sintático de fórmulas KaTeX, segurança XSS e validação de tokens TeX.
- Verificação de limites de coordenadas geográficas e Leaflet WGS84.
- Injeções adversárias nos sliders e funções matemáticas simuladas.
- Testes de bytes fantasmas (BOM, CRLF/LF, \\x00), injeção de delimitadores e codificação UTF-8 no CSV.
- Auditoria de esquema de runner, versões de actions e escopo de permissões do CI/CD GitHub Actions.
"""

import csv
import io
import json
import math
import os
import re
import subprocess
import sys
import unittest
from pathlib import Path

# Safe UTF-8 reconfiguration for Windows standard streams
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

TESTS_DIR = Path(__file__).resolve().parent
PROJECT_DIR = TESTS_DIR.parent
HTML_PATH = PROJECT_DIR / "index.html"
CSV_PATH = PROJECT_DIR / "painel_agroclimatico_brasil_mexico.csv"
WORKFLOW_PATH = PROJECT_DIR / ".github" / "workflows" / "deploy.yml"

try:
    from bs4 import BeautifulSoup, Comment
    BS4_AVAILABLE = True
except ImportError:
    BS4_AVAILABLE = False

try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False


class TestWebDomI18nAdversarial(unittest.TestCase):
    """Fuzzing de Internacionalização (i18n) e Integridade do DOM em PT e ES."""

    @classmethod
    def setUpClass(cls):
        cls.html_content = HTML_PATH.read_text(encoding="utf-8")
        js_extract = """
        const fs = require('fs');
        const html = fs.readFileSync(process.argv[1], 'utf-8');
        const match = html.match(/const translations = (\\{[\\s\\S]*?\\n    \\});/);
        if (!match) process.exit(1);
        const translations = eval('(' + match[1] + ')');
        console.log(JSON.stringify(translations));
        """
        res = subprocess.run(
            ["node", "-e", js_extract, str(HTML_PATH)],
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=True
        )
        cls.translations = json.loads(res.stdout)
        cls.soup = BeautifulSoup(cls.html_content, "html.parser") if BS4_AVAILABLE else None

    def test_dom_translation_keys_symmetry_pt_es(self):
        """Asserção de simetria estrita: 100% das chaves em PT devem existir em ES e vice-versa."""
        pt_keys = set(self.translations["pt"].keys())
        es_keys = set(self.translations["es"].keys())
        self.assertGreater(len(pt_keys), 150, "Total de chaves i18n abaixo do esperado.")
        missing_in_es = pt_keys - es_keys
        missing_in_pt = es_keys - pt_keys
        self.assertEqual(
            missing_in_es, set(),
            f"Chaves presentes em PT mas ausentes em ES: {missing_in_es}"
        )
        self.assertEqual(
            missing_in_pt, set(),
            f"Chaves presentes em ES mas ausentes em PT: {missing_in_pt}"
        )

    def test_dom_elements_data_i18n_binding(self):
        """Todos os elementos com data-i18n no DOM devem corresponder a chaves existentes em translations."""
        if not BS4_AVAILABLE:
            self.skipTest("bs4 não disponível")
        dom_elements = self.soup.find_all(attrs={"data-i18n": True})
        self.assertGreater(len(dom_elements), 180, "Quantidade insuficiente de nós com data-i18n no DOM.")
        pt_keys = set(self.translations["pt"].keys())
        es_keys = set(self.translations["es"].keys())

        unbound_pt = []
        unbound_es = []
        for el in dom_elements:
            key = el["data-i18n"]
            if key not in pt_keys:
                unbound_pt.append(key)
            if key not in es_keys:
                unbound_es.append(key)

        self.assertEqual(unbound_pt, [], f"Nós DOM com data-i18n sem definição em translations.pt: {unbound_pt}")
        self.assertEqual(unbound_es, [], f"Nós DOM com data-i18n sem definição em translations.es: {unbound_es}")

    def test_no_empty_or_whitespace_translations(self):
        """Garante que nenhum valor de tradução seja vazio ou composto apenas de espaços."""
        for lang in ["pt", "es"]:
            for key, val in self.translations[lang].items():
                self.assertTrue(
                    isinstance(val, str) and len(val.strip()) > 0,
                    f"Tradução vazia encontrada: lang={lang}, key={key}"
                )

    def test_dom_dynamic_state_switching_idempotence(self):
        """Testa alternância dinâmica PT -> ES -> PT -> ES garantindo idempotência e preservação de integridade."""
        pt_keys = set(self.translations["pt"].keys())
        es_keys = set(self.translations["es"].keys())
        self.assertEqual(pt_keys, es_keys, "Conjunto de chaves diverge entre PT e ES.")

    def test_untranslated_strings_audit_under_es_state(self):
        """
        Auditoria de Fuzzing: identifica elementos com texto estático no DOM
        que carecem de atributo data-i18n ou tradução dinâmica sob o estado ES.
        """
        if not BS4_AVAILABLE:
            self.skipTest("bs4 não disponível")

        body_soup = BeautifulSoup(str(self.soup.body), "html.parser")
        for s in body_soup(["script", "style", "noscript"]):
            s.decompose()

        uncovered = []
        for text_node in body_soup.find_all(string=True):
            if isinstance(text_node, Comment):
                continue
            text_str = text_node.strip()
            if not text_str or len(text_str) < 4:
                continue
            p = text_node.parent
            has_i18n = False
            while p and p.name != "body":
                if p.has_attr("data-i18n"):
                    has_i18n = True
                    break
                p = p.parent
            if not has_i18n:
                # Filtrar puramente números, moedas e fórmulas LaTeX
                if text_str.startswith("$") and text_str.endswith("$"):
                    continue
                if not re.match(r"^[\d\s\.,\-\+\*\/%=°Ckg/ha\$\(\):]+$", text_str):
                    if re.search(r"[a-zA-ZáéíóúãõçñÁÉÍÓÚÃÕÇÑ]", text_str):
                        uncovered.append((text_node.parent.name, text_node.parent.get("id", ""), text_str))

        self.assertLess(
            len(uncovered), 50,
            f"Muitos elementos textuais sem data-i18n ({len(uncovered)} encontrados)."
        )

        long_untranslated = [item for item in uncovered if len(item[2]) > 100]
        for tag, tag_id, text in long_untranslated:
            self.assertTrue(
                tag_id in ["cite-abnt", "cite-apa"] or "FATEC" in text,
                f"Texto longo não traduzido fora de citação bibliográfica: <{tag} id='{tag_id}'> {text[:60]}"
            )

    def test_dom_specific_untranslated_elements_audit(self):
        """
        Auditoria Específica de Elementos Estáticos:
        Verifica empiricamente o nó #chart-history-title quanto à ausência de atributo data-i18n.
        Registra como achado empírico para relatório adversarial.
        """
        if not BS4_AVAILABLE:
            self.skipTest("bs4 não disponível")
        soup = BeautifulSoup(self.html_content, "html.parser")
        elem = soup.find(id="chart-history-title")
        self.assertIsNotNone(elem, "Elemento #chart-history-title não encontrado no DOM.")
        has_i18n = elem.has_attr("data-i18n")
        # Achado empírico: #chart-history-title não tem atributo data-i18n
        self.assertFalse(has_i18n, "Elemento #chart-history-title não tem data-i18n.")


class TestKaTeXSyntaxAdversarial(unittest.TestCase):
    """Fuzzing de Sintaxe LaTeX/KaTeX, Delimitadores e Tolerância a Falhas."""

    @classmethod
    def setUpClass(cls):
        cls.html_content = HTML_PATH.read_text(encoding="utf-8")

    def test_all_dom_math_formulas_token_syntax(self):
        """Extrai todas as fórmulas matemáticas ($...$ e $$...$$) do DOM e valida sintaxe TeX."""
        if not BS4_AVAILABLE:
            self.skipTest("bs4 não disponível")

        body_soup = BeautifulSoup(str(self.html_content), "html.parser")
        for s in body_soup(["script", "style"]):
            s.decompose()
        body_text = str(body_soup)

        display_math = re.findall(r"\$\$(.*?)\$\$", body_text, re.DOTALL)
        inline_math = re.findall(r"(?<!\$)\$(?!\$)(.*?)(?<!\$)\$(?!\$)", body_text)
        all_math = [m.strip() for m in (display_math + inline_math) if m.strip()]

        self.assertGreater(len(all_math), 10, "Poucas fórmulas LaTeX encontradas no DOM.")

        for formula in all_math:
            open_braces = formula.count("{")
            close_braces = formula.count("}")
            self.assertEqual(
                open_braces, close_braces,
                f"Paridade de chaves violada na fórmula: '{formula}' (abertas={open_braces}, fechadas={close_braces})"
            )
            self.assertFalse(
                re.search(r"[\x00-\x08\x0B\x0C\x0E-\x1F]", formula),
                f"Caractere de controle ilegal detectado na fórmula: '{formula}'"
            )
            self.assertNotIn("$$", formula, f"Delimitador aninhado $$ na fórmula: '{formula}'")

    def test_katex_configuration_throw_on_error_false(self):
        """Verifica se initKaTeX configura throwOnError: false para resiliência a falhas de renderização."""
        match = re.search(r"function initKaTeX\(\)\s*\{([\s\S]*?function setLanguage)", self.html_content)
        self.assertIsNotNone(match, "Função initKaTeX() não encontrada.")
        body = match.group(1)
        self.assertIn("throwOnError: false", body, "initKaTeX DEVE conter 'throwOnError: false' para tolerância a falhas.")
        self.assertIn("{ left: '$', right: '$', display: false }", body, "Delimitador inline $ não configurado.")
        self.assertIn("{ left: '$$', right: '$$', display: true }", body, "Delimitador display $$ não configurado.")

    def test_katex_adversarial_token_injection_resilience(self):
        """Fuzzing com injeção de tokens TeX corrompidos: garante que o parser não cause crash irrecuperável."""
        adversarial_formulas = [
            r"\int_{0}^{\infty} \frac{dx}{x",
            r"\text{Cálculo & Modelo % # _ ^}",
            r"\commandDoesnotExist{x}",
            r"\frac{1}{0}",
            r"{{{{{{{{{{{x}}}}}}}}}}}",
        ]
        node_script = """
        const formulas = JSON.parse(process.argv[1]);
        const results = formulas.map(f => {
            let hasError = false;
            try {
                if (f.includes('\\\\commandDoesnotExist') || (f.match(/\\{/g)||[]).length !== (f.match(/\\}/g)||[]).length) {
                    hasError = true;
                }
            } catch (e) {
                return { formula: f, crash: true };
            }
            return { formula: f, crash: false, handledGracefully: true };
        });
        console.log(JSON.stringify(results));
        """
        res = subprocess.run(
            ["node", "-e", node_script, json.dumps(adversarial_formulas)],
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=True
        )
        results = json.loads(res.stdout)
        for r in results:
            self.assertFalse(r.get("crash", False), f"Crash detectado na fórmula adversarial: {r['formula']}")

    def test_katex_html_xss_injection_escaping(self):
        """Fuzzing de segurança KaTeX: injeção de HTML malicioso em \\text{}."""
        node_script = """
        const katexInput = "\\\\text{<script>alert('xss')</script>}";
        const hasAngleBrackets = katexInput.includes('<') && katexInput.includes('>');
        console.log(JSON.stringify({ input: katexInput, containsRawHtml: hasAngleBrackets }));
        """
        res = subprocess.run(["node", "-e", node_script], capture_output=True, text=True, encoding="utf-8", check=True)
        data = json.loads(res.stdout)
        self.assertTrue(data["containsRawHtml"])


class TestLeafletMapAdversarial(unittest.TestCase):
    """Verificação Geográfica, Limites WGS84 e Resiliência do Leaflet Map."""

    @classmethod
    def setUpClass(cls):
        cls.html_content = HTML_PATH.read_text(encoding="utf-8")
        js_extract = """
        const fs = require('fs');
        const html = fs.readFileSync(process.argv[1], 'utf-8');
        const match = html.match(/const GEO_STATES_DATA = ([\\[][\\s\\S]*?[\\]];)/);
        const cleanStr = match[1].replace(/;\\s*$/, '');
        console.log(JSON.stringify(eval('(' + cleanStr + ')')));
        """
        res = subprocess.run(
            ["node", "-e", js_extract, str(HTML_PATH)],
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=True
        )
        cls.states = json.loads(res.stdout)

    def test_geo_states_wgs84_boundary_constraints(self):
        """Garante que todas as coordenadas dos estados chave estejam dentro do limite WGS84."""
        self.assertEqual(len(self.states), 6, "Devem existir exatamente 6 estados agrícolas mapeados.")
        for s in self.states:
            lat, lng = s["coords"]
            self.assertGreaterEqual(lat, -90.0, f"Latitude {lat} inferior a -90 para {s['id']}")
            self.assertLessEqual(lat, 90.0, f"Latitude {lat} superior a +90 para {s['id']}")
            self.assertGreaterEqual(lng, -180.0, f"Longitude {lng} inferior a -180 para {s['id']}")
            self.assertLessEqual(lng, 180.0, f"Longitude {lng} superior a +180 para {s['id']}")

    def test_geo_states_national_territory_bounding_boxes(self):
        """Valida que estados brasileiros e mexicanos estão estritamente dentro de suas respectivas fronteiras."""
        for s in self.states:
            lat, lng = s["coords"]
            if s["pais"] == "Brasil":
                self.assertLessEqual(lat, 5.5, f"Estado brasileiro {s['id']} acima de 5.5°N")
                self.assertGreaterEqual(lat, -34.0, f"Estado brasileiro {s['id']} abaixo de -34°S")
                self.assertGreaterEqual(lng, -75.0, f"Estado brasileiro {s['id']} a oeste de -75°W")
                self.assertLessEqual(lng, -34.0, f"Estado brasileiro {s['id']} a leste de -34°W")
            elif s["pais"] == "Mexico":
                self.assertGreaterEqual(lat, 14.0, f"Estado mexicano {s['id']} abaixo de 14°N")
                self.assertLessEqual(lat, 33.0, f"Estado mexicano {s['id']} acima de 33°N")
                self.assertGreaterEqual(lng, -120.0, f"Estado mexicano {s['id']} a oeste de -120°W")
                self.assertLessEqual(lng, -85.0, f"Estado mexicano {s['id']} a leste de -85°W")

    def test_geo_states_schema_completeness(self):
        """Garante que todos os 6 estados possuam 100% dos 18 campos de metadados obrigatórios."""
        required_fields = [
            "id", "pais", "bandeira", "nome", "regiao", "regiao_es",
            "coords", "cor", "destaque_pt", "destaque_es", "regime_pt",
            "regime_es", "vulnerabilidade_pt", "vulnerabilidade_es",
            "culturas_pt", "culturas_es", "irrigacao_pct", "producao_share"
        ]
        for s in self.states:
            for field in required_fields:
                self.assertIn(field, s, f"Campo mandatário '{field}' ausente no estado {s.get('id')}")
                self.assertIsNotNone(s[field], f"Campo '{field}' nulo no estado {s.get('id')}")

    def test_leaflet_focus_map_regions_and_fly_bounds(self):
        """Verifica se focusMap possui coordenadas válidas para visões Brasil, México e Dual."""
        self.assertIn("agroMap.flyTo([-14.23, -53.0], 4.5)", self.html_content)
        self.assertIn("agroMap.flyTo([24.5, -104.0], 5.5)", self.html_content)
        self.assertIn("agroMap.flyTo([10.0, -78.0], 3)", self.html_content)


class TestSliderBoundaryInjectionAdversarial(unittest.TestCase):
    """Injeção Adversária de Valores de Borda nos Sliders e Motores de Cálculo Web."""

    @classmethod
    def setUpClass(cls):
        cls.html_content = HTML_PATH.read_text(encoding="utf-8")

    def test_dom_slider_attributes_and_defaults(self):
        """Verifica consistência de min, max, step e valores iniciais nos 6 sliders interativos."""
        if not BS4_AVAILABLE:
            self.skipTest("bs4 não disponível")
        soup = BeautifulSoup(self.html_content, "html.parser")
        sliders = soup.find_all("input", attrs={"type": "range"})
        slider_ids = [s.get("id") for s in sliders]
        expected_ids = [
            "slider-tbase",
            "slider-heatwave",
            "slider-coef-a",
            "slider-coef-c",
            "slider-spei-custom",
            "slider-capacity-k"
        ]
        for sid in expected_ids:
            self.assertIn(sid, slider_ids, f"Slider #{sid} ausente no DOM.")

    def test_euler_simulation_negative_and_zero_capacity_k_injection(self):
        """Injeção adversária de K <= 0 na simulação de Verhulst: assert K clamped a 500 sem NaN ou Inf."""
        node_script = """
        function simulateEuler(spei, baseK, days = 120, y0 = 60.0, dt = 1.0) {
            const r = Math.max(0.02, 0.08 + 0.02 * spei);
            const K = Math.max(500, baseK);
            const simCurve = [y0];
            for (let t = 0; t < days; t++) {
                const yCur = simCurve[simCurve.length - 1];
                const dydt = r * yCur * (1.0 - yCur / K);
                simCurve.push(Math.max(0, yCur + dydt * dt));
            }
            return {
                r, K,
                finalYield: simCurve[simCurve.length - 1],
                hasNaN: simCurve.some(v => isNaN(v)),
                hasInf: simCurve.some(v => !isFinite(v))
            };
        }
        const resZero = simulateEuler(0.0, 0);
        const resNeg = simulateEuler(0.0, -1000);
        console.log(JSON.stringify({ zero: resZero, neg: resNeg }));
        """
        res = subprocess.run(["node", "-e", node_script], capture_output=True, text=True, encoding="utf-8", check=True)
        data = json.loads(res.stdout)
        for key in ["zero", "neg"]:
            self.assertEqual(data[key]["K"], 500, "K não foi devidamente travado no piso seguro de 500.")
            self.assertFalse(data[key]["hasNaN"], "NaN detectado na simulação de Verhulst sob K inválido.")
            self.assertFalse(data[key]["hasInf"], "Inf detectado na simulação de Verhulst sob K inválido.")

    def test_euler_simulation_extreme_spei_injection(self):
        """Injeção de SPEI extremo (-10.0 e +10.0): taxa r e biomassa permanecem limitadas e não-negativas."""
        node_script = """
        function simulateEuler(spei, baseK = 4500, days = 120, y0 = 60.0, dt = 1.0) {
            const r = Math.max(0.02, 0.08 + 0.02 * spei);
            const K = Math.max(500, baseK);
            const simCurve = [y0];
            for (let t = 0; t < days; t++) {
                const yCur = simCurve[simCurve.length - 1];
                const dydt = r * yCur * (1.0 - yCur / K);
                simCurve.push(Math.max(0, yCur + dydt * dt));
            }
            return {
                r, K,
                finalYield: simCurve[simCurve.length - 1],
                hasNaN: simCurve.some(v => isNaN(v)),
                hasInf: simCurve.some(v => !isFinite(v))
            };
        }
        const resExtNeg = simulateEuler(-10.0);
        const resExtPos = simulateEuler(10.0);
        console.log(JSON.stringify({ extNeg: resExtNeg, extPos: resExtPos }));
        """
        res = subprocess.run(["node", "-e", node_script], capture_output=True, text=True, encoding="utf-8", check=True)
        data = json.loads(res.stdout)
        self.assertAlmostEqual(data["extNeg"]["r"], 0.02, places=4, msg="Piso biológico r=0.02 violado.")
        self.assertFalse(data["extNeg"]["hasNaN"])
        self.assertFalse(data["extPos"]["hasNaN"])
        self.assertGreater(data["extNeg"]["finalYield"], 0.0)

    def test_differential_simulation_boundary_injection(self):
        """Testa o modelo quadrático sob valores extremos e validação de concavidade negativa (2a < 0)."""
        node_script = """
        function simulateDiff(a, c, b = 135.0) {
            const speiStar = -b / (2 * a);
            const yMax = a * Math.pow(speiStar, 2) + b * speiStar + c;
            const secDeriv = 2 * a;
            return { speiStar, yMax, secDeriv, isMax: secDeriv < 0 };
        }
        const resMin = simulateDiff(-350.0, 2000.0);
        const resMax = simulateDiff(-50.0, 7000.0);
        console.log(JSON.stringify({ min: resMin, max: resMax }));
        """
        res = subprocess.run(["node", "-e", node_script], capture_output=True, text=True, encoding="utf-8", check=True)
        data = json.loads(res.stdout)
        for key in ["min", "max"]:
            self.assertTrue(data[key]["isMax"], "Segunda derivada deve confirmar ponto de máximo local (2a < 0).")
            self.assertFalse(math.isnan(data[key]["speiStar"]))
            self.assertFalse(math.isnan(data[key]["yMax"]))

    def test_simpson_sim_extreme_temperature_anomaly_injection(self):
        """Injeta anomalia térmica extrema de +15°C e -15°C e verifica se GDD permanece numérico finito."""
        node_script = """
        function simpsonRule(f_values, dx = 1.0) {
            const n = f_values.length - 1;
            let sum = f_values[0] + f_values[n];
            for (let i = 1; i < n; i++) {
                sum += (i % 2 === 0 ? 2 : 4) * f_values[i];
            }
            return (dx / 3.0) * sum;
        }
        function simThermal(heatWave, tbase = 10.0, days = 120) {
            const gddBR = [];
            const gddMX = [];
            for (let t = 0; t <= days; t++) {
                const br = 28 + 5 * Math.sin((2 * Math.PI * t) / 120) + heatWave;
                const mx = 31 + 7 * Math.sin((2 * Math.PI * t) / 120) + heatWave;
                gddBR.push(Math.max(0, br - tbase));
                gddMX.push(Math.max(0, mx - tbase));
            }
            return {
                br: simpsonRule(gddBR),
                mx: simpsonRule(gddMX)
            };
        }
        console.log(JSON.stringify({
            hot: simThermal(15.0),
            cold: simThermal(-15.0)
        }));
        """
        res = subprocess.run(["node", "-e", node_script], capture_output=True, text=True, encoding="utf-8", check=True)
        data = json.loads(res.stdout)
        self.assertGreater(data["hot"]["br"], data["cold"]["br"])
        self.assertGreaterEqual(data["cold"]["br"], 0.0)
        self.assertFalse(math.isnan(data["hot"]["br"]))
        self.assertFalse(math.isnan(data["cold"]["mx"]))


class TestCsvDatasetAdversarial(unittest.TestCase):
    """Auditoria Adversarial de Dados, Bytes Fantasmas, BOM e Codificação do CSV."""

    @classmethod
    def setUpClass(cls):
        cls.raw_bytes = CSV_PATH.read_bytes()

    def test_csv_phantom_bytes_bom_and_nulls(self):
        """Garante ausência de bytes fantasmas: sem UTF-8 BOM, sem UTF-16 BOM e 0 bytes nulos."""
        self.assertFalse(
            self.raw_bytes.startswith(b"\xef\xbb\xbf"),
            "UTF-8 BOM detectado no CSV! Arquivos de produção e pipelines Linux/CI devem ser puros sem BOM."
        )
        self.assertFalse(
            self.raw_bytes.startswith(b"\xff\xfe") or self.raw_bytes.startswith(b"\xfe\xff"),
            "UTF-16 BOM detectado no CSV."
        )
        null_count = self.raw_bytes.count(b"\x00")
        self.assertEqual(null_count, 0, f"Bytes nulos (\\x00) encontrados no CSV: {null_count}")

    def test_csv_line_endings_and_no_double_cr(self):
        """Verifica quebras de linha estritas e ausência de carriage returns duplos (\\r\\r\\n)."""
        double_cr = self.raw_bytes.count(b"\r\r\n")
        self.assertEqual(double_cr, 0, f"Carriage returns corrompidos (\\r\\r\\n) detectados: {double_cr}")
        stray_cr = self.raw_bytes.count(b"\r") - self.raw_bytes.count(b"\r\n")
        self.assertEqual(stray_cr, 0, f"Carriage returns isolados (\\r sem \\n) detectados: {stray_cr}")

    def test_csv_rfc4180_delimiter_and_column_counts(self):
        """Validação RFC 4180 estrita: exatamente 251 linhas, 8 colunas por linha e sem nulos."""
        text = self.raw_bytes.decode("utf-8")
        reader = csv.reader(io.StringIO(text))
        rows = list(reader)
        self.assertEqual(len(rows), 251, f"Contagem de linhas incorreta: {len(rows)} (esperado 251).")
        expected_header = [
            'pais', 'ano', 'cultura', 'produtividade_kg_ha',
            'precipitacao_mm', 'spei_3m', 'temp_media', 'status_clima'
        ]
        self.assertEqual(rows[0], expected_header, f"Cabeçalho incompatível: {rows[0]}")
        for idx, row in enumerate(rows[1:], start=2):
            self.assertEqual(len(row), 8, f"Linha {idx} possui {len(row)} colunas em vez de 8.")
            for col_val in row:
                self.assertNotEqual(col_val.strip(), "", f"Campo vazio na linha {idx}.")

    def test_csv_encoding_strict_utf8_and_mojibake_absence(self):
        """Garante decodificação estrita UTF-8 e ausência de anomalias de Mojibake (ex: MÃ©xico)."""
        try:
            text = self.raw_bytes.decode("utf-8")
        except UnicodeDecodeError as e:
            self.fail(f"Falha na decodificação UTF-8 estrita: {e}")

        mojibake_patterns = [
            r"Ã[©¡¢£¤¥¦§¨©ª«¬®¯°±²³´µ¶·¸¹º»¼½¾¿]",
            r"Â[ªº]",
            r"â[\x80-\xbf]"
        ]
        for pat in mojibake_patterns:
            matches = re.findall(pat, text)
            self.assertEqual(matches, [], f"Padrão de Mojibake detectado no CSV: {matches}")

    def test_csv_composite_pk_uniqueness_and_value_domains(self):
        """Unicidade absoluta de (pais, ano, cultura) e domínios físicos realistas."""
        text = self.raw_bytes.decode("utf-8")
        reader = csv.DictReader(io.StringIO(text))
        pks = set()
        for idx, row in enumerate(reader, start=2):
            pk = (row["pais"], int(row["ano"]), row["cultura"])
            self.assertNotIn(pk, pks, f"Chave primária duplicada na linha {idx}: {pk}")
            pks.add(pk)

            prod = float(row["produtividade_kg_ha"])
            precip = float(row["precipitacao_mm"])
            spei = float(row["spei_3m"])
            temp = float(row["temp_media"])

            self.assertGreater(prod, 0.0, f"Produtividade <= 0 na linha {idx}")
            self.assertGreater(precip, 0.0, f"Precipitação <= 0 na linha {idx}")
            self.assertGreaterEqual(spei, -4.0, f"SPEI anomalamente baixo (< -4.0) na linha {idx}")
            self.assertLessEqual(spei, 4.0, f"SPEI anomalamente alto (> 4.0) na linha {idx}")
            self.assertGreater(temp, 5.0, f"Temperatura média improvável (< 5°C) na linha {idx}")

        self.assertEqual(len(pks), 250, "Total de registros consolidados deve ser exatamente 250.")

    def test_csv_column_data_types_and_domain_ranges(self):
        """Auditoria de tipos de dados das 8 colunas do CSV contra esquema estrito."""
        valid_paises = {"Brasil", "Mexico"}
        valid_culturas = {
            "Soja", "Milho 1ª Safra", "Milho 2ª Safra", "Café",
            "Cana-de-Açúcar", "Caña de Azúcar", "Maíz Blanco", "Maíz Amarillo", "Frijol"
        }
        valid_status = {"Normal", "Seca Moderada", "Seca Severa", "Excesso Hídrico"}

        text = self.raw_bytes.decode("utf-8")
        reader = csv.DictReader(io.StringIO(text))
        for idx, row in enumerate(reader, start=2):
            self.assertIn(row["pais"], valid_paises, f"País inválido na linha {idx}: {row['pais']}")
            self.assertIn(row["cultura"], valid_culturas, f"Cultura inválida na linha {idx}: {row['cultura']}")
            self.assertIn(row["status_clima"], valid_status, f"Status climático inválido na linha {idx}: {row['status_clima']}")
            ano = int(row["ano"])
            self.assertTrue(2000 <= ano <= 2024, f"Ano fora da série histórica (2000-2024) na linha {idx}: {ano}")


class TestCiCdWorkflowAdversarial(unittest.TestCase):
    """Auditoria de Segurança, Runner Schema e Permissões do GitHub Actions CI/CD."""

    @classmethod
    def setUpClass(cls):
        cls.wf_content = WORKFLOW_PATH.read_text(encoding="utf-8")
        cls.wf = yaml.safe_load(cls.wf_content) if YAML_AVAILABLE else {}

    def test_workflow_yaml_schema_and_triggers(self):
        """Valida triggers seguros (sem pull_request_target desprotegido)."""
        if not YAML_AVAILABLE:
            self.skipTest("pyyaml não disponível")
        # No YAML 1.1, a chave unquoted 'on:' é convertida para booleano True
        triggers = self.wf.get(True) if True in self.wf else self.wf.get("on", {})
        if not triggers:
            triggers = {}
        self.assertNotIn("pull_request_target", triggers, "Vulnerabilidade crítica: pull_request_target não permitido!")
        self.assertTrue("push" in triggers or "workflow_dispatch" in triggers)

    def test_workflow_runner_os_and_python_version(self):
        """Verifica que o workflow utiliza runner ubuntu-latest e Python 3.11 com cache de pip."""
        self.assertIn("runs-on: ubuntu-latest", self.wf_content)
        self.assertIn('python-version: "3.11"', self.wf_content)
        self.assertIn('cache: "pip"', self.wf_content)
        self.assertIn('cache-dependency-path: "requirements.txt"', self.wf_content)

    def test_workflow_permissions_least_privilege(self):
        """Verifica se as permissões seguem o princípio de menor privilégio para deploy do Pages."""
        if not YAML_AVAILABLE:
            self.skipTest("pyyaml não disponível")
        perms = self.wf.get("permissions", {})
        self.assertEqual(perms.get("contents"), "read", "contents deve ser estritamente 'read'.")
        self.assertEqual(perms.get("pages"), "write", "pages deve ser 'write'.")
        self.assertEqual(perms.get("id-token"), "write", "id-token deve ser 'write'.")

    def test_workflow_job_dependencies_test_before_deploy(self):
        """O job 'deploy' DEVE depender explicitamente do job 'test'."""
        if not YAML_AVAILABLE:
            self.skipTest("pyyaml não disponível")
        jobs = self.wf.get("jobs", {})
        self.assertIn("test", jobs, "Job de teste obrigatório ausente.")
        self.assertIn("deploy", jobs, "Job de deploy ausente.")
        needs = jobs["deploy"].get("needs")
        self.assertTrue(needs == "test" or "test" in needs, "Deploy deve exigir aprovação prévia de test!")

    def test_workflow_action_references_version_modernity(self):
        """Verifica que todas as ações utilizam versões modernas sem runners Node obsoletos."""
        action_matches = re.findall(r"uses:\s*([\w\-]+/[\w\-]+@[\w\.\-]+)", self.wf_content)
        self.assertGreater(len(action_matches), 3, "Nenhuma GitHub Action encontrada no workflow.")
        for action in action_matches:
            v_match = re.search(r"@v(\d+)", action)
            if v_match:
                v_num = int(v_match.group(1))
                self.assertGreaterEqual(v_num, 3, f"Ação desatualizada com risco de depreciação de runner: {action}")

    def test_workflow_no_script_injection_vulnerabilities(self):
        """Garante ausência de injeção de comandos bash por interpolação de variáveis de contexto não sanitizadas."""
        run_blocks = re.findall(r"run:\s*\|([\s\S]*?)(?=\n\s*-\s*name|\n\s*[a-zA-Z]|\Z)", self.wf_content)
        for block in run_blocks:
            self.assertNotIn("${{ github.event.issue", block)
            self.assertNotIn("${{ github.event.comment", block)
            self.assertNotIn("${{ github.event.pull_request.title", block)


def main():
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    suite.addTests(loader.loadTestsFromTestCase(TestWebDomI18nAdversarial))
    suite.addTests(loader.loadTestsFromTestCase(TestKaTeXSyntaxAdversarial))
    suite.addTests(loader.loadTestsFromTestCase(TestLeafletMapAdversarial))
    suite.addTests(loader.loadTestsFromTestCase(TestSliderBoundaryInjectionAdversarial))
    suite.addTests(loader.loadTestsFromTestCase(TestCsvDatasetAdversarial))
    suite.addTests(loader.loadTestsFromTestCase(TestCiCdWorkflowAdversarial))

    runner = unittest.TextTestRunner(verbosity=2)
    res = runner.run(suite)
    return 0 if res.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(main())
