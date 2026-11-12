# Protocolo executado — transições espaciais anuais Coleção 9

Checkpoint de 11/11/2026. Escopo autorizado: matrizes e medidas contínuas para
255 municípios fixos, 1985–2023, com relatório exploratório. Não define tau,
A_min, elegibilidade mínima definitiva, variável-alvo ou treinamento.

## Fontes e território

- `referencias/manifesto_rasters_transicoes_col9.json`: 39 rasters anuais,
  SHA256 integral, tamanho, data de modificação, origem, CRS, transformada,
  dimensões, NoData e complemento. Os hashes foram calculados na preparação e
  conferidos novamente antes da execução integral.
- GeoPackage aprovado de 255 municípios IBGE 2025 e consolidado Col9 externo:
  hashes no manifesto. As geometrias também são conferidas contra os hashes WKB
  de `referencias/territorio_col9_hashes.json`, iguais aos utilizados no dashboard.
- A seleção dos arquivos é explícita por ano: os sufixos de 2016/2017 não
  permitem deduzir a sequência temporal pelo nome. Para 2002 é usado o arquivo
  `municipios_coverage_2002_COL9_validado.tif`, byte a byte igual ao alias
  `municipios_coverage_2002-023.tif` do consolidado aprovado.
- O complemento aprovado de três municípios do Maranhão é aplicado somente
  sobre zeros e dentro dos três códigos, exceto 2002. Divergência com pixel já
  classificado interrompe o processamento. Contagens complementadas são auditadas.
- Não são usados PNGs de visualização, Coleção 10/10.1 ou áreas administrativas
  variáveis entre anos. Rasters e resultados anteriores permanecem intactos.

As grades anuais são idênticas, sem reamostragem. A máscara territorial considera
o centro do pixel, independentemente para cada município, como no consolidado
aprovado. Não há fracionamento de pixels na fronteira. A transformação do
GeoPackage EPSG:4674 para a grade EPSG:4326 resultou em operação `+proj=noop`
neste ambiente, com WKB idêntico nos 255 municípios; ver
`docs/evidencias/transicoes_crs_equivalencia_20261111.json`. Essa verificação não
afirma equivalência geral dos referenciais fora deste ambiente e aplicação.

Os 39 rasters foram inspecionados quanto às máscaras GDAL: somente máscaras
`all_valid`/`nodata`, sem máscaras especiais alpha/per_dataset. Evidência em
`docs/evidencias/transicoes_mascaras_gdal_20261111.json`, incluindo o hash do
auxiliar encontrado. O suporte válido exclui 0, 27 e o NoData declarado; código
inesperado dentro do território causa erro.

## Cálculo e auditoria

Para cada município e par t→t+1:

1. Construir a interseção dos pixels válidos dos dois anos dentro da máscara
   municipal. Registrar também válidos somente em t, somente em t+1 e inválidos
   em ambos; essas quatro parcelas conservam o total da grade municipal.
2. Contabilizar a matriz densa de origem × destino, em pixels e hectares.
   Os 29 códigos terminais da legenda oficial Col9 permanecem nos eixos;
   a linha/coluna 27 é mantida zerada. Zero não representa classe de conversão.
3. Calcular a área geodésica do pixel WGS84 por linha/latitude, sem assumir
   0,09 ha constantes. Conservar estoques, marginais e áreas comuns.
4. Somar C = área de origem {3,4,5,6,49,11,12,50} e destino
   {9,15,20,21,24,30,31,35,39,40,41,46,47,48,62}.
5. D é toda a vegetação nativa inicial observada no suporte comum, inclusive
   pixels que permanecem nativos ou vão para outros destinos válidos.
   R = 100 C/D (%/comparação anual); D=0 produz valor ausente.
6. Elegibilidade = 100 D/VN inicialmente observada. Cobertura válida comum é
   informada separadamente sobre a grade municipal. Nenhuma dessas medidas é
   substituída pela diferença entre área territorial e área classificada.

Cada estoque anual, por classe, é comparado ao consolidado aprovado: nenhuma
diferença de pixels é aceita; tolerância de 0,0001 ha acomoda o arredondamento
do CSV a quatro casas. Essa paridade valida a implementação em relação ao acervo,
não a acurácia temática do mapa. A verificação independente do relatório confere
somas, marginais, partições, C, D, R e hashes dos artefatos consolidados.

Buriticupu é auditado nos pares 2001→2002 e 2002→2003 e no suporte válido comum
aos três anos. Matrizes completas por par e triplas são preservadas em NPZ e
exportadas como quatro CSVs densos de 841 células, inclusive zeros.

Sensibilidades: destino adicional 25; origens adicionais 29, 32 e 29+32;
combinação 29+32 com destino 25. A classificação principal e a oficial continuam
separadas. Adicionar origens altera numerador e denominador; não se presume
monotonicidade da taxa. O cenário lógico de ausência de observação varia de
nenhuma a toda a VN inicial excluída convertida. Sua amplitude é 100 menos a
elegibilidade, em pontos percentuais, sobre o estoque inicial completo; não é
intervalo de confiança nem tratamento do erro temático.

## Reprodução sem banco e sem implantação

Usar ambiente geoespacial separado. Versões efetivas da execução:
Python 3.14.6, numpy 2.5.4, pandas 2.3.3, rasterio 1.5.2, geopandas 1.2.0,
shapely 2.2.0, pyproj 3.8.0; GDAL 3.12.2 e PROJ 9.8.1.
As versões também constam em `execucao.json`. Não misturar silenciosamente
esse ambiente com o do app (pandas 3.1.0). Os comandos abaixo são exemplos para
uma **nova pasta de saída**; não devem ser executados sobre o relatório existente.

```powershell
$geoPython = 'D:/mestrado/.venv_territorial/Scripts/python.exe'
& $geoPython processamento/transicoes_col9.py --manifesto referencias/manifesto_rasters_transicoes_col9.json --saida resultados_transicoes_col9/NOVA_EXECUCAO --workers 2 --bloco 512 --cache-mb 2048 --verificar-hashes
& $geoPython processamento/relatorio_transicoes_col9.py --resultados resultados_transicoes_col9/NOVA_EXECUCAO --relatorio docs/NOVO_RELATORIO_TRANSICOES.md
& $geoPython processamento/exportar_matriz_col9.py --resultados resultados_transicoes_col9/NOVA_EXECUCAO --municipio 2102325 --ano-origem 2001 --mascara tripla --saida resultados_transicoes_col9/NOVA_EXECUCAO/buriticupu_2001_tripla.csv
```

O manifesto existente contém caminhos absolutos da base e datas/versões das
fontes. Para transportar o acervo, preparar um novo manifesto com os mesmos
hashes científicos, sem editar o manifesto histórico. Consultar `--help` de
`processamento/manifesto_transicoes_col9.py`. Esse programa não sobrescreve saídas.

`--retomar` aceita somente a mesma assinatura de manifesto, código, metodologia,
anos, municípios, bloco e versões; valida os checkpoints antes de reutilizar.
Workers/cache são recursos computacionais e podem mudar sem mudar as fórmulas.
A primeira execução foi interrompida de forma controlada para aumentar o cache
GDAL de 256 para 2048 MB por trabalhador; a retomada conservou os checkpoints
válidos e as tentativas anteriores. Não usar parâmetros maiores sem verificar RAM.

Cada município conclui uma tentativa em pasta nova e publica `concluido.json`
com hashes. O consolidado inclui eixos explícitos em NPZ, sem pickle. Não se
deve usar arquivos de tentativa sem checkpoint concluído. As saídas usam modo
de criação exclusiva e recusam substituição. Resultados volumosos ficam fora
do Git e da imagem Docker; os códigos, manifesto e relatórios são preservados.

O relatório inclui uma leitura crítica revista após a geração automática e
seis figuras científicas, inspecionadas visualmente. As figuras são criadas por
`processamento/figuras_transicoes_col9.py` em contêiner temporário sem rede ou
acesso ao banco. Seus hashes ficam no manifesto da pasta `figuras/`.

O checkpoint portátil pode ser criado em novo nome com
`processamento/empacotar_transicoes_col9.py --resultados PASTA_CONCLUIDA --saida NOVO.zip`.
Inclui somente as tentativas municipais referenciadas por checkpoints concluídos,
o consolidado, análises, figuras, códigos, referências, testes e documentação.
Rasters brutos e banco são externos; não inclui credenciais. O ZIP contém um
manifesto SHA256 por arquivo e possui hash externo, com releitura CRC e hashes.
Os checkpoints históricos mantêm caminhos Windows: o pacote documenta a
execução nesse sistema. Reutilização em outra plataforma exige adaptação validada
de caminhos em uma nova execução, preservando os arquivos históricos.

## Testes e limite da interpretação

- Regressão principal: 51 testes passaram, dois módulos geoespaciais foram
  ignorados nesse ambiente por ausência de rasterio.
- Ambiente geoespacial: 12 testes passaram, incluindo os dois testes de mapas
  e dez de transições. Total: 63 testes distintos, sem remoção dos anteriores.
- Novos testes cobrem direção origem/destino, conservação e marginais,
  denominador zero, máscara tripla, invariância ao particionamento, área por
  latitude, complemento sem substituição, divergência, grades incompatíveis,
  limites de ponto flutuante e exportação das matrizes com zeros.
- Evidências: `docs/evidencias/transicoes_regressao_completa_20261111.txt` e
  `docs/evidencias/transicoes_testes_geoespaciais_finais_20261111.txt`.

Nenhuma diferença líquida de estoque é usada como conversão espacial.
Matrizes indicam mudanças **mapeadas**, que exigem validação temática independente.
A grade de candidatos no relatório fornece contagens agregadas para discutir
relevância, sem criar uma coluna de alvo e sem otimização por balanceamento.
Antes de modelar: validar tau, A_min, regra de combinação e elegibilidade;
avaliar referência independente e incerteza; construir a resposta t→t+1 somente
após essas decisões. Preditores deverão estar disponíveis até t, com seleção,
transformações e ajuste restritos aos períodos de treino e validação temporal
e espacial; nenhum dado futuro poderá antecipar o evento.

A implantação do app foi autorizada e realizada separadamente; ver
`RELATORIO_IMPLANTACAO_COL9_20261111.md`. Esta rotina científica não consulta nem
modifica PostgreSQL, views, contêineres ou o dashboard legado.
