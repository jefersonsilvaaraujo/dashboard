"""Matriz CANDIDATA de regressão Col9. Sem estimadores, treino, banco ou deploy.

Todas as saídas são novas. Referência do fenômeno e dependência algorítmica do
produto são dimensões diferentes: construir janelas causais não desfaz filtros
temporais retrospectivos aplicados pelo produtor da Coleção9.
"""
import argparse
from datetime import datetime,timezone
import hashlib
import importlib.metadata
import json
from pathlib import Path
import sys

import geopandas as gpd
import numpy as np
import pandas as pd
from pyproj import Geod
from shapely.geometry.polygon import orient

PROJETO=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(PROJETO))
from processamento.cenarios_validacao_col9 import VN,UA,conferir_acervo,sha,csv_novo
from modelagem.contrato_matriz_col9 import divisao_temporal,divisao_loso

ANOS=tuple(range(1985,2024));CHAVES=['CD_MUN','ano_t']
GRUPOS={'vn':VN,'ua':UA,'pastagem':[15],
    'agricultura':[20,35,39,40,41,46,47,48,62],
    'formacoes_florestais':[3,5,6,49],'savanica':[4],'campestre':[12],
    'mosaico':[21],'classe25':[25],'classe29':[29],'classe32':[32],'classe33':[33]}
PROIBIDOS={'C_ha','D_ha','R_pct','Q_pct','Y','candidato','area_convertida_ha',
    'vn_inicial_elegivel_ha','taxa_conversao_pct','elegibilidade_vn_pct',
    'pixels_comuns','classe_t1','ano_t1','SIGLA_UF','NM_MUN'}
GEOD=Geod(ellps='WGS84')


def exigir_autorizacao_treinamento(*args,**kwargs):
    raise PermissionError('Etapa exclusiva de preparação: treinamento/otimização não autorizados. Exige nova decisão científica.')


def area_geodesica(g):
    if g.is_empty:return 0.
    if g.geom_type=='Polygon':return abs(GEOD.geometry_area_perimeter(orient(g,sign=1.))[0])/10000
    if hasattr(g,'geoms'):return sum(area_geodesica(p) for p in g.geoms)
    return 0.


def salvar(df,p):
    if p.exists():raise FileExistsError(str(p))
    p.parent.mkdir(parents=True,exist_ok=True)
    df.to_parquet(p,index=False,engine='pyarrow',compression='zstd')


def validar_X(x,catalogo):
    atributos={m['variavel'] for m in catalogo}
    if set(x)-set(CHAVES)!=atributos:raise ValueError('Colunas não correspondem ao catálogo aprovado para preparação.')
    if set(x)&PROIBIDOS or any(c.startswith(('qual_','alvo_','resposta_')) for c in x):
        raise ValueError('Desfecho/qualidade futura/agrupamento não permitido em X.')
    if x.duplicated(CHAVES).any():raise ValueError('Chaves duplicadas em X.')
    if not x.CD_MUN.str.fullmatch(r'\d{7}').all():raise ValueError('Código municipal não canônico.')
    for m in catalogo:
        if m['fim_fenomeno_offset']>0 or m['usa_mascara_desfecho_atual']:
            raise ValueError('Informação do fenômeno posterior a t em atributo.')
        if m['status_temporal'] not in ['permitido_em_principio','sujeito_a_analise']:
            raise ValueError('Atributo proibido/não classificado.')


def tendencia(s,k):
    centro=np.arange(k,dtype=float)-(k-1)/2
    return s.rolling(k,min_periods=k).apply(lambda v:float(v@centro/(centro@centro)),raw=True)


def construir_cobertura(estoques,passadas,geometria):
    """estoques: áreas por classe em cada ano; passadas: intervalos por ano de TÉRMINO."""
    x=estoques[CHAVES].copy();cat=[]
    def add(nome,v,unidade,formula,primeiro=1985,inicio_offset=0,fim_offset=0,fonte='estoques_col9',tipo='medida'):
        x[nome]=v
        cat.append({'variavel':nome,'bloco':'historico_cobertura','unidade':unidade,'formula':formula,
            'fonte_id':fonte,'colecao':'9','versao':'Coleção9,1985–2023, manifesto aprovado',
            'primeiro_ano_historico_suficiente':primeiro,'inicio_fenomeno_offset':inicio_offset,
            'fim_fenomeno_offset':fim_offset,'usa_mascara_desfecho_atual':False,
            'status_temporal':'sujeito_a_analise','dependencia_algoritmica_max_ano_conservadora':2023,
            'dependencia_futura':'Potencial: filtros/frequência/integração retrospectivos do produtor; efeito individual não determinado.',
            'publicacao_ou_revisao':'Col9 lançada2024; ATBDv2set2024. Data da extração local não equivale a disponibilidade histórica.',
            'data_publicacao_exata':None,'data_revisao_exata':None,'tipo':tipo,'selecionada_para_treino':False})
    classes=[c for c in estoques if c.startswith('area_classe_') and not c.endswith('_27')]
    classificada=estoques[classes].sum(axis=1,min_count=1)
    for nome,codigos in GRUPOS.items():
        area=estoques[[f'area_classe_{c}' for c in codigos]].sum(axis=1,min_count=1)
        add(f'mb_{nome}_t_ha',area,'ha',f'Soma de áreas das classes{codigos} somente em t')
        add(f'mb_{nome}_t_pct',100*area/classificada.replace(0,np.nan),'%',
            f'100 × área{nome}(t)/área classificada(t); inclui25/33 no denominador, exclui0/27/NoData')
    add('mb_area_classificada_t_ha',classificada,'ha','Soma de classes válidas somente em t')
    add('mb_pixels_validos_t',estoques.pixels_validos_t,'pixels','Soma de pixels de classes válidas do mapa t')
    grade=estoques.CD_MUN.map(geometria.set_index('CD_MUN').pixels_grade_municipio)
    area_fix=estoques.CD_MUN.map(geometria.set_index('CD_MUN').territorio_area_geodesica_ha)
    add('mb_pixels_sem_classe_valida_t',grade-estoques.pixels_validos_t,'pixels',
        'Pixels da grade canônica menos válidos somente em t; não atribui causa automaticamente a NoData')
    add('mb_cobertura_grade_t_pct',100*estoques.pixels_validos_t/grade,'%',
        '100 × pixels válidos(t)/pixels da grade fixa; sem máscara comum futura')
    add('mb_razao_classificada_territorial_t_pct',100*classificada/area_fix,'%',
        '100 × área classificada(t)/área geodésica fixa; pode exceder100 por suporte; sem truncamento')
    add('mb_diferenca_classificada_territorial_t_ha',classificada-area_fix,'ha',
        'Área classificada(t) menos área geodésica fixa; não é desmatamento/NoData')
    for variavel,unidade in [('mb_vn_t_ha','ha/ano'),('mb_vn_t_pct','pontos_percentuais/ano')]:
        delta=x.groupby('CD_MUN',sort=False)[variavel].diff()
        add(variavel.replace('_t_','_variacao_liquida_1ano_'),delta,unidade,
            f'{variavel}(t)−{variavel}(t−1); variação líquida, não transição',1986,-1)
    add('lacuna_variacao_liquida_1ano',x.ano_t.eq(1985),'booleano','Histórico t−1 inexistente na série',tipo='indicador_lacuna')
    p=passadas[CHAVES+['C_passada_ha','R_passada_pct']]
    p=x[CHAVES].merge(p,on=CHAVES,how='left',validate='one_to_one')
    for nome,col,unid in [('mb_conv_passada_ha','C_passada_ha','ha'),('mb_taxa_passada_pct','R_passada_pct','%')]:
        add(nome,p[col],unid,'Conversão histórica t−1→t, encerrada até t; não é o desfecho corrente',1986,-1,fonte='transicoes_col9_encerradas')
    add('lacuna_conversao_passada',p.C_passada_ha.isna(),'booleano','Sem intervalo anterior disponível',tipo='indicador_lacuna')
    for k in [3,5]:
        for base,unid in [('mb_vn_t_ha','ha/ano'),('mb_vn_t_pct','pontos_percentuais/ano')]:
            v=x.groupby('CD_MUN',sort=False)[base].transform(lambda s:tendencia(s,k))
            add(f'{base}_tendencia_{k}anos',v,unid,
                f'Inclinação descritiva por pesos fixos em t−{k-1}…t; janela completa, sem filtro centrado',1984+k,1-k)
        media=x.groupby('CD_MUN',sort=False).mb_vn_t_pct.transform(lambda s:s.rolling(k,min_periods=k).mean())
        add(f'mb_vn_pct_media_{k}anos',media,'%',f'Média municipal dos{k} estoques anuais encerrados em t',1984+k,1-k)
        for base,unid in [('mb_conv_passada_ha','ha'),('mb_taxa_passada_pct','%')]:
            v=x.groupby('CD_MUN',sort=False)[base].transform(lambda s:s.rolling(k,min_periods=k).mean())
            add(f'{base}_media_{k}anos',v,unid,f'Média de{k} conversões passadas com fim entre t−{k-1} e t',1985+k,-k,
                fonte='transicoes_col9_encerradas')
        add(f'lacuna_janela_estoque_{k}anos',x.ano_t.lt(1984+k),'booleano',
            'Janela completa de estoque não disponível; valores não imputados',tipo='indicador_lacuna')
        add(f'lacuna_janela_conversao_{k}anos',x.ano_t.lt(1985+k),'booleano',
            'Janela completa de conversões encerradas não disponível',tipo='indicador_lacuna')
    return x,cat


def territorio(m,matrizes,saida):
    gpkg=Path(m['base_dados'])/m['territorio']['arquivo']
    if sha(gpkg)!=m['territorio']['sha256']:raise ValueError('Território alterado.')
    g=gpd.read_file(gpkg);g.CD_MUN=g.CD_MUN.astype(str)
    esperado=json.loads((PROJETO/'referencias/territorio_col9_hashes.json').read_text(encoding='utf-8'))['geometrias_sha256_wkb_ndr']
    if set(g.CD_MUN)!=set(esperado):raise ValueError('Municípios fora do conjunto canônico.')
    for r in g.itertuples():
        if hashlib.sha256(r.geometry.wkb).hexdigest()!=esperado[r.CD_MUN]:raise ValueError('WKB divergente.')
    g=g.to_crs(4326).sort_values('CD_MUN').reset_index(drop=True)
    ref=g.to_crs(5880).geometry.representative_point().to_crs(4326)
    if not ref.covered_by(g.geometry).all():raise ValueError('Referência territorial fora do polígono.')
    tab=g[['CD_MUN','NM_MUN','SIGLA_UF']].copy()
    tab['territorio_area_geodesica_ha']=g.geometry.map(area_geodesica)
    tab['territorio_lon_referencia']=ref.x;tab['territorio_lat_referencia']=ref.y
    fonte=Path(m['base_dados'])/'biomas_ibge/lm_bioma_250.shp'
    b=gpd.read_file(fonte).to_crs(4326)
    if not b.is_valid.all() or not g.is_valid.all():raise ValueError('Geometrias inválidas; não reparar silenciosamente.')
    inter=[]
    for r in g.itertuples():
        for bi in b.itertuples():
            if not r.geometry.intersects(bi.geometry):continue
            ar=area_geodesica(r.geometry.intersection(bi.geometry))
            if ar>0:inter.append({'CD_MUN':r.CD_MUN,'bioma':bi.Bioma,'area_intersecao_ha':ar})
    inter=pd.DataFrame(inter)
    soma=inter.groupby('CD_MUN').area_intersecao_ha.sum().reindex(tab.CD_MUN).to_numpy()
    tab['biomas_fechamento_area_pct']=100*soma/tab.territorio_area_geodesica_ha
    tab['biomas_fechamento_fora_tolerancia_01pp']=abs(tab.biomas_fechamento_area_pct-100)>.1
    for nome,rotulo in [('amazonia','Amazônia'),('cerrado','Cerrado')]:
        ar=inter.loc[inter.bioma.eq(rotulo)].groupby('CD_MUN').area_intersecao_ha.sum()
        # Zero somente por interseção geométrica efetivamente vazia com camada completa.
        tab[f'territorio_fracao_{nome}_pct']=100*tab.CD_MUN.map(ar).fillna(0)/tab.territorio_area_geodesica_ha
    outros=inter.loc[~inter.bioma.isin(['Amazônia','Cerrado'])].groupby('CD_MUN').area_intersecao_ha.sum()
    tab['territorio_fracao_outros_biomas_pct']=100*tab.CD_MUN.map(outros).fillna(0)/tab.territorio_area_geodesica_ha
    fix=matrizes.groupby('CD_MUN').pixels_grade_municipio.agg(['nunique','first'])
    if fix['nunique'].ne(1).any():raise ValueError('Grade municipal não constante.')
    tab['pixels_grade_municipio']=tab.CD_MUN.map(fix['first'])
    csv_novo(inter,saida/'INTERSECOES_BIOMAS_CANONICOS_COL9.csv')
    salvar(tab,saida/'TERRITORIO_CANONICO_COL9.parquet')
    fontes={str(p):sha(p) for p in fonte.parent.glob(fonte.stem+'.*') if p.is_file()}
    prov={'geopackage':str(gpkg),'sha256_gpkg':sha(gpkg),'biomas_arquivos_sha256':fontes,
        'metodo_ponto':'representative_point em EPSG5880, transformado para4326; não é centróide/população',
        'area':'Geod WGS84, anéis orientados, hectares; consistente com processamento anterior',
        'fechamento_max_abs_pp':float(abs(tab.biomas_fechamento_area_pct-100).max()),
        'municipios_fechamento_fora_01pp':int(tab.biomas_fechamento_fora_tolerancia_01pp.sum()),
        'biomas_em_X_base':False,'nota_biomas':'Frações candidatas em tabela separada; nenhuma normalização ou fechamento forçado. Compatibilização pendente.'}
    # O bloco complementar não impede a matriz-base; não ocultar sobreposição/lacuna
    # entre vintages cartográficos nem transformar a área residual em novo bioma.
    base_tab=tab.drop(columns=[c for c in tab if c.startswith('territorio_fracao_') or c.startswith('biomas_')])
    return base_tab,prov


def executar(matrizes,saida):
    if saida.exists():raise FileExistsError('Usar novo checkpoint; nenhuma saída substituída.')
    q=conferir_acervo(matrizes);q.CD_MUN=q.CD_MUN.astype(str)
    saida.mkdir(parents=True);pasta=saida/'matriz';pasta.mkdir();(saida/'metadados').mkdir()
    mpath=PROJETO/'referencias/manifesto_rasters_transicoes_col9.json'
    m=json.loads(mpath.read_text(encoding='utf-8'))
    geo,provg=territorio(m,q,pasta)
    estoques=[];fontes_npz={}
    for cd in sorted(geo.CD_MUN):
        mun=matrizes/'municipios'/cd;ck=json.loads((mun/'concluido.json').read_text(encoding='utf-8'))
        for n,h in ck['artefatos'].items():
            if sha(mun/n)!=h:raise ValueError('Checkpoint municipal alterado.')
        with np.load(mun/ck['npz'],allow_pickle=False) as z:
            if z['anos'].tolist()!=list(ANOS):raise ValueError('Série diferente de1985–2023.')
            cl=z['classes'];ar=z['estoque_area_ha'];px=z['estoque_pixels']
            for j,a in enumerate(ANOS):
                linha={'CD_MUN':cd,'ano_t':a,'pixels_validos_t':int(px[j].sum())}
                linha.update({f'area_classe_{int(c)}':float(ar[j,i]) for i,c in enumerate(cl)})
                estoques.append(linha)
        fontes_npz[str(mun/ck['npz'])]=sha(mun/ck['npz'])
    est=pd.DataFrame(estoques).sort_values(CHAVES).reset_index(drop=True)
    # Conferência independente de todo estoque com CSV consolidado arredondado.
    cons=Path(m['base_dados'])/m['consolidado']['arquivo']
    if sha(cons)!=m['consolidado']['sha256']:raise ValueError('Consolidado alterado.')
    ref=pd.read_csv(cons,sep=';',encoding='utf-8-sig',dtype={'CD_MUN':str})
    pr=ref.pivot_table(index=['CD_MUN','ano'],columns='classe_cobertura',values='area_ha',aggfunc='sum').fillna(0)
    erro=0.
    for c in cl:
        valores=pr[c].reindex(pd.MultiIndex.from_frame(est[CHAVES])).to_numpy() if c in pr else np.zeros(len(est))
        erro=max(erro,float(np.max(abs(est[f'area_classe_{int(c)}'].to_numpy()-valores))))
    if erro>.0001:raise ValueError('Estoque não confere com CSV aprovado.')
    passadas=q[['CD_MUN','ano_destino','area_convertida_ha','taxa_conversao_pct']].rename(columns={
        'ano_destino':'ano_t','area_convertida_ha':'C_passada_ha','taxa_conversao_pct':'R_passada_pct'})
    x,cat=construir_cobertura(est,passadas,geo)
    for nome in [c for c in geo if c.startswith('territorio_')]:
        x[nome]=x.CD_MUN.map(geo.set_index('CD_MUN')[nome])
        cat.append({'variavel':nome,'bloco':'territorio','unidade':'ha' if nome.endswith('_ha') else ('graus' if 'referencia' in nome else '%'),
            'formula':'Área geodésica; ponto interior representativo; fração por interseção IBGE2019, conforme proveniência',
            'fonte_id':'geometrias_ibge_canonicas','colecao':None,'versao':'IBGE2025 e biomasIBGE2019, hashes locais',
            'primeiro_ano_historico_suficiente':1985,'inicio_fenomeno_offset':0,'fim_fenomeno_offset':0,
            'usa_mascara_desfecho_atual':False,'status_temporal':'permitido_em_principio',
            'dependencia_algoritmica_max_ano_conservadora':None,
            'dependencia_futura':'Convenção territorial estática retrospectiva; não representa divisão administrativa histórica.',
            'publicacao_ou_revisao':'Território2025 e biomas2019: vintages posteriores a parte da série; não variam por ano.',
            'data_publicacao_exata':None,'data_revisao_exata':None,'tipo':'medida_estatica','selecionada_para_treino':False})
    validar_X(x,cat)
    cadastro=geo[['CD_MUN','NM_MUN','SIGLA_UF']]
    indice=est[CHAVES].merge(cadastro,on='CD_MUN',validate='many_to_one')
    indice['ano_t1']=pd.array(indice.ano_t+1,dtype='Int64');indice.loc[indice.ano_t.eq(2023),'ano_t1']=pd.NA
    indice['situacao_resposta']=np.where(indice.ano_t.eq(2023),'nao_observada_na_serie','medida_mapeada_candidata_nao_homologada')
    principal=indice[indice.ano_t.le(2022)].copy();naoobs=indice[indice.ano_t.eq(2023)].copy()
    respostas=q[['CD_MUN','ano_origem','area_convertida_ha','vn_inicial_elegivel_ha','taxa_conversao_pct']].rename(
        columns={'ano_origem':'ano_t','area_convertida_ha':'C_ha','vn_inicial_elegivel_ha':'D_ha','taxa_conversao_pct':'R_pct'})
    qualidade=q[['CD_MUN','ano_origem','elegibilidade_vn_pct','cobertura_comum_pixels_pct',
        'cobertura_comum_area_grade_pct','pixels_so_inicial','pixels_so_final','pixels_invalidos_ambos']].rename(
        columns={'ano_origem':'ano_t','elegibilidade_vn_pct':'Q_pct'})
    for qmin in [99.5,99.9,99.95]:qualidade[f'passa_Q_{str(qmin).replace(".","_")}']=qualidade.Q_pct.ge(qmin)
    r2023=naoobs[CHAVES].copy()
    for n in ['C_ha','D_ha','R_pct']:r2023[n]=np.nan
    r2023['motivo_ausencia']='t+1 não observado na série autorizada; não usar2024'
    salvar(principal,pasta/'INDICE_CANONICO_9690_COL9.parquet');salvar(naoobs,pasta/'INDICE_2023_SEM_RESPOSTA_COL9.parquet')
    salvar(x[x.ano_t.le(2022)],pasta/'MATRIZ_ATRIBUTOS_CANDIDATOS_COL9.parquet')
    salvar(x[x.ano_t.eq(2023)],pasta/'ATRIBUTOS_2023_SEM_RESPOSTA_COL9.parquet')
    salvar(respostas,pasta/'RESPOSTAS_CONTINUAS_COL9.parquet');salvar(r2023,pasta/'RESPOSTAS_NAO_OBSERVADAS_2023_COL9.parquet')
    salvar(qualidade,pasta/'QUALIDADE_ELEGIBILIDADE_COL9.parquet')
    part=principal[CHAVES+['SIGLA_UF']].copy();part['papel']=divisao_temporal(part.ano_t)
    salvar(part,pasta/'PARTICOES_TEMPORAIS_COL9.parquet')
    loso=[]
    for uf in sorted(part.SIGLA_UF.unique()):
        f=part[CHAVES+['SIGLA_UF']].copy();f['UF_retida']=uf;f['papel']=divisao_loso(f,uf);loso.append(f)
    salvar(pd.concat(loso,ignore_index=True),pasta/'PARTICOES_LOSO_COL9.parquet')
    internos=[]
    for i,(fim,a,b) in enumerate([(2001,2003,2005),(2005,2007,2009),(2009,2011,2013)],1):
        f=part[CHAVES].copy();f['fold']=i
        f['papel']=np.where(f.ano_t.le(fim),'treino',np.where(f.ano_t.between(a,b),'validacao_interna',
            np.where(f.ano_t.eq(fim+1),'embargo','fora_deste_fold')));internos.append(f)
    salvar(pd.concat(internos,ignore_index=True),pasta/'FOLDS_INTERNOS_AVANCO_COL9.parquet')
    disponibilidade=[]
    for meta in cat:
        z=x[CHAVES].copy();z['variavel']=meta['variavel'];z['disponivel']=x[meta['variavel']].notna()
        z['ano_inicio_fenomeno']=np.maximum(1985,x.ano_t+meta['inicio_fenomeno_offset'])
        z['ano_max_informacao_fenomeno']=x.ano_t+meta['fim_fenomeno_offset']
        z['status_temporal']=meta['status_temporal']
        z['dependencia_algoritmica_ate']=pd.array([meta['dependencia_algoritmica_max_ano_conservadora']]*len(x),dtype='Int64')
        z['motivo_ausencia']=np.where(z.disponivel,'nao_ausente','historico_insuficiente_ou_fonte_ausente')
        disponibilidade.append(z)
    salvar(pd.concat(disponibilidade,ignore_index=True),saida/'metadados/DISPONIBILIDADE_ATRIBUTOS_COL9.parquet')
    csv_novo(pd.DataFrame(cat),saida/'metadados/CATALOGO_ATRIBUTOS_COL9.csv')
    with (saida/'metadados/catalogo_atributos.json').open('x',encoding='utf-8') as f:json.dump(cat,f,ensure_ascii=False,indent=2)
    fontes={'manifesto_rasters_sha256':sha(mpath),'matrizes_concluido_sha256':sha(matrizes/'concluido.json'),
        'consolidado_csv':str(cons),'consolidado_sha256':sha(cons),'estoques_npz_sha256':fontes_npz,'territorio':provg}
    with (saida/'metadados/fontes_matriz.json').open('x',encoding='utf-8') as f:json.dump(fontes,f,ensure_ascii=False,indent=2)
    contrato={'criado_UTC':datetime.now(timezone.utc).isoformat(),'municipios':255,'intervalos':38,'linhas_X':len(principal),
        'linhas_2023_sem_resposta':len(naoobs),'n_atributos_candidatos':len(cat),'R_principal':'proposta para orientador, não homologada',
        'C_complementar':'resposta candidata secundária independente, não equivalente estatisticamente a R',
        'treinamento_autorizado':False,'otimizacao_autorizada':False,'mudanca_objetivos_homologada':False,
        'politica_2024':'reservado, não utilizado','erro_max_estoque_csv_ha':erro,
        'versoes':{p:importlib.metadata.version(p) for p in ['numpy','pandas','pyarrow','geopandas','shapely','pyproj']},
        'codigo_sha256':sha(Path(__file__)),'artefatos_sha256':{str(p.relative_to(saida)):sha(p) for p in saida.rglob('*') if p.is_file()}}
    with (saida/'contrato_preparacao.json').open('x',encoding='utf-8') as f:json.dump(contrato,f,ensure_ascii=False,indent=2)
    print(json.dumps({k:v for k,v in contrato.items() if k!='artefatos_sha256'},ensure_ascii=False,indent=2),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--matrizes',type=Path,required=True);p.add_argument('--saida',type=Path,required=True)
    a=p.parse_args();executar(a.matrizes,a.saida)
