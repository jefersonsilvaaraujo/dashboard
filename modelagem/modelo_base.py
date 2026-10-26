"""Modelo de referência: risco de desmatamento no ano seguinte por município.

Alvo: taxa de desmatamento PRODES no ano seguinte (% da vegetação nativa restante).
Divisão temporal em três partes, sem embaralhar anos:
- a configuração do modelo é escolhida treinando com 2013-2017 e validando em 2018-2019;
- a configuração escolhida é retreinada com 2013-2019 e avaliada uma única vez no teste
  (anos PRODES 2020-2024, alvos 2021-2025).
O modelo é comparado com duas regras simples; só tem valor se as superar.

Entrada: historico/painel_municipio_ano.csv (gerado por processamento/painel.py).
Saída:   modelagem/resultados/ (relatório, métricas, importância e risco previsto).

Uso:  docker compose run --rm etl python ../modelagem/modelo_base.py
"""
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.inspection import permutation_importance
from sklearn.metrics import mean_absolute_error

PROJETO = Path(__file__).resolve().parent.parent
PAINEL_CSV = PROJETO / "historico" / "painel_municipio_ano.csv"
RESULTADOS = Path(__file__).resolve().parent / "resultados"
SEMENTE = 42

ALVO = "alvo_taxa_desmatamento_t1"
PRIMEIRO_ANO = 2013          # PRODES anual em toda a área
ULTIMO_ANO_AJUSTE = 2017     # treino usado para escolher a configuração
ULTIMO_ANO_TREINO = 2019     # 2018-2019 = validação; depois, treino final até aqui

# Configurações candidatas, escolhidas na validação (nunca no teste)
HIPERPARAMETROS = {
    "moderado": dict(max_iter=400, learning_rate=0.05, max_leaf_nodes=15, min_samples_leaf=30, l2_regularization=1.0),
    "regularizado": dict(max_iter=200, learning_rate=0.03, max_leaf_nodes=7, min_samples_leaf=60, l2_regularization=1.0),
}
CONFIGURACOES = [
    {"nome": f"{nome}{' + desvio da persistência' if residual else ''}", "hiper": hiper, "residual": residual}
    for nome, hiper in HIPERPARAMETROS.items() for residual in (False, True)
]
# Identificadores, textos e alvos não entram como variáveis; o ano também não, pois árvores
# não extrapolam para anos fora do treino
FORA_DO_MODELO = {"cd_mun", "nm_mun", "sigla_uf", "ano", "comparavel_prodes",
                  "alvo_desmatamento_ha_t1", "alvo_taxa_desmatamento_t1"}
CATEGORICAS = ["bioma_predominante", "cd_uf"]
PARCELA_MAIOR_RISCO = 0.2


def preparar(painel):
    dados = painel[(painel["ano"] >= PRIMEIRO_ANO)].copy()
    for coluna in CATEGORICAS:
        dados[coluna] = dados[coluna].astype("category")
    # Áreas em hectares viram fração da área do município: municípios de tamanhos
    # diferentes ficam comparáveis
    area_ha = dados["area_km2"] * 100
    for coluna in [c for c in dados.columns if c.endswith(("_ha", "_ha_lag1", "_ha_lag2", "_ha_mm3"))]:
        if not coluna.startswith("alvo"):
            dados[coluna] = dados[coluna] / area_ha
    variaveis = [c for c in dados.columns if c not in FORA_DO_MODELO]
    return dados, variaveis


def treinar(dados, variaveis, configuracao):
    """Ajusta o modelo em log(1 + taxa); com `residual`, aprende o desvio em relação à taxa atual."""
    alvo = np.log1p(dados[ALVO].to_numpy())
    if configuracao["residual"]:
        alvo = alvo - np.log1p(dados["pd_taxa_desmatamento"].fillna(0).to_numpy())
    modelo = HistGradientBoostingRegressor(categorical_features="from_dtype", random_state=SEMENTE,
                                           **configuracao["hiper"])
    return modelo.fit(dados[variaveis], alvo)


def prever(modelo, dados, variaveis, configuracao):
    previsto = modelo.predict(dados[variaveis])
    if configuracao["residual"]:
        previsto = previsto + np.log1p(dados["pd_taxa_desmatamento"].fillna(0).to_numpy())
    return np.clip(np.expm1(previsto), 0, None)


def precisao_maior_risco(real, previsto, ano):
    """Entre os municípios com maior risco previsto em cada ano, fração que está de fato
    entre os de maior desmatamento real (mesma quantidade)."""
    acertos, total = 0, 0
    for _, grupo in pd.DataFrame({"real": real, "previsto": previsto, "ano": ano}).groupby("ano"):
        n = max(1, int(round(len(grupo) * PARCELA_MAIOR_RISCO)))
        previstos = set(grupo.nlargest(n, "previsto").index)
        reais = set(grupo.nlargest(n, "real").index)
        acertos += len(previstos & reais)
        total += n
    return acertos / total


def avaliar(nome, real, previsto, ano):
    return {
        "modelo": nome,
        "erro_medio_absoluto_pp": mean_absolute_error(real, previsto),
        "correlacao_ranking_spearman": pd.Series(real).corr(pd.Series(previsto, index=real.index), method="spearman"),
        f"acerto_top_{int(PARCELA_MAIOR_RISCO * 100)}pct": precisao_maior_risco(real, previsto, ano),
    }


def main():
    RESULTADOS.mkdir(exist_ok=True)
    painel = pd.read_csv(PAINEL_CSV, sep=";", decimal=",")
    dados, variaveis = preparar(painel)

    com_alvo = dados.dropna(subset=[ALVO])
    ajuste = com_alvo[com_alvo["ano"] <= ULTIMO_ANO_AJUSTE]
    validacao = com_alvo[com_alvo["ano"].between(ULTIMO_ANO_AJUSTE + 1, ULTIMO_ANO_TREINO)]
    treino = com_alvo[com_alvo["ano"] <= ULTIMO_ANO_TREINO]
    teste = com_alvo[com_alvo["ano"] > ULTIMO_ANO_TREINO]

    # 1. Escolha da configuração na validação, pela correlação de ranking
    resultados_validacao = pd.DataFrame([
        avaliar(c["nome"], validacao[ALVO], prever(treinar(ajuste, variaveis, c), validacao, variaveis, c),
                validacao["ano"])
        for c in CONFIGURACOES
    ])
    escolhida = CONFIGURACOES[int(resultados_validacao["correlacao_ranking_spearman"].idxmax())]
    resultados_validacao.to_csv(RESULTADOS / "validacao.csv", index=False, float_format="%.4f")

    # 2. Retreino com 2013-2019 e avaliação única no teste
    modelo = treinar(treino, variaveis, escolhida)
    previsto = prever(modelo, teste, variaveis, escolhida)

    # Regras de referência (taxa relativa à vegetação nativa, como o alvo)
    persistencia = teste["pd_taxa_desmatamento"].fillna(0)
    media_3_anos = (100 * teste["pd_desmatamento_ha_mm3"] / teste["pd_vegetacao_nativa_fim_ha"]).fillna(0)

    metricas = pd.DataFrame([
        avaliar("Persistência (repete o ano atual)", teste[ALVO], persistencia.values, teste["ano"]),
        avaliar("Média dos últimos 3 anos", teste[ALVO], media_3_anos.values, teste["ano"]),
        avaliar(f"Gradient boosting ({escolhida['nome']})", teste[ALVO], previsto, teste["ano"]),
    ])
    metricas.to_csv(RESULTADOS / "metricas.csv", index=False, float_format="%.4f")

    # Importância por permutação, medida no teste (queda do ranking ao embaralhar a variável)
    def pontuacao_ranking(estimador, x, y):
        previsao = estimador.predict(x)
        if escolhida["residual"]:
            previsao = previsao + np.log1p(x["pd_taxa_desmatamento"].fillna(0).to_numpy())
        return pd.Series(y).corr(pd.Series(previsao, index=y.index), method="spearman")

    importancia = permutation_importance(modelo, teste[variaveis], np.log1p(teste[ALVO]),
                                         scoring=pontuacao_ranking, n_repeats=10, random_state=SEMENTE)
    importancias = (pd.DataFrame({"variavel": variaveis, "importancia": importancia.importances_mean,
                                  "desvio": importancia.importances_std})
                    .sort_values("importancia", ascending=False))
    importancias.to_csv(RESULTADOS / "importancia_variaveis.csv", index=False, float_format="%.4f")

    # Modelo final com todos os anos com alvo; risco previsto a partir do último ano do painel
    modelo = treinar(com_alvo, variaveis, escolhida)
    ultimo_ano = int(dados["ano"].max())
    atual = dados[dados["ano"] == ultimo_ano]
    risco = atual[["cd_mun", "nm_mun", "sigla_uf", "bioma_predominante"]].assign(
        taxa_prevista_pct=prever(modelo, atual, variaveis, escolhida))
    risco["posicao"] = risco["taxa_prevista_pct"].rank(ascending=False, method="min").astype(int)
    risco = risco.sort_values("posicao")
    risco.to_csv(RESULTADOS / f"risco_previsto_{ultimo_ano + 1}.csv", index=False, float_format="%.4f")

    escrever_relatorio(metricas, resultados_validacao, escolhida, importancias, treino, teste,
                       variaveis, risco, ultimo_ano + 1)
    print(metricas.to_string(index=False))
    print(f"\nResultados em {RESULTADOS}")


def tabela_markdown(df):
    linhas = ["| " + " | ".join(df.columns) + " |", "|" + "---|" * len(df.columns)]
    for registro in df.itertuples(index=False):
        valores = [f"{v:.3f}" if isinstance(v, float) else str(v) for v in registro]
        linhas.append("| " + " | ".join(valores) + " |")
    return "\n".join(linhas)


def leitura_resultados(metricas, importancias):
    """Texto de interpretação derivado das métricas (continua correto se os dados mudarem)."""
    modelo = metricas.iloc[-1]
    referencias = metricas.iloc[:-1]
    colunas = {"erro_medio_absoluto_pp": "erro médio", "correlacao_ranking_spearman": "ranking",
               f"acerto_top_{int(PARCELA_MAIOR_RISCO * 100)}pct": f"acerto nos {int(PARCELA_MAIOR_RISCO * 100)}% de maior risco"}
    vence, perde = [], []
    for coluna, nome in colunas.items():
        melhor_referencia = referencias[coluna].min() if coluna.startswith("erro") else referencias[coluna].max()
        melhor = modelo[coluna] < melhor_referencia if coluna.startswith("erro") else modelo[coluna] > melhor_referencia
        (vence if melhor else perde).append(nome)

    historico = importancias[importancias["variavel"].str.startswith("pd_desmatamento") |
                             (importancias["variavel"] == "pd_taxa_desmatamento")]["importancia"].clip(lower=0).sum()
    total = importancias["importancia"].clip(lower=0).sum()
    frases = []
    if vence:
        frases.append(f"O modelo supera as regras simples em: {', '.join(vence)}.")
    if perde:
        frases.append(f"Não supera a melhor regra simples em: {', '.join(perde)}.")
    if total > 0:
        frases.append(
            f"As variáveis de histórico de desmatamento respondem por {100 * historico / total:.0f}% da importância "
            "total: o desmatamento futuro de um município é previsto sobretudo pelo seu próprio passado recente. "
            "Para ir além da persistência, a modelagem da dissertação precisa de fatores externos ao histórico "
            "(acesso por estradas, distância à borda do desmatamento, situação fundiária/CAR, embargos, preços de "
            "commodities, anomalias climáticas)."
        )
    return " ".join(frases)


def escrever_relatorio(metricas, validacao, escolhida, importancias, treino, teste, variaveis, risco, ano_previsto):
    texto = f"""# Modelo de referência: risco de desmatamento no ano seguinte

Gerado por `modelagem/modelo_base.py` a partir de `historico/painel_municipio_ano.csv`.

- **Alvo:** taxa de desmatamento PRODES no ano seguinte (% da vegetação nativa no início daquele ano).
- **Divisão temporal, sem embaralhar anos:** configuração escolhida treinando com {PRIMEIRO_ANO}–{ULTIMO_ANO_AJUSTE} e validando em {ULTIMO_ANO_AJUSTE + 1}–{ULTIMO_ANO_TREINO}; depois, treino com {int(treino['ano'].min())}–{int(treino['ano'].max())} ({len(treino)} linhas) e avaliação única no teste {int(teste['ano'].min())}–{int(teste['ano'].max())} ({len(teste)} linhas).
- **Modelo:** gradient boosting de histogramas (scikit-learn), {len(variaveis)} variáveis (áreas como fração da área do município), alvo em log(1 + taxa).
- **Regras de referência:** persistência (o ano seguinte repete o atual) e média dos últimos 3 anos.

## Escolha da configuração (validação {ULTIMO_ANO_AJUSTE + 1}–{ULTIMO_ANO_TREINO})

{tabela_markdown(validacao)}

Escolhida pela maior correlação de ranking: **{escolhida['nome']}**.

## Desempenho no teste

{tabela_markdown(metricas)}

- `erro_medio_absoluto_pp`: erro médio absoluto, em pontos percentuais de taxa (menor é melhor).
- `correlacao_ranking_spearman`: concordância entre a ordem prevista e a real dos municípios (maior é melhor).
- `acerto_top_{int(PARCELA_MAIOR_RISCO * 100)}pct`: entre os {int(PARCELA_MAIOR_RISCO * 100)}% de municípios com maior risco previsto em cada ano, fração que estava de fato entre os {int(PARCELA_MAIOR_RISCO * 100)}% com maior taxa real.

## Variáveis mais importantes

Queda na correlação de ranking (teste) quando a variável é embaralhada; média de 10 repetições.

{tabela_markdown(importancias.head(15))}

## Risco previsto para {ano_previsto}

Modelo treinado com todos os anos com alvo e aplicado ao último ano do painel. Arquivo completo:
`risco_previsto_{ano_previsto}.csv`. Os 15 municípios de maior risco:

{tabela_markdown(risco.head(15)[['posicao', 'nm_mun', 'sigla_uf', 'bioma_predominante', 'taxa_prevista_pct']])}

## Leitura dos resultados

{leitura_resultados(metricas, importancias)}

## Limitações

- Modelo de referência, com uma busca pequena de configurações; serve de linha de base para os modelos da dissertação.
- A taxa é relativa à vegetação nativa restante: municípios com pouca vegetação remanescente tendem a taxas altas mesmo com pouca área desmatada. Para priorização territorial, considere também a área prevista em hectares.
- Atributos de focos (FRP, risco de fogo, dias sem chuva) faltam em parte dos anos; o modelo trata ausências nativamente.
- As variáveis de vizinhança usam o mesmo ano das demais (não antecipam o alvo, que é do ano seguinte).
"""
    (RESULTADOS / "relatorio_modelo_base.md").write_text(texto, encoding="utf-8")


if __name__ == "__main__":
    main()
