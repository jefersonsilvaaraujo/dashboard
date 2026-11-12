"""Reavalia DN já baixados sem resolver arbitrariamente metadados conflitantes.

Earth Search pode declarar simultaneamente offset=-0.1 no asset e
earthsearch:boa_offset_applied=true. Calculam-se as duas hipóteses; cenas assim
não fornecem confirmação radiométrica independente da conversão.
"""
import argparse
import json
from pathlib import Path
import sys
import numpy as np
import pandas as pd

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from processamento.cenarios_validacao_col9 import sha,csv_novo


def calcular_ndvi(red,nir,w,escala,offset):
    r=red.astype(float)*escala+offset;n=nir.astype(float)*escala+offset
    ok=(red>0)&(nir>0)&(w>0)&(r>=0)&(n>=0)&((r+n)>0)
    if not w.sum():raise ValueError('Sem interseção de suporte.')
    valor=float(np.sum(((n[ok]-r[ok])/(n[ok]+r[ok]))*w[ok])/w[ok].sum()) if ok.any() else None
    return valor,float(w[ok].sum()/w.sum())


def executar(origem,saida):
    if saida.exists():raise FileExistsError('Saída anterior preservada.')
    saida.mkdir(parents=True)
    base=pd.read_csv(origem/'NDVI_cenas.csv',sep=';',encoding='utf-8-sig');res=[]
    for row in base.itertuples():
        if row.situacao!='calculado':continue
        meta=json.loads((origem/row.fonte_json).read_text(encoding='utf-8'))
        raw=origem/row.fonte_json.replace('_fonte.json','_dados.npz')
        if sha(raw)!=meta['dados_sha256']:raise ValueError('Recorte DN divergiu.')
        s2=row.sensor=='Sentinel-2';prop=meta['item']['properties']
        flag=prop.get('earthsearch:boa_offset_applied')
        offset=meta['calibracao_red']['offset'];esc=meta['calibracao_red']['scale']
        conflito=s2 and flag is True and offset!=0
        with np.load(raw,allow_pickle=False) as z:
            v0,f0=calcular_ndvi(z['red_DN'],z['nir_DN'],z['pesos_intersecao_m2'],esc,0 if s2 else offset)
            vm,fm=calcular_ndvi(z['red_DN'],z['nir_DN'],z['pesos_intersecao_m2'],esc,offset)
        res.append({'id':row.id,'CD_MUN':row.CD_MUN,'ano':row.ano,'ano_t':row.ano_t,'ano_t1':row.ano_t1,
            'cena':row.cena,'sensor':row.sensor,'data_imagem':row.data_imagem,
            'flag_offset_aplicado':flag,'offset_asset':offset,'conflito_metadados':conflito,
            'NDVI_hipotese_offset_ja_aplicado':v0,'fracao_valida_hipotese_ja_aplicado':f0,
            'NDVI_hipotese_asset_literal':vm,'fracao_valida_hipotese_asset_literal':fm,
            'QA_completo':row.QA_footprint_completo,
            'evidencia':'inconclusiva_calibracao_conflitante' if conflito else 'proxy_sem_rotulo_tematico',
            'dados_DN_sha256':sha(raw),'fonte_json':str(origem/row.fonte_json)})
    d=pd.DataFrame(res);csv_novo(d,saida/'NDVI_duas_hipoteses.csv');pares=[]
    for idp,g in d.groupby('id'):
        t=int(g.ano_t.iloc[0]);r={'id':idp,'CD_MUN':int(g.CD_MUN.iloc[0]),'ano_t':t,'ano_t1':t+1}
        g=g.set_index('ano')
        if t not in g.index or t+1 not in g.index:
            r['evidencia']='inconclusivo_cena_ausente'
        else:
            a,b=g.loc[t],g.loc[t+1];dias=abs(pd.Timestamp(a.data_imagem).dayofyear-pd.Timestamp(b.data_imagem).dayofyear)
            dias=min(dias,366-dias)
            r.update(delta_NDVI_ja_aplicado=b.NDVI_hipotese_offset_ja_aplicado-a.NDVI_hipotese_offset_ja_aplicado,
                delta_NDVI_asset_literal=b.NDVI_hipotese_asset_literal-a.NDVI_hipotese_asset_literal,
                distancia_sazonal_dias=dias,conflito_metadados=bool(a.conflito_metadados or b.conflito_metadados))
            motivo=[]
            if r['conflito_metadados']:motivo.append('calibracao')
            if dias>45:motivo.append('sazonalidade')
            if a.sensor!=b.sensor:motivo.append('familia_sensor')
            if not(a.QA_completo and b.QA_completo):motivo.append('QA')
            if a.fracao_valida_hipotese_asset_literal<.999 or b.fracao_valida_hipotese_asset_literal<.999:motivo.append('reflectancia')
            r['evidencia']='inconclusivo_'+'_'.join(motivo) if motivo else 'proxy_comparavel_sem_adjudicacao'
        r['limite']='Nenhuma hipótese é nova interpretação humana ou prova de uso antrópico.'
        pares.append(r)
    csv_novo(pd.DataFrame(pares),saida/'NDVI_pares_hipoteses.csv')
    (saida/'manifesto_radiometria.json').write_text(json.dumps({'origem_manifesto_sha256':sha(origem/'manifesto_espectral.json'),
        'n_cenas':len(d),'n_metadados_conflitantes':int(d.conflito_metadados.sum()),
        'resolucao':'Não escolher calibração por concordância. Preservar DN e hipóteses, marcar inconclusivo até confirmação do provedor/original.',
        'fonte_discussao_primaria_provedor':'https://github.com/Element84/earth-search/issues/71',
        'arquivos':{p.name:sha(p) for p in saida.iterdir() if p.is_file()}},ensure_ascii=False,indent=2),encoding='utf-8')
    print('Sensibilidade radiométrica:',len(d),'cenas;',int(d.conflito_metadados.sum()),'com metadados conflitantes.',flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--origem',type=Path,required=True)
    p.add_argument('--saida',type=Path,required=True);a=p.parse_args();executar(a.origem,a.saida)
