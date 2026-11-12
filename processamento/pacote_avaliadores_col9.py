"""Pacotes cegos independentes A/B; gestão/estratos/classes ficam fora dos ZIPs."""
import argparse
import html
import json
from pathlib import Path
import shutil
import sys
from zipfile import ZipFile,ZIP_DEFLATED

import pandas as pd

PROJETO=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(PROJETO))
from processamento.cenarios_validacao_col9 import csv_novo,sha

PROIBIDAS={'id','CD_MUN','NM_MUN','SIGLA_UF','classe_t','classe_t1','classe_t_menos1','classe_t_mais2',
    'estrato_pixel','estrato_psu','pi_inclusao','peso_expansao_ha','chave_sorteio','magnitude','candidato'}


def verificar_ficha_cega(d):
    if PROIBIDAS&set(d.columns): raise ValueError('Ficha revela atributos do mapa/desenho.')
    if d.caso.duplicated().any(): raise ValueError('Alias repetido.')
    if not d.ano_t.between(1985,2022).all() or not d.ano_t1.eq(d.ano_t+1).all():
        raise ValueError('Horizonte/anos do piloto divergentes.')


def verificar_metadados(m):
    if PROIBIDAS&set(m): raise ValueError('Metadados não cegos.')
    for e in m['evidencias']:
        if not 1985<=e['ano']<=2023: raise ValueError('Ano2024 reservado apareceu na referência.')
        if e.get('situacao')=='disponivel_para_interpretacao':
            if pd.Timestamp(e['data_imagem']).year!=e['ano']: raise ValueError('Cena fora do ano solicitado.')


def executar(piloto,instrucoes,saida):
    if saida.exists(): raise FileExistsError('Entrega anterior preservada.')
    cobertura=pd.read_csv(piloto/'gestao_restrita/cobertura_referencias.csv',sep=';')
    if len(cobertura)!=120: raise ValueError('Aguardar conclusão dos 120 casos, inclusive indisponíveis.')
    for caso in cobertura.caso:
        pasta=piloto/'referencias_cegas'/caso
        ck=json.loads((pasta/'concluido.json').read_text(encoding='utf-8'))
        for nome,h in ck['sha256'].items():
            if sha(pasta/nome)!=h: raise ValueError('Referência divergente.')
        verificar_metadados(json.loads((pasta/'metadados.json').read_text(encoding='utf-8')))
    saida.mkdir(parents=True)
    recibos=[]
    for avaliador in ('A','B'):
        origem=piloto/('avaliador_'+avaliador); destino=saida/('avaliador_'+avaliador); destino.mkdir()
        ficha=pd.read_csv(origem/'ficha_independente.csv',sep=';',keep_default_na=False)
        verificar_ficha_cega(ficha)
        ficha=ficha.drop(columns='situacao_referencia').merge(cobertura[['caso','par_com_recortes','n_recortes']],
            on='caso',validate='one_to_one',sort=False)
        ficha['situacao_referencia']=ficha.par_com_recortes.map({True:'recortes_nos_dois_anos_a_interpretar',False:'cobertura_parcial_ou_ausente_manter_caso'})
        ficha=ficha.drop(columns=['par_com_recortes','n_recortes'])
        verificar_ficha_cega(ficha); csv_novo(ficha,destino/'ficha_independente.csv')
        shutil.copyfile(instrucoes,destino/'INSTRUCOES.md')
        geos=[]; linhas=[]
        for caso in ficha.caso:
            pasta=piloto/'referencias_cegas'/caso; dp=destino/'casos'/caso; dp.mkdir(parents=True)
            for p in pasta.iterdir():
                if p.name in ('metadados.json','pixel.geojson','prancha.png') or p.suffix=='.tif' or (p.name.startswith('catalogo_') and p.suffix=='.json'):
                    shutil.copyfile(p,dp/p.name)
            m=json.loads((pasta/'metadados.json').read_text(encoding='utf-8'))
            geos.append(json.loads((pasta/'pixel.geojson').read_text(encoding='utf-8')))
            linhas.append(f'<article id="{caso}"><h2>{caso} — {m["ano_t"]} / {m["ano_t1"]}</h2><p>Referência a interpretar; ausência não significa ausência de conversão.</p><a href="casos/{caso}/metadados.json">Datas, cenas e limitações</a> · <a href="casos/{caso}/pixel.geojson">Pixel georreferenciado</a><br><a href="casos/{caso}/prancha.png"><img loading="lazy" src="casos/{caso}/prancha.png" alt="Prancha {caso}"></a></article>')
        (destino/'pixels_piloto.geojson').write_text(json.dumps({'type':'FeatureCollection','features':geos}),encoding='utf-8')
        cab='<!doctype html><meta charset="utf-8"><title>Piloto Col9</title><style>body{font-family:Arial;max-width:1600px;margin:24px auto}img{max-width:100%}article{margin:2em 0;border-top:1px solid #aaa}</style>'
        menu=' '.join(f'<a href="#{x}">{x}</a>' for x in ficha.caso)
        (destino/'indice.html').write_text(cab+f'<h1>Piloto — avaliador {avaliador}</h1><p>120 casos. Preencher apenas sua ficha, sem consultar o outro avaliador ou a classificação MapBiomas.</p>'+menu+''.join(linhas),encoding='utf-8')
        manifesto={'avaliador':avaliador,'casos':120,'sem_classes_do_mapa':True,'sem_resultados_outro_avaliador':True,
            'sem_2024':True,'sha256':{p.relative_to(destino).as_posix():sha(p) for p in destino.rglob('*') if p.is_file()}}
        (destino/'manifesto.json').write_text(json.dumps(manifesto,ensure_ascii=False,indent=2),encoding='utf-8')
        zipfile=saida/f'piloto_col9_avaliador_{avaliador}.zip'
        with ZipFile(zipfile,'x',ZIP_DEFLATED,compresslevel=6) as z:
            for p in sorted(destino.rglob('*')):
                if p.is_file(): z.write(p,p.relative_to(destino).as_posix())
        with ZipFile(zipfile) as z:
            if z.testzip() is not None: raise ValueError('ZIP inválido.')
            import hashlib
            for n,h in manifesto['sha256'].items():
                if hashlib.sha256(z.read(n)).hexdigest()!=h: raise ValueError('Hash de conteúdo divergente.')
            if any(n.startswith('gestao_restrita') for n in z.namelist()): raise ValueError('Vazamento da gestão.')
        h=sha(zipfile)
        with zipfile.with_suffix('.sha256').open('x',encoding='utf-8') as f: f.write(f'{h}  {zipfile.name}\n')
        recibos.append({'avaliador':avaliador,'zip':zipfile.name,'bytes':zipfile.stat().st_size,'sha256':h})
    (saida/'recibo_entrega.json').write_text(json.dumps(recibos,indent=2),encoding='utf-8')
    print(json.dumps(recibos,indent=2))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for n in ('piloto','instrucoes','saida'): p.add_argument('--'+n,type=Path,required=True)
    a=p.parse_args(); executar(a.piloto,a.instrucoes,a.saida)
