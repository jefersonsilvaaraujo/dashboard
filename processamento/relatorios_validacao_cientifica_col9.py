"""Relatórios A/B: tabelas reproduzíveis e notas explícitas da inspeção preliminar."""
import argparse
import json
from pathlib import Path
import sys

import pandas as pd

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from processamento.cenarios_validacao_col9 import csv_novo

NOTAS={
 'd_2102325_2001_6931_56309':'Landsat: cobertura visualmente vegetada em 2000–2002 e abertura no contexto em 2003; não resolve a data da conversão no par 2001→2002; lacunas SLC-off em 2003.',
 'd_2102325_2002_6453_56805':'Landsat: imagem 2003 com lacuna junto ao centro e 2004 com nuvens; par 2002→2003 inconclusivo neste ponto.',
 'd_2102325_2019_7690_56215':'Mudança de aspecto e abertura no contexto em 2020, compatível com conversão; tipo de uso e suporte completo do pixel exigem adjudicação.',
 'd_2102325_2021_7818_56397':'Mosaico de vegetação e talhões; abertura não inequívoca no centro em junho/2022; nuvens/sombras limitam dezembro. Inconclusivo.',
 'd_2102325_2022_7482_56626':'Abertura visível entre julho e dezembro/2023 no contexto central antes vegetado; compatível com mudança tardia. Pastagem e ano exato do estado anual ainda requerem validação.',
 'd_2102325_2022_7556_56653':'Controle com faixa vegetada no lote seco; fim de 2023 parcialmente encoberto. Permanência anual não certificada.',
 'd_2109908_2019_5961_59926':'Centro/contexto vegetado nas cenas consultadas; não há abertura inequívoca no ponto para 2019→2020. Não concluir falso positivo sem série intra-anual.',
 'd_2109908_2021_5265_60229':'Abertura central visível em dezembro/2022, ausente na cena de julho/2022; compatível com conversão tardia. Destino de uso ainda não adjudicado.',
 'd_2109908_2022_5543_60241':'Controle vegetado no lote seco; nuvens/sombras nos recortes de fim de ano impedem confirmar permanência.',
 'd_2109908_2022_5555_60257':'Abertura no contexto em dezembro/2023; cobertura mista e nuvens em dezembro/2022 impedem certificar o pixel completo e o destino.',
 'd_5103809_2019_49348_11023':'Borda de vegetação e campo aberto; névoa/fumaça em 2019. Diferença anual e natureza nativa/antrópica inconclusivas.',
 'd_5103809_2021_49245_10323':'Centro em remanescente/borda com vegetação visível até 2023; fim de 2021/2022 afetado por nuvens. Requer pixel completo e série temporal.',
 'd_5103809_2022_48903_10938':'Controle com vegetação visível em 2021–2023; continuidade visual compatível, sem certificação temática do pixel inteiro.',
 'd_5103809_2022_49261_10687':'Faixa vegetada estreita persiste junto ao centro até dezembro/2023; mistura com área aberta adjacente. Prioridade para auditar suporte/geolocalização e classe 3→15.',
 'd_5105507_1985_46567_5513':'Landsat 1985–1987 com baixa separação visual de coberturas naturais herbáceas/áreas manejadas; sazonalidade distinta. Não confirma o extremo municipal 1985→1986.',
 'd_5105507_1986_44937_4989':'Controle temporal subsequente: textura vegetada em 1985–1988; ausência de referência anterior a 1985 e resolução 30 m limitam o diagnóstico.',
 'd_5105507_2019_51351_6699':'Área herbácea com variação de cor, nuvens/sombra em 2019; natural versus pastagem inconclusivo sem referência de manejo.',
 'd_5105507_2021_46886_6511':'Mosaico aberto e vegetado, nuvens em dezembro/2021; não há evidência suficiente para atribuir conversão anual ao centro.',
 'd_5105507_2022_45993_5056':'Textura vegetada persiste no contexto; borda sem dados na janela e nuvens em dezembro/2022. Conversão 3→15 não inequívoca neste recorte.',
 'd_5105507_2022_47892_4394':'Controle em faixa vegetada/borda com área aberta; nuvens na origem. Permanência exata do pixel completo não adjudicada.',
 'd_5107107_2019_49692_12059':'Árvores dispersas/borda de campo, névoa/fumaça em 2019; não separa vegetação nativa e manejo com segurança.',
 'd_5107107_2021_49585_11766':'Centro em borda vegetada com campo aberto adjacente; nuvens na referência de fim de 2021. Conversão anual inconclusiva.',
 'd_5107107_2022_48689_12978':'Controle com cobertura vegetada no contexto em 2021–2023, inclusive dezembro; compatível com permanência, sem adjudicação independente.',
 'd_5107107_2022_49412_11562':'Centro/contexto vegetado persiste nas cenas até dezembro/2023; origem com névoa e possível pixel misto. Auditar 3→15 sem declarar erro automaticamente.'
}


def tabela(d,cols):
    def fmt(v):
        if pd.isna(v): return 'NA'
        if isinstance(v,float): return f'{v:.4f}'.replace('.',',')
        return str(v).replace('|','/')
    return '\n'.join(['| '+' | '.join(cols)+' |','|'+'|'.join(['---']*len(cols))+'|']+
        ['| '+' | '.join(fmt(r[c]) for c in cols)+' |' for _,r in d.iterrows()])


def executar(base,docs):
    a=docs/'RELATORIO_VALIDACAO_TEMATICA_COL9.md'; b=docs/'RELATORIO_COMPARACAO_LIMIARES_COL9.md'
    if a.exists() or b.exists(): raise FileExistsError('Relatórios anteriores preservados.')
    l=base/'limiares'; am=base/'amostragem'
    g=pd.read_csv(l/'comparacao_por_global.csv',sep=';')
    est=pd.read_csv(l/'comparacao_por_estado.csv',sep=';')
    anual=pd.read_csv(l/'comparacao_por_ano.csv',sep=';')
    principal=g[g.variante.eq('principal')]
    sens=g[g.Q_min_pct.eq(99.5)][['cenario','variante','n_eventos_candidatos','n_discordantes_principal','n_proximos_limite']]
    col=['cenario','Q_min_pct','n_avaliaveis','n_eventos_candidatos','proporcao_eventos_avaliaveis_pct','n_excluidos_qualidade','n_proximos_limite']
    ano=anual[anual.variante.eq('principal')&anual.Q_min_pct.eq(99.5)].pivot(index='ano_destino',columns='cenario',values='n_eventos_candidatos').reset_index()
    estado=est[est.variante.eq('principal')&est.Q_min_pct.eq(99.5)]
    texto=f'''# Comparação científica dos limiares candidatos — Coleção 9

11/11/2026. Etapa B executada nos 9.690 pares, preservando o acervo anterior.
Nenhum cenário foi homologado como Y, selecionado por balanceamento ou usado para treinar.

## Regras e denominadores

A: R≥0,25% **e** C≥25 ha; B: R≥0,50% **e** C≥100 ha;
C: R≥1,00% **e** C≥250 ha. R=100 C/D; D é a VN inicial no suporte comum.
Igualdade satisfaz o critério. Comparadas Q≥99,5%, 99,9% e 99,95%.
Q é a fração da VN inicial observada que permanece no suporte comum.
Ausência, D=0 ou qualidade insuficiente são não avaliáveis, não negativos.

Proporção entre avaliáveis = candidatos/avaliáveis; proporção no universo =
candidatos/total. Ambos os denominadores estão nos CSVs. A segunda medida não
transforma exclusões em negativos. Contagens municipais têm 38 oportunidades;
por UF/ano usam a quantidade efetiva de pares. São frequências de eventos
municipais mapeados, não percentuais da área regional.

Casos próximos: `abs(min(R/tau,C/A_min)−1)≤0,10`, entre avaliáveis. É uma faixa
de auditoria de ±10% relativa à fronteira conjunta, não incerteza estatística
nem tolerância para modificar o evento. CSVs incluem margens em ha e pontos percentuais.

## Resultado principal

{tabela(principal,col)}

A exclusão principal em 99,9%/99,95% é Buriticupu 2002→2003,
Q=99,70158117%. A máscara tripla mantém os resultados anteriores; essa
exclusão por cenário não apaga a observação nem certifica sua incorreção temática.

## Quantidade por ano de destino — principal, Q≥99,5%

{tabela(ano,['ano_destino','A','B','C'])}

As demais qualidades, proporções, proximidades e exclusões estão em
`{l/'comparacao_por_ano.csv'}`; 2.052 combinações ano/cenário/qualidade/classificação.

## Estados — principal, Q≥99,5%

{tabela(estado,['SIGLA_UF','cenario','n_total','n_eventos_candidatos','proporcao_eventos_avaliaveis_pct','n_proximos_limite'])}

Tabela completa por estado: `{l/'comparacao_por_estado.csv'}`.
Tabela por cada um dos 255 municípios: `{l/'comparacao_por_municipio.csv'}`,
com 13.770 combinações e as mesmas contagens/proporções/flags agregadas.
Não são substituídas por rankings dos extremos. As somas por ano, estado e
município foram conferidas contra as 54 linhas globais para todas as contagens.

## Sensibilidade de classificação — Q≥99,5%

{tabela(sens,list(sens.columns))}

29/32 ampliam a origem e alteram C, D e o estoque inicial usado em Q;
25 amplia somente o destino. A elegibilidade de cada variante foi recalculada
com os estoques por classe dos NPZs, sem reutilizar silenciosamente Q principal.
Há discordâncias mesmo quando o total líquido de candidatos permanece igual
(por exemplo B, +29): entradas e saídas podem se compensar. A taxonomia oficial
não foi alterada. Esses cenários não tornam 25 uso antrópico comprovado.

Arquivos detalhados: `casos_proximos.csv`, `exclusoes_qualidade.csv`,
`discordancias_classificacao.csv`, `medidas_sensibilidades_continuas.csv`.
Os estados exploratórios candidato/abaixo/não avaliável não são rótulos homologados
e devem ficar fora de qualquer X ou Y definitivo.

## Interpretação ambiental e recomendação

O limiar efetivo em hectares é `max(A_min,tau D/100)`. As áreas elegíveis em que
as duas condições se igualam são 10.000 ha (A), 20.000 ha (B) e 25.000 ha (C).
Na mediana de D=71.835,02 ha, os pisos efetivos são aproximadamente 179,59 ha,
359,18 ha e 718,35 ha. A descreve a perda de pelo menos 1/400 do estoque
e 25 ha; B, 1/200 e 100 ha; C, 1/100 e 250 ha por comparação anual.
Essas são interpretações operacionais, não padrões oficiais de relevância ecológica.

O piso é agregado no município: não garante uma mancha contínua, elimina erro
temático ou mede fragmentação, biodiversidade e conectividade. A mesma perda
relativa pode ter impactos diferentes entre formações florestais, savânicas,
campestres e alagáveis. A prioridade ambiental deve ser vinculada a uma hipótese
explícita sobre perda de estoque e escala espacial, apoiada por referência independente.

Recomenda-se **manter A/B/C em avaliação**, sem hierarquia de vencedor. A reduz
o piso substantivo; C exige maior perda relativa/absoluta; B ocupa escala
intermediária. Nenhum é recomendado porque gera mais ou menos positivos.
As proporções acima dimensionam os cenários e não justificam sua escolha.
Antes de homologar: concluir respostas temáticas, avaliar incerteza perto de
cada fronteira, justificar a escala ambiental e decidir o tratamento dos
casos ambíguos. A inspeção dirigida encontrou heterogeneidade e não autoriza
certificar nenhum dos três cenários para treinamento neste checkpoint.

## Reprodução, testes e arquivos

`processamento/cenarios_validacao_col9.py` calcula os 54 cenários; a assinatura
de `concluido.json` anterior e os hashes municipais são conferidos antes da leitura.
`processamento/relatorios_validacao_cientifica_col9.py` gera este relatório.
Saídas novas em `{base}`. Testes de AND, igualdade, qualidade, D=0,
denominadores, proximidade e aninhamento em `testes/test_validacao_cientifica_col9.py`.
77 testes distintos passaram na regressão completa (61 principais +16 geoespaciais).
Nenhum banco, raster, CSV anterior, checkpoint ou dashboard foi substituído.
'''
    b.write_text(texto,encoding='utf-8')
    notas=pd.DataFrame([{'id':i,'observacao_preliminar':v,'interprete':'Codex; inspeção visual preliminar assistida por IA',
        'situacao':'requer_adjudicacao_independente','rotulo_referencia_homologado':False} for i,v in NOTAS.items()])
    csv_novo(notas,base/'inspecao_dirigida_notas.csv')
    h=pd.read_csv(am/'estratos.csv',sep=';')
    picos=pd.read_csv(base/'picos/conversao_por_ano_classe.csv',sep=';')
    picos=picos[picos.ano_destino.isin([2022,2023])].sort_values(['ano_destino','area_ha'],ascending=[True,False]).groupby('ano_destino').head(5)
    prioridade=pd.read_csv(base/'picos/serie_prioritarios_38_pares.csv',sep=';')
    prioridade=prioridade[prioridade.ano_origem.isin([2019,2021,2022])]
    texto=f'''# Validação temática das transições Coleção 9 — relatório preliminar

11/11/2026. **Etapa A executada como desenho/sorteio, levantamento de referência
e inspeção preliminar dirigida. A validação temática representativa permanece
aberta: não há acurácia estimada nem referência homologada para as 3.744 unidades
probabilísticas.** Nenhuma conversão consolidada foi corrigida ou removida.

## Acervo e independência

Foi inventariada a pasta indicada pelo pesquisador `D:/mestrado/Mapas-Estudo`,
incluindo os índices dos ZIPs sem extração. Inventário ativo:
`{base/'inventario_mapas_estudo_v2.json'}`: 161 arquivos, 59 metadados AppleDouble,
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

Obtidos **{len(h)} estratos não vazios**, **234 município–transições**,
até dois por estrato; **{int(h.N_psu.eq(h.n_psu).sum())} estratos censitários**.
Estratos unitários são censo, não amostras de tamanho um para estimar variância.
Probabilidade de primeiro estágio varia de {h.pi_psu.min():.8f} a 1.

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
de fim de ano. Notas por ID: `{base/'inspecao_dirigida_notas.csv'}`.
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

{tabela(picos,['ano_destino','classe_origem','classe_destino','area_ha','participacao_conversao_anual_pct'])}

Códigos: 3 formação florestal, 4 formação savânica, 6 floresta alagável,
11 campo alagado/área pantanosa, 12 formação campestre; 15 pastagem e 21 mosaico
de usos. A hierarquia oficial Col9 está preservada em `referencias/legenda_col9.csv`.
Não se atribui causalidade a essa decomposição.

Controles municipais e picos recentes:

{tabela(prioridade,['NM_MUN','ano_destino','taxa_conversao_pct','area_convertida_ha','origem_dominante','destino_dominante'])}

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
'''
    a.write_text(texto,encoding='utf-8')
    print(f'Relatórios criados: {a}, {b}')


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__); p.add_argument('--base',type=Path,required=True)
    p.add_argument('--docs',type=Path,required=True); a=p.parse_args(); executar(a.base,a.docs)
