"""Inventário e bloco de focos reintersectado nos255 limites. Não integra ao X-base."""
import argparse
import json
from pathlib import Path
import re
import sys
from zipfile import ZipFile
import geopandas as gpd
import numpy as np
import pandas as pd

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from processamento.cenarios_validacao_col9 import sha,csv_novo
from modelagem.preparar_regressao_continua_col9 import salvar


def executar(checkpoint,saida):
    if saida.exists():raise FileExistsError('Preservar bloco anterior.')
    saida.mkdir(parents=True)
    m=json.loads(Path('referencias/manifesto_rasters_transicoes_col9.json').read_text(encoding='utf-8'))
    base=Path(m['base_dados']);g=gpd.read_file(base/m['territorio']['arquivo']).to_crs(4326);g.CD_MUN=g.CD_MUN.astype(str)
    if sha(base/m['territorio']['arquivo'])!=m['territorio']['sha256']:raise ValueError('Território alterado.')
    xmin,ymin,xmax,ymax=g.total_bounds
    logs=[];mensais=[];ids_vistos=set();ambiguos=[]
    for ano in range(2003,2024):
        f=base/f'queimadas_inpe/focos_br_ref_2003_2025/focos_br_ref_{ano}.zip'
        if not f.exists():logs.append({'ano':ano,'status':'arquivo_ausente'});continue
        with ZipFile(f) as z:
            nomes=[n for n in z.namelist() if n.endswith('.csv') and not Path(n).name.startswith('._')]
            if len(nomes)!=1:raise ValueError('Inventário ZIP ambíguo.')
            d=pd.read_csv(z.open(nomes[0]),usecols=['foco_id','id_bdq','lat','lon','data_pas'],dtype={'foco_id':str})
        nacional=len(d);dt=pd.to_datetime(d.data_pas,utc=True,errors='coerce')
        bad=dt.isna()|dt.dt.year.ne(ano)|~d.lon.between(-180,180)|~d.lat.between(-90,90)|d.foco_id.isna()
        d=d.loc[~bad].copy();d['instante_UTC']=dt.loc[~bad]
        exatas=d.duplicated(['foco_id','data_pas','lat','lon']).sum()
        d=d.drop_duplicates(['foco_id','data_pas','lat','lon'])
        conflitos=d.foco_id.duplicated(keep=False)
        if conflitos.any():
            csv_novo(d.loc[conflitos],saida/f'QUARENTENA_IDS_CONFLITANTES_{ano}.csv')
            d=d.loc[~conflitos]
        d=d.loc[d.lon.between(xmin,xmax)&d.lat.between(ymin,ymax)].copy()
        p=gpd.GeoDataFrame(d,geometry=gpd.points_from_xy(d.lon,d.lat),crs=4326)
        inter=gpd.sjoin(p,g[['CD_MUN','geometry']],how='inner',predicate='intersects')
        mult=inter.foco_id.duplicated(keep=False)
        if mult.any():
            ambiguos.extend(inter.loc[mult,['foco_id','lat','lon','CD_MUN']].to_dict('records'))
            inter=inter.loc[~mult]
        repetidos=inter.foco_id.isin(ids_vistos)
        n_cross=int(repetidos.sum());inter=inter.loc[~repetidos];ids_vistos.update(inter.foco_id)
        inter['mes']=inter.instante_UTC.dt.month;inter['ano_t']=ano
        ag=inter.groupby(['CD_MUN','ano_t','mes']).size().rename('focos_registrados_mes').reset_index()
        mensais.append(ag)
        logs.append({'ano':ano,'arquivo':str(f),'sha256':sha(f),'n_nacional':nacional,
            'n_data_coordenada_id_invalida_ou_outro_ano':int(bad.sum()),'n_duplicatas_exatas':int(exatas),
            'n_ids_conflitantes':int(conflitos.sum()),'n_duplicatas_entre_arquivos_no_recorte':n_cross,
            'n_ambiguos_limite_linhas':int(mult.sum()),'n_no_recorte':len(inter),
            'n_municipios_com_registro':int(inter.CD_MUN.nunique()),
            'primeiro_instante_UTC':str(dt.min()),'ultimo_instante_UTC':str(dt.max()),
            'satelite':'Sem campo por linha; produto nacional satélite de referência INPE, AQUA_M-T segundo configuração/FAQ histórica.',
            'status':'candidato_separado_sem_completude_observacional_comprovada'})
        print(f'Focos{ano}: {len(inter)} registros em {inter.CD_MUN.nunique()} municípios canônicos.',flush=True)
    index=pd.MultiIndex.from_product([sorted(g.CD_MUN),range(1985,2024),range(1,13)],names=['CD_MUN','ano_t','mes']).to_frame(index=False)
    dados=pd.concat(mensais,ignore_index=True)
    index=index.merge(dados,on=['CD_MUN','ano_t','mes'],how='left',validate='one_to_one')
    index['tem_registro_no_mes']=index.focos_registrados_mes.notna()
    anos_presentes={r['ano'] for r in logs if r.get('arquivo')}
    index['fonte_anual_local_presente']=index.ano_t.isin(anos_presentes)
    index['motivo_ausencia']=np.where(index.tem_registro_no_mes,'nao_ausente',np.where(
        index.fonte_anual_local_presente,'nenhum_registro_no_mes_nao_equivale_ausencia_fenomeno','fonte_referencia_ausente_neste_ano'))
    salvar(index,saida/'FOCOS_MENSAIS_CANDIDATOS_SEPARADOS.parquet')
    anual=index.groupby(['CD_MUN','ano_t']).agg(focos_registrados_ano=('focos_registrados_mes',lambda x:x.sum(min_count=1)),
        meses_com_registro=('tem_registro_no_mes','sum'),fonte_anual_local_presente=('fonte_anual_local_presente','max')).reset_index()
    anual['calendario']='AnoUTC, termina antes do corte local de t; não é calendário PRODES nem garantia de cobertura instrumental.'
    anual['status_uso']='candidato_complementar_sujeito_analise_nao_incorporado_X_base'
    salvar(anual,saida/'FOCOS_ANUAIS_CANDIDATOS_SEPARADOS.parquet')
    csv_novo(pd.DataFrame(logs),saida/'AUDITORIA_FOCOS_POR_ARQUIVO.csv')
    if ambiguos:csv_novo(pd.DataFrame(ambiguos),saida/'PONTOS_FOCOS_LIMITES_AMBIGUOS.csv')
    legados=[]
    aprov=set(g.CD_MUN)
    for nome in ['focos_municipio_mensal.csv','prodes_area_classe_municipio.csv','painel_municipio_ano.csv']:
        f=Path('historico')/nome;d=pd.read_csv(f,sep=';',encoding='utf-8-sig',dtype={'CD_MUN':str,'cd_mun':str},
            usecols=lambda c:c in ['CD_MUN','cd_mun','ano'],low_memory=False)
        col='CD_MUN' if 'CD_MUN' in d else 'cd_mun';cod=set(d[col].dropna())
        legados.append({'arquivo':str(f),'sha256':sha(f),'linhas':len(d),'municipios_origem':len(cod),
            'municipios_intersecao_255':len(cod&aprov),'faltantes_255':sorted(aprov-cod),
            'ano_min':int(d.ano.min()),'ano_max_metadado':int(d.ano.max()),
            'uso':'Somente inventário de esquema e cobertura; valores numéricos não usados como atributos. Filtrar<=2023 em futura harmonização.'})
    # Arquivos de anos proibidos são apenas identificados por nome no inventário,
    # nunca abertos para completar a série ou confirmar persistência.
    arquivos=[]
    for pasta in [base/'desmatamento_prodes',base/'queimadas_inpe']:
        for f in sorted(pasta.rglob('*')):
            if not f.is_file() or f.name.startswith('._') or f.suffix.lower() not in ['.tif','.qml','.shp','.zip','.csv','.txt']:continue
            anos=re.findall(r'(?<!\d)(?:19|20)\d{2}(?!\d)',f.name)
            proibido='2024' in f.name or (anos and min(map(int,anos))>2023)
            arquivos.append({'arquivo':str(f),'bytes':f.stat().st_size,
                'situacao':'excluido_por_nome_ano_reservado_ou_posterior_sem_leitura_de_valores' if proibido else 'acervo_local_a_harmonizar_ou_ja_auditado'})
    csv_novo(pd.DataFrame(arquivos),saida/'INVENTARIO_ARQUIVOS_COMPLEMENTARES.csv')
    inventario={'legados':legados,'PRODES':{'status':'bloqueio_metodologico_para_X_base',
        'produto_preferivel_a_auditar':'PRODES Brasil2023 local, TIFF/QML, conforme checkpoint oficial anterior',
        'motivos':['Proveniência exata/vintage do download local não comprovada.',
            'Calendários e intervalos bienais/anuais por bioma precisam dicionário temporal validado.',
            'Classe de estoque2023 e máscara retrospectiva não podem ser propagadas como estoque observado em t.',
            'Legado251/255 nos limites antigos não está harmonizado; reinterseção integral e auditoria de cobertura necessárias.'],
        'nao_e_substituto_da_resposta':True},
        'area_queimada':{'status':'sem_serie_local_harmonizada_identificada','fontes_candidatas':[
            'INPE AQ1km/AQ30m com versão, grade e período a registrar','MapBiomas Fogo: coleção própria, sem equivalência automática com coberturaCol9'],
            'nao_substituir_por_focos':True},
        'socioeconomia':{'status':'fontes_adicionais_e_compatibilizacao_territorial_necessarias',
            'PAM':'IBGE SIDRA5457: áreas, produção, rendimento e valor, verificar unidades e mudanças de culturas.',
            'PPM':'IBGE SIDRA3939: efetivos por espécie; não somar espécies indiscriminadamente.',
            'populacao':'Estimativas/censos IBGE, tabela6579 a verificar; sem interpolação usando futuro.',
            'PIB':'SIDRA5938, referência2010: verificar revisão, cobertura e deflator; não tratar valores nominais como reais.',
            'datas_publicacao':'Por extração/tabela/ano a documentar; nenhuma disponibilidade histórica foi presumida.',
            'territorio':'Código oficial, sem aproximação de nomes; limites históricos e emancipações exigem correspondência aos255 fixos; não ratear automaticamente.'},
        'focos':{'bloco_separado':True,'periodo_dados_utilizados':[2003,2023],
            'mensais_sem_linha':'NA com motivo, nunca zero','antes2003':'NA; shapefiles de outros sensores/recortes não substituem série de referência automaticamente.',
            'FRP_chuva':'Não integrados: atributos condicionados aos focos exigem pareamento e não representam clima médio municipal.',
            'calendario':'UTC conforme arquivo fonte; anos e consistência auditados. Nenhum arquivo2024 aberto.'}}
    with (saida/'inventario_metodologico.json').open('x',encoding='utf-8') as f:json.dump(inventario,f,ensure_ascii=False,indent=2)
    manifesto={
        'sem_alteracao_X_base':True,'sem_2024':True,'codigo_sha256':sha(Path(__file__)),
        'artefatos_sha256':{p.name:sha(p) for p in saida.iterdir() if p.is_file()}}
    with (saida/'manifesto_blocos.json').open('x',encoding='utf-8') as f:json.dump(manifesto,f,ensure_ascii=False,indent=2)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--checkpoint',type=Path,required=True);p.add_argument('--saida',type=Path,required=True)
    a=p.parse_args();executar(a.checkpoint,a.saida)
