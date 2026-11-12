# Relatório de pendências e decisões — piloto e modelagem retrospectiva

## Decisões do pesquisador registradas neste encaminhamento

1. Entrega computacional aprovada provisoriamente; validação temática aberta.
2. Nenhum A/B/C homologado; prevalência não define relevância ambiental.
3. Experimento principal de **predição retrospectiva**, com avaliação temporal
   e espacial; sem alegação de disponibilidade operacional histórica comprovada.
4. Ano2024 reservado para utilização metodológica separada, ainda não definida.
5. Sem autorização para treinamento definitivo ou desfecho binário homologado.

As decisões também estão em `referencias/decisoes_pesquisador_col9_piloto_v1.json`.
Os relatórios e checkpoints anteriores foram preservados, sem reescrever seus
estados históricos de aprovação/pendência.

## Entrega executada

| Entregável | Resultado e arquivo |
|---|---|
| Protocolo operacional do piloto | [PROTOCOLO_PILOTO_TEMATICO_COL9.md](PROTOCOLO_PILOTO_TEMATICO_COL9.md): proposta de120 pontos,120 estratos, cegamento, esforço e ampliação |
| Instruções/fichas independentes | [INSTRUCOES_AVALIADORES_PILOTO_COL9.md](INSTRUCOES_AVALIADORES_PILOTO_COL9.md), dois ZIPs ativos em `pacotes_v2/` |
| Nota sobre relevância | [NOTA_CONVERSAO_RELEVANTE_COL9.md](NOTA_CONVERSAO_RELEVANTE_COL9.md): ocorrência/magnitude/contexto/persistência e efeitos temporais |
| Protocolo retrospectivo | [PROTOCOLO_MODELAGEM_RETROSPECTIVA_COL9.md](PROTOCOLO_MODELAGEM_RETROSPECTIVA_COL9.md), catálogo de17 grupos candidatos e índices sem rótulos |
| Rastreabilidade técnica | `gestao_restrita/` com vínculo, ranking para ampliação, protocolos/hashes e auditoria; não enviar aos avaliadores |

Checkpoint novo: `validacao_cientifica_col9/piloto_interpretacao_20261111_v1/`.
O identificador/seed acompanha o checkpoint original; datas reais de aquisição
estão em UTC nos metadados de cada caso.

Os120 casos são subconjunto dos3.744 pontos **probabilísticos** originais,
sem inclusão de inspeções dirigidas ou seleção por disponibilidade. Cada
estrato original tem um ponto. Os pesos/probabilidades da amostra-pai foram
mantidos na gestão; a subamostragem condicional não é usada para estimar acurácia.

Foram obtidos **320 recortes georreferenciados**, com ao menos um em cada ano
do par para **120/120 casos**. Isso mede disponibilidade na busca executada,
não capacidade de interpretar conclusivamente todos os casos. Consulta limitada,
resolução, nuvens/névoa, SLC-off, sazonalidade e manejo permanecem limitações.
Não houve substituição de ponto nem preenchimento de resposta. Não foi usado2024.

Auditoria offline dos320 recortes: todos os footprints estão contidos no
recorte e na geometria da cena; nenhum tem amostra RGB inteiramente zerada
dentro da célula. QA é triagem, não validação temática. Seis pranchas históricas
e recentes (P001,P002,P006,P065,P114,P117) foram inspecionadas para conferir
legibilidade, datas, contexto, zoom e footprint, sem preencher suas fichas.

Pacotes ativos: `pacotes_v2/piloto_col9_avaliador_A.zip` e
`piloto_col9_avaliador_B.zip`. Cada um tem os120 casos em ordem independente,
GeoTIFFs, GeoJSONs, pranchas, catálogos públicos, metadados, índice HTML,
instruções e ficha sem respostas. Os primeiros ZIPs foram mantidos;
v2 acrescenta os catálogos citados pelos metadados. Nenhum contém gestão,
classes MapBiomas, estratos, magnitudes, limiares ou respostas do outro avaliador.
Hashes/CRC e conteúdo foram verificados. Não houve envio a outras pessoas.

## Decisões ainda a aprovar

| Questão | Proposta preparada | Estado |
|---|---|---|
| Tamanho e organização do piloto |120 pontos, um/estrato original; mesmos casos para dois avaliadores | materializado como proposta, ainda sem aceite/respostas |
| Equipe, calibração e esforço | dois avaliadores independentes, exemplos externos, orçamento aproximado60–100 horas-pessoa totais | confirmar disponibilidade, calibração e cronograma |
| Categorias/mistura/georregistro | VN/UA/OUTROS/INCONCLUSIVO, descrições, confiança, mistura e evidência; sem corte automático de predominância | validar clareza das instruções antes da resposta definitiva |
| Gatilhos de revisão/ampliação | exemplos >20% de não resposta/divergência, revisão de custos e rodada2 por ranking fixo | parâmetros de planejamento propostos, não aprovados como normas científicas |
| Definição de relevância | relativa, absoluta, conjunção, contexto ou magnitude contínua; A/B/C permanecem hipóteses | decisão ambiental fundamentada, sem otimizar balanceamento/ML |
| Persistência | sensibilidade separada a t+2/t+3, com suporte e atraso explícitos | nenhuma rotina municipal de persistência calculada ou incorporada ao alvo |
| Denominador de persistência | suporte comum ampliado versus limites lógicos sobre denominador original | comparar proposta antes de calcular/homologar |
| Blocos explicativos |17 grupos, por disponibilidade/harmonização/fonte adicional | seleção não homologada; auditar dependência temporal do processamento retrospectivo |
| Coorte e partições |255×38, temporal e cinco LOSO mantidos como proposta | congelar antes de treinar, registrando exposição científica anterior |
|2024 | nenhum uso neste encaminhamento | decisão metodológica futura separada |

Não há acurácia representativa do piloto ou recomendação de um limiar vencedor.
Não foram produzidos rótulos temáticos por IA, Y municipal homologado ou modelos.
O pacote está pronto para revisão do protocolo e execução humana independente.

## Implementação, testes e preservação

Novos arquivos de código:

- `processamento/piloto_interpretacao_col9.py`: subamostra/aliases/fichas e ordem futura.
- `processamento/referencias_piloto_col9.py`: aquisição pública/GeoTIFFs, QA e pranchas cegas.
- `processamento/pacote_avaliadores_col9.py`: montagem/verificação dos ZIPs A/B.
- `processamento/auditar_piloto_col9.py`: auditoria offline do suporte e hashes.
- `modelagem/protocolo_retrospectivo_col9.py`: catálogo e índices/partições, sem X/Y.
- `processamento/fechar_piloto_col9.py`: fechamento do checkpoint da gestão.
- `testes/test_piloto_retrospectivo_col9.py` e `test_referencias_piloto_col9_geo.py`:
  doze testes novos, mantendo os anteriores.

Regressão: **70 testes principais** aprovados; quatro módulos ignorados nesse
ambiente foram executados no geoespacial, onde **19 testes** passaram.
Total: **89 testes distintos**. Testes cobrem subset/reordenação,120 estratos,
propriedades da amostra-pai, ranking para adição, cegamento, ano reservado,
distinção publicação/fenômeno/dependência futura, QA do footprint e leitura
fora da referência que não pode virar pixel Landsat “claro”.

O código exato usado na aquisição foi arquivado em
`gestao_restrita/codigo_aquisicao_executado.py`, com hash do protocolo. Um teste
adicionou defesa de máscara para leitura boundless de QA na versão de código
final; a auditoria demonstrou que todos os320 footprints deste lote estão
dentro das cenas, sem alteração de nenhum recorte. A assinatura mudou: nova
execução dessa versão exige novo lote, não retoma/reescreve silenciosamente
o lote executado. Catálogos, metadados e código executado permitem auditar a versão.

Logs novos: `docs/evidencias/piloto_*_20261111_v1.txt`.
Não foram editados rasters, matrizes, CSVs, referências ou ZIPs dos checkpoints
anteriores, nem o código do app/ETL legado. Nenhuma migração, carga, refresh,
operação Docker, implantação ou escrita no banco foi executada neste incremento;
os testes existentes usaram consultas de leitura. As verificações finais de
hashes/metadados e o manifesto do novo checkpoint documentam a preservação.
