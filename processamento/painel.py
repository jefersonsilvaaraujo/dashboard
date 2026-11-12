"""Painel integrado município x ano PRODES (MapBiomas, focos de calor e PRODES).

Recalcula a base materializada, grava historico/painel_municipio_ano.csv (modo CSV do
app e entrada da modelagem) e gera docs/dicionario_painel.md a partir dos comentários
das colunas no banco, com o tipo e a cobertura de cada variável.

Uso:  python processamento/painel.py
"""
import pandas as pd

import config
from banco import aplicar_migracoes, conectar

VISAO = "analise.vw_painel_municipio_ano"


def atualizar(conexao):
    conexao.execute("REFRESH MATERIALIZED VIEW analise.mv_painel_base")
    conexao.execute("ANALYZE analise.mv_painel_base")
    print("analise.mv_painel_base atualizada")


def ler_painel(conexao):
    cursor = conexao.execute(f"SELECT * FROM {VISAO} ORDER BY cd_mun, ano")
    return pd.DataFrame(cursor.fetchall(), columns=[c.name for c in cursor.description])


def exportar_csv(painel):
    painel.to_csv(config.PAINEL_CSV, sep=";", decimal=",", float_format="%.6f", index=False, encoding="utf-8")
    print(f"{len(painel)} linhas e {painel.shape[1]} colunas gravadas em {config.PAINEL_CSV}")


def gerar_dicionario(conexao, painel):
    """Dicionário de variáveis a partir do catálogo do PostgreSQL.

    Colunas herdadas da base materializada usam o comentário de lá.
    """
    descricoes = dict(conexao.execute(
        """
        SELECT a.attname, coalesce(col_description('analise.vw_painel_municipio_ano'::regclass, a.attnum),
                                   col_description('analise.mv_painel_base'::regclass, b.attnum))
        FROM pg_attribute a
        LEFT JOIN pg_attribute b ON b.attrelid = 'analise.mv_painel_base'::regclass AND b.attname = a.attname
        WHERE a.attrelid = 'analise.vw_painel_municipio_ano'::regclass AND a.attnum > 0
        """
    ).fetchall())
    tipos = dict(conexao.execute(
        "SELECT column_name, data_type FROM information_schema.columns"
        " WHERE table_schema = 'analise' AND table_name = 'vw_painel_municipio_ano'"
    ).fetchall())
    comentario_visao = conexao.execute(
        "SELECT obj_description('analise.vw_painel_municipio_ano'::regclass)").fetchone()[0]

    linhas = [
        "# Dicionário de variáveis do painel município x ano",
        "",
        f"{comentario_visao}.",
        "",
        f"Fonte: `{VISAO}` (gerado por `processamento/painel.py`). "
        f"{len(painel)} linhas: {painel['cd_mun'].nunique()} municípios, anos PRODES "
        f"{painel['ano'].min()} a {painel['ano'].max()}.",
        "",
        "Prefixos: `mb_` MapBiomas (mapa do ano civil anterior), `fq_` focos de calor, `pd_` PRODES, "
        "`vz_` média dos municípios vizinhos, `alvo_` variável a prever (ano seguinte).",
        "",
        "| Variável | Tipo | Preenchida | Descrição |",
        "|---|---|---|---|",
    ]
    for coluna in painel.columns:
        preenchida = f"{painel[coluna].notna().mean() * 100:.0f}%"
        descricao = (descricoes.get(coluna) or "").replace("|", "/")
        linhas.append(f"| `{coluna}` | {tipos.get(coluna, '')} | {preenchida} | {descricao} |")
    config.DICIONARIO_PAINEL.parent.mkdir(exist_ok=True)
    config.DICIONARIO_PAINEL.write_text("\n".join(linhas) + "\n", encoding="utf-8")
    print(f"Dicionário com {painel.shape[1]} variáveis gravado em {config.DICIONARIO_PAINEL}")


def main():
    with conectar() as conexao:
        aplicar_migracoes(conexao)
        atualizar(conexao)
        painel = ler_painel(conexao)
        exportar_csv(painel)
        gerar_dicionario(conexao, painel)


if __name__ == "__main__":
    main()
