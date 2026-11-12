# Inventário de blocos e pendências
A base principal foi concluída sem depender da harmonização dos complementos.

| Bloco | Situação | Uso |
|---|---|---|
| Col9/histórico |harmonizado255×39|50 atributos sujeitos à análise temporal |
| Território básico |canônico2025|3 atributos estáticos |
| BiomasIBGE2019 |reinterseção executada,6 divergências de fechamento|tabela separada, fora de X |
| FocosINPE |21 ZIPs2003–2023 reintersectados|bloco separado, sem zeros presumidos |
| PRODES |TIFF/QML2023/2025 e CSV legado|bloqueio temporal/vintage/suporte para X |
| Área queimada |sem série local harmonizada identificada|fonte adicional, não substituída por focos |
| PAM/PPM/população/PIB |fontes oficiais identificadas|aquisição/vintage/território pendentes |
| Relevo/solo/infraestrutura/grafo |não harmonizados255|nenhuma variável criada/herdada268 |

## Biomas
| CD_MUN | NM_MUN | biomas_fechamento_area_pct |
|---|---|---|
| 2101707 | Barreirinhas | 99.7852 |
| 2105005 | Humberto de Campos | 99.8516 |
| 2107506 | Paço do Lumiar | 98.3363 |
| 2109452 | Raposa | 86.9906 |
| 2110278 | Santo Amaro do Maranhão | 99.7042 |
| 2111201 | São José de Ribamar | 99.2927 |

Não se atribuiu o desvio automaticamente ao mar, erro ou NoData nem se
normalizaram frações para 100%.0,1 ponto percentual é alarme de fechamento,
não elegibilidade temática. Interseções, frações brutas e hashes do shapefile
estão emTERRITORIO_CANONICO_COL9.parquet eINTERSECOES_BIOMAS_CANONICOS_COL9.csv.

## Focos
835.818 registros de 2003–2023 foram reintersectados pelas coordenadas nos 255
polígonos. Não houve data inválida/fora do ano, duplicata exata, ID conflitante
ou atribuição múltipla nos arquivos auditados. Ao longo da série há registros
nos 255 municípios, com cobertura anual desigual. O legado 251/255 não foi
reutilizado para calcular o novo bloco.

O calendário éUTC conforme INPE: termina antes do corte local de t, mas
difere do ano civil local em suas bordas. Não há campo de satélite individual;
a referência/AQUA_M-T deriva da documentação/configuração, não de verificação
por detecção. Fonte: [FAQ INPE](https://data.inpe.br/queimadas/faq/).
Contagens são registros detectados, não fogo verdadeiro nem hectares queimados.

Mês sem linha ficaNA com motivo; meses com registros não medem completude
instrumental. 1985–2002 ficamNA. Shapefiles antigos, inclusive com início
em 31/janeiro, exigem auditoria de sensor/janela e não completam a série
automaticamente. FRP/chuva/risco condicionados a focos não foram integrados
nem tratados como clima médio municipal. O bloco não foi anexado ao X-base.

## PRODES e área queimada
Inventário registra arquivos/versões/tamanhos. Arquivos 2024 ou posteriores
foram apenas identificados por nome, sem seus valores. Nos CSVs legados
somente código e ano foram lidos para inventário, sem medidas 2024/2025.
O Brasil 2023 já auditado evita recorrer ao 2025, mas faltam proveniência
exata/vintage e dicionário de intervalos por bioma, máscaras e correspondência
temporal. Não propagar estoque 2023 para t nem assumir ausência de linha=zero.
Reinterseção futura deve conferir cobertura nos 255 limites; nenhuma taxa
PRODES substitui Y MapBiomas.

Área queimada exige fonte própria, como
[INPE AQ1km](https://terrabrasilis.dpi.inpe.br/queimadas/aq1km/), produto 30 m
ou MapBiomas Fogo com versão/grade/máscara documentadas. Foco não equivale
a cicatriz e coleção de Fogo não equivale à coleção de cobertura.

## Socioeconomia
[PAM5457](https://sidra.ibge.gov.br/tabela/5457): áreas plantada/destinada,
colhida e produção, com unidades/revisões por cultura.
[PPM3939](https://sidra.ibge.gov.br/tabela/3939): rebanhos por espécie;
não somar espécies indiscriminadamente.
[PIB5938](https://sidra.ibge.gov.br/tabela/5938): referência 2010, nominal,
com revisões/cobertura/deflator a definir. População: censos e estimativasIBGE,
com tabela/ano e data de publicação a conferir. Não foram adquiridos valores
nem inventadas datas efetivas de disponibilidade.

Integrar por código oficial, nunca aproximação de nomes. Emancipações e
limites históricos exigem correspondência aos 255 fixos; código igual não
comprova suporte territorial igual. Sem compatibilidade, manter bloqueio/NA,
sem rateio ou interpolação com dados futuros. Detalhes no inventário JSON.
