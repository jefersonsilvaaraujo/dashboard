# Entrega da avaliação oficial e auditoria automatizada da Coleção 9

Data: 12/11/2026. A comparação computacional foi executada; a validação temática
representativa permanece não estabelecida. Nenhum limiar ou desfecho foi homologado.

Os principais resultados são 8.586 pontos oficiais dentro do território canônico,
dos quais 1.305 marcados como treinamento; cobertura em 253 dos 255 municípios;
e somente um ponto com classe de referência em 2023. Na coorte sem marcação de
treinamento, a coincidência da conversão no ano exato tem precisão descritiva
26,81% e sensibilidade 35,12%. Para 2022, são 7 coincidências em 80 conversões
mapeadas comparáveis. Esses números não estimam acurácia populacional ou erro em hectares.

## Relatórios para validação científica

1. [Pontos oficiais: fontes, cobertura, classes e comparações](RELATORIO_PONTOS_OFICIAIS_COL9.md).
2. [Consistência temporal, Buriticupu e referências externas](RELATORIO_CONSISTENCIA_REFERENCIAS_COL9.md).
3. [Suporte inferencial, pesos e limitações](AVALIACAO_INFERENCIA_PONTOS_COL9.md).
4. [Recomendação sobre o desfecho e cenários A/B/C](RECOMENDACAO_DESFECHO_CENARIOS_COL9.md).
5. [Texto acadêmico para metodologia e limitações](TEXTO_METODOLOGIA_LIMITACOES_COL9.md).

Recomendação atual: manter A/B/C em aberto. A magnitude contínua da conversão
**mapeada** é uma alternativa complementar viável a discutir, sem eliminar o erro
de medição. Os dados atuais não autorizam tratar as conversões como ocorrência
verdadeira validada, ajustar hectares pela precisão pontual ou iniciar treinamento definitivo.

## Arquivos implementados

Foram criados nove scripts, um arquivo de testes, cinco relatórios científicos,
este índice e um registro do encaminhamento. Não se modificaram módulos da
aplicação ou scripts anteriores. O novo diretório de resultados é
`validacao_cientifica_col9/oficial_col9_20261112_v1/`.

| Arquivo | Função |
|---|---|
| `processamento/fontes_oficiais_col9.py` | Download oficial, ZIP seguro, URL/data/licença/hash |
| `processamento/avaliar_pontos_oficiais_col9.py` | Seleção espacial canônica, extração dos39 rasters e comparação das referências |
| `processamento/diagnosticos_pontos_oficiais_col9.py` | Classes25/29/32, datação, vizinhança, suporte inferencial e repetição temporal |
| `processamento/auditoria_complementar_oficial_col9.py` | Matrizes completas, PRODES2023, Buriticupu e inventário do acervo de imagens |
| `processamento/auditoria_espectral_col9.py` | DN RED/NIR/QA, suporte geográfico e proxies espectrais dirigidos |
| `processamento/sensibilidade_radiometrica_col9.py` | Hipóteses de offset Sentinel conflitantes, sem escolha por concordância |
| `processamento/cenarios_evidencias_oficiais_col9.py` | Cenários candidatos cruzados com cobertura de referência municipal/anual |
| `processamento/relatorios_oficiais_col9.py` | Geração dos cinco relatórios a partir das tabelas |
| `processamento/fechar_avaliacao_oficial_col9.py` | Verificação de integridade, manifesto e pacote reproduzível |
| `testes/test_pontos_oficiais_col9_geo.py` |16 novos testes, incluindo contratos científicos e execução integral |
| `referencias/encaminhamento_avaliacao_oficial_col9_v1.json` | Restrições e decisões vigentes do pesquisador |

Os resultados incluem 652.536 comparações ponto–par–versão de referência,
326.268 trajetórias ponto–par, auditoria das 9.690 matrizes e 87.210 combinações
município–par–cenário–elegibilidade. Esses totais não são tamanhos amostrais independentes.
O vetor auxiliar não preenche a referência 2023 do CSV.

O pacote contém os pontos oficiais baixados e documentos metodológicos arquivados,
tabelas, extrações compactas, DN espectrais, metadados, scripts, testes e relatórios.
Os rasters completos, GeoPackage canônico, matrizes anteriores e banco permanecem
no acervo original, referenciados por caminhos e manifestos/hashes. Não são duplicados
no ZIP. As dependências locais de código necessárias à reprodução acompanham o pacote.

## Testes e preservação

Foram aprovados **105 testes distintos**: 70 na suíte principal e 35 na suíte
geoespacial. A primeira registra cinco módulos geoespaciais ignorados por ausência
dessas dependências naquele ambiente; os testes correspondentes foram executados
no ambiente geoespacial. Nenhuma falha permaneceu.

Os 16 testes novos cobrem classes agregadas/ambíguas, ausência diferente de negativo,
pesos e denominadores, leitura sem deslocamento, limites da grade, censura de t+2,
PRODES não equivalente, janelas temporais, deduplicação de cenas, calibração e seus
conflitos, integridade dos cenários e igualdade de C/D sob a máscara tripla de Buriticupu.
Logs: `docs/evidencias/oficial_col9_regressao_20261112.txt` e
`docs/evidencias/oficial_col9_testes_geo_finais_20261112.txt`.

Foram verificados os hashes dos 634 arquivos do checkpoint científico anterior
e dos 1.175 arquivos do checkpoint do piloto: **1.805 caminhos distintos, zero divergências**.
`app.py` e `dados.py` conferem com os hashes anteriores; os 39 rasters conferem
em tamanho/mtime com o manifesto íntegro. O GeoPackage e as geometrias WKB
canônicas foram verificados; as matrizes conferem com seus manifestos.
Não foram recalculados todos os hashes dos 159 GB de rasters nesta etapa.

Não houve operação de migração, atualização de tabela/view, exclusão, Docker,
implantação ou troca do processo do dashboard. O banco não foi alterado; isso
descreve as operações executadas e não uma comparação binária de todo o volume
PostgreSQL. Os testes existentes que consultam dados mantêm sua natureza de leitura.

## Ambiente e reprodução

Ambiente científico utilizado: Python 3.14.6, numpy 2.5.4, pandas 2.3.3,
rasterio 1.5.2, geopandas 1.2.0, shapely 2.2.0 e pyproj 3.8.0.
O manifesto final registra também as versões dos demais componentes utilizados.
Não houve instalação de dependências nesta etapa. A suíte principal usa o
ambiente já existente do dashboard, com pandas 3.1.0.

Os scripts recusam substituir saídas existentes. Para reproduzir, mantenha os
acervos apontados nos manifestos e use um novo diretório de destino. Exemplo
PowerShell, a partir da raiz do projeto:
```powershell
$geoPython = 'D:/mestrado/.venv_territorial/Scripts/python.exe'
$novaExecucao = 'validacao_cientifica_col9/reproducao_oficial_col9_001'
$fontesPreservadas = 'validacao_cientifica_col9/oficial_col9_20261112_v1/fontes'
$matrizesPreservadas = 'resultados_transicoes_col9/integral_255_1985_2023_20261111'
& $geoPython processamento/avaliar_pontos_oficiais_col9.py --fontes $fontesPreservadas --saida "$novaExecucao/avaliacao"
& $geoPython processamento/diagnosticos_pontos_oficiais_col9.py --fontes $fontesPreservadas --avaliacao "$novaExecucao/avaliacao" --saida "$novaExecucao/diagnosticos"
& $geoPython processamento/auditoria_complementar_oficial_col9.py --avaliacao "$novaExecucao/avaliacao" --matrizes $matrizesPreservadas --saida "$novaExecucao/complementar"
& $geoPython processamento/auditoria_espectral_col9.py --checkpoint validacao_cientifica_col9/checkpoint_20261111 --saida "$novaExecucao/espectral_v2"
& $geoPython processamento/sensibilidade_radiometrica_col9.py --origem "$novaExecucao/espectral_v2" --saida "$novaExecucao/radiometria"
& $geoPython processamento/cenarios_evidencias_oficiais_col9.py --avaliacao "$novaExecucao/avaliacao" --matrizes $matrizesPreservadas --saida "$novaExecucao/cenarios_evidencias"
& $geoPython processamento/relatorios_oficiais_col9.py --checkpoint $novaExecucao --saida-docs "$novaExecucao/relatorios"
```

Para outra aquisição oficial, use `fontes_oficiais_col9.py --saida NOVA_PASTA`:
uma URL mutável pode retornar conteúdo diferente; compare hashes antes de afirmar
reprodução do mesmo conjunto. A reprodução numérica da avaliação dos pontos e
da radiometria pode usar as fontes/DN preservados, sem nova consulta à internet.
Reobter os DN das cenas exige acesso público aos COGs e assinatura pública
temporária de leitura Landsat; tokens não são gravados no pacote.

O checkpoint registra a extração por célula, incluindo os nove vizinhos,
permitindo reexaminar as comparações sem ler os 39 rasters novamente. As cenas
auxiliares não substituem os rasters Col 9. Na radiometria,38 cenas têm metadados
de offset conflitantes; as duas hipóteses são preservadas e a situação continua
inconclusiva. Uma primeira tentativa espectral, com cenas duplicadas em dois
catálogos, foi preservada em `espectral/` e **não integra os resultados ativos**.
O pacote final usa `espectral_v2/` e `radiometria/`; os logs de diagnóstico da
tentativa permanecem como trilha de auditoria. Avisos de tipos/depreciação das
tentativas foram tratados sem modificar fontes; a execução final e os testes passaram.

## Limitações e próximas decisões

Faltam referências adequadas para 2023, documentação de inclusão após retirada
para treino, tratamento justificável dos estratos isolados e confirmação da
calibração Sentinel. Não existe referência de área queimada harmonizada no
acervo; focos não foram utilizados como substitutos. Não se reivindicou acurácia
representativa ou independência comprovada. A ausência de interpretação humana
adicional foi respeitada.

As próximas decisões são científicas: significado ambiental de relevância,
eventual papel da magnitude contínua e da persistência, e tratamento dos anos
sem referência. Mantêm-se o experimento retrospectivo, a avaliação temporal e
leave-one-state-out e o registro de que extremos/anos finais já foram explorados.
Não foi utilizado 2024, criado Y homologado ou iniciado treinamento definitivo.

O fechamento produz `manifesto_final.json`, `recibo_pacote.json` e o arquivo
`entregas_transicoes_col9/checkpoint_avaliacao_oficial_col9_20261112_v2.zip`, com
SHA256 e conferência de CRC e hashes internos. O recibo é o registro final de
integridade e permite localizar cada arquivo do pacote.

Revis?o documental 1: este ?ndice corrige a formata??o do bloco de comandos.
O pacote v2 acrescenta este guia e um manifesto complementar ao conte?do integral
do pacote v1, preservado sem altera??es. Os dados, scripts, testes e cinco
relat?rios cient?ficos s?o id?nticos; o manifesto cient?fico original continua v?lido.
