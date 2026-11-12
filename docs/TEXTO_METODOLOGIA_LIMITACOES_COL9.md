# Texto para metodologia e limitações da dissertação — avaliação Col 9

Versão 12/11/2026. Texto proposto, condicionado à revisão científica do pesquisador.
Os valores abaixo descrevem a execução documentada; não devem ser apresentados
como acurácia populacional ou validação humana realizada pela dissertação.

## Metodologia

A pesquisa utiliza a Coleção 9 do MapBiomas entre 1985 e 2023, em uma delimitação
fixa de 255 municípios da zona de contato Cerrado–Amazônia, representados pelos
polígonos IBGE 2025. As comparações anuais preservam a máscara comum de pixels
válidos e todas as categorias das matrizes de origem e destino. A vegetação
nativa operacional compreende as classes 3,4,5,6,49,11,12 e 50; os destinos de usos
antrópicos compreendem 9,15,20,21,24,30,31,35,39,40,41,46,47,48 e 62. A classificação
operacional da pesquisa é mantida separada da legenda oficial. Calculam-se a
área de conversão mapeada C, em hectares, a vegetação nativa inicial elegível D e
a taxa R=100 C/D. Diferenças líquidas de estoque não substituem essas transições.

Para examinar sua qualidade temática, foram obtidos os arquivos vinculados à
Coleção 9 na [página oficial de validação](https://brasil.mapbiomas.org/downloads/pontos-de-validacao/),
com registro de data, URL, licença e SHA256. A referência consiste em pontos
interpretados pelo produtor, com campos anuais de classe, concordância e borda.
Sua seleção para a área de estudo foi feita pelas coordenadas e pelos polígonos
canônicos, independentemente do código municipal eventualmente fornecido.
Foram identificados 8.586 pontos em 253 municípios, dos quais 1.305 tinham marcação
de treinamento e foram excluídos da coorte principal. Os 7.281 restantes foram
denominados “sem marcação de treinamento”, sem presumir independência absoluta.

Os valores dos 39 rasters anuais foram extraídos na célula que contém cada
coordenada, sem reprojeção categórica, deslocamento para melhor ajuste ou
alteração das fontes. Classes de referência agrícola agregadas foram comparadas
no nível VN/UA/outros; categorias ambíguas e não observadas foram mantidas como
não comparáveis. Para cada par consecutivo, comparou-se a ocorrência VN→UA nas
referências e no mapa, incluindo pontos de todas as trajetórias válidas para
permitir examinar omissões e comissões. As contagens e razões são descritivas.
Foram realizadas sensibilidades por treinamento, COUNT, BORDA, classes 25/29/32,
vizinhança espacial e coincidência em anos próximos, sem substituir a análise
do ano exato pela alternativa de maior concordância.

A auditoria complementar examinou fluxos inversos e estabilidade das matrizes,
trajetórias nos pontos, persistência em t+2 quando disponível até 2023 e o suporte
comum aos três anos 2001–2003 em Buriticupu. Foi realizado confronto espacial
com o PRODES 2023 local, conservando as diferenças de escopo e de intervalo
temporal do sistema [INPE](https://data.inpe.br/biomasbr/prodes-monitoramento-anual-da-supressao-de-vegetacao-nativa/).
Em casos dirigidos anteriores, cenas Landsat/Sentinel foram submetidas a
verificação automatizada de QA e de NDVI ponderado pelo footprint do pixel,
sem nova interpretação humana ou geração de rótulos temáticos. Divergências
radiométricas foram registradas em hipóteses separadas e mantidas inconclusivas.

## Limitações e interpretação dos resultados

A concordância anual de grupos de cobertura nos pontos sem marcação de treino
foi 90,55% em 1985–2022. Entretanto, a coincidência das transições no ano exato
apresentou precisão descritiva 26,81% e sensibilidade 35,12%. A concordância
binária global 98,56% é dominada pela abundância de pares sem evento e não
deve ser interpretada como alta capacidade de identificar conversões. Essas
medidas são comparações com a referência publicada, que também possui incerteza.

A referência 2023 mostrou-se substancialmente incompleta: apenas um ponto
com classe preenchida dentro do recorte, enquanto o vetor auxiliar termina
em 2022. Assim, não foi possível avaliar adequadamente a transição 2022→2023
pelos pontos oficiais, inclusive nos municípios com maiores taxas mapeadas.
Ausência de mudança na amostra, especialmente onde não há pontos VN iniciais,
não equivale à ausência de conversão no município.

Não foram estimados intervalos de confiança ou acurácia representativa do
recorte. Embora o desenho original seja probabilístico e os pesos publicados
sejam inversos das probabilidades fornecidas, a retirada de pontos de treinamento,
a não resposta anual, os estratos com uma unidade e os subconjuntos temáticos
exigem documentação adicional para reconstruir a inferência de domínio.
Os mesmos locais são repetidos ao longo dos anos e não constituem amostras
temporais independentes. Tampouco se converteram contagens ponderadas em
hectares corrigidos por erro.

A referência compartilha insumos de sensoriamento remoto com o mapeamento
e sofreu revisões; a exclusão dos pontos marcados não comprova independência
integral. A persistência no raster é afetada pela própria filtragem temporal
da coleção, descrita no [ATBD Col9](https://brasil.mapbiomas.org/wp-content/uploads/sites/4/2025/02/ATBD-Collection-9-versao2-v2.pdf).
O PRODES não representa universalmente reconversões de vegetação secundária
nem o destino de uso. NDVI não distingue, por si, formação nativa de pastagem
ou agricultura, e as imagens auxiliares possuem restrições sazonais, de QA e
de calibração. Portanto, concordâncias e discordâncias entre produtos não
foram utilizadas para corrigir automaticamente as matrizes de conversão.

Os cenários relativos e absolutos A/B/C permanecem hipóteses científicas, sem
homologação. A qualidade anual das classes, a qualidade das transições,
a validade de um desfecho municipal e o desempenho preditivo são dimensões
distintas. A magnitude contínua da conversão mapeada constitui alternativa
complementar a discutir, sem eliminar a incerteza da medição. O experimento
principal é retrospectivo, com validação temporal e espacial, e não uma
simulação operacional histórica com disponibilidade anual comprovada das fontes.
Os anos finais e casos extremos já foram explorados cientificamente, de modo
que o teste não é completamente cego à formulação do desfecho. O ano 2024
permanece reservado e não foi utilizado. Nenhum desfecho binário foi homologado
e não houve treinamento definitivo nesta etapa.
