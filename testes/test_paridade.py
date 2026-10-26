"""Paridade entre as duas fontes de dados do painel: PostgreSQL e CSVs.

O painel lendo do banco deve mostrar exatamente o que mostrava lendo dos CSVs.
Requer o banco no ar e carregado:

    docker compose up -d db
    docker compose run --rm etl
    pytest testes

Sem as variáveis PG*, o teste usa o .env do projeto (usuário somente leitura do app).
"""
import json
import os
import re
import subprocess
import sys
from pathlib import Path

import pandas as pd
import pytest

PROJETO = Path(__file__).resolve().parent.parent
MUNICIPIOS_TESTE = ["Cabixi (RO)", "Pau D'Arco (PA)", "Pau D'Arco (TO)", "Campos de Júlio (MT)", "Raposa (MA)"]


def ambiente_banco():
    """Variáveis PG* do ambiente ou, na falta delas, derivadas do .env."""
    if os.environ.get("PGHOST"):
        return {k: v for k, v in os.environ.items() if k.startswith("PG")}
    env_arquivo = PROJETO / ".env"
    if not env_arquivo.exists():
        pytest.skip("Sem PGHOST e sem .env: banco indisponível")
    valores = dict(
        linha.split("=", 1) for linha in env_arquivo.read_text(encoding="utf-8").splitlines()
        if "=" in linha and not linha.lstrip().startswith("#")
    )
    return {
        "PGHOST": "localhost",
        "PGPORT": valores.get("DB_PORTA", "5432"),
        "PGDATABASE": valores.get("POSTGRES_DB", "dashboard"),
        "PGUSER": valores.get("APP_DB_USER", "dashboard_app"),
        "PGPASSWORD": valores["APP_DB_PASSWORD"],
    }


@pytest.fixture(scope="module")
def banco():
    from sqlalchemy import create_engine, text

    os.environ.update(ambiente_banco())
    engine = create_engine("postgresql+psycopg://")
    with engine.connect() as conexao:
        conexao.execute(text("SELECT 1"))
    return engine


def ler(banco, sql):
    from sqlalchemy import text

    with banco.connect() as conexao:
        return pd.read_sql(text(sql), conexao)


def test_cobertura(banco):
    csv = pd.read_csv(PROJETO / "historico" / "estatisticas_coverage_historico.csv", sep=";", decimal=",")
    bd = ler(banco, "SELECT cd_mun AS \"CD_MUN\", nm_mun AS \"NM_MUN\", sigla_uf AS \"SIGLA_UF\", ano,"
                    " classe_cobertura, area_ha, perc_ocupacao FROM mapbiomas.vw_cobertura_municipio")
    chaves = ["CD_MUN", "ano", "classe_cobertura"]
    juntos = csv.merge(bd, on=chaves, how="outer", suffixes=("_csv", "_bd"), indicator=True)

    assert (juntos["_merge"] == "both").all(), "Linhas presentes em só uma das fontes"
    assert (juntos["NM_MUN_csv"] == juntos["NM_MUN_bd"]).all()
    assert (juntos["SIGLA_UF_csv"] == juntos["SIGLA_UF_bd"]).all()
    # O CSV guarda 2 casas decimais; o banco guarda o valor completo da fonte
    assert (juntos["area_ha_csv"] - juntos["area_ha_bd"]).abs().max() <= 0.005
    assert (juntos["perc_ocupacao_csv"] - juntos["perc_ocupacao_bd"]).abs().max() <= 0.005


def test_legenda(banco):
    csv = pd.read_csv(PROJETO / "historico" / "legenda_mapbiomas.csv")
    bd = ler(banco, "SELECT classe_id AS classe_cobertura, nome AS nome_classe, cor AS cor_rgb, grupo, tipo"
                    " FROM mapbiomas.classe ORDER BY classe_id")
    pd.testing.assert_frame_equal(csv, bd, check_dtype=False)


def test_municipios(banco):
    csv = pd.read_csv(PROJETO / "coordenadas" / "municipios_coord.csv").sort_values("CD_MUN").reset_index(drop=True)
    bd = ler(banco, "SELECT cd_mun AS \"CD_MUN\", nome AS nome_municipio, sigla_uf AS \"SIGLA_UF\","
                    " area_km2::float8 AS \"AREA_KM2\", latitude, longitude FROM ref.vw_municipio ORDER BY cd_mun")
    pd.testing.assert_frame_equal(csv, bd, check_dtype=False, atol=1e-9, rtol=0)


def test_focos_mensais(banco):
    csv = pd.read_csv(PROJETO / "historico" / "focos_municipio_mensal.csv", sep=";", decimal=",")
    bd = ler(banco, 'SELECT cd_mun AS "CD_MUN", nm_mun AS "NM_MUN", sigla_uf AS "SIGLA_UF", ano, mes, focos,'
                    " focos_com_frp, frp_medio, frp_maximo, precipitacao_media, dias_sem_chuva_medio, risco_fogo_medio"
                    " FROM queimadas.vw_focos_municipio_mes ORDER BY cd_mun, ano, mes")
    pd.testing.assert_frame_equal(csv, bd, check_dtype=False, atol=1e-4, rtol=0)


def test_focos_2024_conferem_com_contagem_independente(banco):
    # 51.628 focos em 2024 na área de estudo, contados com geopandas direto do arquivo do INPE
    # (validação feita na Fase 2). O ano de 2024 é fechado; o número não deve mudar.
    total = ler(banco, "SELECT sum(focos) AS n FROM queimadas.vw_focos_municipio_mes WHERE ano = 2024")["n"][0]
    assert total == 51628


def test_prodes(banco):
    csv = pd.read_csv(PROJETO / "historico" / "prodes_area_classe_municipio.csv", sep=";", decimal=",")
    bd = ler(banco, 'SELECT cd_mun AS "CD_MUN", nm_mun AS "NM_MUN", sigla_uf AS "SIGLA_UF", bioma,'
                    " classe_id, rotulo, tipo, ano, area_ha"
                    " FROM prodes.vw_area_classe_municipio ORDER BY cd_mun, bioma, classe_id")
    pd.testing.assert_frame_equal(csv, bd, check_dtype=False, atol=1e-4, rtol=0)


def test_prodes_cobre_a_area_oficial_dos_municipios(banco):
    # A soma das classes PRODES de cada município deve reproduzir a sua área oficial (IBGE).
    # Pode faltar área onde o limite municipal inclui mar ou passa da fronteira do Brasil
    # no raster (ex.: litoral do MA, fronteira com a Bolívia), mas nunca sobrar.
    RAPOSA = 2109452  # 13% do limite municipal é mar
    razao = ler(banco, "SELECT a.cd_mun, sum(a.area_ha) / (m.area_km2 * 100) AS razao"
                       " FROM prodes.area_classe a JOIN ref.municipio m USING (cd_mun)"
                       " GROUP BY a.cd_mun, m.area_km2").set_index("cd_mun")["razao"]

    assert (razao <= 1.001).all(), f"Área PRODES acima da oficial: {razao[razao > 1.001].to_dict()}"
    assert abs(razao.median() - 1) < 0.0001, f"Viés sistemático na área dos pixels: mediana {razao.median():.5f}"
    abaixo = razao.drop(RAPOSA)
    assert (abaixo >= 0.98).all(), f"Área PRODES muito abaixo da oficial: {abaixo[abaixo < 0.98].to_dict()}"


def test_painel(banco):
    csv = pd.read_csv(PROJETO / "historico" / "painel_municipio_ano.csv", sep=";", decimal=",")
    bd = ler(banco, "SELECT * FROM analise.vw_painel_municipio_ano ORDER BY cd_mun, ano")
    assert list(csv.columns) == list(bd.columns)
    pd.testing.assert_frame_equal(csv, bd, check_dtype=False, atol=1e-5, rtol=0)


CONSISTENCIA_PAINEL = {
    "desmatamento igual ao PRODES": """
        SELECT abs((SELECT sum(pd_desmatamento_ha) FROM analise.mv_painel_base) -
                   (SELECT sum(a.area_ha) FROM prodes.area_classe a JOIN prodes.classe c USING (classe_id)
                    JOIN ref.municipio m USING (cd_mun)
                    WHERE c.tipo = 'desmatamento' AND c.ano >= 2008 AND m.area_estudo)) < 1e-6""",
    "focos iguais à contagem por data": """
        SELECT (SELECT sum(fq_focos) FROM analise.mv_painel_base) =
               (SELECT count(*) FROM queimadas.foco f JOIN ref.municipio m USING (cd_mun)
                WHERE m.area_estudo AND f.data_hora >= make_timestamptz((SELECT min(ano) FROM analise.mv_painel_base) - 1, 8, 1, 0, 0, 0, 'UTC')
                  AND f.data_hora < make_timestamptz((SELECT max(ano) FROM analise.mv_painel_base), 8, 1, 0, 0, 0, 'UTC'))""",
    "MapBiomas do ano anterior": """
        SELECT NOT EXISTS (
            SELECT 1 FROM analise.mv_painel_base p
            JOIN (SELECT c.cd_mun, c.ano + 1 AS ano, sum(c.area_ha) AS natural_ha
                  FROM mapbiomas.cobertura c JOIN mapbiomas.classe k USING (classe_id)
                  WHERE k.grupo IN ('Floresta', 'Vegetação Herbácea e Arbustiva') GROUP BY 1, 2) m USING (cd_mun, ano)
            WHERE abs(p.mb_vegetacao_natural_ha - m.natural_ha) > 1e-6)""",
    "vegetação nativa contínua entre anos": """
        SELECT NOT EXISTS (
            SELECT 1 FROM analise.mv_painel_base a
            JOIN analise.mv_painel_base b ON b.cd_mun = a.cd_mun AND b.ano = a.ano - 1
            WHERE abs(a.pd_vegetacao_nativa_inicio_ha - b.pd_vegetacao_nativa_fim_ha) > 1e-6)""",
    "defasagens e alvos coerentes": """
        SELECT NOT EXISTS (
            SELECT 1 FROM analise.vw_painel_municipio_ano a
            JOIN analise.vw_painel_municipio_ano b ON b.cd_mun = a.cd_mun AND b.ano = a.ano + 1
            WHERE b.pd_desmatamento_ha_lag1 IS DISTINCT FROM a.pd_desmatamento_ha
               OR a.alvo_desmatamento_ha_t1 IS DISTINCT FROM b.pd_desmatamento_ha
               OR b.fq_focos_lag1 IS DISTINCT FROM a.fq_focos)""",
    "vizinhança simétrica": """
        SELECT NOT EXISTS (
            SELECT 1 FROM ref.mv_municipio_vizinho v
            WHERE NOT EXISTS (SELECT 1 FROM ref.mv_municipio_vizinho w
                              WHERE w.cd_mun = v.cd_mun_vizinho AND w.cd_mun_vizinho = v.cd_mun))""",
    "uma linha por município e ano": """
        SELECT count(*) = count(DISTINCT (cd_mun, ano)) FROM analise.vw_painel_municipio_ano""",
}


@pytest.mark.parametrize("descricao", CONSISTENCIA_PAINEL)
def test_consistencia_do_painel(banco, descricao):
    from sqlalchemy import text

    with banco.connect() as conexao:
        assert conexao.execute(text(CONSISTENCIA_PAINEL[descricao])).scalar(), descricao


ROTEIRO_APP = r"""
import json, sys
from streamlit.testing.v1 import AppTest
resultado = {}
for municipio in json.loads(sys.argv[1]):
    at = AppTest.from_file(sys.argv[2], default_timeout=300)
    at.run()
    if municipio != "Todos":
        at.sidebar.selectbox[0].select(municipio).run()
    resultado[municipio] = {
        "excecoes": [e.value for e in at.exception],
        "metricas": [[m.label, m.value, m.delta] for m in at.metric],
        "alertas": [w.value for w in at.warning],
        "infos": [i.value for i in at.info],
        "graficos": len(at.get("plotly_chart")),
    }
print("RESULTADO=" + json.dumps(resultado, ensure_ascii=False))
"""


def rodar_app(ambiente):
    municipios = ["Todos"] + MUNICIPIOS_TESTE
    saida = subprocess.run(
        [sys.executable, "-c", ROTEIRO_APP, json.dumps(municipios), str(PROJETO / "app.py")],
        capture_output=True, text=True, encoding="utf-8", env={**ambiente, "PYTHONUTF8": "1"},
        cwd=PROJETO, timeout=900,
    )
    linha = [l for l in saida.stdout.splitlines() if l.startswith("RESULTADO=")]
    assert linha, saida.stderr[-3000:]
    return json.loads(linha[0].removeprefix("RESULTADO="))


def numero(token):
    """Converte '16273.05', '1.253.056' ou '-63.1' em float."""
    if token.count(".") > 1:  # separador de milhar no formato brasileiro
        token = token.replace(".", "")
    return float(token)


def equivalentes(a, b):
    """Igualdade estrutural; números podem diferir só no arredondamento.

    O CSV guarda as áreas com 2 casas decimais e o banco guarda o valor completo,
    então somas de milhares de linhas podem diferir na última casa exibida.
    """
    if isinstance(a, dict) and isinstance(b, dict):
        return a.keys() == b.keys() and all(equivalentes(a[k], b[k]) for k in a)
    if isinstance(a, list) and isinstance(b, list):
        return len(a) == len(b) and all(equivalentes(x, y) for x, y in zip(a, b))
    if isinstance(a, str) and isinstance(b, str):
        padrao = r"-?\d[\d.]*"
        if re.sub(padrao, "#", a) != re.sub(padrao, "#", b):
            return False
        return all(
            abs(numero(x) - numero(y)) <= max(0.1, 1e-4 * abs(numero(x)))
            for x, y in zip(re.findall(padrao, a), re.findall(padrao, b))
        )
    return a == b


def test_app_mostra_o_mesmo_nas_duas_fontes(banco):
    sem_banco = {k: v for k, v in os.environ.items() if not k.startswith("PG")}
    com_banco = {**sem_banco, **ambiente_banco()}

    pelo_csv = rodar_app(sem_banco)
    pelo_banco = rodar_app(com_banco)

    for municipio, resultado in pelo_banco.items():
        assert resultado["excecoes"] == [], f"{municipio}: {resultado['excecoes']}"
        assert pelo_csv[municipio]["excecoes"] == [], f"{municipio} (CSV): {pelo_csv[municipio]['excecoes']}"
        # O mapa de pontos dos focos só existe com o banco, então o total de gráficos difere
        assert resultado["graficos"] > 0 and pelo_csv[municipio]["graficos"] > 0
        del resultado["graficos"], pelo_csv[municipio]["graficos"]
    for municipio in pelo_csv:
        assert equivalentes(pelo_banco[municipio], pelo_csv[municipio]), (
            f"{municipio}:\n  banco: {pelo_banco[municipio]}\n  csv:   {pelo_csv[municipio]}"
        )
