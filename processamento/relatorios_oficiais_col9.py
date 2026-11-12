"""Relatórios da avaliação oficial Col9, gerados de tabelas auditáveis e fontes arquivadas."""
import argparse
import json
from pathlib import Path
import re
import sys
import pandas as pd

PROJETO=Path(__file__).resolve().parents[1]
PASTA_DOCS=PROJETO/'docs'
sys.path.insert(0,str(PROJETO))


def ler(p):return pd.read_csv(p,sep=';',encoding='utf-8-sig',low_memory=False)


def tabela(df,cols=None):
    df=df if cols is None else df[cols]
    def fmt(x):
        if pd.isna(x):return '—'
        if isinstance(x,float):return f'{x:.4f}'
        return str(x).replace('|','/').replace('\n',' ')
    return '\n'.join(['| '+' | '.join(df.columns)+' |','|'+'|'.join(['---']*len(df.columns))+'|']+
                     ['| '+' | '.join(fmt(x) for x in row)+' |' for row in df.itertuples(index=False,name=None)])


def formatar_prosa(txt):
    """Espaçamento tipográfico sem alterar URLs, hashes, caminhos ou tabelas."""
    linhas=[]
    protegido=r'(`[^`]+`|\[[^\]]+\]\([^)]+\)|\b[A-Za-z0-9/]*_[A-Za-z0-9_/.]*\b|\bd\d{4}\b|\b\d+(?:[.,]\d+)?e[-+]?\d+\b|\b(?:log1p|SHA256|WGS84|F1)\b)'
    for linha in txt.splitlines():
        if linha.startswith('|'):
            linhas.append(linha);continue
        partes=re.split(protegido,linha)
        for i in range(0,len(partes),2):
            x=re.sub(r'(?<=[A-Za-zÀ-ÿ])(?=\d)',' ',partes[i])
            x=re.sub(r'(?<=\d)(?=[A-Za-zÀ-ÿ])',' ',x)
            x=re.sub(r'(?<=[:;])(?=\d)',' ',x)
            x=re.sub(r'\bdet\b','de t',x)
            x=re.sub(r'\bet\+','e t+',x)
            x=re.sub(r'\bemt\+','em t+',x)
            for antes,depois in [('emha','em hectares'),('emhectares','em hectares'),
                                 ('eR','e R'),('deR','de R'),('MAEha','MAE em hectares'),
                                 ('exportados,+por','exportados, por')]:
                x=x.replace(antes,depois)
            partes[i]=x
        linhas.append(''.join(partes))
    return '\n'.join(linhas).strip()+'\n'


def escrever(nome,txt):
    with (PASTA_DOCS/nome).open('x',encoding='utf-8') as f:f.write(formatar_prosa(txt))


def executar(raiz,saida_docs=None):
    global PASTA_DOCS
    if saida_docs is not None:
        PASTA_DOCS=saida_docs;PASTA_DOCS.mkdir(parents=True,exist_ok=True)
    a=raiz/'avaliacao';c=raiz/'complementar';d=raiz/'diagnosticos';s=raiz/'cenarios_evidencias'
    info=json.loads((a/'resumo_execucao.json').read_text(encoding='utf-8'))
    manifest=json.loads((raiz/'fontes/manifesto_download.json').read_text(encoding='utf-8'))
    cov=ler(a/'cobertura_255_municipios.csv');pts=ler(a/'pontos_selecionados.csv')
    estados=pts.groupby('SIGLA_UF').agg(pontos=('TARGETID','size'),treinamento_marcado=('AMOSTRA_AM','sum')).reset_index()
    estados['sem_marcacao_treino']=estados.pontos-estados.treinamento_marcado
    cg=ler(a/'concordancia_global.csv');cg=cg[cg.versao_referencia.eq('csv_principal')]
    ca=ler(a/'concordancia_ano.csv');ca=ca[ca.versao_referencia.eq('csv_principal')&ca.coorte.eq('sem_marcacao_treino')]
    cp=ler(a/'comparacoes_ponto_par.csv');cp=cp[cp.versao_referencia.eq('csv_principal')&cp.AMOSTRA_AM.eq(0)]
    pri=pts[pts.CD_MUN.isin([2102325,2109908,5103809,5105507,5107107])].groupby(['CD_MUN','NM_MUN']).agg(
        pontos=('TARGETID','size'),treino=('AMOSTRA_AM','sum'),classes_ref2023=('CLASS_2023','count')).reset_index()
    pr=cp[cp.CD_MUN.isin(pri.CD_MUN)&cp.ano_destino.isin([2002,2003,2022,2023])].copy()
    pr['refVN']=pr.comparavel&pr.ref_t.isin([3,4,5,6,49,11,12,50])
    pr['TP']=pr.comparavel&pr.evento_mapa&pr.evento_referencia
    pr['FP']=pr.comparavel&pr.evento_mapa&~pr.evento_referencia
    pr['FN']=pr.comparavel&~pr.evento_mapa&pr.evento_referencia
    pr=pr.groupby(['NM_MUN','ano_destino']).agg(n_pontos=('TARGETID','size'),comparaveis=('comparavel','sum'),
        refVN=('refVN','sum'),TP=('TP','sum'),FP=('FP','sum'),FN=('FN','sum')).reset_index()
    csv_nacional=ler(a/'cobertura_nacional_ano.csv')
    arquivos=pd.DataFrame([{'papel':f['papel'],'arquivo':f['arquivo'],'bytes':f['bytes'],
        'SHA256':f['sha256']} for f in manifest['fontes']])
    pesos=ler(a/'estratos_originais_nacionais_recorte.csv')
    isolados=pesos.query('n_nacional<2 and n_recorte>0')
    flux=ler(c/'fluxos_regionais_por_ano.csv')
    temporal=ler(a/'auditoria_temporal_pontos.csv');conv=temporal[temporal.conversao&temporal.AMOSTRA_AM.eq(0)]
    per=conv.groupby('ano_destino').agg(conversoes_pontos=('TARGETID','size'),
        com_t2=('persiste_UA_t2',lambda x:int((x>=0).sum())),
        persistem_UA=('persiste_UA_t2',lambda x:int((x==1).sum())),
        retornam_VN=('reverte_VN_t2',lambda x:int((x==1).sum()))).reset_index()
    lag=ler(d/'sensibilidade_datacao.csv').groupby('janela_mais_menos_anos')[
        ['n_conversoes_mapa_com_janela_ref_observada','n_com_evento_ref_na_janela']].sum().reset_index()
    lag['fracao_coincidente']=lag.n_com_evento_ref_na_janela/lag.n_conversoes_mapa_com_janela_ref_observada
    prodes=ler(c/'confronto_PRODES_conversoes_pontos.csv');prodes=prodes[prodes.AMOSTRA_AM.eq(0)]
    prodes_agg=prodes.groupby('confronto_PRODES').size().rename('n_pares_ponto').reset_index()
    rad=ler(raiz/'radiometria/NDVI_pares_hipoteses.csv')
    cs=ler(s/'cobertura_cenarios_global.csv');cs=cs[cs.Q_min_pct.eq(99.5)].copy()
    cs['prevalencia_mapeada_pct']=100*cs.n_candidatos/cs.n_pares
    last=ler(s/'cobertura_cenarios_ano.csv').query('Q_min_pct==99.5 and ano_destino>=2022')
    antigo=ler(PROJETO/'validacao_cientifica_col9/checkpoint_20261111/limiares/comparacao_por_global.csv')
    antigo=antigo[antigo.Q_min_pct.eq(99.5)]
    texto_pontos=f'''
# Avaliação dos pontos oficiais da Coleção 9 nos 255 municípios

Data: 12/11/2026. Checkpoint: `validacao_cientifica_col9/oficial_col9_20261112_v1`.
Resultado: comparação computacional concluída; validação temática representativa **não estabelecida**.
Não houve interpretação humana própria, alteração das conversões ou homologação do desfecho.

## Fontes e versões efetivamente utilizadas

O CSV principal e o vetor auxiliar foram obtidos pelos links explicitamente rotulados
Coleção 9 na [página oficial de pontos](https://brasil.mapbiomas.org/downloads/pontos-de-validacao/).
A página declara CC BY4.0. URL resolvida, data UTC, cabeçalhos HTTP, ZIP, conteúdo extraído
e SHA256 estão em `fontes/manifesto_download.json`. O nome legado `col2_1` identifica a
versão da referência, não uma autorização para substituir a coleção dos rasters.

{tabela(arquivos)}

CSV extraído: 85.152 IDs únicos, 135 colunas, sem código municipal, com classes **textuais**
de 1985–2023. Seu SHA256 é `{manifest['fontes'][0]['csv_sha256']}`.
O vínculo foi registrado em 12/11/2026; o caminho da URL contém2024, mas o cabeçalho
Last-Modified informa14/08/2026. Isso não comprova que este conteúdo era disponível
historicamente em cada ano. A execução é retrospectiva.

O vetor tem 85.152 geometrias WGS84 e classes numéricas somente até2022. Seus atributos
LON/LAT estão invertidos; a geometria coincide com as coordenadas do CSV a menos de
1,5e-14 grau. Não foram usadas essas colunas invertidas para localizar pontos.
As referências das duas versões divergem pontualmente no recorte, conforme
`avaliacao/divergencias_versoes_recorte_ano.csv`; as contagens de eventos coincidentes
até2022 são iguais. O vetor acrescenta um par comparável sem evento. Não explica,
portanto, a baixa concordância anual das mudanças. Nenhuma versão preenche lacunas da outra.

O [apêndice de avaliação Col9, versão1, agosto2024](https://brasil.mapbiomas.org/wp-content/uploads/sites/4/2024/08/ACCURACY-ASSESSMENT-Appendix-Collection-9.pdf)
descreve sorteio por127 grupos de cartas e seis faixas de declividade; informa uso de
10 mil pontos no treinamento amazônico e avaliação dos75.152 restantes. Relata revisão
dos rótulos entre versões e referência até2022. O arquivo baixado marca9.999 pontos
como treinamento, inclusive pontos classificados pelos biomas do arquivo como Cerrado
e Pantanal. A diferença de um ID não foi resolvida por suposição.

## Recorte territorial e suporte espacial

Seleção por interseção das coordenadas com os255 polígonos IBGE2025 canônicos, com
verificação do SHA256 do GeoPackage e do WKB de cada município. Não há atribuições
múltiplas em limites. Foram selecionados8.586 pontos em253 municípios;1.305 têm marcação
de treinamento e7.281 não têm essa marcação. “Sem marcação” não comprova independência absoluta.

{tabela(estados)}

Municípios sem pontos: {', '.join(cov.loc[cov.n_pontos.eq(0),'NM_MUN'])}.
Há76 divergências em relação ao código municipal publicado no vetor; prevalece a
interseção com a geometria canônica. A tabela dos IDs divergentes foi preservada.
Um ponto está dentro do polígono, mas o centro da célula raster correspondente está
fora dele: não foi deslocado nem automaticamente eliminado. Dados de borda permanecem identificados.

Os39 rasters foram abertos somente em leitura, nas grades do manifesto aprovado.
Tamanho/mtime e grade conferem; seus SHA256 já calculados permanecem referenciados
no manifesto. Não foi repetida a leitura integral de159GB para novos hashes nesta etapa.
A recuperação dos três municípios MA usa a mesma regra aprovada: somente zeros,
somente dentro do município, sem complemento para2002. Não houve reamostragem.

As coordenadas oficiais apresentam deslocamento quase constante em relação ao centro
da célula exportada: dx≈−0,30825 e dy≈0,15869 pixel; distância≈0,34670pixel, cerca de10m.
Essa constatação não demonstra qual grade estaria deslocada. A comparação principal
usa a célula que contém a coordenada, preservando-a; a vizinhança3×3 é apenas sensibilidade.
Não se escolheu o vizinho que melhor concordasse com a referência.

## Legenda e critérios de comparação

VN:3,4,5,6,49,11,12,50. UA:9,15,20,21,24,30,31,35,39,40,41,46,47,48,62.
A referência contém lavouras agregadas19/36: ambas pertencem ao grupo operacional UA,
sem atribuir-lhes uma subclasse terminal artificial. Vegetação urbana, classe13,
rótulo corrompido, ausência e não observado não recebem grupo operacional presumido.
O dicionário original e a harmonização estão separados em `dicionario_harmonizacao.csv`.
A classe21 não tem rótulo de referência explícito correspondente no CSV; pode haver
UA agrícola genérica, mas não é possível certificar especificamente o mosaico de usos.
Também não há base para uma acurácia terminal da restinga arbórea49 por esse arquivo.

Um par é comparável se ambas as referências têm grupo conhecido e COUNT>0 e os dois
rasters têm classe válida. A ausência não é tratada como “sem conversão”.
COUNT1/2/3 e BORDA são preservados; não foram convertidos em probabilidades de certeza.
O arquivo não traz os votos individuais necessários a estimar uma concordância
interintérpretes própria. Há coortes com/sem treinamento, sem borda e COUNT3 nos dois anos.

## Cobertura temporal e principal lacuna

Em2023 o CSV tem4.053 classes preenchidas nacionalmente, de85.152 pontos; no recorte
há somente uma, em Açailândia/MA (TARGETID79521, COUNT2). Nenhum dos cinco municípios
prioritários tem referência2023. O vetor não tem esse ano. O único par local não
contém evento VN→UA de referência nem mapeado; não permite inferir precisão/sensibilidade
da conversão2022→2023. **Ausência de referência não é evidência de ausência de conversão.**

Cobertura por ano, UF, município, classe, transição e estrato original foi exportada
nas tabelas `avaliacao/cobertura_*.csv`. Existem linhas para os255 municípios no
inventário territorial, inclusive zeros; as comparações por ponto incluem todos os38 intervalos.

## Concordância observada, sem estimativa populacional

Linhas=evento mapeado; colunas=evento na referência. TP=ambos positivos;
FP=apenas mapa positivo; FN=apenas referência positiva; TN=ambos negativos.
São denominações de **discordância com a referência publicada**, não adjudicação de
erro verdadeiro. Precisão=TP/(TP+FP); sensibilidade=TP/(TP+FN).

{tabela(cg,['coorte','n_pares','n_pontos','TP','FP','FN','TN','precisao_descritiva','sensibilidade_descritiva'])}

A coorte principal tem268.980 pares até2022 e um em2023, repetidos nos mesmos7.281
locais. As razões principais são26,81% e35,12%, respectivamente; a ponderação
exploratória pelos pesos publicados produz26,73% e34,96%. Nenhuma tem IC representativo.
A concordância binária global de98,56% é dominada por TN e não demonstra boa detecção de conversão.

{tabela(ca[ca.ano_destino.ge(2019)],['ano_destino','n_pares','TP','FP','FN','TN','precisao_descritiva','sensibilidade_descritiva'])}

Em2022 são7 coincidências de80 conversões mapeadas comparáveis (8,75%) e7 de21 eventos
de referência (33,33%). Dois outros eventos mapeados em pontos sem treino nesse ano
não têm referência comparável. A concordância anual agregada de grupos VN/UA/outros
em1985–2022 é90,55%; ela não equivale à concordância das transições nem à precisão do
evento municipal. Não foram reutilizadas acurácias de outra coleção.

## Municípios prioritários

{tabela(pri)}

{tabela(pr)}

Figueirópolis D'Oeste não tem ponto de referência VN inicial comparável nas comparações
destacadas: os12 pontos não cobrem adequadamente o remanescente responsável pelo
denominador. Nenhuma conversão observada nesses pontos não significa inexistência
municipal. Buriticupu tem referência para eventos distintos em2001→2002 e2002→2003;
a discordância entre suas localizações/anos não foi corrigida.

Consultar [inferência e limites](AVALIACAO_INFERENCIA_PONTOS_COL9.md) e
[auditoria temporal/externa](RELATORIO_CONSISTENCIA_REFERENCIAS_COL9.md).
'''
    escrever('RELATORIO_PONTOS_OFICIAIS_COL9.md',texto_pontos)
    texto_consistencia=f'''
# Consistência temporal e confronto com referências externas — Col9

Data:12/11/2026. Série principal:1985–2023;255 municípios canônicos.
As matrizes originais permanecem intactas. Os resultados abaixo não constituem
novos rótulos de referência ou correções automáticas.

## Matrizes completas e estabilidade

Foram verificadas as9.690 matrizes e seus artefatos consolidados; os totais de VN→UA
recalculados das matrizes conferem com as métricas anteriores. Foram exportados, por município/par, estabilidade exata da classe, fluxo inverso UA→VN e destinos
pastagem, agricultura, mosaico e demais UA. Fluxo inverso agregado simultâneo não
prova reversão no mesmo pixel: tal afirmação requer trajetória de três anos.

{tabela(flux[flux.ano_destino.ge(2020)])}

Pastagem responde por88,09% da área convertida de2022 e83,52% de2023; agricultura
por1,92% e2,01%; mosaico por9,92% e14,41%. Os principais fluxos regionais são
3→15 (444.847,62ha em2022;530.199,08ha em2023), seguidos de4→15. Em2022 também
se destaca11→15; em2023,12→15 e4→21. Esses padrões orientam a investigação de
confusão temática e manejo; não comprovam causa ambiental ou erro de integração.

O [ATBD geral Col9 v2, setembro2024](https://brasil.mapbiomas.org/wp-content/uploads/sites/4/2025/02/ATBD-Collection-9-versao2-v2.pdf)
descreve filtros espaciais/temporais e regras de integração, inclusive regra envolvendo
MapBiomas Alerta e classe21 a partir de2019. Assim, persistência e concordância com
produtos empregados na integração não são validações independentes por si mesmas.
As matrizes desta dissertação derivam diretamente dos rasters anuais; não reproduzem
necessariamente o filtro espacial adicional dos produtos oficiais de transição.

## Trajetórias nos pontos oficiais

Em7.281 pontos sem marcação de treinamento foram examinados todos os38 pares,
classes anterior/posterior e a vizinhança3×3. Foram encontradas3.289 conversões
mapeadas;3.175 têm grupo válido emt+2,3.174 permanecem UA e nenhuma retorna VN
no ano seguinte. Um destino vai para outro grupo. Para2022→2023, t+2 não existe
na série autorizada;114 conversões desses pontos ficam censuradas, nunca negativas.
Os números são diagnósticos dos pontos; não áreas nem proporções representativas
de persistência de todos os pixels municipais.

{tabela(per[per.ano_destino.ge(2018)])}

A alta persistência é compatível com a própria filtragem do produto e não resolve
a baixa coincidência com a referência. Foi também auditada a presença de UA emt−1:
12 episódios mapeados têm esse padrão. Isso não significa que12 sejam erros de
classificação, pois reconversões reais e manejos podem existir.

## Datação, registro e categorias

Entre2.304 discordâncias de mapa positivo com referência comparável,1.412 têm UA
nos dois anos de referência e875 têm VN nos dois anos; as demais17 têm outros
percursos. Isso é compatível com defasagem de datação e/ou discordância temática,
sem escolher automaticamente a explicação. Foram exportadas as classes de cada caso.

{tabela(lag)}

As janelas±1/±2 anos aumentam a coincidência, mas alteram a pergunta; seus
denominadores também mudam por falta de referência em parte das janelas. As janelas
são truncadas no início/fim da série e nenhuma usa2024. Não se deslocou o ano
do evento para melhorar uma medida. A comparação exata continua principal.

A sensibilidade “alguma das9 células” tem1.210 TP e6.982 FP, precisão descritiva14,77%
e sensibilidade50,35%. A ampliação inclui suportes vizinhos e aumenta oportunidades
de coincidência; não melhora de modo inequívoco o diagnóstico nem autoriza corrigir
registro. Homogeneidade e BORDA permanecem como indicadores auxiliares.

As classes25/29/32 foram reavaliadas em referência e mapa. Incluir25 resulta em
871TP,2.354FP,1.536FN, precisão27,01% e sensibilidade36,19%;29/32 não alteram as
contagens de eventos nessa amostra. Isso não demonstra ausência de efeitos dessas
classes nas áreas municipais. A classe21 é operacionalmente UA, mas a referência
não permite validar sua subclasse terminal de mosaico separadamente.

## Buriticupu2001–2003 e controles

A máscara válida comum aos três anos foi conferida no NPZ anterior:2.852.945 pixels
por intervalo. O teste automatizado confirmou que C e D com essa máscara coincidem
com os valores consolidados de ambos os pares. C=5.843,61ha eR=3,06205% em2001→2002;
C=23.350,95ha eR=12,08391% em2002→2003. A elegibilidade VN é100% e99,701581%,
respectivamente. Essa auditoria de suporte não confirma a natureza temática da conversão
nem atribui automaticamente diferenças de área a NoData.

Dos29 pontos sem treino em Buriticupu, há uma mudança de referência em cada um dos
dois pares. Em2001→2002 o mapa não assinala evento nesses locais; em2002→2003 mapa
e referência assinalam um evento cada em pontos distintos:0TP,1FP,1FN. Os controles
de anos anteriores e subsequentes permanecem na tabela por ponto. Em2023 não há
referência local anual. A comparação espectral dirigida de2001→2002 registra
ΔNDVI≈−0,0144;2002→2003 tem distância sazonal99dias e fica inconclusiva.

## PRODES2023

Foi amostrado o raster legado `prodes_brasil_2023.tif`, sem abrir o produto2025
como referência desta etapa. SHA256 do TIFF, QML, grade, legenda e proveniência
estão em `complementar/proveniencia_PRODES2023.json`. A origem institucional é
[INPE/TerraBrasilis](https://terrabrasilis.dpi.inpe.br/downloads/); a URL exata e a
data do download original local não foram comprovadas e não foram inventadas.

O [INPE descreve o PRODES](https://data.inpe.br/biomasbr/prodes-monitoramento-anual-da-supressao-de-vegetacao-nativa/)
como monitoramento de supressão primária, com diferenças entre biomas. Seu ano de
observação, unidades mínimas, classes acumuladas e intervalos históricos podem
divergir das classes anuais de cobertura e das reconversões secundárias da Col9.
O confronto conserva d2000 como acumulado, códigos bienais como intervalos e±1ano
apenas como proximidade exploratória; não usa uma tolerância para declarar acerto anual.

{tabela(prodes_agg)}

Em2023 há9 coincidências de ano em114 conversões dos pontos sem treino e uma
proximidade de um ano. Os demais casos são históricos, outra cronologia ou escopos
incompatíveis. Isso não transforma os104 restantes em erros comprovados: a ausência
de incremento PRODES pode decorrer de vegetação secundária, suporte ou definição.
O mesmo vale para coincidências positivas: não certificam o destino pastagem/agricultura.

## Imagens Landsat/Sentinel: auditoria automatizada, sem interpretação adicional

Foram reutilizadas as cenas já selecionadas no checkpoint dirigido anterior:
84 combinações únicas local/ano,15 Landsat e69 Sentinel, em24 locais dos cinco
municípios prioritários, incluindo controles. Cinco repetições da mesma cena em
dois catálogos foram identificadas e deduplicadas por local/ano/ID, sem escolher
uma cena que concordasse melhor com a conversão. A tentativa inicial incompleta
foi preservada em `espectral/`; os dados finais são `espectral_v2/` e `radiometria/`.

Foram extraídos RED/NIR e QA, arquivados DN, transformações, interseção do footprint
Col9, URLs sem tokens e hashes. NDVI é média ponderada pela interseção espacial,
não classificação de uso. QA cobre o footprint inteiro; sazonalidade≤45dias e mesma
família de sensor são condições técnicas de comparação, sem validação de manejo.
QA_RADSAT, BRDF e atmosfera residual permanecem limitações. A calibração Landsat
segue os fatores da [USGS](https://www.usgs.gov/faqs/how-do-i-use-a-scale-factor-landsat-level-2-science-products).

Em38 cenas Sentinel o asset declara offset−0,1 enquanto o próprio item informa
`earthsearch:boa_offset_applied=true`. Aplicar literalmente o offset produz valores
negativos em parte das bandas vermelhas. Foi registrada a incompatibilidade local
e a [discussão no repositório do provedor](https://github.com/Element84/earth-search/issues/71).
A mudança de baseline e seus offsets também estão na
[documentação Copernicus](https://sentiwiki.copernicus.eu/web/s2-products).
Foram calculadas as hipóteses “offset já aplicado” e “asset literal”, sem escolher
por concordância. As comparações afetadas ficam inconclusivas até confirmação da
calibração pelo provedor/original; não foram confundidas com inexistência de imagens
ou com erro do MapBiomas. Esse conflito é específico do fornecedor das imagens auxiliares.

Após os critérios conservadores, apenas dois dos24 pares dirigidos têm proxy
comparável sem conflito: Buriticupu2001→2002 (−0,0144) e2019→2020 (−0,5779).
Os demais têm conflito radiométrico, sazonalidade ou QA. Mesmo os dois proxies
não adjudicam VN→UA nem sua relevância; são evidência espectral complementar.
Para os picos2022/2023, as hipóteses podem mostrar aumentos ou reduções, mas não
fornecem confirmação temática automática. Não houve nova interpretação visual.

O inventário dos320 recortes prévios do piloto foi reutilizado apenas para
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
'''
    escrever('RELATORIO_CONSISTENCIA_REFERENCIAS_COL9.md',texto_consistencia)
    texto_inferencia=f'''
# Possibilidade de inferência estatística — pontos oficiais Col9

Data:12/11/2026. Decisão analítica desta execução: **somente diagnósticos descritivos**.
Não se estimaram acurácias representativas, área corrigida por erro ou IC populacionais.
O desenho nacional é probabilístico; isso não garante a validade automática de
qualquer subconjunto de pontos, anos, classes ou municípios.

## O que foi verificado

No arquivo completo há85.152 IDs únicos e756 estratos observados CARTA_2×DECLIVIDAD.
PESO_AMOS e PROB_AMOS_ foram lidos com vírgula decimal; o produto é1 dentro de
erro numérico. O peso é constante em cada estrato. O recorte intercepta119
estratos,117 com algum ponto sem marcação de treino. Isso permite reconhecer a
estrutura, mas não demonstra que a probabilidade original seja a probabilidade
condicional do conjunto independente depois das exclusões e da não resposta.

Há143 estratos nacionais comn=1, dos quais{len(isolados)} têm ponto no recorte;
um desses pontos está marcado como treino. Mesmo antes das demais limitações,
a variância intrasestrato não pode ser estimada diretamente para esses estratos.
Não foi criada uma regra arbitrária de colapso nem um bootstrap iid para contornar isso.

O apêndice oficial registra10 mil pontos de treinamento; o arquivo identifica9.999.
Não foi localizada documentação suficiente das probabilidades do conjunto
remanescente para garantir que os pesos fornecidos continuem corretos após remover
os marcados. Não se presume que a diferença de um ID não tenha efeito.

Além disso, a disponibilidade2023 é seletiva:4.053 classes nacionais e apenas um
ponto local. Não há mecanismo de não resposta/inclusão documentado para extrapolar
essa fração a255 municípios. Os rótulos agregados/ambíguos e filtros COUNT/BORDA
geram novos subconjuntos, que não podem ser tratados como sorteio simples sem evidência.

## Estimação de domínio e pesos: o que seria necessário

Pesos nacionais podem, em princípio, servir à estimação de domínio municipal ou
regional quando o desenho e a inclusão estão documentados. Não se exige uma
amostra municipal separada por definição. Deve-se trabalhar com o desenho nacional
completo e o indicador de domínio I_D; unidades fora do domínio contribuem zero.
Não se renormalizam pesos por município apenas para reproduzir sua área territorial.

Sob sorteio estratificado simples realmente válido, um total de célula de erro
seria estimado por soma_h (N_h/n_h) soma_i I_D(i) I_célula(i). Precisão e
sensibilidade seriam razões desses totais, com variância de razão por
linearização/replicação estratificada e correções de população finita apropriadas.
Seriam necessários N_h/unidade populacional, probabilidades válidas, tratamento
documentado da retirada para treino, da não resposta e dos estratos isolados.
Essas condições **não foram verificadas integralmente** para nosso desfecho/domínio.

Os mesmos pontos reaparecem em38 comparações:268.981 pares comparáveis não são
268.981 unidades independentes. Uma avaliação conjunta deve somar a contribuição
temporal dentro de cada ID e respeitar sua inclusão e estrato no cálculo de
variância. Bootstrap por linha ponto-ano, IC binomial simples e multiplicação
de amostra por38 produziriam precisão artificial. Tampouco independência espacial
entre pontos implica independência dos anos ou dos erros de um pixel persistente.

## Produtos permitidos e interpretação

Foram disponibilizadas matrizes binárias de frequências e somas de pesos publicados,
mais razões **descritivas**. Os pesos não foram calibrados para o recorte nem
convertidos em hectares corrigidos. Os resultados ponderados são uma sensibilidade,
sem reivindicar inferência válida. Não há IC nos arquivos; a ausência é deliberada.

Nenhum ponto em dois municípios, poucos pontos VN nos remanescentes de outros,
eventos raros e referências ausentes impedem afirmações municipais robustas.
“Sem evento na amostra” não significa “sem evento municipal”. A validação original
de classes gerais não foi dimensionada especificamente para nosso evento VN→UA,
e a amostra adicional de classes raras descrita pelo produtor não foi presumida
como parte desse CSV nem fundida aos85.152 pontos.

Três distinções de independência são necessárias: ausência de uso explícito no
treinamento, independência da interpretação e independência do insumo/sistema.
Excluir os marcados melhora a primeira, mas não comprova as demais. A referência
e o mapa compartilham sensores/imagens e o conjunto foi revisado ao longo das
coleções; a identificação individual de treinamento/participação em revisões é incompleta.
Não se declara circularidade universal, nem independência absoluta sem documentação.

## Pendências verificáveis

1. Esclarecer com a documentação do produtor a versão exata, o ID de treinamento
   não identificado e a cobertura2023, sem enviar mensagens em nome do pesquisador.
2. Obter informação de inclusão/retirada por estrato e mecanismo de atualização
   da referência; verificar a unidade dos pesos e a disponibilidade dos estratos.
3. Definir tratamento científico para estratos isolados e ausência temática/temporal,
   sem escolher procedimentos para favorecer resultados.
4. Só então avaliar a precisão necessária para o evento regional e para cada
   domínio municipal; municípios com suporte insuficiente continuarão sem estimativa.

Detalhes numéricos e condições estão em
`diagnosticos/avaliacao_suporte_inferencial.json`, com tabelas de estratos e IDs.
A continuidade desta estratégia prioriza documentação e fontes oficiais existentes;
não depende de novos pacotes de interpretação humana.
'''
    escrever('AVALIACAO_INFERENCIA_PONTOS_COL9.md',texto_inferencia)
    texto_desfecho=f'''
# Recomendação sobre o desfecho e cenários A/B/C — Col9

Data:12/11/2026. **Nenhum cenário homologado; nenhum modelo treinado.**
A evidência atual recomenda conservar C eR como medidas de conversão **mapeada**,
mantendo candidatos A/B/C apenas como hipóteses. Sua denominação não deve sugerir
conversão verdadeira confirmada, relevância ambiental demonstrada ou significância estatística.

## Critérios e cobertura da evidência

C é a área VN(t)→UA(t+1) na máscara válida comum; D é a VN inicial nessa mesma
máscara; R=100C/D; Q=100D/VN inicial observada. O evento candidato exige
simultaneamente R≥tau eC≥A_min, entre pares com D>0 eQ≥Q_min.
Q mede elegibilidade do suporte, não acurácia temática nem cobertura de validação.

A:tau0,25% e25ha; B:0,50% e100ha; C:1,00% e250ha.
As contagens anteriores foram conferidas, sem alterar matrizes:

{tabela(cs)}

EmQ99,9% e99,95%, cada cenário perde apenas Buriticupu2002→2003 por elegibilidade,
ficando9.314/8.756/7.284 candidatos em9.689 avaliáveis. Essa alteração não resolve
discordância temática de outros municípios ou falta de referência2023.
As prevalências altas não são motivo para elevar limiares visando balanceamento:
podem refletir pressão difundida, denominadores remanescentes, definição operacional
e erros/datação do produto em combinação. Não foi escolhida uma explicação única.

{tabela(last)}

Dos250 candidatos A de2023,249 não têm referência de par no município; para B são
244 de245 e para C221 de222. Ter um ponto comparável também não valida o agregado.
Para A/B/C,1.124/1.072/944 candidatos no conjunto não têm sequer ponto de referência
VN inicial comparável. As tabelas por município, UF e ano preservam os zeros e
explicitam essa cobertura, sem transformá-la em probabilidade de verdade do evento.

## Consequências das auditorias

No ano exato, a precisão descritiva entre pontos sem marcação de treino é26,81%
e a sensibilidade35,12%; em2022 a primeira cai a8,75%, com apenas21 eventos de
referência. Isso é evidência contrária à adoção imediata de uma etiqueta anual
de ocorrência verdadeira. Não é estimativa válida de erro da área municipal,
nem permite multiplicar C por26,81% para “corrigir” hectares.

Referências em anos próximos melhoram a coincidência, mas não confirmam horizonte
anual. A persistência do raster é alta e depende dos seus filtros. PRODES tem
escopo/calendário próprios; os proxies espectrais dirigidos são limitados por
calibração, sazonalidade e QA. Nenhuma dessas fontes autoriza homologar o cenário
C por ser mais restritivo, nem supor que A/B estejam ambientalmente errados.

As sensibilidades25/29/32 nas matrizes permanecem nos relatórios anteriores;
as novas comparações pontuais não mudam com29/32 e melhoram apenas marginalmente
com25. A ausência de efeito na amostra não comprova ausência territorial.
Comparação global original das variantes emQ99,5%:

{tabela(antigo,['cenario','variante','n_eventos_candidatos','n_discordantes_principal'])}

## Significado ambiental a decidir

O componente relativo representa a pressão sobre o estoque elegível remanescente;
o absoluto representa hectares municipais somados, que podem estar dispersos.
Nenhum dos dois mede sozinho integridade de habitat, conectividade, tipo de
formação, condição primária/secundária, permanência de uso ou consequências locais.
A_min não é área mínima de uma mancha e não deve ser equiparado à unidade mínima
de outro sistema. Tau não deve receber interpretação normativa/biológica sem hipótese.

A definição defensável precisa declarar a consequência de interesse: perda de uma
fração substantiva do remanescente, escala absoluta de transformação ou alteração
persistente de uso. O pesquisador poderá escolher uma definição substantiva mesmo
com prevalência elevada; a escolha deverá apoiar-se no processo ambiental e na
qualidade do desfecho, sem otimização por balanceamento ou resultados de modelos.

## Magnitude contínua como análise complementar

É viável especificar futuramente C(t,t+1) emha eR(t,t+1) em% como respostas contínuas
de **conversão mapeada**, retendo D,Q e o motivo de ausência. Isso preserva magnitude
e evita uma dicotomia ainda não fundamentada. Não elimina erros de classificação,
denominadores pequenos, assimetria, dependência espacial/temporal ou revisão retrospectiva.
Sugere-se avaliar C eR separadamente e conjuntamente com o suporte; log1p(C) pode
ser transformação pré-especificada, sem alterar as áreas originais ou substituir
o estimando sem discussão. Um valor ausente por suporte não vira zero.

Em eventual experimento autorizado, relatar erros nas unidades originais (MAEha,
erro percentual/pontos percentuais deR), calibração e comportamento por estoque,
UF e período. Toda transformação/normalização será ajustada apenas no treino.
Não há treinamento nem seleção de melhor resposta nesta entrega.

## Horizonte e protocolo retrospectivo preservados

Mantêm-se255 municípios,38 transições, previsores até o final det e desfecho
entre t et+1;2023 não recebe rótulo observado de t+1 e2024 permanece reservado.
Confirmar uma conversão emt+2 pode ser adjudicação posterior do evento t→t+1,
mas acrescenta um ano de disponibilidade da referência; redefinir o evento como
persistente emt+2 altera o desfecho. No segundo caso, somente t≤2021 é observável
dentro de1985–2023. A transição2022→2023 fica censurada, sem consultar2024.
Nenhum índice det+2 será previsor det. Não se selecionou critério de persistência.

O experimento segue retrospectivo, sem reivindicar disponibilidade operacional
histórica de todas as fontes. Mantêm-se validação temporal e leave-one-state-out;
os últimos anos e extremos já foram explorados e os testes não são completamente
cegos à formulação do desfecho. O protocolo anterior permanece preservado.

## Decisões que dependem de validação científica

1. Se o objetivo será ocorrência verdadeira relevante ou magnitude mapeada com
   incerteza explícita; uma eventual mudança de estimando exige aprovação.
2. Qual justificativa ambiental sustentaria tau/A_min, sem usar desempenho preditivo.
3. Como tratar o ano final sem referência e a discordância de datação, sem corrigir
   automaticamente a matriz nem deslocar anos para aumentar concordância.
4. Se persistência será apenas auditoria ou parte da definição, com censura/horizonte explícitos.
5. Como resolver proveniência/inclusão dos pontos e calibração dos auxiliares antes
   de qualquer afirmação representativa.

Recomendação atual: manter A/B/C em aberto; conservar as medidas contínuas para
auditoria e preparar apenas uma proposta complementar de regressão retrospectiva.
Não homologar Y nem iniciar treinamento definitivo com as evidências atuais.
'''
    escrever('RECOMENDACAO_DESFECHO_CENARIOS_COL9.md',texto_desfecho)
    texto_academico='''
# Texto para metodologia e limitações da dissertação — avaliação Col9

Versão12/11/2026. Texto proposto, condicionado à revisão científica do pesquisador.
Os valores abaixo descrevem a execução documentada; não devem ser apresentados
como acurácia populacional ou validação humana realizada pela dissertação.

## Metodologia

A pesquisa utiliza a Coleção9 do MapBiomas entre1985 e2023, em uma delimitação
fixa de255 municípios da zona de contato Cerrado–Amazônia, representados pelos
polígonos IBGE2025. As comparações anuais preservam a máscara comum de pixels
válidos e todas as categorias das matrizes de origem e destino. A vegetação
nativa operacional compreende as classes3,4,5,6,49,11,12 e50; os destinos de usos
antrópicos compreendem9,15,20,21,24,30,31,35,39,40,41,46,47,48 e62. A classificação
operacional da pesquisa é mantida separada da legenda oficial. Calculam-se a
área de conversão mapeada C, emhectares, a vegetação nativa inicial elegível D e
a taxa R=100C/D. Diferenças líquidas de estoque não substituem essas transições.

Para examinar sua qualidade temática, foram obtidos os arquivos vinculados à
Coleção9 na [página oficial de validação](https://brasil.mapbiomas.org/downloads/pontos-de-validacao/),
com registro de data, URL, licença e SHA256. A referência consiste em pontos
interpretados pelo produtor, com campos anuais de classe, concordância e borda.
Sua seleção para a área de estudo foi feita pelas coordenadas e pelos polígonos
canônicos, independentemente do código municipal eventualmente fornecido.
Foram identificados8.586 pontos em253 municípios, dos quais1.305 tinham marcação
de treinamento e foram excluídos da coorte principal. Os7.281 restantes foram
denominados “sem marcação de treinamento”, sem presumir independência absoluta.

Os valores dos39 rasters anuais foram extraídos na célula que contém cada
coordenada, sem reprojeção categórica, deslocamento para melhor ajuste ou
alteração das fontes. Classes de referência agrícola agregadas foram comparadas
no nível VN/UA/outros; categorias ambíguas e não observadas foram mantidas como
não comparáveis. Para cada par consecutivo, comparou-se a ocorrência VN→UA nas
referências e no mapa, incluindo pontos de todas as trajetórias válidas para
permitir examinar omissões e comissões. As contagens e razões são descritivas.
Foram realizadas sensibilidades por treinamento, COUNT, BORDA, classes25/29/32,
vizinhança espacial e coincidência em anos próximos, sem substituir a análise
do ano exato pela alternativa de maior concordância.

A auditoria complementar examinou fluxos inversos e estabilidade das matrizes,
trajetórias nos pontos, persistência emt+2 quando disponível até2023 e o suporte
comum aos três anos2001–2003 em Buriticupu. Foi realizado confronto espacial
com o PRODES2023 local, conservando as diferenças de escopo e de intervalo
temporal do sistema [INPE](https://data.inpe.br/biomasbr/prodes-monitoramento-anual-da-supressao-de-vegetacao-nativa/).
Em casos dirigidos anteriores, cenas Landsat/Sentinel foram submetidas a
verificação automatizada de QA e de NDVI ponderado pelo footprint do pixel,
sem nova interpretação humana ou geração de rótulos temáticos. Divergências
radiométricas foram registradas em hipóteses separadas e mantidas inconclusivas.

## Limitações e interpretação dos resultados

A concordância anual de grupos de cobertura nos pontos sem marcação de treino
foi90,55% em1985–2022. Entretanto, a coincidência das transições no ano exato
apresentou precisão descritiva26,81% e sensibilidade35,12%. A concordância
binária global98,56% é dominada pela abundância de pares sem evento e não
deve ser interpretada como alta capacidade de identificar conversões. Essas
medidas são comparações com a referência publicada, que também possui incerteza.

A referência2023 mostrou-se substancialmente incompleta: apenas um ponto
com classe preenchida dentro do recorte, enquanto o vetor auxiliar termina
em2022. Assim, não foi possível avaliar adequadamente a transição2022→2023
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
que o teste não é completamente cego à formulação do desfecho. O ano2024
permanece reservado e não foi utilizado. Nenhum desfecho binário foi homologado
e não houve treinamento definitivo nesta etapa.
'''
    escrever('TEXTO_METODOLOGIA_LIMITACOES_COL9.md',texto_academico)
    print('Cinco relatórios científicos gerados exclusivamente em arquivos novos.',flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--checkpoint',type=Path,required=True)
    p.add_argument('--saida-docs',type=Path)
    a=p.parse_args();executar(a.checkpoint,a.saida_docs)
