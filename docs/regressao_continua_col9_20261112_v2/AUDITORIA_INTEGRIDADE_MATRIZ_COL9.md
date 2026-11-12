# Auditoria de integridade
Auditoria final: auditoria_v3/auditoria.json.

São 255 códigos iguais ao conjunto WKB canônico,38 intervalos por município,
9.690 chaves únicas/ordenadas em 1985–2022 e 255 linhas de 2023 com C/D/R
ausentes e ano de resposta observado nulo. Não houve retorno à base 268.
X contém 53 atributos e duas chaves, sem colunas proibidas ou janelas posteriores
at. C/D/R conferem com as métricas auditadas; 0≤C≤D,0≤R≤100 e R=100 C/D.
Os 255 estoques NPZ foram verificados por hash e pelo CSV aprovado:
erro máximo 5,06671 × 10⁻⁵ha, compatível com arredondamento, sem alterar fontes.

| variavel | n_ausentes | pct_ausentes | primeiro_ano_historico_suficiente |
|---|---|---|---|
| mb_vn_variacao_liquida_1ano_ha | 255 | 2.6316 | 1986 |
| mb_vn_variacao_liquida_1ano_pct | 255 | 2.6316 | 1986 |
| mb_conv_passada_ha | 255 | 2.6316 | 1986 |
| mb_taxa_passada_pct | 255 | 2.6316 | 1986 |
| mb_vn_t_ha_tendencia_3anos | 510 | 5.2632 | 1987 |
| mb_vn_t_pct_tendencia_3anos | 510 | 5.2632 | 1987 |
| mb_vn_pct_media_3anos | 510 | 5.2632 | 1987 |
| mb_conv_passada_ha_media_3anos | 765 | 7.8947 | 1988 |
| mb_taxa_passada_pct_media_3anos | 765 | 7.8947 | 1988 |
| mb_vn_t_ha_tendencia_5anos | 1020 | 10.5263 | 1989 |
| mb_vn_t_pct_tendencia_5anos | 1020 | 10.5263 | 1989 |
| mb_vn_pct_media_5anos | 1020 | 10.5263 | 1989 |
| mb_conv_passada_ha_media_5anos | 1275 | 13.1579 | 1990 |
| mb_taxa_passada_pct_media_5anos | 1275 | 13.1579 | 1990 |

As ausências estruturais não foram substituídas por zero. Frações de biomas
não estão em X; zeros de interseção bruta representam interseções vazias
na camada consultada, sem certificar compatibilidade dos suportes.

Foram verificados 2080 caminhos dos três checkpoints
anteriores, zero divergências; 255 NPZs e código legado preservados. Os 39 rasters
conferem em tamanho/mtime e hashes prévios; 159 GB não foram relidos integralmente.
Não houve migração, escrita no banco, Docker ou implantação. Isso descreve
operações, não comparação binária do volume PostgreSQL.

Passaram 125 testes distintos: 70 principais e 55 geoespaciais, incluindo 20 novos.
Os seis módulos geoespaciais ignorados pelo ambiente principal foram executados
no apropriado. O contrafactual altera dados posteriores e verifica invariância
de X anterior: testa a janela implementada, não o classificador externo.
