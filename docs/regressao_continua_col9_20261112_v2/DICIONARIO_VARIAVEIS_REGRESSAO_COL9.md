# Dicionário dos 53 atributos candidatos
Chaves: CD_MUN, string de 7 dígitos, e ano_t. Não são preditores numéricos automáticos.
UF/nome ficam no índice/partições, fora de X. Nenhum atributo foi selecionado.

Composição percentual: 100 ×área do grupo(t)/toda área classificada(t), incluindo
25/33 e excluindo 0/27/NoData. Agricultura exclui pastagem/silvicultura/mosaico.
Formações florestais aqui=[3,5,6,49], savânica=4, campestre=12; não são partição
completa de VN nem substituem a hierarquia oficial.

| variavel | bloco | unidade | formula | primeiro_ano_historico_suficiente | inicio_fenomeno_offset | fim_fenomeno_offset | status_temporal |
|---|---|---|---|---|---|---|---|
| mb_vn_t_ha | historico_cobertura | ha | Soma de áreas das classes[3, 4, 5, 6, 49, 11, 12, 50] somente em t | 1985 | 0 | 0 | sujeito_a_analise |
| mb_vn_t_pct | historico_cobertura | % | 100 × áreavn(t)/área classificada(t); inclui25/33 no denominador, exclui0/27/NoData | 1985 | 0 | 0 | sujeito_a_analise |
| mb_ua_t_ha | historico_cobertura | ha | Soma de áreas das classes[9, 15, 20, 21, 24, 30, 31, 35, 39, 40, 41, 46, 47, 48, 62] somente em t | 1985 | 0 | 0 | sujeito_a_analise |
| mb_ua_t_pct | historico_cobertura | % | 100 × áreaua(t)/área classificada(t); inclui25/33 no denominador, exclui0/27/NoData | 1985 | 0 | 0 | sujeito_a_analise |
| mb_pastagem_t_ha | historico_cobertura | ha | Soma de áreas das classes[15] somente em t | 1985 | 0 | 0 | sujeito_a_analise |
| mb_pastagem_t_pct | historico_cobertura | % | 100 × áreapastagem(t)/área classificada(t); inclui25/33 no denominador, exclui0/27/NoData | 1985 | 0 | 0 | sujeito_a_analise |
| mb_agricultura_t_ha | historico_cobertura | ha | Soma de áreas das classes[20, 35, 39, 40, 41, 46, 47, 48, 62] somente em t | 1985 | 0 | 0 | sujeito_a_analise |
| mb_agricultura_t_pct | historico_cobertura | % | 100 × áreaagricultura(t)/área classificada(t); inclui25/33 no denominador, exclui0/27/NoData | 1985 | 0 | 0 | sujeito_a_analise |
| mb_formacoes_florestais_t_ha | historico_cobertura | ha | Soma de áreas das classes[3, 5, 6, 49] somente em t | 1985 | 0 | 0 | sujeito_a_analise |
| mb_formacoes_florestais_t_pct | historico_cobertura | % | 100 × áreaformacoes_florestais(t)/área classificada(t); inclui25/33 no denominador, exclui0/27/NoData | 1985 | 0 | 0 | sujeito_a_analise |
| mb_savanica_t_ha | historico_cobertura | ha | Soma de áreas das classes[4] somente em t | 1985 | 0 | 0 | sujeito_a_analise |
| mb_savanica_t_pct | historico_cobertura | % | 100 × áreasavanica(t)/área classificada(t); inclui25/33 no denominador, exclui0/27/NoData | 1985 | 0 | 0 | sujeito_a_analise |
| mb_campestre_t_ha | historico_cobertura | ha | Soma de áreas das classes[12] somente em t | 1985 | 0 | 0 | sujeito_a_analise |
| mb_campestre_t_pct | historico_cobertura | % | 100 × áreacampestre(t)/área classificada(t); inclui25/33 no denominador, exclui0/27/NoData | 1985 | 0 | 0 | sujeito_a_analise |
| mb_mosaico_t_ha | historico_cobertura | ha | Soma de áreas das classes[21] somente em t | 1985 | 0 | 0 | sujeito_a_analise |
| mb_mosaico_t_pct | historico_cobertura | % | 100 × áreamosaico(t)/área classificada(t); inclui25/33 no denominador, exclui0/27/NoData | 1985 | 0 | 0 | sujeito_a_analise |
| mb_classe25_t_ha | historico_cobertura | ha | Soma de áreas das classes[25] somente em t | 1985 | 0 | 0 | sujeito_a_analise |
| mb_classe25_t_pct | historico_cobertura | % | 100 × áreaclasse25(t)/área classificada(t); inclui25/33 no denominador, exclui0/27/NoData | 1985 | 0 | 0 | sujeito_a_analise |
| mb_classe29_t_ha | historico_cobertura | ha | Soma de áreas das classes[29] somente em t | 1985 | 0 | 0 | sujeito_a_analise |
| mb_classe29_t_pct | historico_cobertura | % | 100 × áreaclasse29(t)/área classificada(t); inclui25/33 no denominador, exclui0/27/NoData | 1985 | 0 | 0 | sujeito_a_analise |
| mb_classe32_t_ha | historico_cobertura | ha | Soma de áreas das classes[32] somente em t | 1985 | 0 | 0 | sujeito_a_analise |
| mb_classe32_t_pct | historico_cobertura | % | 100 × áreaclasse32(t)/área classificada(t); inclui25/33 no denominador, exclui0/27/NoData | 1985 | 0 | 0 | sujeito_a_analise |
| mb_classe33_t_ha | historico_cobertura | ha | Soma de áreas das classes[33] somente em t | 1985 | 0 | 0 | sujeito_a_analise |
| mb_classe33_t_pct | historico_cobertura | % | 100 × áreaclasse33(t)/área classificada(t); inclui25/33 no denominador, exclui0/27/NoData | 1985 | 0 | 0 | sujeito_a_analise |
| mb_area_classificada_t_ha | historico_cobertura | ha | Soma de classes válidas somente em t | 1985 | 0 | 0 | sujeito_a_analise |
| mb_pixels_validos_t | historico_cobertura | pixels | Soma de pixels de classes válidas do mapa t | 1985 | 0 | 0 | sujeito_a_analise |
| mb_pixels_sem_classe_valida_t | historico_cobertura | pixels | Pixels da grade canônica menos válidos somente em t; não atribui causa automaticamente a NoData | 1985 | 0 | 0 | sujeito_a_analise |
| mb_cobertura_grade_t_pct | historico_cobertura | % | 100 × pixels válidos(t)/pixels da grade fixa; sem máscara comum futura | 1985 | 0 | 0 | sujeito_a_analise |
| mb_razao_classificada_territorial_t_pct | historico_cobertura | % | 100 × área classificada(t)/área geodésica fixa; pode exceder100 por suporte; sem truncamento | 1985 | 0 | 0 | sujeito_a_analise |
| mb_diferenca_classificada_territorial_t_ha | historico_cobertura | ha | Área classificada(t) menos área geodésica fixa; não é desmatamento/NoData | 1985 | 0 | 0 | sujeito_a_analise |
| mb_vn_variacao_liquida_1ano_ha | historico_cobertura | ha/ano | mb_vn_t_ha(t)−mb_vn_t_ha(t−1); variação líquida, não transição | 1986 | -1 | 0 | sujeito_a_analise |
| mb_vn_variacao_liquida_1ano_pct | historico_cobertura | pontos_percentuais/ano | mb_vn_t_pct(t)−mb_vn_t_pct(t−1); variação líquida, não transição | 1986 | -1 | 0 | sujeito_a_analise |
| lacuna_variacao_liquida_1ano | historico_cobertura | booleano | Histórico t−1 inexistente na série | 1985 | 0 | 0 | sujeito_a_analise |
| mb_conv_passada_ha | historico_cobertura | ha | Conversão histórica t−1→t, encerrada até t; não é o desfecho corrente | 1986 | -1 | 0 | sujeito_a_analise |
| mb_taxa_passada_pct | historico_cobertura | % | Conversão histórica t−1→t, encerrada até t; não é o desfecho corrente | 1986 | -1 | 0 | sujeito_a_analise |
| lacuna_conversao_passada | historico_cobertura | booleano | Sem intervalo anterior disponível | 1985 | 0 | 0 | sujeito_a_analise |
| mb_vn_t_ha_tendencia_3anos | historico_cobertura | ha/ano | Inclinação descritiva por pesos fixos em t−2…t; janela completa, sem filtro centrado | 1987 | -2 | 0 | sujeito_a_analise |
| mb_vn_t_pct_tendencia_3anos | historico_cobertura | pontos_percentuais/ano | Inclinação descritiva por pesos fixos em t−2…t; janela completa, sem filtro centrado | 1987 | -2 | 0 | sujeito_a_analise |
| mb_vn_pct_media_3anos | historico_cobertura | % | Média municipal dos3 estoques anuais encerrados em t | 1987 | -2 | 0 | sujeito_a_analise |
| mb_conv_passada_ha_media_3anos | historico_cobertura | ha | Média de3 conversões passadas com fim entre t−2 e t | 1988 | -3 | 0 | sujeito_a_analise |
| mb_taxa_passada_pct_media_3anos | historico_cobertura | % | Média de3 conversões passadas com fim entre t−2 e t | 1988 | -3 | 0 | sujeito_a_analise |
| lacuna_janela_estoque_3anos | historico_cobertura | booleano | Janela completa de estoque não disponível; valores não imputados | 1985 | 0 | 0 | sujeito_a_analise |
| lacuna_janela_conversao_3anos | historico_cobertura | booleano | Janela completa de conversões encerradas não disponível | 1985 | 0 | 0 | sujeito_a_analise |
| mb_vn_t_ha_tendencia_5anos | historico_cobertura | ha/ano | Inclinação descritiva por pesos fixos em t−4…t; janela completa, sem filtro centrado | 1989 | -4 | 0 | sujeito_a_analise |
| mb_vn_t_pct_tendencia_5anos | historico_cobertura | pontos_percentuais/ano | Inclinação descritiva por pesos fixos em t−4…t; janela completa, sem filtro centrado | 1989 | -4 | 0 | sujeito_a_analise |
| mb_vn_pct_media_5anos | historico_cobertura | % | Média municipal dos5 estoques anuais encerrados em t | 1989 | -4 | 0 | sujeito_a_analise |
| mb_conv_passada_ha_media_5anos | historico_cobertura | ha | Média de5 conversões passadas com fim entre t−4 e t | 1990 | -5 | 0 | sujeito_a_analise |
| mb_taxa_passada_pct_media_5anos | historico_cobertura | % | Média de5 conversões passadas com fim entre t−4 e t | 1990 | -5 | 0 | sujeito_a_analise |
| lacuna_janela_estoque_5anos | historico_cobertura | booleano | Janela completa de estoque não disponível; valores não imputados | 1985 | 0 | 0 | sujeito_a_analise |
| lacuna_janela_conversao_5anos | historico_cobertura | booleano | Janela completa de conversões encerradas não disponível | 1985 | 0 | 0 | sujeito_a_analise |
| territorio_area_geodesica_ha | territorio | ha | Área geodésica; ponto interior representativo; fração por interseção IBGE2019, conforme proveniência | 1985 | 0 | 0 | permitido_em_principio |
| territorio_lon_referencia | territorio | graus | Área geodésica; ponto interior representativo; fração por interseção IBGE2019, conforme proveniência | 1985 | 0 | 0 | permitido_em_principio |
| territorio_lat_referencia | territorio | graus | Área geodésica; ponto interior representativo; fração por interseção IBGE2019, conforme proveniência | 1985 | 0 | 0 | permitido_em_principio |

Tendências usam inclinação descritiva por pesos temporais fixos em janelas
completas, sem modelo preditivo. Estoque 3/5 anos disponível desde 1987/1989;
conversão histórica 3/5 desde 1988/1990. Em 1985 não há conversão anterior.
Flags de lacuna não imputam valores.

As três variáveis territoriais derivam apenas dos polígonos canônicos 2025:
área Geod WGS84, latitude/longitude de ponto interior representative_point
calculado emEPSG 5880 e convertido para 4326. Não é centróide/população.
O catálogo resume o pacote territorial 2019/2025, mas frações de biomas 2019
ficam separadas e não fornecem valores às três variáveis de X.

CATALOGO_ATRIBUTOS_COL9.csv/json registra fonte, versão, unidade, fórmula,
referência temporal, publicação/revisão conhecida ou desconhecida, risco e
seleção=false. DISPONIBILIDADE_ATRIBUTOS_COL9.parquet contém 527.085 combinações
dos 9.945 município–anos com 53 atributos: presença, motivo de ausência,
limites do fenômeno e dependência algorítmica. Datas exatas não comprovadas
permanecem nulas; lançamento tardio não prova disponibilidade histórica.

Arquivos independentes: índice, X, C/D/R, qualidade/eligibilidade, metadados
e partições. D e Q correntes nunca entram em X; VN somente emt não éD.
