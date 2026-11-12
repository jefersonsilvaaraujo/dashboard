"""Cenários exploratórios A/B/C, sem homologar Y e sem escrever no acervo anterior."""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

VN=[3,4,5,6,49,11,12,50]
UA=[9,15,20,21,24,30,31,35,39,40,41,46,47,48,62]
CENARIOS={'A':(.25,25.),'B':(.5,100.),'C':(1.,250.)}
QUALIDADES=(99.5,99.9,99.95)
VARIANTES={'principal':([],[]),'mais25':([],[25]),'mais29':([29],[]),
           'mais32':([32],[]),'mais29_32':([29,32],[]),'mais29_32_25':([29,32],[25])}


def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(8*1024*1024),b''): h.update(b)
    return h.hexdigest()


def csv_novo(df,p):
    df.to_csv(p,sep=';',index=False,encoding='utf-8-sig',mode='x')


def conferir_acervo(raiz):
    ck=json.loads((raiz/'concluido.json').read_text(encoding='utf-8'))
    for n,h in ck['artefatos'].items():
        if sha(raiz/n)!=h: raise ValueError(f'Artefato consolidado alterado: {n}')
    q=pd.read_csv(raiz/'metricas_municipio_ano.csv',encoding='utf-8-sig')
    if len(q)!=9690 or q.duplicated(['CD_MUN','ano_origem']).any(): raise ValueError('Contrato dos 255×38 violado.')
    if not q.ano_destino.eq(q.ano_origem+1).all(): raise ValueError('Anos incompatíveis.')
    return q


def medidas(raiz,q):
    """Recalcula inclusive elegibilidade expandida com os estoques iniciais corretos."""
    registros=[]; estabilidade=[]; fluxos=[]
    prioridades={5103809,2109908,5107107,5105507,2102325}
    with np.load(raiz/'matrizes_completas_255.npz',allow_pickle=False) as z:
        classes=z['classes']; areas=z['area_ha']; codigos=z['CD_MUN']; anos=z['anos']
        for i,cd in enumerate(codigos):
            pasta=raiz/'municipios'/str(cd)
            ck=json.loads((pasta/'concluido.json').read_text(encoding='utf-8'))
            for n,h in ck['artefatos'].items():
                if sha(pasta/n)!=h: raise ValueError('Checkpoint municipal alterado.')
            with np.load(pasta/ck['npz'],allow_pickle=False) as m:
                estoque=m['estoque_area_ha']
            a=areas[i]; total=a.sum(axis=(1,2)); diag=np.trace(a,axis1=1,axis2=2)
            for j,t in enumerate(anos[:-1]):
                estabilidade.append({'CD_MUN':int(cd),'ano_origem':int(t),
                    'estabilidade_classe_pct':100*diag[j]/total[j] if total[j] else np.nan})
                if cd in prioridades:
                    for x,y in zip(*np.nonzero(a[j])):
                        fluxos.append({'CD_MUN':int(cd),'ano_origem':int(t),'ano_destino':int(t+1),
                            'classe_origem':int(classes[x]),'classe_destino':int(classes[y]),'area_ha':a[j,x,y],
                            'conversao_principal':int(classes[x]) in VN and int(classes[y]) in UA})
            for nome,(extra_o,extra_d) in VARIANTES.items():
                o=np.flatnonzero(np.isin(classes,VN+extra_o)); d=np.flatnonzero(np.isin(classes,UA+extra_d))
                c=a[:,o,:][:,:,d].sum(axis=(1,2)); den=a[:,o,:].sum(axis=(1,2))
                inicial=estoque[:-1,o].sum(axis=1)
                taxa=np.divide(100*c,den,out=np.full_like(c,np.nan),where=den>0)
                elig=np.divide(100*den,inicial,out=np.full_like(c,np.nan),where=inicial>0)
                elig[np.isclose(elig,100,rtol=0,atol=1e-9)]=100
                for j,t in enumerate(anos[:-1]):
                    registros.append({'CD_MUN':int(cd),'ano_origem':int(t),'variante':nome,
                        'C_ha':c[j],'D_ha':den[j],'VN_inicial_ha':inicial[j],'R_pct':taxa[j],'Q_pct':elig[j]})
    m=pd.DataFrame(registros).merge(q[['CD_MUN','NM_MUN','SIGLA_UF','ano_origem','ano_destino']],
        on=['CD_MUN','ano_origem'],validate='many_to_one')
    principal=m[m.variante.eq('principal')].set_index(['CD_MUN','ano_origem'])
    ref=q.set_index(['CD_MUN','ano_origem']).reindex(principal.index)
    for nova,velha in [('C_ha','area_convertida_ha'),('D_ha','vn_inicial_elegivel_ha'),('R_pct','taxa_conversao_pct')]:
        np.testing.assert_allclose(principal[nova],ref[velha],atol=1e-8,rtol=1e-10)
    return m,pd.DataFrame(estabilidade),pd.DataFrame(fluxos)


def avaliar(df,tau,amin,qmin):
    r=df.copy()
    valido=r[['C_ha','D_ha','R_pct','Q_pct']].notna().all(axis=1)&r.D_ha.gt(0)&r.VN_inicial_ha.gt(0)
    r['avaliavel']=valido&r.Q_pct.ge(qmin)
    r['exclusao_qualidade']=~r.avaliavel
    r['candidato']=r.avaliavel&r.R_pct.ge(tau)&r.C_ha.ge(amin)
    r['distancia_relativa_fronteira']=np.minimum(r.R_pct/tau,r.C_ha/amin)-1
    r['proximo']=r.avaliavel&r.distancia_relativa_fronteira.abs().le(.1+1e-12)
    r['margem_taxa_pp']=r.R_pct-tau; r['margem_area_ha']=r.C_ha-amin
    return r


def agregar(r,chaves):
    g=r.groupby(chaves,dropna=False,sort=True)
    a=g.agg(n_total=('CD_MUN','size'),n_avaliaveis=('avaliavel','sum'),
            n_eventos_candidatos=('candidato','sum'),n_excluidos_qualidade=('exclusao_qualidade','sum'),
            n_proximos_limite=('proximo','sum'),n_discordantes_principal=('discordante_principal','sum'),
            area_convertida_somada_ha_evento=('C_ha','sum')).reset_index()
    a['proporcao_eventos_avaliaveis_pct']=100*a.n_eventos_candidatos/a.n_avaliaveis.replace(0,np.nan)
    a['proporcao_eventos_total_pct']=100*a.n_eventos_candidatos/a.n_total
    return a


def executar(raiz,saida):
    if saida.exists(): raise FileExistsError('Saída anterior preservada.')
    q=conferir_acervo(raiz); m,est,fluxos=medidas(raiz,q)
    saida.mkdir(parents=True)
    csv_novo(m,saida/'medidas_sensibilidades_continuas.csv')
    csv_novo(est,saida/'estabilidade_municipio_par.csv'); csv_novo(fluxos,saida/'fluxos_prioritarios.csv')
    tabelas={k:[] for k in ('global','ano','estado','municipio')}; proximos=[]; exclusoes=[]; discordantes=[]
    for nome,(tau,amin) in CENARIOS.items():
        for qmin in QUALIDADES:
            base=avaliar(m[m.variante.eq('principal')],tau,amin,qmin)
            base['estado_principal']=np.where(~base.avaliavel,'nao_avaliavel',np.where(base.candidato,'candidato','abaixo'))
            r=avaliar(m,tau,amin,qmin).merge(base[['CD_MUN','ano_origem','estado_principal']],on=['CD_MUN','ano_origem'],validate='many_to_one')
            r['estado_cenario']=np.where(~r.avaliavel,'nao_avaliavel',np.where(r.candidato,'candidato','abaixo'))
            r['discordante_principal']=r.estado_cenario.ne(r.estado_principal)
            r['cenario']=nome; r['tau_pct']=tau; r['A_min_ha']=amin; r['Q_min_pct']=qmin
            idcols=['cenario','tau_pct','A_min_ha','Q_min_pct','variante']
            for k,grupos in [('global',[]),('ano',['ano_origem','ano_destino']),('estado',['SIGLA_UF']),('municipio',['CD_MUN','NM_MUN','SIGLA_UF'])]:
                tabelas[k].append(agregar(r,idcols+grupos))
            col=idcols+['CD_MUN','NM_MUN','SIGLA_UF','ano_origem','ano_destino','C_ha','D_ha','R_pct','Q_pct',
                        'distancia_relativa_fronteira','margem_taxa_pp','margem_area_ha','estado_cenario','estado_principal']
            proximos.append(r.loc[r.proximo,col]); exclusoes.append(r.loc[~r.avaliavel,col]); discordantes.append(r.loc[r.discordante_principal,col])
    for k,v in tabelas.items(): csv_novo(pd.concat(v,ignore_index=True),saida/f'comparacao_por_{k}.csv')
    for nome,v in [('casos_proximos',proximos),('exclusoes_qualidade',exclusoes),('discordancias_classificacao',discordantes)]:
        csv_novo(pd.concat(v,ignore_index=True),saida/f'{nome}.csv')
    registro={'fonte_concluido_sha256':sha(raiz/'concluido.json'),'codigo_sha256':sha(Path(__file__)),
        'pares':len(q),'cenarios':CENARIOS,'qualidades_pct':QUALIDADES,'variantes':VARIANTES,
        'proximidade':'abs(min(R/tau,C/A_min)-1)<=0.10 entre avaliáveis; apenas faixa de auditoria',
        'sem_alvo_homologado':True,'sem_treinamento':True,
        'arquivos_sha256':{p.name:sha(p) for p in saida.iterdir() if p.is_file()}}
    (saida/'manifesto.json').write_text(json.dumps(registro,ensure_ascii=False,indent=2),encoding='utf-8')
    print(pd.concat(tabelas['global']).query("variante=='principal'").to_string(index=False),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__); p.add_argument('--resultados',type=Path,required=True)
    p.add_argument('--saida',type=Path,required=True); a=p.parse_args(); executar(a.resultados,a.saida)
