# Validação temática das transições Coleção 9 — relatório preliminar

11/11/2026. **Etapa A executada como desenho/sorteio, levantamento de referência
e inspeção preliminar dirigida. A validação temática representativa permanece
aberta: não há acurácia estimada nem referência homologada para as 3.744 unidades
probabilísticas.** Nenhuma conversão consolidada foi corrigida ou removida.

## Acervo e independência

Foi inventariada a pasta indicada pelo pesquisador `D:/mestrado/Mapas-Estudo`,
incluindo os índices dos ZIPs sem extração. Inventário ativo:
`validacao_cientifica_col9\checkpoint_20261111\inventario_mapas_estudo_v2.json`: 161 arquivos, 59 metadados AppleDouble,
21 ZIPs reais e zero falhas de leitura dos cabeçalhos/índices. Os 59 arquivos
`._*` são metadados auxiliares, não rasters/ZIPs corrompidos. O primeiro inventário
que tentou abri-los como dados foi preservado, com essa interpretação corrigida.

Há 51 rasters de uma banda uint8 e um complemento de 38 bandas uint8; os nomes,
grades e descrições identificam principalmente classificações MapBiomas, variantes
de 2002 e produtos derivados. Os índices também contêm PRODES, focos, vetores,
PNGs e código. Não foi identificada nessa pasta uma série bruta multiespectral
ou interpretação de campo com datas/proveniência que permita tratá-la como
verdade independente. Concordância entre aliases ou derivações da mesma Col9
é verificação de acervo, não validação temática. PRODES/focos são corroboradores
com outras definições/janelas, não rótulos substitutos.

Foram adquiridas referências públicas Sentinel-2 (sensor distinto do Landsat
usado pela Col9) e Landsat Collection 2. A interpretação de Landsat é separada
do classificador, mas compartilha sensor/observação e pode ter erros correlacionados.
Não se afirma independência absoluta ou verdade de campo. Fontes:
[Earth Search/Element 84](https://element84.com/earth-search/),
[Copernicus/ESA](https://dataspace.copernicus.eu/data-collections/copernicus-sentinel-missions/sentinel-2),
[Landsat/USGS](https://www.usgs.gov/landsat-missions/landsat-science-products) e
[Planetary Computer](https://planetarycomputer.microsoft.com/docs/quickstarts/reading-stac/).

## Desenho probabilístico executado

População: 9.690 unidades município–transição, incluindo os 255 municípios,
1985→1986 a 2022→2023. Amostra em dois estágios, SRS sem reposição,
semente 20261111, sorteio por chave SHA256 estável, sem substituição por falta de imagem.

Primeiro estágio: cruzamento UF (MA/MT/PA/RO/TO), período
(1986–1999, 2000–2009, 2010–2019, 2020–2021, 2022, 2023), magnitude
(R<0,5%; 0,5≤R<2%; R≥2%) e estabilidade de códigos
(diagonal/área comum ≥95% ou <95%). Os cortes são parâmetros de desenho,
não tau final ou diagnóstico de acurácia. Essa estabilidade é concordância
do próprio mapa entre dois anos; não prova estabilidade real da paisagem.

Obtidos **120 estratos não vazios**, **234 município–transições**,
até dois por estrato; **11 estratos censitários**.
Estratos unitários são censo, não amostras de tamanho um para estimar variância.
Probabilidade de primeiro estágio varia de 0.00399202 a 1.

Segundo estágio: quatro pixels por subestrato não vazio, até censo se menor:
VN→UA, VN→outros destinos, outras origens→UA e outras origens→outros destinos,
no suporte válido comum. Os dois últimos estratos permitem investigar omissão
da origem nativa, em vez de validar somente positivos do mapa. Foram sorteados
**3.744 pixels-pares**, com linhas/colunas, coordenadas, área geodésica,
probabilidades e pesos. Contexto t−1/t+2 foi extraído como diagnóstico do mapa;
t+2 é ausente quando indisponível, especialmente para destino 2023.

Para pixel i, município–par j e estrato h:
`pi_i = (n_h/N_h) (n_jk/N_jk)`; `peso_ha = area_pixel_ha/pi_i`.
O estimador futuro de área de uma categoria de referência é a soma dos
indicadores de referência multiplicados por peso_ha (Horvitz–Thompson).
Matrizes de erro devem usar esses pesos e o desenho por conglomerados;
não usar média simples, bootstrap de pixels independentes ou contagem dirigida.
Unidade de inferência é área-pixel-par municipal no suporte comum, não toda
área territorial incluindo observações ausentes. Anos somados são hectares-evento.

O tamanho é um piloto viável de resposta, sem precisão pré-garantida. Quando
houver respostas, estimar variância nos dois estágios (com correção de população
finita), incerteza das razões e possível ampliação pré-especificada da amostra.
Não se pode prometer acurácia municipal para cada uma das 9.690 comparações
com esse tamanho. O desenho segue os princípios de amostragem probabilística,
resposta independente e análise coerente de
[Olofsson et al. (2014)](https://doi.org/10.1016/j.rse.2014.02.015).

## Inspeção dirigida separada e evidências

33 unidades dirigidas, 528 pixels-pares, foram selecionadas nos cinco municípios
prioritários, com pares 2018→2019 a 2022→2023. Incluem ainda Buriticupu
1999→2000 a 2003→2004 e Vila Bela 1985→1986, 1986→1987, 1987→1988.
Não existe controle anterior a 1985 nesta coleção; os controles subsequentes
não são apresentados como se fossem anteriores.

Dois lotes complementares de referência foram obtidos sem substituir o primeiro:
`referencias_v2/`: 74 recortes sobre 24 pontos dirigidos (85 consultas ponto–ano);
`referencias_fim_ano/`: 30 recortes sobre 15 pontos, em novembro/dezembro;
`referencias_historicas_v3/`: 15 recortes históricos sobre quatro pontos,
superando a limitação HTTP 429 por reutilização de assinatura pública de leitura.
São recortes/cenas, não unidades independentes adicionais: pontos/anos podem repetir.
Metadados, identificadores STAC, datas, QA, CRS, transformadas e hashes foram
preservados. Tokens temporários não são gravados. A primeira tentativa
`referencias/` com erro de ordenação foi conservada como histórico.

Sentinel: até oito cenas candidatas, até três tentadas no lote maio–outubro;
SCL central 4/5/6. Complemento novembro–dezembro: até 100 retornadas, até 30
mais recentes tentadas. Landsat histórico: janela anual, QA_PIXEL sem
fill/dilated cloud/cloud/shadow/snow. QA no centro **não garante** todo o pixel
MapBiomas ou janela sem nuvem. Os painéis localizam o centro; o quadrado não
é uma delimitação georreferenciada rigorosa do pixel de referência.

Foram inspecionadas visualmente as 24 sequências dirigidas, incluindo o caso
histórico inicialmente sem painel após sua recuperação, e os 15 complementos
de fim de ano. Notas por ID: `validacao_cientifica_col9\checkpoint_20261111\inspecao_dirigida_notas.csv`.
**Interpretação preliminar assistida por IA, não adjudicação humana independente**;
nenhuma nota foi copiada para as fichas cegas como resposta homologada.

Achados que precisam orientar a revisão:

- Buriticupu `d_2102325_2022_7482_56626`: vegetação no contexto em julho/2023 e
  abertura em dezembro/2023; compatível com mudança tardia. Santa Inês
  `d_2109908_2021_5265_60229`: situação semelhante entre julho e dezembro/2022.
  A análise somente na estação seca teria sido insuficiente. O destino específico
  pastagem e o estado representado no mapa anual ainda não foram adjudicados.
- Figueirópolis `d_5103809_2022_49261_10687` e São José
  `d_5107107_2022_49412_11562`: vegetação visível junto ao centro até dezembro/2023,
  com bordas/mistura e limitações da imagem de origem. Não se observou abertura
  inequívoca nesse suporte; são casos para auditoria do pixel completo e registro
  temporal, não prova automática de falso positivo ou de erro municipal total.
- Vila Bela: confusão visual entre vegetação herbácea/alagável e pastagem,
  sazonalidade, bordas sem dados e nuvens. O caso histórico 1985→1986 não foi
  confirmado tematicamente por um único ponto Landsat de 30 m.
- Buriticupu 2001–2003: as cenas de 2003 mostram lacunas/faixas SLC-off e
  diferenças no contexto. As máscaras Col9 permanecem auditadas e iguais no
  teste triplo, mas as referências consultadas não resolvem todos os pares.
  O [USGS documenta o SLC-off do Landsat 7](https://www.usgs.gov/faqs/what-landsat-7-etm-slc-data?items_per_page=6&page=1).

## Picos e classes envolvidas

| ano_destino | classe_origem | classe_destino | area_ha | participacao_conversao_anual_pct |
|---|---|---|---|---|
| 2022,0000 | 3,0000 | 15,0000 | 444847,6191 | 46,1552 |
| 2022,0000 | 4,0000 | 15,0000 | 166943,8128 | 17,3213 |
| 2022,0000 | 11,0000 | 15,0000 | 139557,0264 | 14,4797 |
| 2022,0000 | 6,0000 | 15,0000 | 51783,9428 | 5,3728 |
| 2022,0000 | 4,0000 | 21,0000 | 49096,8450 | 5,0940 |
| 2023,0000 | 3,0000 | 15,0000 | 530199,0840 | 43,8355 |
| 2023,0000 | 4,0000 | 15,0000 | 226735,1203 | 18,7459 |
| 2023,0000 | 12,0000 | 15,0000 | 136342,2306 | 11,2724 |
| 2023,0000 | 4,0000 | 21,0000 | 83143,3122 | 6,8741 |
| 2023,0000 | 3,0000 | 21,0000 | 70023,5779 | 5,7894 |

Códigos: 3 formação florestal, 4 formação savânica, 6 floresta alagável,
11 campo alagado/área pantanosa, 12 formação campestre; 15 pastagem e 21 mosaico
de usos. A hierarquia oficial Col9 está preservada em `referencias/legenda_col9.csv`.
Não se atribui causalidade a essa decomposição.

Controles municipais e picos recentes:

| NM_MUN | ano_destino | taxa_conversao_pct | area_convertida_ha | origem_dominante | destino_dominante |
|---|---|---|---|---|---|
| Buriticupu | 2020 | 3,1834 | 3387,8503 | 3 | 15 |
| Buriticupu | 2022 | 7,1829 | 7480,7139 | 3 | 15 |
| Buriticupu | 2023 | 9,4289 | 9279,6627 | 3 | 15 |
| Santa Inês | 2020 | 8,0946 | 1229,8958 | 3 | 15 |
| Santa Inês | 2022 | 40,5903 | 5335,6791 | 3 | 15 |
| Santa Inês | 2023 | 52,0325 | 4055,9762 | 3 | 15 |
| Figueirópolis D'Oeste | 2020 | 1,1270 | 99,5466 | 4 | 15 |
| Figueirópolis D'Oeste | 2022 | 26,9148 | 2501,1221 | 3 | 15 |
| Figueirópolis D'Oeste | 2023 | 52,9902 | 3595,2532 | 3 | 15 |
| Vila Bela da Santíssima Trindade | 2020 | 2,7675 | 17011,4330 | 11 | 15 |
| Vila Bela da Santíssima Trindade | 2022 | 6,0281 | 36697,7641 | 11 | 15 |
| Vila Bela da Santíssima Trindade | 2023 | 3,5865 | 20766,9463 | 3 | 15 |
| São José dos Quatro Marcos | 2020 | 1,9488 | 272,9218 | 3 | 15 |
| São José dos Quatro Marcos | 2022 | 21,5420 | 2984,5853 | 3 | 15 |
| São José dos Quatro Marcos | 2023 | 49,2066 | 5348,8469 | 3 | 15 |

As séries completas dos cinco municípios, todos os fluxos não nulos prioritários
e a decomposição por UF/ano/código estão em `picos/` e `limiares/`.

## Protocolo de resposta e não resposta

`fichas_cegas.csv` oculta classes MapBiomas, magnitude, estrato e cenário do
intérprete. Registrar para os dois anos: VN, UA, OUTROS ou INCONCLUSIVO,
datas reais das imagens, fonte, evidência, intérprete, justificativa e confiança.
Usar o pixel completo georreferenciado, contexto e série intra-anual comparável;
ampliar datas quando necessário, sem deslocar a unidade sorteada.
Cobertura mista sem predominância confiável, nuvem/sombra, lacuna SLC,
resolução ou falta de informação de manejo devem permanecer inconclusivas.

Recomenda-se que dois intérpretes humanos independentes classifiquem as fichas às cegas;
guardar respostas separadas e adjudicar divergências, sem sobrescrever opiniões.
A adjudicação só verá o mapa depois de fixar a interpretação de referência.
Manter protocolos, histórico de versões e eventuais conflitos de fontes.

As 3.744 fichas probabilísticas estão pendentes de referência interpretada.
Não se calculou comissão, omissão, acurácia global ou IC com os casos dirigidos.
Não resposta pode ser informativa: não excluir nuvens/ambiguidades silenciosamente
nem chamar a proporção dos casos respondidos de acurácia do universo. Quando
completar a resposta, implementar/validar o estimador e variância do desenho;
se persistir não resposta, reportar suas taxas ponderadas/estratos e limites de
sensibilidade, com eventual ajuste de não resposta justificado cientificamente.

## Arquivos, reprodução, testes e pendências

Rotinas: `amostra_tematica_col9.py`, `inventariar_referencias_locais_col9.py`,
`referencias_tematica_col9.py`, `referencias_fim_ano_col9.py`,
`diagnostico_picos_col9.py`, `respostas_tematica_col9.py` e este gerador, em
`processamento/`. Cada CLI tem `--help`; exemplo de nova execução:

```powershell
python processamento/amostra_tematica_col9.py --resultados resultados_transicoes_col9/integral_255_1985_2023_20261111 --limiares validacao_cientifica_col9/checkpoint_20261111/limiares --manifesto referencias/manifesto_rasters_transicoes_col9.json --saida validacao_cientifica_col9/NOVA_AMOSTRA --workers 2
```

Usar ambiente geoespacial documentado no protocolo anterior, acrescido de Pillow;
a versão efetiva é registrada no manifesto de ambiente desta entrega. Rede é necessária somente para
recuperar referências. Reusar metadados/recortes com hashes preserva a evidência
mesmo se o catálogo remoto mudar. Os testes verificam sorteio, probabilidades,
amostragem sem reposição, controles de omissão, não resposta e integridade;
**não substituem validação temática**. Regressão: 77 testes distintos aprovados.

Foram produzidas ainda 42 pranchas em `pranchas_pixel/`, com os quatro cantos
da célula Col9 transformados para o CRS de cada cena e um zoom local. Seu
`indice.html` permite percorrer as imagens sem revelar classes do mapa.
O footprint é rigoroso para a grade nominal; não corrige erro de registro
entre sensores. As três pranchas críticas de Figueirópolis, São José e
Buriticupu 2022→2023 foram reinspecionadas com esse suporte explícito.
As fichas `fichas_interprete_A.csv` e `fichas_interprete_B.csv` são cópias novas
com campos adicionais para confiança, mistura e georreferenciamento.

Pendências: respostas independentes da amostra, avaliação do registro espacial,
adjudicação, estimativa de erro/área e incerteza coerente com o
desenho, confirmação dos casos históricos/mistos e validação científica dos
limiares. Nenhum banco, dado original, resultado consolidado, dashboard ou
checkpoint anterior foi alterado. Nenhum Y ou modelo definitivo foi homologado.
