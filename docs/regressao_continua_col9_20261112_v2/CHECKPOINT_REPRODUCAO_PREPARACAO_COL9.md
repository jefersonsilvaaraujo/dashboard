# Checkpoint e reprodução
Ativo: validacao_cientifica_col9/preparacao_regressao_20261112_v2. Tentativas anteriores preservadas.
Artefatos candidatos, sem autorização de treino.

1. [Desfecho](PROTOCOLO_DESFECHO_CONTINUO_COL9.md)
2. [Dicionário](DICIONARIO_VARIAVEIS_REGRESSAO_COL9.md)
3. [Integridade](AUDITORIA_INTEGRIDADE_MATRIZ_COL9.md)
4. [Vazamento](AUDITORIA_VAZAMENTO_TEMPORAL_COL9.md)
5. [Inventário](INVENTARIO_VARIAVEIS_PENDENTES_COL9.md)
6. [Regressão](PROTOCOLO_REGRESSAO_RETROSPECTIVA_COL9.md)
7. [Nota ao orientador](NOTA_DECISAO_CIENTIFICA_ORIENTADOR_COL9.md)
8. [Conclusão](RELATORIO_EXECUTIVO_PREPARACAO_COL9.md)

matriz/: índices, X principal/X 2023, C/D/R e 2023 ausentes, qualidade,
território e partições. metadados/: catálogo, disponibilidade, fontes e código
executado. diagnosticos/: distribuições/extremos/estoques/máscara.
complementares/: focos separados e inventários. auditoria_v3/: auditoria final.
fontes/: documentação consultada com URL/data/hash.

Entradas grandes não são duplicadas: rasters, NPZs, GeoPackage, CSV aprovado,
biomas e ZIPs de focos continuam nos caminhos dos manifestos. O pacote inclui
Parquets, tabelas, scripts, testes, relatórios, fontes documentais e logs.
Nenhuma senha, modelo ajustado ou previsão do teste integra a entrega.

Ambiente: Python 3.14.6,numpy 2.5.4,pandas 2.3.3,pyarrow 26.0.1,
geopandas 1.2.0,shapely 2.2.0,pyproj 3.8.0. Parquet está em dependência
temporária isolada. Scripts recusam sobrescrever: usar destino novo.

```powershell
$env:PYTHONUTF8 = '1'
$env:PYTHONPATH = "$env:TEMP/defesa_regressao_col9_deps_20261112;$env:TEMP/defesa_mestrado_geo_testdeps_20261111"
$geoPython = 'D:/mestrado/.venv_territorial/Scripts/python.exe'
$novaExecucao = 'validacao_cientifica_col9/preparacao_regressao_reproducao_001'
$matrizesOriginais = 'resultados_transicoes_col9/integral_255_1985_2023_20261111'
& $geoPython modelagem/preparar_regressao_continua_col9.py --matrizes $matrizesOriginais --saida $novaExecucao
& $geoPython modelagem/diagnosticar_resposta_continua_col9.py --checkpoint $novaExecucao --saida "$novaExecucao/diagnosticos"
& $geoPython modelagem/blocos_complementares_regressao_col9.py --checkpoint $novaExecucao --saida "$novaExecucao/complementares"
& $geoPython modelagem/auditar_preparacao_regressao_col9.py --checkpoint $novaExecucao --saida "$novaExecucao/auditoria_v3"
& $geoPython modelagem/relatorios_preparacao_regressao_col9.py --checkpoint $novaExecucao --docs "$novaExecucao/relatorios"
```

O fechamento dos biomas é auditado sem bloquear X. A emissão do manifesto
complementar foi corrigida no código atual; o código/manifesto executados
anteriores permanecem preservados em cadeia aditiva de integridade.
Testes sintéticos independem do acervo; para integração em outro destino,
ajustar o fixture ou reproduzir a estrutura de pastas.

manifesto_final_preparacao.json guarda hashes, versões, fontes e resultados;
o recibo final guarda SHA256 do ZIP e conferência de CRC/hashes internos.
2024 não foi utilizado; nenhuma alteração científica foi homologada.
