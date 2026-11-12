"""Verificação independente e exploração das transições, sem alvo binário/modelo."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

import numpy as np
import pandas as pd

PROJETO=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(PROJETO))
from processamento.transicoes_col9 import CLASSES,selecionar,POLITICA
from processamento.manifesto_transicoes_col9 import sha256

METRICAS=['taxa_conversao_pct','area_convertida_ha','vn_inicial_elegivel_ha',
          'elegibilidade_vn_pct','cobertura_comum_area_grade_pct']


def estatisticas(serie):
    s=serie.dropna()
    d={'n_observados':int(s.size),'n_na':int(serie.isna().sum()),'zeros':int(s.eq(0).sum())}
    if not len(s): return {**d,**{k:None for k in ['min','media','mediana','p01','p05','p10','p25','p75','p90','p95','p99','max']}}
    return {**d,'min':float(s.min()),'media':float(s.mean()),'mediana':float(s.median()),
            **{f'p{int(q*100):02d}':float(s.quantile(q,interpolation='linear')) for q in (.01,.05,.1,.25,.75,.9,.95,.99)},'max':float(s.max())}


def verificar(resultados):
    final=json.loads((resultados/'concluido.json').read_text(encoding='utf-8'))
    for nome,h in final['artefatos'].items():
        if sha256(resultados/nome)!=h: raise ValueError(f'Artefato divergente: {nome}')
    qa=pd.read_csv(resultados/'metricas_municipio_ano.csv',encoding='utf-8-sig')
    if len(qa)!=255*38 or qa.duplicated(['CD_MUN','ano_origem']).any(): raise ValueError('Esperados 9.690 pares únicos.')
    if not qa.ano_destino.eq(qa.ano_origem+1).all(): raise ValueError('Par de anos não consecutivo.')
    vn=selecionar(POLITICA['vegetacao_nativa']); ua=selecionar(POLITICA['usos_antropicos'])
    with np.load(resultados/'matrizes_completas_255.npz',allow_pickle=False) as m:
        if not np.array_equal(m['classes'],CLASSES) or m['pixels'].shape!=(255,38,29,29): raise ValueError('Contrato das matrizes completas divergente.')
        if not np.array_equal(m['anos'],np.arange(1985,2024)): raise ValueError('Eixo temporal divergente.')
        c=m['pixels']; a=m['area_ha']; codigos=m['CD_MUN']
        if (c<0).any() or (a<0).any() or not np.isfinite(a).all(): raise ValueError('Valores inválidos nas matrizes.')
        q=qa.set_index(['CD_MUN','ano_origem']).reindex(pd.MultiIndex.from_product([codigos,np.arange(1985,2023)]))
        np.testing.assert_array_equal(c.sum(axis=(-2,-1)).ravel(),q.pixels_comuns.to_numpy())
        np.testing.assert_allclose(a.sum(axis=(-2,-1)).ravel(),q.area_comum_ha.to_numpy(),rtol=0,atol=.0001)
        convertido=a[:,:,vn,:][:,:,:,ua].sum(axis=(-2,-1)).ravel()
        elegivel=a[:,:,vn,:].sum(axis=(-2,-1)).ravel()
        np.testing.assert_allclose(convertido,q.area_convertida_ha.to_numpy(),rtol=0,atol=.0001)
        np.testing.assert_allclose(elegivel,q.vn_inicial_elegivel_ha.to_numpy(),rtol=0,atol=.0001)
        esperado=np.divide(100*convertido,elegivel,out=np.full_like(convertido,np.nan),where=elegivel>0)
        np.testing.assert_allclose(esperado,q.taxa_conversao_pct.to_numpy(),rtol=0,atol=1e-9,equal_nan=True)
        i27=int(np.flatnonzero(CLASSES==27)[0])
        if c[:,:,i27,:].sum() or c[:,:,:,i27].sum(): raise ValueError('Não observado entrou como transição.')
    for cd in codigos:
        pasta=resultados/'municipios'/str(cd)
        ck=json.loads((pasta/'concluido.json').read_text(encoding='utf-8'))
        with np.load(pasta/ck['npz'],allow_pickle=False) as z:
            if (z['pixels'].sum(axis=2)>z['estoque_pixels'][:-1]).any(): raise ValueError('Marginal inicial excede estoque.')
            if (z['pixels'].sum(axis=1)>z['estoque_pixels'][1:]).any(): raise ValueError('Marginal final excede estoque.')
            if (z['area_ha'].sum(axis=2)>z['estoque_area_ha'][:-1]+.0001).any(): raise ValueError('Área marginal inicial excede estoque.')
            if (z['area_ha'].sum(axis=1)>z['estoque_area_ha'][1:]+.0001).any(): raise ValueError('Área marginal final excede estoque.')
            if cd==2102325:
                for i,j in enumerate((2001-1985,2002-1985)):
                    if (z['tripla_pixels'][i]>z['pixels'][j]).any(): raise ValueError('Máscara tripla não é subconjunto da máscara por par.')
                if z['tripla_pixels'][0].sum()!=z['tripla_pixels'][1].sum(): raise ValueError('Suporte triplo mudou entre os pares.')
    particao=qa.pixels_comuns+qa.pixels_so_inicial+qa.pixels_so_final+qa.pixels_invalidos_ambos
    if not particao.eq(qa.pixels_grade_municipio).all(): raise ValueError('Partição dos pixels não conserva a máscara municipal.')
    validacao=pd.read_csv(resultados/'validacao_estoques.csv',encoding='utf-8-sig')
    if validacao.erro_pixels.max()!=0 or validacao.erro_area_ha.max()>.0001: raise ValueError('Paridade de estoques falhou.')
    return qa,{'pares_verificados':len(qa),'municipios':int(qa.CD_MUN.nunique()),
               'estoques_municipio_ano':255*39,'erro_max_pixels_estoques':int(validacao.erro_pixels.max()),
               'erro_max_area_estoques_ha':float(validacao.erro_area_ha.max()),
               'conservacao_matrizes':True,'mascara_tripla_subconjunto':True,'hashes_artefatos':True}


def fmt(x,casas=4):
    if pd.isna(x): return 'NA'
    return f'{float(x):,.{casas}f}'.replace(',','_').replace('.',',').replace('_','.')


def tabela(df,colunas,casas=4):
    linhas=['| '+' | '.join(colunas)+' |','|'+'|'.join(['---']*len(colunas))+'|']
    for _,r in df.iterrows():
        campos=[]
        for c in colunas:
            v=r[c]
            if c.startswith('ano') or c.startswith('n_'): campos.append(str(int(v)) if pd.notna(v) else 'NA')
            elif isinstance(v,(float,np.floating,int,np.integer)): campos.append(fmt(v,casas))
            else: campos.append(str(v).replace('|','/'))
        linhas.append('| '+' | '.join(campos)+' |')
    return '\n'.join(linhas)


def explorar(resultados,relatorio):
    saida=resultados/'analise_exploratoria'
    if saida.exists() or relatorio.exists(): raise FileExistsError('Análise/relatório já existe; não sobrescrever.')
    qa,integridade=verificar(resultados)
    saida.mkdir()
    resumo={c:estatisticas(qa[c]) for c in METRICAS}
    stats=pd.DataFrame([{'metrica':c,**v} for c,v in resumo.items()])
    stats.to_csv(saida/'distribuicoes_globais.csv',sep=';',index=False,encoding='utf-8-sig')
    anual=[]; por_ano=[]; por_mun=[]
    for ano,g in qa.groupby('ano_destino',sort=True):
        d=g.vn_inicial_elegivel_ha.sum()
        anual.append({'ano_destino':ano,'n_pares':len(g),'area_convertida_ha':g.area_convertida_ha.sum(),
            'vn_elegivel_ha':d,'taxa_regional_razao_somas_pct':100*g.area_convertida_ha.sum()/d if d else np.nan,
            'taxa_mediana_municipal_pct':g.taxa_conversao_pct.median(),'taxa_p95_municipal_pct':g.taxa_conversao_pct.quantile(.95),
            'elegibilidade_min_pct':g.elegibilidade_vn_pct.min()})
        for c in METRICAS: por_ano.append({'ano_destino':ano,'metrica':c,**estatisticas(g[c])})
    for cd,g in qa.groupby('CD_MUN',sort=True):
        por_mun.append({'CD_MUN':cd,'NM_MUN':g.NM_MUN.iloc[0],'SIGLA_UF':g.SIGLA_UF.iloc[0],
            'taxa_mediana_pct':g.taxa_conversao_pct.median(),'taxa_p95_pct':g.taxa_conversao_pct.quantile(.95),
            'taxa_max_pct':g.taxa_conversao_pct.max(),'area_convertida_mediana_ha':g.area_convertida_ha.median(),
            'area_convertida_max_ha':g.area_convertida_ha.max(),'elegibilidade_min_pct':g.elegibilidade_vn_pct.min()})
    anual=pd.DataFrame(anual)
    anual.to_csv(saida/'resumo_anual.csv',sep=';',index=False,encoding='utf-8-sig')
    pd.DataFrame(por_ano).to_csv(saida/'distribuicoes_por_ano.csv',sep=';',index=False,encoding='utf-8-sig')
    pd.DataFrame(por_mun).to_csv(saida/'distribuicoes_por_municipio.csv',sep=';',index=False,encoding='utf-8-sig')
    top_col=['CD_MUN','NM_MUN','SIGLA_UF','ano_origem','ano_destino','taxa_conversao_pct','area_convertida_ha','vn_inicial_elegivel_ha','elegibilidade_vn_pct']
    top_taxa=qa.sort_values(['taxa_conversao_pct','area_convertida_ha'],ascending=False).head(30)[top_col]
    top_area=qa.sort_values(['area_convertida_ha','taxa_conversao_pct'],ascending=False).head(30)[top_col]
    top_taxa.to_csv(saida/'maiores_taxas.csv',sep=';',index=False,encoding='utf-8-sig')
    top_area.to_csv(saida/'maiores_areas.csv',sep=';',index=False,encoding='utf-8-sig')
    sens=[]
    for nome,suf in [('principal',''),('mais25','_mais25'),('mais29','_mais29'),('mais32','_mais32'),('mais29_32','_mais29_32'),('mais29_32_25','_mais29_32_25')]:
        c='taxa_conversao_pct' if not suf else f'taxa{suf}_pct'
        area='area_convertida_ha' if not suf else f'area_convertida{suf}_ha'
        delta=qa[c]-qa.taxa_conversao_pct
        sens.append({'cenario':nome,**estatisticas(qa[c]),'mediana_delta_taxa_pp':delta.median(),
                     'min_delta_taxa_pp':delta.min(),'max_delta_taxa_pp':delta.max(),
                     'conversao_somada_ha_evento':qa[area].sum()})
    sens=pd.DataFrame(sens)
    sens.to_csv(saida/'sensibilidade_classes_resumo.csv',sep=';',index=False,encoding='utf-8-sig')
    # Cenários lógicos da parte da VN inicial que fica fora da máscara comum.
    # Não são intervalos de confiança e não corrigem erro temático.
    qa['vn_inicial_excluida_ha']=(qa.vn_inicial_observada_ha-qa.vn_inicial_elegivel_ha).clip(lower=0)
    qa.loc[qa.elegibilidade_vn_pct.eq(100),'vn_inicial_excluida_ha']=0
    den=qa.vn_inicial_observada_ha.where(qa.vn_inicial_observada_ha>0)
    qa['taxa_min_cenario_mascara_pct']=100*qa.area_convertida_ha/den
    qa['taxa_max_cenario_mascara_pct']=100*(qa.area_convertida_ha+qa.vn_inicial_excluida_ha)/den
    qa['amplitude_cenario_mascara_pp']=100*qa.vn_inicial_excluida_ha/den
    qa[['CD_MUN','ano_origem','ano_destino','vn_inicial_excluida_ha','elegibilidade_vn_pct',
        'taxa_min_cenario_mascara_pct','taxa_max_cenario_mascara_pct','amplitude_cenario_mascara_pp']].to_csv(
        saida/'sensibilidade_mascara.csv',sep=';',index=False,encoding='utf-8-sig')
    candidatos=[]
    for tau in (.1,.25,.5,1.,2.):
        for amin in (5.,10.,25.,50.,100.):
            for qmin in (95.,99.,99.5,99.9,99.95):
                elegivel=qa.elegibilidade_vn_pct.ge(qmin)&qa.taxa_conversao_pct.notna()
                acima=elegivel&qa.taxa_conversao_pct.ge(tau)&qa.area_convertida_ha.ge(amin)
                cruza=elegivel&qa.taxa_min_cenario_mascara_pct.lt(tau)&qa.taxa_max_cenario_mascara_pct.ge(tau)
                candidatos.append({'tau_candidato_pct':tau,'A_min_candidato_ha':amin,'elegibilidade_min_candidata_pct':qmin,
                    'n_pares_com_elegibilidade_suficiente':int(elegivel.sum()),'n_pares_satisfariam_criterios':int(acima.sum()),
                    'n_pares_cenario_mascara_cruza_tau':int(cruza.sum()),
                    'elegibilidade_para_amplitude_mascara_tau_sobre2_pct':100-tau/2})
    pd.DataFrame(candidatos).to_csv(saida/'candidatos_limiares_contagens_agregadas.csv',sep=';',index=False,encoding='utf-8-sig')
    bur=qa[qa.CD_MUN.eq(2102325)&qa.ano_origem.isin([2001,2002])]
    trip=pd.read_csv(resultados/'buriticupu_mascara_tripla.csv',encoding='utf-8-sig')
    b=bur.merge(trip,on=['CD_MUN','ano_origem','ano_destino'],suffixes=('_par','_tripla'),validate='one_to_one')
    for c in ('pixels_comuns','area_comum_ha','area_convertida_ha','vn_inicial_elegivel_ha','taxa_conversao_pct'):
        b[f'delta_{c}']=b[f'{c}_tripla']-b[f'{c}_par']
    b.to_csv(saida/'buriticupu_pares_vs_tripla.csv',sep=';',index=False,encoding='utf-8-sig')
    resumo_json={'integridade':integridade,'distribuicoes':resumo,
        'taxa_regional_anual_min':anual.loc[anual.taxa_regional_razao_somas_pct.idxmin()].to_dict(),
        'taxa_regional_anual_max':anual.loc[anual.taxa_regional_razao_somas_pct.idxmax()].to_dict(),
        'elegibilidade':{str(v):{'n_abaixo':int(qa.elegibilidade_vn_pct.lt(v).sum()),'n_na':int(qa.elegibilidade_vn_pct.isna().sum())} for v in (95,99,99.5,99.9,99.95)},
        'amplitude_mascara_pp':estatisticas(qa.amplitude_cenario_mascara_pp),
        'sem_alvo_binario':True,'limiares_apenas_candidatos':True,
        'proveniencia':{'resultados':str(resultados.resolve()),'concluido_sha256':sha256(resultados/'concluido.json'),
                       'codigo_relatorio_sha256':sha256(Path(__file__))}}
    with (saida/'resumo.json').open('x',encoding='utf-8') as f: json.dump(resumo_json,f,ensure_ascii=False,indent=2,allow_nan=False)
    coltop=['NM_MUN','SIGLA_UF','ano_destino','taxa_conversao_pct','area_convertida_ha','vn_inicial_elegivel_ha','elegibilidade_vn_pct']
    texto=f'''# Relatório exploratório de transições espaciais Coleção 9

Status: resultados contábeis auditados para validação científica; nenhum tau,
A_min ou elegibilidade mínima definitiva foi adotado. Nenhum alvo binário ou modelo
foi produzido. Unidade temporal: par t→t+1, identificado pelo ano de destino.

## Cobertura e integridade

Foram calculados 255 municípios × 38 pares = **9.690 comparações**, entre 1985→1986
e 2022→2023. Matrizes completas 29×29, de pixels e hectares, preservam as demais
classes para auditoria. Zero/27/NoData não participam; a linha/coluna 27 permanece
zerada na matriz densa. O suporte é a máscara válida comum de cada par, sem reamostragem.

Os 9.945 estoques município–ano foram comparados ao consolidado aprovado:
erro máximo **{integridade['erro_max_pixels_estoques']} pixels** e
**{fmt(integridade['erro_max_area_estoques_ha'],8)} ha** por classe, compatível com o
arredondamento a quatro casas do consolidado. Soma de células, marginais, partições
de máscara e subconjunto triplo foram verificados independentemente.

O manifesto está em `referencias/manifesto_rasters_transicoes_col9.json`, com os
39 hashes, nomes, grades, NoData, origem, complemento e evidência de 2002. O raster
2002 validado é byte a byte idêntico ao alias usado no consolidado. A aprovação do
acervo e a validação amostral não são prova temática de todos os pixels dos 39 anos.

## Definição das medidas

VN inicial: 3,4,5,6,49,11,12,50. Destinos antrópicos: 9,15,20,21,24,30,31,35,
39,40,41,46,47,48,62. Área convertida C é a soma geodésica de VN(t)→UA(t+1).
Denominador D é a VN em t com observação válida nos dois anos. Taxa = 100 C/D;
denominador zero é NA, nunca evento negativo. Elegibilidade = 100 D/VN observada
inicialmente. A área de pixel varia com a latitude e foi calculada em WGS84.

As distribuições abaixo dão o mesmo peso a cada município–par observado. Elas
não são uma taxa regional por média simples: a taxa regional anual é calculada
separadamente por 100 soma(C)/soma(D). Quantis usam interpolação linear.

## Distribuições globais

{tabela(stats,['metrica','n_observados','n_na','min','p25','mediana','p75','p95','p99','max'])}

CSV completo: `{saida/'distribuicoes_globais.csv'}`. Distribuições por ano e por
município são fornecidas em arquivos próprios, com medianas, percentis e extremos.
Áreas somadas em anos diferentes representam hectares-evento e podem conter
reconversões do mesmo local; não equivalem a área territorial única.

## Maiores taxas municipais

{tabela(top_taxa.head(12),coltop)}

Taxas altas precisam ser lidas junto à VN elegível e à área absoluta: pequenos
denominadores podem gerar valores extremos sem grande conversão em hectares.

## Maiores áreas absolutas convertidas

{tabela(top_area.head(12),coltop)}

Os arquivos `maiores_taxas.csv` e `maiores_areas.csv` contêm as 30 maiores
comparações, com códigos IBGE e ambos os anos para rastreamento.

## Variação temporal

{tabela(anual,['ano_destino','area_convertida_ha','vn_elegivel_ha','taxa_regional_razao_somas_pct','taxa_mediana_municipal_pct','elegibilidade_min_pct'])}

Oscilações e anos extremos são achados para inspeção, não evidência causal de
desmatamento real nem autorização para remover observações. A máscara comum
controla ausência de observação, mas não elimina erro temático ou instabilidade
de classificação entre anos. Antes de modelar, examinar independentemente os
casos extremos e a coerência temporal dos mapas de origem/destino.

## Sensibilidade às classes 25, 29 e 32

{tabela(sens,['cenario','mediana','p95','max','mediana_delta_taxa_pp','min_delta_taxa_pp','max_delta_taxa_pp'])}

Incluir 25 como destino potencial aumenta o numerador, com denominador constante;
não transforma a classe 25 em uso antrópico comprovado. Incluir 29/32 no conjunto
inicial altera numerador **e** denominador e pode aumentar ou diminuir a taxa.
As versões principal, +29, +32, +29/32 e combinadas são cenários, sem consolidação
de uma nova definição operacional ou intervalo de confiança.

## Máscaras e Buriticupu

Elegibilidade da VN: mediana {fmt(resumo['elegibilidade_vn_pct']['mediana'],8)}%,
mínimo {fmt(resumo['elegibilidade_vn_pct']['min'],8)}%. A cobertura comum refere-se
à área da grade municipal por centro de pixel, não à diferença entre a área
cadastrada e a geodésica. Exclusões foram contadas diretamente nos rasters.

{tabela(b,['ano_origem','ano_destino','pixels_comuns_par','pixels_comuns_tripla','area_convertida_ha_par','area_convertida_ha_tripla','taxa_conversao_pct_par','taxa_conversao_pct_tripla','delta_taxa_conversao_pct'])}

`buriticupu_pares_vs_tripla.csv` inclui áreas e pixels excluídos, denominadores,
elegibilidade e diferenças entre os suportes. A máscara tripla usa apenas pixels
válidos em 2001, 2002 e 2003 para ambos os pares. Não se contabiliza 0→classe
como conversão. Se uma elevação persistir com a máscara tripla, ela não pode ser
atribuída automaticamente à diferença de suporte; requer inspeção temática.

Para toda a série foi calculado um cenário lógico: VN inicialmente observada que
fica fora da máscara comum pode ter convertido zero ou toda sua área. Sobre a
VN inicial completa, a amplitude desse cenário é 100 − elegibilidade, em pontos
percentuais. Isso não é intervalo de confiança e não inclui erro de classificação.
O arquivo `sensibilidade_mascara.csv` preserva os valores contínuos por comparação.

## Valores candidatos para discussão científica

Propõem-se **candidatos**, não parâmetros finais:

- tau: 0,10%, 0,25%, 0,50%, 1,00% e 2,00% da VN inicial elegível por ano.
- A_min: 5, 10, 25, 50 e 100 ha de conversão mapeada no município–par.
- Elegibilidade mínima: 95%, 99%, 99,5%, 99,9% e 99,95%; 95% é referência
  permissiva de sensibilidade, não recomendação automática para treino.

A grade cobre diferentes escalas relativas e absolutas para discutir relevância
ambiental e viabilidade de confirmação em referência independente. A_min reduz
a dependência de poucos pixels, mas não garante continuidade espacial nem elimina
erro temático. tau evita que apenas municípios grandes definam relevância; A_min
evita que uma área muito pequena produza evento por denominador diminuto.
Nenhum valor foi escolhido por prevalência, balanceamento ou desempenho de modelo.

Como critério adicional a discutir, limitar a amplitude do cenário de máscara a
no máximo tau/2 exigiria elegibilidade ≥ 100 − tau/2: 99,95% para tau=0,10%;
99,875% para 0,25%; 99,75% para 0,50%; 99,5% para 1%; e 99% para 2%.
É uma proposta de controle de incerteza por ausência de observação, não garantia
de estabilidade de rótulo ou de acurácia temática. Casos próximos ao limiar ainda
exigem revisão. O requisito precisa ser validado pelo pesquisador.

Para dimensionar a relevância, tau=0,50% corresponde a 5, 50 e 500 ha quando
D é 1.000, 10.000 e 100.000 ha, respectivamente. A_min=10 ha é um exemplo
para discussão, não uma escolha. A área é agregada no município: não exige
uma mancha contínua de 10 ha. A combinação simultânea de tau e A_min também
é uma hipótese a validar; grandes áreas absolutas com taxa pequena continuam
no relatório. Uma regra alternativa com critérios ligados por “ou” exigiria
decisão científica própria e nova análise.

`candidatos_limiares_contagens_agregadas.csv` contém somente frequências agregadas
dos cenários e quantos cenários de máscara atravessariam tau. Não contém Y nem
uma coluna binária por município–ano. Essas contagens dimensionam a revisão;
não são critério suficiente para escolher o evento científico.

As recomendações de [Olofsson et al. (2014)](https://doi.org/10.1016/j.rse.2014.02.015)
fundamentam a necessidade de referência independente, amostragem adequada e
avaliação de erro para áreas de mudança. Elas não fornecem tau/A_min para esta
dissertação. Estes resultados são áreas mapeadas, sem ajuste amostral de erro ou
intervalos de confiança. É necessário verificar os extremos, fronteiras de classe,
casos próximos aos candidatos e estratos município/ano antes de validar limiares.

## Preservação e próximos passos

Nenhum raster, tabela, view, CSV anterior ou resultado das Fases 1/2 foi substituído.
Os novos resultados estão em `{resultados}`; as matrizes densas estão em NPZ,
com os eixos de municípios, anos e classes incluídos e carregamento sem pickle.
As verificações/checkpoints por município permitem retomar sem substituir saídas.

Faltam validação temática independente e decisão científica dos candidatos.
Não houve geração de variável-alvo binária, treinamento ou escolha definitiva de
tau/A_min/elegibilidade mínima. A implantação das Fases 1/2 foi realizada em
atividade separada, após confirmação expressa, preservando banco e volume;
ver `docs/RELATORIO_IMPLANTACAO_COL9_20261111.md` para evidências e limitações.
'''
    with relatorio.open('x',encoding='utf-8') as f: f.write(texto)
    print(json.dumps({'integridade':integridade,'distribuicoes':resumo},ensure_ascii=False,indent=2))
    print(f'Relatório novo: {relatorio}',flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--resultados',type=Path,required=True); p.add_argument('--relatorio',type=Path,required=True)
    a=p.parse_args(); explorar(a.resultados,a.relatorio)
