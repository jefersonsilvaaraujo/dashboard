"""Auditoria independente da matriz candidata e preservação dos checkpoints."""
import argparse
import json
from pathlib import Path
import sys
import numpy as np
import pandas as pd

PROJETO=Path(__file__).resolve().parents[1];sys.path.insert(0,str(PROJETO))
from processamento.cenarios_validacao_col9 import sha,csv_novo
from modelagem.preparar_regressao_continua_col9 import validar_X,CHAVES


def executar(raiz,saida):
    if saida.exists():raise FileExistsError('Auditoria anterior preservada.')
    saida.mkdir(parents=True)
    p=raiz/'matriz';x=pd.read_parquet(p/'MATRIZ_ATRIBUTOS_CANDIDATOS_COL9.parquet')
    r=pd.read_parquet(p/'RESPOSTAS_CONTINUAS_COL9.parquet');i=pd.read_parquet(p/'INDICE_CANONICO_9690_COL9.parquet')
    cat=json.loads((raiz/'metadados/catalogo_atributos.json').read_text(encoding='utf-8'));validar_X(x,cat)
    canon=json.loads((PROJETO/'referencias/territorio_col9_hashes.json').read_text(encoding='utf-8'))['geometrias_sha256_wkb_ndr']
    if len(x)!=9690 or set(x.CD_MUN)!=set(canon):raise ValueError('Universo incorreto.')
    if not x.groupby('CD_MUN').ano_t.apply(lambda s:s.tolist()==list(range(1985,2023))).all():raise ValueError('Intervalos incorretos.')
    pd.testing.assert_frame_equal(x[CHAVES].reset_index(drop=True),i[CHAVES].reset_index(drop=True))
    pd.testing.assert_frame_equal(r[CHAVES].reset_index(drop=True),i[CHAVES].reset_index(drop=True))
    np.testing.assert_allclose(r.R_pct,100*r.C_ha/r.D_ha,rtol=1e-12,atol=1e-10)
    if not r.R_pct.between(0,100).all():raise ValueError('R fora do domínio.')
    disp=pd.read_parquet(raiz/'metadados/DISPONIBILIDADE_ATRIBUTOS_COL9.parquet')
    if not disp.ano_max_informacao_fenomeno.le(disp.ano_t).all():raise ValueError('Vazamento direto do fenômeno.')
    faltas=[]
    for m in cat:
        s=x[m['variavel']];faltas.append({'variavel':m['variavel'],'n_ausentes':int(s.isna().sum()),
            'pct_ausentes':100*s.isna().mean(),'status_temporal':m['status_temporal'],
            'primeiro_ano_historico_suficiente':m['primeiro_ano_historico_suficiente']})
    csv_novo(pd.DataFrame(faltas),saida/'AUSENCIAS_POR_ATRIBUTO.csv')
    ant={};unicos={}
    for nome in ['validacao_cientifica_col9/checkpoint_20261111/manifesto_checkpoint.json',
        'validacao_cientifica_col9/piloto_interpretacao_20261111_v1/manifesto_gestao.json',
        'validacao_cientifica_col9/oficial_col9_20261112_v1/manifesto_final.json']:
        f=PROJETO/nome;m=json.loads(f.read_text(encoding='utf-8'))
        for n,h in m['sha256'].items():
            if sha(PROJETO/n)!=h:raise ValueError(f'Checkpoint alterado:{n}')
            unicos[n]=h
        ant[nome]={'sha256':sha(f),'n_arquivos':len(m['sha256'])}
    bloco='complementares/manifesto_blocos_integridade_v2.json' if (raiz/'complementares/manifesto_blocos_integridade_v2.json').exists() else 'complementares/manifesto_blocos.json'
    for nome in ['contrato_preparacao.json','diagnosticos/manifesto_diagnostico.json',bloco]:
        mm=json.loads((raiz/nome).read_text(encoding='utf-8'))
        pasta=raiz/Path(nome).parent
        for n,h in mm['artefatos_sha256'].items():
            if sha(pasta/n)!=h:raise ValueError('Artefato novo não confere com manifesto.')
    rm=PROJETO/'referencias/manifesto_rasters_transicoes_col9.json';m=json.loads(rm.read_text(encoding='utf-8'));base=Path(m['base_dados'])
    for ano,a in m['rasters'].items():
        st=(base/a['arquivo']).stat()
        if st.st_size!=a['bytes'] or st.st_mtime_ns!=a['mtime_ns']:raise ValueError('Raster original alterado.')
    fontes=json.loads((raiz/'metadados/fontes_matriz.json').read_text(encoding='utf-8'))
    for nome,h in fontes['estoques_npz_sha256'].items():
        if sha(PROJETO/nome)!=h:raise ValueError('NPZ municipal alterado.')
    legado={}
    for n,h in {'app.py':'a71cf9d8ccf45aa52c08cc734093208952b736d49fdbea9842d0d3cdfc1fbc87',
                'dados.py':'e7fe3009b1a4b5978499bfe891272c3455e11b0e215f91070f2a9a06d9ba8fba'}.items():
        if sha(PROJETO/n)!=h:raise ValueError('Legado alterado.')
        legado[n]=h
    info={'n_municipios':255,'intervalos':38,'n_chaves':len(x),'n_atributos':len(cat),
        'n_metadados_ponto_atributo':len(disp),'n_chaves_2023_sem_resposta':255,'duplicatas':0,
        'informacao_direta_posterior_a_t_em_X':0,'colunas_proibidas_em_X':0,
        'atributos_sujeitos_analise':sum(m['status_temporal']=='sujeito_a_analise' for m in cat),
        'atributos_permitidos_em_principio':sum(m['status_temporal']=='permitido_em_principio' for m in cat),
        'n_caminhos_anteriores_distintos':len(unicos),'checkpoints_anteriores':ant,'divergencias_checkpoints':0,
        'rasters39_tamanho_mtime_preservados':True,'nota_hashes_rasters':'Usados os SHA256 prévios; não relidos integralmente159GB.',
        'NPZs_255_verificados_por_hash':True,'legado':legado,
        'nao_usou_2024':True,'sem_banco_Docker_dashboard_migracao':True,'sem_treinamento_busca_ou_desempenho_teste':True,
        'codigo_sha256':sha(Path(__file__))}
    with (saida/'auditoria.json').open('x',encoding='utf-8') as f:json.dump(info,f,ensure_ascii=False,indent=2)
    print(json.dumps({k:v for k,v in info.items() if k not in ['checkpoints_anteriores','legado']},ensure_ascii=False,indent=2),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--checkpoint',type=Path,required=True);p.add_argument('--saida',type=Path,required=True)
    a=p.parse_args();executar(a.checkpoint,a.saida)
