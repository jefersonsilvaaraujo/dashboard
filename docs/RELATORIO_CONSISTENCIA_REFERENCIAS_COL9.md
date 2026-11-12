# Consistência temporal e confronto com referências externas — Col 9

Data: 12/11/2026. Série principal: 1985–2023; 255 municípios canônicos.
As matrizes originais permanecem intactas. Os resultados abaixo não constituem
novos rótulos de referência ou correções automáticas.

## Matrizes completas e estabilidade

Foram verificadas as 9.690 matrizes e seus artefatos consolidados; os totais de VN→UA
recalculados das matrizes conferem com as métricas anteriores. Foram exportados, por município/par, estabilidade exata da classe, fluxo inverso UA→VN e destinos
pastagem, agricultura, mosaico e demais UA. Fluxo inverso agregado simultâneo não
prova reversão no mesmo pixel: tal afirmação requer trajetória de três anos.

| ano_destino | C_ha | fluxo_inverso_UA_VN_ha | VN_pastagem_ha | VN_agricultura_ha | VN_mosaico_ha | VN_outros_UA_ha |
|---|---|---|---|---|---|---|
| 2020 | 568441.4247 | 312016.0231 | 451236.7109 | 14726.4457 | 97614.5510 | 4863.7170 |
| 2021 | 544652.8085 | 220723.4480 | 452021.2769 | 10687.2458 | 73216.9229 | 8727.3628 |
| 2022 | 963808.9575 | 215602.9396 | 849022.9597 | 18524.0537 | 95627.1661 | 634.7780 |
| 2023 | 1209521.0670 | 258949.7072 | 1010216.2818 | 24350.7942 | 174242.5917 | 711.3994 |

Pastagem responde por 88,09% da área convertida de 2022 e 83,52% de 2023; agricultura
por 1,92% e 2,01%; mosaico por 9,92% e 14,41%. Os principais fluxos regionais são
3→15 (444.847,62 ha em 2022; 530.199,08 ha em 2023), seguidos de 4→15. Em 2022 também
se destaca 11→15; em 2023,12→15 e 4→21. Esses padrões orientam a investigação de
confusão temática e manejo; não comprovam causa ambiental ou erro de integração.

O [ATBD geral Col9 v2, setembro2024](https://brasil.mapbiomas.org/wp-content/uploads/sites/4/2025/02/ATBD-Collection-9-versao2-v2.pdf)
descreve filtros espaciais/temporais e regras de integração, inclusive regra envolvendo
MapBiomas Alerta e classe 21 a partir de 2019. Assim, persistência e concordância com
produtos empregados na integração não são validações independentes por si mesmas.
As matrizes desta dissertação derivam diretamente dos rasters anuais; não reproduzem
necessariamente o filtro espacial adicional dos produtos oficiais de transição.

## Trajetórias nos pontos oficiais

Em 7.281 pontos sem marcação de treinamento foram examinados todos os 38 pares,
classes anterior/posterior e a vizinhança 3 × 3. Foram encontradas 3.289 conversões
mapeadas; 3.175 têm grupo válido em t+2,3.174 permanecem UA e nenhuma retorna VN
no ano seguinte. Um destino vai para outro grupo. Para 2022→2023, t+2 não existe
na série autorizada; 114 conversões desses pontos ficam censuradas, nunca negativas.
Os números são diagnósticos dos pontos; não áreas nem proporções representativas
de persistência de todos os pixels municipais.

| ano_destino | conversoes_pontos | com_t2 | persistem_UA | retornam_VN |
|---|---|---|---|---|
| 2018 | 48 | 48 | 48 | 0 |
| 2019 | 60 | 60 | 60 | 0 |
| 2020 | 53 | 53 | 53 | 0 |
| 2021 | 53 | 53 | 53 | 0 |
| 2022 | 82 | 82 | 82 | 0 |
| 2023 | 114 | 0 | 0 | 0 |

A alta persistência é compatível com a própria filtragem do produto e não resolve
a baixa coincidência com a referência. Foi também auditada a presença de UA emt−1:
12 episódios mapeados têm esse padrão. Isso não significa que 12 sejam erros de
classificação, pois reconversões reais e manejos podem existir.

## Datação, registro e categorias

Entre 2.304 discordâncias de mapa positivo com referência comparável,1.412 têm UA
nos dois anos de referência e 875 têm VN nos dois anos; as demais 17 têm outros
percursos. Isso é compatível com defasagem de datação e/ou discordância temática,
sem escolher automaticamente a explicação. Foram exportadas as classes de cada caso.

| janela_mais_menos_anos | n_conversoes_mapa_com_janela_ref_observada | n_com_evento_ref_na_janela | fracao_coincidente |
|---|---|---|---|
| 0 | 3148 | 844 | 0.2681 |
| 1 | 3060 | 1343 | 0.4389 |
| 2 | 2999 | 1517 | 0.5058 |

As janelas±1/±2 anos aumentam a coincidência, mas alteram a pergunta; seus
denominadores também mudam por falta de referência em parte das janelas. As janelas
são truncadas no início/fim da série e nenhuma usa 2024. Não se deslocou o ano
do evento para melhorar uma medida. A comparação exata continua principal.

A sensibilidade “alguma das 9 células” tem 1.210 TP e 6.982 FP, precisão descritiva 14,77%
e sensibilidade 50,35%. A ampliação inclui suportes vizinhos e aumenta oportunidades
de coincidência; não melhora de modo inequívoco o diagnóstico nem autoriza corrigir
registro. Homogeneidade e BORDA permanecem como indicadores auxiliares.

As classes 25/29/32 foram reavaliadas em referência e mapa. Incluir 25 resulta em
871 TP,2.354 FP,1.536 FN, precisão 27,01% e sensibilidade 36,19%; 29/32 não alteram as
contagens de eventos nessa amostra. Isso não demonstra ausência de efeitos dessas
classes nas áreas municipais. A classe 21 é operacionalmente UA, mas a referência
não permite validar sua subclasse terminal de mosaico separadamente.

## Buriticupu 2001–2003 e controles

A máscara válida comum aos três anos foi conferida no NPZ anterior: 2.852.945 pixels
por intervalo. O teste automatizado confirmou que C e D com essa máscara coincidem
com os valores consolidados de ambos os pares. C=5.843,61 ha e R=3,06205% em 2001→2002;
C=23.350,95 ha e R=12,08391% em 2002→2003. A elegibilidade VN é 100% e 99,701581%,
respectivamente. Essa auditoria de suporte não confirma a natureza temática da conversão
nem atribui automaticamente diferenças de área a NoData.

Dos 29 pontos sem treino em Buriticupu, há uma mudança de referência em cada um dos
dois pares. Em 2001→2002 o mapa não assinala evento nesses locais; em 2002→2003 mapa
e referência assinalam um evento cada em pontos distintos: 0 TP,1 FP,1 FN. Os controles
de anos anteriores e subsequentes permanecem na tabela por ponto. Em 2023 não há
referência local anual. A comparação espectral dirigida de 2001→2002 registra
ΔNDVI≈−0,0144; 2002→2003 tem distância sazonal 99 dias e fica inconclusiva.

## PRODES 2023

Foi amostrado o raster legado `prodes_brasil_2023.tif`, sem abrir o produto 2025
como referência desta etapa. SHA256 do TIFF, QML, grade, legenda e proveniência
estão em `complementar/proveniencia_PRODES2023.json`. A origem institucional é
[INPE/TerraBrasilis](https://terrabrasilis.dpi.inpe.br/downloads/); a URL exata e a
data do download original local não foram comprovadas e não foram inventadas.

O [INPE descreve o PRODES](https://data.inpe.br/biomasbr/prodes-monitoramento-anual-da-supressao-de-vegetacao-nativa/)
como monitoramento de supressão primária, com diferenças entre biomas. Seu ano de
observação, unidades mínimas, classes acumuladas e intervalos históricos podem
divergir das classes anuais de cobertura e das reconversões secundárias da Col 9.
O confronto conserva d2000 como acumulado, códigos bienais como intervalos e±1 ano
apenas como proximidade exploratória; não usa uma tolerância para declarar acerto anual.

| confronto_PRODES | n_pares_ponto |
|---|---|
| coincidencia_ano_ou_intervalo_PRODES | 249 |
| cronologia_distinta_inconclusiva_sobre_reconversao | 1808 |
| historico_ate2000_sem_data_de_conversao | 648 |
| inconclusivo_escopos_ou_cobertura_distintos | 386 |
| proximidade_temporal_um_ano_sem_validacao_anual | 198 |

Em 2023 há 9 coincidências de ano em 114 conversões dos pontos sem treino e uma
proximidade de um ano. Os demais casos são históricos, outra cronologia ou escopos
incompatíveis. Isso não transforma os 104 restantes em erros comprovados: a ausência
de incremento PRODES pode decorrer de vegetação secundária, suporte ou definição.
O mesmo vale para coincidências positivas: não certificam o destino pastagem/agricultura.

## Imagens Landsat/Sentinel: auditoria automatizada, sem interpretação adicional

Foram reutilizadas as cenas já selecionadas no checkpoint dirigido anterior:
84 combinações únicas local/ano,15 Landsat e 69 Sentinel, em 24 locais dos cinco
municípios prioritários, incluindo controles. Cinco repetições da mesma cena em
dois catálogos foram identificadas e deduplicadas por local/ano/ID, sem escolher
uma cena que concordasse melhor com a conversão. A tentativa inicial incompleta
foi preservada em `espectral/`; os dados finais são `espectral_v2/` e `radiometria/`.

Foram extraídos RED/NIR e QA, arquivados DN, transformações, interseção do footprint
Col 9, URLs sem tokens e hashes. NDVI é média ponderada pela interseção espacial,
não classificação de uso. QA cobre o footprint inteiro; sazonalidade≤45 dias e mesma
família de sensor são condições técnicas de comparação, sem validação de manejo.
QA_RADSAT, BRDF e atmosfera residual permanecem limitações. A calibração Landsat
segue os fatores da [USGS](https://www.usgs.gov/faqs/how-do-i-use-a-scale-factor-landsat-level-2-science-products).

Em 38 cenas Sentinel o asset declara offset−0,1 enquanto o próprio item informa
`earthsearch:boa_offset_applied=true`. Aplicar literalmente o offset produz valores
negativos em parte das bandas vermelhas. Foi registrada a incompatibilidade local
e a [discussão no repositório do provedor](https://github.com/Element84/earth-search/issues/71).
A mudança de baseline e seus offsets também estão na
[documentação Copernicus](https://sentiwiki.copernicus.eu/web/s2-products).
Foram calculadas as hipóteses “offset já aplicado” e “asset literal”, sem escolher
por concordância. As comparações afetadas ficam inconclusivas até confirmação da
calibração pelo provedor/original; não foram confundidas com inexistência de imagens
ou com erro do MapBiomas. Esse conflito é específico do fornecedor das imagens auxiliares.

Após os critérios conservadores, apenas dois dos 24 pares dirigidos têm proxy
comparável sem conflito: Buriticupu 2001→2002 (−0,0144) e 2019→2020 (−0,5779).
Os demais têm conflito radiométrico, sazonalidade ou QA. Mesmo os dois proxies
não adjudicam VN→UA nem sua relevância; são evidência espectral complementar.
Para os picos 2022/2023, as hipóteses podem mostrar aumentos ou reduções, mas não
fornecem confirmação temática automática. Não houve nova interpretação visual.

O inventário dos 320 recortes prévios do piloto foi reutilizado apenas para
documentar datas/QA; são locais diferentes dos pontos oficiais. Não foram criados
novos pacotes de interpretação. Não há raster de área queimada harmonizado e
manifestado neste acervo: focos de calor não são cicatrizes/área queimada.
Esse confronto permanece **inconclusivo**, sem substituir fogo por uso antrópico.

## Síntese de evidências

“Concordante” designa coincidência explícita na comparação especificada;
“discordante” designa evidência contraditória à atribuição do ano/grupo, sujeita
à qualidade da referência; “inconclusivo” abrange ausência, escopos distintos e
ambiguidade de calibração. Nenhum desses estados modifica os rasters ou as matrizes.
Há evidência suficiente para questionar a fidelidade anual das conversões nos
locais comparados; não há suporte para estimar quantos hectares municipais são
verdadeiros ou falsos, nem para descartar automaticamente os extremos.
