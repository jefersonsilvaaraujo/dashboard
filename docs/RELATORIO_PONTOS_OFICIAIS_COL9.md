# Avaliação dos pontos oficiais da Coleção 9 nos 255 municípios

Data: 12/11/2026. Checkpoint: `validacao_cientifica_col9/oficial_col9_20261112_v1`.
Resultado: comparação computacional concluída; validação temática representativa **não estabelecida**.
Não houve interpretação humana própria, alteração das conversões ou homologação do desfecho.

## Fontes e versões efetivamente utilizadas

O CSV principal e o vetor auxiliar foram obtidos pelos links explicitamente rotulados
Coleção 9 na [página oficial de pontos](https://brasil.mapbiomas.org/downloads/pontos-de-validacao/).
A página declara CC BY 4.0. URL resolvida, data UTC, cabeçalhos HTTP, ZIP, conteúdo extraído
e SHA256 estão em `fontes/manifesto_download.json`. O nome legado `col2_1` identifica a
versão da referência, não uma autorização para substituir a coleção dos rasters.

| papel | arquivo | bytes | SHA256 |
|---|---|---|---|
| csv_zip | mapbiomas_85k_col2_1_points_w_edge_and_edited_v1.csv_-1.zip | 3283559 | 043c8bb9cff486c027e2022a55e32d61e10473df5dfde8df704351252fc63b82 |
| vetor_auxiliar_zip | mapbiomas_85k_points_validation.zip | 6695150 | ee7ce4e244be3255ddfbb7b96a7dc78389bfc10d44fff1c2d69599b2faacaddd |

CSV extraído: 85.152 IDs únicos, 135 colunas, sem código municipal, com classes **textuais**
de 1985–2023. Seu SHA256 é `e0ad3451ff3724ba05843946cbe84823b22016c5a4380ab1ff9452b2748f3d35`.
O vínculo foi registrado em 12/11/2026; o caminho da URL contém 2024, mas o cabeçalho
Last-Modified informa 14/08/2026. Isso não comprova que este conteúdo era disponível
historicamente em cada ano. A execução é retrospectiva.

O vetor tem 85.152 geometrias WGS84 e classes numéricas somente até 2022. Seus atributos
LON/LAT estão invertidos; a geometria coincide com as coordenadas do CSV a menos de
1,5e-14 grau. Não foram usadas essas colunas invertidas para localizar pontos.
As referências das duas versões divergem pontualmente no recorte, conforme
`avaliacao/divergencias_versoes_recorte_ano.csv`; as contagens de eventos coincidentes
até 2022 são iguais. O vetor acrescenta um par comparável sem evento. Não explica,
portanto, a baixa concordância anual das mudanças. Nenhuma versão preenche lacunas da outra.

O [apêndice de avaliação Col9, versão1, agosto2024](https://brasil.mapbiomas.org/wp-content/uploads/sites/4/2024/08/ACCURACY-ASSESSMENT-Appendix-Collection-9.pdf)
descreve sorteio por 127 grupos de cartas e seis faixas de declividade; informa uso de
10 mil pontos no treinamento amazônico e avaliação dos 75.152 restantes. Relata revisão
dos rótulos entre versões e referência até 2022. O arquivo baixado marca 9.999 pontos
como treinamento, inclusive pontos classificados pelos biomas do arquivo como Cerrado
e Pantanal. A diferença de um ID não foi resolvida por suposição.

## Recorte territorial e suporte espacial

Seleção por interseção das coordenadas com os 255 polígonos IBGE 2025 canônicos, com
verificação do SHA256 do GeoPackage e do WKB de cada município. Não há atribuições
múltiplas em limites. Foram selecionados 8.586 pontos em 253 municípios; 1.305 têm marcação
de treinamento e 7.281 não têm essa marcação. “Sem marcação” não comprova independência absoluta.

| SIGLA_UF | pontos | treinamento_marcado | sem_marcacao_treino |
|---|---|---|---|
| MA | 1452 | 222 | 1230 |
| MT | 4997 | 729 | 4268 |
| PA | 599 | 184 | 415 |
| RO | 336 | 84 | 252 |
| TO | 1202 | 86 | 1116 |

Municípios sem pontos: Buriti do Tocantins, Bernardo do Mearim.
Há 76 divergências em relação ao código municipal publicado no vetor; prevalece a
interseção com a geometria canônica. A tabela dos IDs divergentes foi preservada.
Um ponto está dentro do polígono, mas o centro da célula raster correspondente está
fora dele: não foi deslocado nem automaticamente eliminado. Dados de borda permanecem identificados.

Os 39 rasters foram abertos somente em leitura, nas grades do manifesto aprovado.
Tamanho/mtime e grade conferem; seus SHA256 já calculados permanecem referenciados
no manifesto. Não foi repetida a leitura integral de 159 GB para novos hashes nesta etapa.
A recuperação dos três municípios MA usa a mesma regra aprovada: somente zeros,
somente dentro do município, sem complemento para 2002. Não houve reamostragem.

As coordenadas oficiais apresentam deslocamento quase constante em relação ao centro
da célula exportada: dx≈−0,30825 e dy≈0,15869 pixel; distância≈0,34670 pixel, cerca de 10 m.
Essa constatação não demonstra qual grade estaria deslocada. A comparação principal
usa a célula que contém a coordenada, preservando-a; a vizinhança 3 × 3 é apenas sensibilidade.
Não se escolheu o vizinho que melhor concordasse com a referência.

## Legenda e critérios de comparação

VN: 3,4,5,6,49,11,12,50. UA: 9,15,20,21,24,30,31,35,39,40,41,46,47,48,62.
A referência contém lavouras agregadas 19/36: ambas pertencem ao grupo operacional UA,
sem atribuir-lhes uma subclasse terminal artificial. Vegetação urbana, classe 13,
rótulo corrompido, ausência e não observado não recebem grupo operacional presumido.
O dicionário original e a harmonização estão separados em `dicionario_harmonizacao.csv`.
A classe 21 não tem rótulo de referência explícito correspondente no CSV; pode haver
UA agrícola genérica, mas não é possível certificar especificamente o mosaico de usos.
Também não há base para uma acurácia terminal da restinga arbórea 49 por esse arquivo.

Um par é comparável se ambas as referências têm grupo conhecido e COUNT>0 e os dois
rasters têm classe válida. A ausência não é tratada como “sem conversão”.
COUNT 1/2/3 e BORDA são preservados; não foram convertidos em probabilidades de certeza.
O arquivo não traz os votos individuais necessários a estimar uma concordância
interintérpretes própria. Há coortes com/sem treinamento, sem borda e COUNT 3 nos dois anos.

## Cobertura temporal e principal lacuna

Em 2023 o CSV tem 4.053 classes preenchidas nacionalmente, de 85.152 pontos; no recorte
há somente uma, em Açailândia/MA (TARGETID 79521, COUNT 2). Nenhum dos cinco municípios
prioritários tem referência 2023. O vetor não tem esse ano. O único par local não
contém evento VN→UA de referência nem mapeado; não permite inferir precisão/sensibilidade
da conversão 2022→2023. **Ausência de referência não é evidência de ausência de conversão.**

Cobertura por ano, UF, município, classe, transição e estrato original foi exportada
nas tabelas `avaliacao/cobertura_*.csv`. Existem linhas para os 255 municípios no
inventário territorial, inclusive zeros; as comparações por ponto incluem todos os 38 intervalos.

## Concordância observada, sem estimativa populacional

Linhas=evento mapeado; colunas=evento na referência. TP=ambos positivos;
FP=apenas mapa positivo; FN=apenas referência positiva; TN=ambos negativos.
São denominações de **discordância com a referência publicada**, não adjudicação de
erro verdadeiro. Precisão=TP/(TP+FP); sensibilidade=TP/(TP+FN).

| coorte | n_pares | n_pontos | TP | FP | FN | TN | precisao_descritiva | sensibilidade_descritiva |
|---|---|---|---|---|---|---|---|---|
| todos | 317168 | 8585 | 1105.0000 | 2714.0000 | 1775.0000 | 311574.0000 | 0.2893 | 0.3837 |
| sem_marcacao_treino | 268981 | 7281 | 844.0000 | 2304.0000 | 1559.0000 | 264274.0000 | 0.2681 | 0.3512 |
| sem_treino_sem_borda | 247967 | 7047 | 774.0000 | 1998.0000 | 1378.0000 | 243817.0000 | 0.2792 | 0.3597 |
| sem_treino_count3_sem_borda | 158255 | 5181 | 394.0000 | 982.0000 | 295.0000 | 156584.0000 | 0.2863 | 0.5718 |

A coorte principal tem 268.980 pares até 2022 e um em 2023, repetidos nos mesmos 7.281
locais. As razões principais são 26,81% e 35,12%, respectivamente; a ponderação
exploratória pelos pesos publicados produz 26,73% e 34,96%. Nenhuma tem IC representativo.
A concordância binária global de 98,56% é dominada por TN e não demonstra boa detecção de conversão.

| ano_destino | n_pares | TP | FP | FN | TN | precisao_descritiva | sensibilidade_descritiva |
|---|---|---|---|---|---|---|---|
| 2019 | 7280 | 5.0000 | 55.0000 | 13.0000 | 7207.0000 | 0.0833 | 0.2778 |
| 2020 | 7279 | 15.0000 | 37.0000 | 7.0000 | 7220.0000 | 0.2885 | 0.6818 |
| 2021 | 7276 | 11.0000 | 42.0000 | 19.0000 | 7204.0000 | 0.2075 | 0.3667 |
| 2022 | 7259 | 7.0000 | 73.0000 | 14.0000 | 7165.0000 | 0.0875 | 0.3333 |
| 2023 | 1 | 0.0000 | 0.0000 | 0.0000 | 1.0000 | — | — |

Em 2022 são 7 coincidências de 80 conversões mapeadas comparáveis (8,75%) e 7 de 21 eventos
de referência (33,33%). Dois outros eventos mapeados em pontos sem treino nesse ano
não têm referência comparável. A concordância anual agregada de grupos VN/UA/outros
em 1985–2022 é 90,55%; ela não equivale à concordância das transições nem à precisão do
evento municipal. Não foram reutilizadas acurácias de outra coleção.

## Municípios prioritários

| CD_MUN | NM_MUN | pontos | treino | classes_ref2023 |
|---|---|---|---|---|
| 2102325 | Buriticupu | 43 | 14 | 0 |
| 2109908 | Santa Inês | 13 | 3 | 0 |
| 5103809 | Figueirópolis D'Oeste | 12 | 0 | 0 |
| 5105507 | Vila Bela da Santíssima Trindade | 153 | 48 | 0 |
| 5107107 | São José dos Quatro Marcos | 23 | 3 | 0 |

| NM_MUN | ano_destino | n_pontos | comparaveis | refVN | TP | FP | FN |
|---|---|---|---|---|---|---|---|
| Buriticupu | 2002 | 29 | 29 | 17 | 0 | 0 | 1 |
| Buriticupu | 2003 | 29 | 29 | 16 | 0 | 1 | 1 |
| Buriticupu | 2022 | 29 | 27 | 9 | 0 | 0 | 0 |
| Buriticupu | 2023 | 29 | 0 | 0 | 0 | 0 | 0 |
| Figueirópolis D'Oeste | 2002 | 12 | 12 | 0 | 0 | 0 | 0 |
| Figueirópolis D'Oeste | 2003 | 12 | 12 | 0 | 0 | 0 | 0 |
| Figueirópolis D'Oeste | 2022 | 12 | 12 | 0 | 0 | 0 | 0 |
| Figueirópolis D'Oeste | 2023 | 12 | 0 | 0 | 0 | 0 | 0 |
| Santa Inês | 2002 | 10 | 10 | 3 | 0 | 0 | 1 |
| Santa Inês | 2003 | 10 | 10 | 2 | 0 | 0 | 0 |
| Santa Inês | 2022 | 10 | 10 | 1 | 0 | 2 | 0 |
| Santa Inês | 2023 | 10 | 0 | 0 | 0 | 0 | 0 |
| São José dos Quatro Marcos | 2002 | 20 | 20 | 4 | 0 | 0 | 0 |
| São José dos Quatro Marcos | 2003 | 20 | 20 | 4 | 0 | 0 | 1 |
| São José dos Quatro Marcos | 2022 | 20 | 20 | 3 | 0 | 1 | 0 |
| São José dos Quatro Marcos | 2023 | 20 | 0 | 0 | 0 | 0 | 0 |
| Vila Bela da Santíssima Trindade | 2002 | 105 | 105 | 62 | 0 | 1 | 5 |
| Vila Bela da Santíssima Trindade | 2003 | 105 | 105 | 57 | 2 | 4 | 0 |
| Vila Bela da Santíssima Trindade | 2022 | 105 | 105 | 43 | 0 | 1 | 0 |
| Vila Bela da Santíssima Trindade | 2023 | 105 | 0 | 0 | 0 | 0 | 0 |

Figueirópolis D'Oeste não tem ponto de referência VN inicial comparável nas comparações
destacadas: os 12 pontos não cobrem adequadamente o remanescente responsável pelo
denominador. Nenhuma conversão observada nesses pontos não significa inexistência
municipal. Buriticupu tem referência para eventos distintos em 2001→2002 e 2002→2003;
a discordância entre suas localizações/anos não foi corrigida.

Consultar [inferência e limites](AVALIACAO_INFERENCIA_PONTOS_COL9.md) e
[auditoria temporal/externa](RELATORIO_CONSISTENCIA_REFERENCIAS_COL9.md).
