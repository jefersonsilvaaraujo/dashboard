"""Auditorias auxiliares Col9: matrizes intactas, PRODES2023 e acervo de imagens.

Nenhuma discordância altera classes. Persistência somente até 2023. PRODES não
é referência universal de uso antrópico, especialmente em vegetação secundária.
"""
import argparse
from datetime import datetime,timezone
import importlib.metadata
import json
from pathlib import Path
import re
import sys
import xml.etree.ElementTree as ET

import numpy as np
import pandas as pd
from pyproj import Transformer
import rasterio

PROJETO=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(PROJETO))
from processamento.cenarios_validacao_col9 import VN,UA,sha,csv_novo,conferir_acervo
from processamento.avaliar_pontos_oficiais_col9 import ler_celulas


def intervalo_prodes(rotulo, bioma):
    """Intervalos conservadores do mosaico legado; não atribuir data exata ao biênio."""
    m=re.search(r'\bd(\d{4})\b',str(rotulo))
    if not m: return None
    ano=int(m.group(1))
    if ano>2023: raise ValueError('PRODES fora do intervalo autorizado.')
    if ano==2000: return (None,2000)
    # Mosaico Brasil2023 não tem d2001/d2003/d2005 e não documenta uma data
    # de observação por pixel. Mantém agregação conservadora também na Amazônia.
    if ano in (2002,2004,2006): return (ano-1,ano)
    if bioma=='CERRADO' and ano<=2012 and ano%2==0: return (ano-1,ano)
    return (ano,ano)


def confronto_prodes(rotulo, t1, bioma):
    iv=intervalo_prodes(rotulo,bioma)
    if iv is None: return 'inconclusivo_escopos_ou_cobertura_distintos'
    a,b=iv
    if a is None: return 'historico_ate2000_sem_data_de_conversao'
    if a<=t1<=b: return 'coincidencia_ano_ou_intervalo_PRODES'
    # ±1 é janela exploratória por calendário/observação; nunca valida o ano.
    if min(abs(t1-a),abs(t1-b))==1:
        return 'proximidade_temporal_um_ano_sem_validacao_anual'
    return 'cronologia_distinta_inconclusiva_sobre_reconversao'


def auditar_matrizes(raiz,saida):
    q=conferir_acervo(raiz)
    registros=[]; fluxos=[]
    with np.load(raiz/'matrizes_completas_255.npz',allow_pickle=False) as z:
        classes=z['classes']; anos=z['anos']; m=z['area_ha']
        if anos.tolist()!=list(range(1985,2024)): raise ValueError('Série indevida.')
        vn=np.flatnonzero(np.isin(classes,VN)); ua=np.flatnonzero(np.isin(classes,UA))
        past=np.flatnonzero(classes==15); agr=np.flatnonzero(np.isin(classes,[20,35,39,40,41,46,47,48,62]))
        mos=np.flatnonzero(classes==21)
        for i,cd in enumerate(z['CD_MUN']):
            for j,t in enumerate(anos[:-1]):
                a=m[i,j]; total=a.sum(); c=a[np.ix_(vn,ua)].sum()
                inv=a[np.ix_(ua,vn)].sum()
                registros.append({'CD_MUN':int(cd),'ano_origem':int(t),'ano_destino':int(t+1),
                    'C_ha':c,'fluxo_inverso_UA_VN_ha':inv,
                    'razao_fluxo_inverso_sobre_conversao':inv/c if c else np.nan,
                    'estabilidade_exata_classe_pct':100*np.trace(a)/total,
                    'VN_pastagem_ha':a[np.ix_(vn,past)].sum(),
                    'VN_agricultura_ha':a[np.ix_(vn,agr)].sum(),
                    'VN_mosaico_ha':a[np.ix_(vn,mos)].sum(),
                    'VN_outros_UA_ha':c-a[np.ix_(vn,np.r_[past,agr,mos])].sum()})
                if cd in [5103809,2109908,5107107,5105507,2102325] or t>=2020:
                    for o,d in zip(*np.nonzero(a)):
                        if classes[o] in VN and classes[d] in UA:
                            fluxos.append({'CD_MUN':int(cd),'ano_destino':int(t+1),
                                'origem':int(classes[o]),'destino':int(classes[d]),'area_ha':a[o,d]})
    r=pd.DataFrame(registros).merge(q[['CD_MUN','NM_MUN','SIGLA_UF','ano_origem',
        'taxa_conversao_pct','elegibilidade_vn_pct','pixels_comuns','pixels_so_inicial','pixels_so_final']],
        on=['CD_MUN','ano_origem'],validate='one_to_one')
    np.testing.assert_allclose(r.C_ha,q.set_index(['CD_MUN','ano_origem']).reindex(
        pd.MultiIndex.from_frame(r[['CD_MUN','ano_origem']])).area_convertida_ha,rtol=1e-10,atol=1e-8)
    csv_novo(r,saida/'fluxos_inversos_estabilidade_9690.csv')
    csv_novo(pd.DataFrame(fluxos),saida/'fluxos_classes_extremos_controles.csv')
    col=['C_ha','fluxo_inverso_UA_VN_ha','VN_pastagem_ha','VN_agricultura_ha','VN_mosaico_ha','VN_outros_UA_ha']
    csv_novo(r.groupby('ano_destino')[col].sum().reset_index(),saida/'fluxos_regionais_por_ano.csv')
    csv_novo(r.loc[r.CD_MUN.isin([5103809,2109908,5107107,5105507,2102325])],saida/'serie_municipios_prioritarios.csv')
    # Resultado triplo já existente: leitura/verificação, sem recalcular/substituir.
    pasta=raiz/'municipios/2102325';ck=json.loads((pasta/'concluido.json').read_text(encoding='utf-8'))
    with np.load(pasta/ck['npz'],allow_pickle=False) as z:
        chaves={k:{'shape':list(z[k].shape),'soma':float(z[k].sum())} for k in z.files if 'trip' in k}
    (saida/'buriticupu_mascara_tripla_preexistente.json').write_text(json.dumps(
        {'checkpoint_sha256':sha(pasta/'concluido.json'),'npz_sha256':sha(pasta/ck['npz']),
        'campos':chaves,'nota':'Não confundir igualdade de máscara com validação temática.'},indent=2),encoding='utf-8')


def auditar_prodes(avaliacao,saida,prodes):
    pts=pd.read_csv(avaliacao/'pontos_selecionados.csv',sep=';',encoding='utf-8-sig',low_memory=False)
    temporal=pd.read_csv(avaliacao/'auditoria_temporal_pontos.csv',sep=';',encoding='utf-8-sig')
    qml=prodes.with_suffix('.qml')
    labels={int(x.attrib['value']):x.attrib['label'] for x in ET.parse(qml).findall('.//paletteEntry')}
    # A legenda local de 2023 deve ser suficiente, sem inferir códigos futuros.
    for label in labels.values(): intervalo_prodes(label,'CERRADO')
    with rasterio.open(prodes) as src:
        tr=Transformer.from_crs(4326,src.crs,always_xy=True)
        x,y=tr.transform(pts.LON.to_numpy(),pts.LAT.to_numpy())
        lin,col=rasterio.transform.rowcol(src.transform,x,y)
        vv,ok=ler_celulas(src,lin,col)
        leitura={'crs':src.crs.to_string(),'transform':list(src.transform)[:6],
                 'shape':list(src.shape),'nodata':src.nodata,'resolucao':list(src.res)}
    pts['prodes_codigo']=vv[:,4];pts['prodes_valido']=ok[:,4]
    pts['prodes_rotulo']=[labels.get(int(x),'sem_rotulo') for x in vv[:,4]]
    pts['prodes_homogeneidade_3x3']=(vv==vv[:,4,None]).mean(axis=1)
    csv_novo(pts[['TARGETID','CD_MUN','NM_MUN','SIGLA_UF','BIOMA_250K','AMOSTRA_AM',
        'prodes_codigo','prodes_rotulo','prodes_valido','prodes_homogeneidade_3x3']],saida/'prodes2023_pontos.csv')
    z=temporal.loc[temporal.conversao].merge(pts[['TARGETID','BIOMA_250K','prodes_codigo','prodes_rotulo',
        'prodes_valido','prodes_homogeneidade_3x3']],on='TARGETID',validate='many_to_one')
    z['confronto_PRODES']=[confronto_prodes(l,int(a),b) if v else 'inconclusivo_NoData'
                          for l,a,b,v in zip(z.prodes_rotulo,z.ano_destino,z.BIOMA_250K,z.prodes_valido)]
    csv_novo(z,saida/'confronto_PRODES_conversoes_pontos.csv')
    csv_novo(z.groupby(['ano_destino','AMOSTRA_AM','confronto_PRODES']).size().rename('n').reset_index(),
              saida/'confronto_PRODES_ano.csv')
    (saida/'proveniencia_PRODES2023.json').write_text(json.dumps({'arquivo':str(prodes),
        'sha256':sha(prodes),'qml':str(qml),'qml_sha256':sha(qml),'grade':leitura,
        'legenda':labels,'origem':'Acervo local legado; referência institucional INPE/TerraBrasilis. URL exata de download original não comprovada.',
        'consulta_institucional':'https://terrabrasilis.dpi.inpe.br/downloads/',
        'papel':'Concordância auxiliar de cronologia espacial, sem equivalência universal de classes/ano.',
        'criterios':'Intervalos d2002/04/06: bienais conservadores; Cerrado pares até2012: bienais; d2000: acumulado. ±1ano apenas proximidade exploratória.',
        'limites':'Mosaico legado sem ano de imagem por pixel/estrato de bioma oficial. Vegetação secundária e novos usos não têm equivalência com supressão primária. Ausência PRODES não prova erro Col9.',
        'sem_2024':True},ensure_ascii=False,indent=2),encoding='utf-8')


def inventario_imagens(piloto,saida):
    """Reúso estritamente automatizado de metadados existentes, sem interpretação."""
    registros=[]
    for p in sorted((piloto/'referencias_cegas').glob('*/metadados.json')):
        d=json.loads(p.read_text(encoding='utf-8'))
        for e in d['evidencias']:
            a=int(e['ano'])
            if not 1985<=a<=2023: raise ValueError('Ano de imagem fora do escopo.')
            registros.append({'caso':d['caso'],'ano':a,'ano_t':d['ano_t'],'ano_t1':d['ano_t1'],
                'situacao':e['situacao'],'sensor':e.get('sensor'), 'cena':e.get('cena'),
                'data_imagem':e.get('data_imagem'),'janela':e['janela'],
                'QA_footprint':e.get('fracao_QA_adequada_footprint'),
                'arquivo_metadados':str(p),'sha256_metadados':sha(p),
                'limite':'Disponibilidade/QA não constitui confirmação temática; casos distintos dos pontos oficiais.'})
    z=pd.DataFrame(registros);csv_novo(z,saida/'acervo_imagens_disponibilidade_QA.csv')
    csv_novo(z.groupby(['ano','sensor','situacao'],dropna=False).size().rename('n').reset_index(),
              saida/'imagens_cobertura_ano_sensor.csv')
    (saida/'limites_referencias_externas.json').write_text(json.dumps({
        'imagens':'320 recortes preexistentes de Landsat/Sentinel em120 locais do piloto: apenas inventário de QA e datas neste processamento; sem novos rótulos nem extrapolação aos pontos oficiais.',
        'area_queimada':'Acervo com focos de calor, mas sem raster harmonizado e manifesto de cicatriz anual. Foco não equivale a área queimada. Confronto temático quantitativo inconclusivo.',
        'sem_nova_interpretacao_humana':True,'sem_modificar_produtos':True},ensure_ascii=False,indent=2),encoding='utf-8')


def executar(avaliacao,raiz,saida,prodes,piloto):
    if saida.exists(): raise FileExistsError('Saída anterior preservada.')
    saida.mkdir(parents=True)
    auditar_matrizes(raiz,saida)
    auditar_prodes(avaliacao,saida,prodes)
    inventario_imagens(piloto,saida)
    (saida/'manifesto_auditoria.json').write_text(json.dumps({'executado_utc':datetime.now(timezone.utc).isoformat(),
        'versoes':{p:importlib.metadata.version(p) for p in ['numpy','pandas','rasterio','pyproj']},
        'matriz_concluido_sha256':sha(raiz/'concluido.json'),
        'arquivos':{p.name:sha(p) for p in saida.iterdir() if p.is_file()},
        'sem_treinamento':True,'sem_homologacao':True},ensure_ascii=False,indent=2),encoding='utf-8')
    print('Auditoria complementar concluída, sem alteração de produtos.',flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--avaliacao',type=Path,required=True);p.add_argument('--matrizes',type=Path,required=True)
    p.add_argument('--saida',type=Path,required=True)
    p.add_argument('--prodes',type=Path,default=Path('D:/mestrado/desmatamento_prodes/prodes_brasil_2023/prodes_brasil_2023.tif'))
    p.add_argument('--piloto',type=Path,default=PROJETO/'validacao_cientifica_col9/piloto_interpretacao_20261111_v1')
    a=p.parse_args();executar(a.avaliacao,a.matrizes,a.saida,a.prodes,a.piloto)
