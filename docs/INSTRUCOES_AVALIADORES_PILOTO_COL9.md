# Instruções de interpretação independente — piloto

Este pacote contém 120 casos para testar o protocolo de interpretação. Não é
uma estimativa de acurácia, nem uma avaliação do seu desempenho individual.
Os pontos não devem ser deslocados, retirados ou substituídos por locais mais fáceis.

## Preparação

1. Extraia seu ZIP em uma pasta nova. Abra `indice.html` e sua
   `ficha_independente.csv` (UTF-8, separador ponto e vírgula).
2. Trabalhe somente na sua ficha, guardando a versão original e cópias datadas.
   Mantenha os aliases P001…P120 e todos os casos/colunas.
3. Não consulte a classificação MapBiomas, relatórios de extremos, os estratos,
   cenários de limiar, a pasta de gestão ou as respostas do outro avaliador.
4. Antes de iniciar, registre seu identificador e a versão do protocolo. Uma
   sessão de calibração deve usar exemplos externos a estes 120 casos e não
   revelar rótulos MapBiomas. Dúvidas de definição devem ser resolvidas por
   instrução comum, preservando respostas anteriores quando houver revisão.

O índice mostra os casos na mesma ordem da sua ficha; a ordem do outro
avaliador é diferente. Você não precisa fornecer dados pessoais além do
identificador acordado com o pesquisador. Nenhuma resposta é enviada automaticamente.

## Unidade e evidências

A unidade é o **pixel inteiro delimitado em amarelo**, observado em dois anos,
não apenas o ponto central. Há imagem de contexto e zoom. A ampliação por
vizinho mais próximo não acrescenta resolução real. GeoTIFFs conservam o CRS
e a transformada da cena; `pixel.geojson` contém o footprint WGS84 da célula.
Podem ser abertos em QGIS. Não confundir o grid Sentinel/Landsat com a célula
avaliada e não mover o pixel para coincidir com uma feição próxima.

As datas reais de aquisição aparecem nas pranchas e em `metadados.json`.
Uma imagem de junho não representa necessariamente dezembro. Compare, quando
houver, a imagem principal e a de novembro/dezembro. A aprovação automática
de QA **não garante** ausência de névoa, sombras, erro de registro ou mistura.
Se a data/qualidade/resolução não sustentar a interpretação, registre inconclusivo.
Um caso sem recorte continua no pacote com uma prancha de indisponibilidade.

Landsat utiliza composição RGB de reflectância com transformação documentada;
Sentinel utiliza TCI. As cores e o contraste podem variar entre datas/sensores.
Variação de cor isolada não comprova conversão ou manejo. Lacunas SLC-off,
nuvens e bordas sem dados não são solo exposto. Imagens Landsat compartilham
tipo de sensor com o produto avaliado; a interpretação deve ser independente,
mas não constitui verdade de campo ou independência absoluta dos erros.

## Sequência por caso

1. Registre início e tempo ativo. Verifique alias, anos, datas e o suporte
   completo do pixel. Avalie georreferenciamento sem fazer deslocamento manual.
2. Interprete **cada ano separadamente**, anotando cobertura observada, mistura,
   confiança, cenas usadas e limitações. Só depois examine a diferença entre anos.
3. Preencha a interpretação da conversão e sua justificativa. Não aplique
   limiares municipais de hectares/percentuais e não suponha que houve mudança
   porque o caso foi selecionado. Existem controles e outras origens/destinos.
4. Registre fim/tempo ativo, fontes adicionais e necessidade de complemento.
   Pode interromper e retornar ao mesmo caso; some apenas tempo ativo.

## Dicionário das respostas

| Campo | Valores/regras |
|---|---|
| `estado_t`, `estado_t1` | `VN`, `UA`, `OUTROS`, `INCONCLUSIVO` |
| `classe_ou_descricao_t`, `classe_ou_descricao_t1` | descrição livre da cobertura/uso observado; não fornecer códigos MapBiomas |
| `confianca_t`, `confianca_t1`, `confianca_conversao` | `ALTA`, `MEDIA`, `BAIXA`, com justificativa quando houver dúvida |
| `fracao_mista_t_pct`, `fracao_mista_t1_pct` | estimativa da parte ambígua/mista do pixel, 0–100, ou vazio se não estimável; não há corte automático de predominância homologado |
| `georregistro_adequado` | `SIM`, `NAO`, `INCERTO`; justificar problema e não corrigir deslocando o ponto |
| `cena_ids_t`, `cena_ids_t1` | identificadores das cenas efetivamente interpretadas |
| `evidencias_t`, `evidencias_t1` | nomes dos arquivos do pacote e, se necessário, referência adicional verificável |
| `limite_temporal_inferior`, `limite_temporal_superior` | datas que delimitam mudança observável; vazios se não inferíveis. Não inventar 31/dez |
| `conversao_interpretada` | `SIM` somente se VN em t e UA em t+1 sustentadas; `NAO` se a condição não ocorre com evidência suficiente; `INCONCLUSIVO` quando não resolvida |
| `situacao` | `nao_iniciado`, `em_analise`, `concluido`, `inconclusivo` |
| `motivo_inconclusivo` | `nuvem_sombra`, `lacuna_sensor`, `resolucao_mistura`, `registro_espacial`, `intervalo_temporal`, `uso_indeterminado`, `sem_imagem`, `outro`; detalhar |
| `justificativa`, `observacoes` | fundamento da interpretação e limitações; não copiar respostas de outro avaliador |
| `solicita_complemento` | `SIM`/`NAO` e complemento desejado nas observações |
| `inicio_utc`, `fim_utc`, `minutos_ativos` | datas ISO com fuso e tempo ativo numérico; usados para estimar esforço, não para imputar respostas |

**VN:** vegetação nativa arbórea, savânica, campestre, alagável/pantanosa,
manguezal ou restinga vegetada, inclusive regeneração nativa reconhecível.
**UA:** uso antrópico com evidência suficiente de manejo/ocupação, por exemplo
pastagem plantada/manejada, agricultura, silvicultura, urbanização, mineração
ou aquicultura. Cobertura verde não é automaticamente nativa; árvore não é
automaticamente floresta nativa. Campo natural e pastagem podem ser inseparáveis
em uma única imagem: registre a incerteza e procure série/contexto de manejo.
**OUTROS:** água ou cobertura natural não vegetada identificável, por exemplo
afloramento rochoso e praia/duna sem vegetação. Solo exposto isolado sem
evidência de origem/uso não deve virar UA por suposição: use INCONCLUSIVO quando
necessário. Descreva misturas e transições entre essas situações.

## Inconclusivos e fontes adicionais

Não use ausência de imagem como `NAO`. A busca pode ser complementada no
**mesmo** footprint e período, com registro de sensor, data, origem/licença,
CRS/registro, arquivo preservado e justificativa. Não usar 2024 neste piloto,
nem completar interpretação com o mapa que está sendo avaliado. Não trocar
imagem de outro ano sem informar a data; se não resolver o estado anual,
manter inconclusivo. Imagem adicional de outro ano pode ser proposta ao gestor,
mas não resolve automaticamente o par.

Como orçamento de busca, proponha sinalizar ao gestor ao atingir 20 minutos
por caso recente ou 30 minutos por caso histórico. Esses tempos são limites
de esforço para discutir, não motivos para impor uma resposta. Casos podem
receber mais esforço documentado ou continuar inconclusivos.

## Entrega e adjudicação

Entregue sua ficha e evidências novas ao pesquisador pelo meio por ele indicado.
Não troque a ficha com o outro avaliador. Respostas independentes serão preservadas;
divergências e inconclusivos serão discutidos em uma etapa separada. O resultado
adjudicado terá versão e justificativa próprias. Sua interpretação do pixel
não homologa um evento municipal, um limiar ou a variável-alvo da dissertação.
