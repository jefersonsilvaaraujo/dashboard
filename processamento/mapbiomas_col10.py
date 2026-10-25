"""Cobertura e uso da terra por município - MapBiomas Coleção 10.1.

Converte a planilha oficial de estatísticas municipais do MapBiomas para o
formato lido pelo app e grava também a legenda da coleção (nome, cor, grupo e
tipo natural/antrópico de cada classe).

Fonte: https://doi.org/10.58053/MapBiomas/SJZOLT
Uso:   python processamento/mapbiomas_col10.py
"""
import re

import pandas as pd

import config
from municipios import carregar_municipios, normalizar_nome

TIPOS = {
    "Natural": "Natural",
    "Antropic": "Antrópico",
    "Natural/Antropic": "Natural ou Antrópico",
    "Undefined": "Não observado",
}

# Classes presentes nos dados mas ausentes da aba de legenda da planilha
CLASSES_EXTRAS = {
    0: ("Não Observado", "#d9d9d9", "Não observado"),  # cor oficial é branca, invisível no gráfico
    13: ("Outras Formações não Florestais", "#d89f5c", "Vegetação Herbácea e Arbustiva"),
}


def ler_legenda(classes_tipo):
    """Monta a legenda a partir da aba LEGEND_CODE da planilha."""
    bruto = pd.read_excel(config.MAPBIOMAS_XLSX, sheet_name=config.MAPBIOMAS_ABA_LEGENDA,
                          header=None, engine="calamine")
    bruto = bruto.iloc[:, [1, 3, 4]].dropna()
    bruto.columns = ["rotulo", "codigo", "cor"]
    bruto = bruto[pd.to_numeric(bruto["codigo"], errors="coerce").notna()]

    linhas, grupos = [], {}
    for rotulo, codigo, cor in bruto.itertuples(index=False):
        numeracao, nome = re.match(r"^([\d.]+)\s*(.+)$", rotulo.strip()).groups()
        nivel = numeracao.strip(".").split(".")
        if len(nivel) == 1:
            grupos[nivel[0]] = nome.strip()
            continue
        linhas.append({
            "classe_cobertura": int(codigo),
            "nome_classe": nome.strip(),
            "cor_rgb": cor.strip().lower(),
            "grupo": grupos[nivel[0]],
        })
    legenda = pd.DataFrame(linhas)

    extras = pd.DataFrame([
        {"classe_cobertura": k, "nome_classe": n, "cor_rgb": c, "grupo": g}
        for k, (n, c, g) in CLASSES_EXTRAS.items()
    ])
    legenda = pd.concat([legenda, extras], ignore_index=True)

    # Mantém só as classes que existem nos dados (descarta níveis agregados)
    legenda = legenda[legenda["classe_cobertura"].isin(classes_tipo.index)].copy()
    legenda["tipo"] = legenda["classe_cobertura"].map(classes_tipo).map(TIPOS)
    return legenda.sort_values("classe_cobertura").reset_index(drop=True)


def gerar_cobertura():
    planilha = pd.read_excel(config.MAPBIOMAS_XLSX, sheet_name=config.MAPBIOMAS_ABA,
                             engine="calamine")
    planilha.columns = [int(c) if isinstance(c, float) else c for c in planilha.columns]
    anos = [c for c in planilha.columns if isinstance(c, int)]

    classes_tipo = planilha.drop_duplicates("class_id").set_index("class_id")["class_level_0"]
    legenda = ler_legenda(classes_tipo)

    municipios = carregar_municipios()
    municipios["chave"] = municipios["nome_municipio"].map(normalizar_nome) + "|" + municipios["SIGLA_UF"]
    planilha["chave"] = planilha["municipality"].map(normalizar_nome) + "|" + planilha["state_acronym"]

    faltando = set(municipios["chave"]) - set(planilha["chave"])
    if faltando:
        raise ValueError(f"Municípios sem correspondência na planilha: {sorted(faltando)}")

    # A planilha separa o município por bioma; soma-se tudo por município
    longa = (
        planilha[planilha["chave"].isin(municipios["chave"])]
        .melt(id_vars=["chave", "class_id"], value_vars=anos, var_name="ano", value_name="area_ha")
        .groupby(["chave", "ano", "class_id"], as_index=False)["area_ha"].sum()
    )
    longa = longa[longa["area_ha"] > 0]

    cobertura = municipios.merge(longa, on="chave")
    cobertura["perc_ocupacao"] = cobertura["area_ha"] / (cobertura["AREA_KM2"] * 100) * 100
    cobertura = cobertura.rename(columns={"nome_municipio": "NM_MUN", "class_id": "classe_cobertura"})
    cobertura["classe_cobertura"] = cobertura["classe_cobertura"].astype(int)
    cobertura = cobertura[["CD_MUN", "NM_MUN", "SIGLA_UF", "ano", "classe_cobertura", "area_ha", "perc_ocupacao"]]

    ordem = {cd: i for i, cd in enumerate(municipios["CD_MUN"])}
    cobertura = cobertura.sort_values(
        ["CD_MUN", "ano", "classe_cobertura"], key=lambda s: s.map(ordem) if s.name == "CD_MUN" else s
    )
    return cobertura, legenda


if __name__ == "__main__":
    cobertura, legenda = gerar_cobertura()
    cobertura.to_csv(config.COBERTURA_CSV, sep=";", decimal=",", float_format="%.2f",
                     index=False, encoding="utf-8")
    legenda.to_csv(config.LEGENDA_CSV, index=False, encoding="utf-8")
    print(f"{len(cobertura)} linhas ({cobertura['CD_MUN'].nunique()} municípios, "
          f"{cobertura['ano'].min()}-{cobertura['ano'].max()}) gravadas em {config.COBERTURA_CSV}")
    print(f"{len(legenda)} classes gravadas em {config.LEGENDA_CSV}")
