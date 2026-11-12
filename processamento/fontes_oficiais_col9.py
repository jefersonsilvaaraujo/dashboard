"""Baixa fontes explicitamente vinculadas à Coleção9, sem sobrescrever dados existentes."""
import argparse
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
import urllib.request
from urllib.parse import urlparse,unquote
from zipfile import ZipFile

PAGINA='https://brasil.mapbiomas.org/downloads/pontos-de-validacao/'
FONTES={
 'csv_zip':'https://brasil.mapbiomas.org/wp-content/uploads/sites/4/2024/08/mapbiomas_85k_col2_1_points_w_edge_and_edited_v1.csv_-1.zip',
 'vetor_auxiliar_zip':'https://brasil.mapbiomas.org/wp-content/uploads/sites/3/2026/10/mapbiomas_85k_points_validation.zip'
}


def baixar(url,pasta,nome=None):
    destino=pasta/(nome or unquote(Path(urlparse(url).path).name))
    h=hashlib.sha256(); n=0
    req=urllib.request.Request(url,headers={'User-Agent':'DefesaMestrado-Col9-avaliacao/1.0'})
    with urllib.request.urlopen(req,timeout=90) as f, destino.open('xb') as g:
        headers={k:f.headers.get(k) for k in ['Content-Type','Content-Length','Last-Modified','ETag']}
        final=f.url
        for bloco in iter(lambda:f.read(1024*1024),b''): g.write(bloco); h.update(bloco); n+=len(bloco)
    return {'url':url,'url_resolvida':final,'arquivo':destino.name,'bytes':n,'sha256':h.hexdigest(),
        'baixado_em_utc':datetime.now(timezone.utc).isoformat(),'headers':headers,'pagina_origem':PAGINA,
        'licenca_declarada_pagina':'CC BY4.0, uso público/aberto/gratuito mediante referência'}


def executar(pasta):
    pasta.mkdir(parents=True,exist_ok=True)
    registros=[]
    for chave,url in FONTES.items():
        print('Baixando',chave,flush=True); d=baixar(url,pasta); d['papel']=chave
        with ZipFile(pasta/d['arquivo']) as z:
            d['conteudo_zip']=[{'arquivo':x.filename,'bytes':x.file_size,'CRC32':x.CRC} for x in z.infolist()]
            if chave=='csv_zip':
                for info in z.infolist():
                    if info.filename.lower().endswith('.csv') and not Path(info.filename).name.startswith('._'):
                        nome=Path(info.filename).name
                        with z.open(info) as f,(pasta/nome).open('xb') as g:
                            for b in iter(lambda:f.read(1024*1024),b''): g.write(b)
                        d['csv_extraido']=nome
                        d['csv_sha256']=hashlib.sha256((pasta/nome).read_bytes()).hexdigest()
        registros.append(d); print(json.dumps(d,ensure_ascii=False,indent=2),flush=True)
    with (pasta/'manifesto_download.json').open('x',encoding='utf-8') as f:
        json.dump({'fontes':registros,'nota':'Nome legado col2_1 não identifica sozinho coleção; vínculo oficial e anos/conteúdo precisam auditoria. Vetor2026 é auxiliar até comparar versões.'},f,ensure_ascii=False,indent=2)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__); p.add_argument('--saida',type=Path,required=True)
    a=p.parse_args(); executar(a.saida)
