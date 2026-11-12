"""Figuras científicas a partir das saídas auditadas; não consulta banco/modelo."""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def gerar(analise,relatorio):
    figuras=analise/'figuras'
    if figuras.exists(): raise FileExistsError('Figuras anteriores preservadas; escolher outra análise.')
    figuras.mkdir()
    raiz=analise.parent
    qa=pd.read_csv(raiz/'metricas_municipio_ano.csv',encoding='utf-8-sig')
    anual=pd.read_csv(analise/'resumo_anual.csv',sep=';',encoding='utf-8-sig')
    bur=pd.read_csv(analise/'buriticupu_pares_vs_tripla.csv',sep=';',encoding='utf-8-sig')
    manifesto={}
    def salvar(fig,nome,titulo):
        fig.update_layout(template='plotly_white',font=dict(family='DejaVu Sans',size=14),
                          title=titulo,margin=dict(l=85,r=40,t=100,b=85),width=1250,height=720)
        p=figuras/(nome+'.png'); fig.write_image(str(p),scale=2)
        manifesto[p.name]={'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'titulo':titulo}
    r=np.sort(qa.taxa_conversao_pct.dropna().to_numpy())
    fig=go.Figure(go.Scatter(x=r,y=100*np.arange(1,len(r)+1)/len(r),mode='lines',line=dict(width=3)))
    fig.update_xaxes(title='Taxa anual de conversão (% da VN inicial elegível)')
    fig.update_yaxes(title='Comparações acumuladas (%)',range=[0,100])
    salvar(fig,'01_distribuicao_taxas','Coleção 9 · 255 municípios · 9.690 pares anuais<br>Distribuição empírica das taxas mapeadas')
    s=qa.area_convertida_ha.dropna(); pos=np.sort(s[s>0].to_numpy())
    fig=go.Figure(go.Scatter(x=pos,y=100*np.arange(1,len(pos)+1)/len(pos),mode='lines',line=dict(width=3)))
    fig.update_xaxes(type='log',title='Área anual convertida (ha) · escala logarítmica')
    fig.update_yaxes(title='Comparações com conversão positiva acumuladas (%)',range=[0,100])
    fig.add_annotation(x=0.02,y=.1,xref='paper',yref='paper',showarrow=False,
                       text=f'{int(s.eq(0).sum())} comparações com área zero fora deste eixo log; incluídas nas tabelas.')
    salvar(fig,'02_distribuicao_areas','Coleção 9 · distribuição das áreas convertidas<br>Somente observações positivas no eixo logarítmico')
    fig=px.bar(anual,x='ano_destino',y='area_convertida_ha',labels={'ano_destino':'Ano de destino (t+1)','area_convertida_ha':'Área anual convertida, soma municipal (ha)'})
    salvar(fig,'03_conversao_anual','Coleção 9 · VN(t) → usos antrópicos(t+1)<br>Áreas mapeadas por ano · máscara válida comum')
    fig=go.Figure()
    for campo,nome in [('taxa_regional_razao_somas_pct','Regional: razão entre somas'),
                        ('taxa_mediana_municipal_pct','Mediana entre municípios'),
                        ('taxa_p95_municipal_pct','P95 entre municípios')]:
        fig.add_trace(go.Scatter(x=anual.ano_destino,y=anual[campo],mode='lines+markers',name=nome))
    fig.update_xaxes(title='Ano de destino (t+1)'); fig.update_yaxes(title='Taxa anual de conversão (%)')
    fig.update_layout(legend=dict(orientation='h',y=-.2))
    salvar(fig,'04_taxas_anuais','Coleção 9 · taxas regionais e distribuição municipal<br>Razão regional ≠ média simples de percentuais')
    positivos=qa[qa.area_convertida_ha.gt(0)&qa.taxa_conversao_pct.notna()]
    fig=px.scatter(positivos,x='area_convertida_ha',y='taxa_conversao_pct',color='SIGLA_UF',
                   opacity=.45,log_x=True,labels={'area_convertida_ha':'Área anual convertida (ha, log)',
                     'taxa_conversao_pct':'Taxa anual de conversão (%)','SIGLA_UF':'UF'})
    salvar(fig,'05_taxa_area','Coleção 9 · taxa relativa versus conversão absoluta<br>Revisar extremos junto ao denominador e à elegibilidade')
    linhas=[]
    for r in bur.itertuples():
        for sufixo,nome in [('par','Máscara comum do par'),('tripla','Máscara comum 2001–2003')]:
            linhas.append({'intervalo':f'{r.ano_origem}→{r.ano_destino}','mascara':nome,
                           'area_ha':getattr(r,f'area_convertida_ha_{sufixo}')})
    fig=px.bar(pd.DataFrame(linhas),x='intervalo',y='area_ha',color='mascara',barmode='group',
               labels={'intervalo':'Comparação anual','area_ha':'Área convertida (ha)','mascara':'Suporte válido'})
    salvar(fig,'06_buriticupu','Buriticupu/MA (2102325) · auditoria 2001–2003<br>Conversão VN→UA sob dois suportes espaciais')
    (figuras/'manifesto.json').write_text(json.dumps(manifesto,ensure_ascii=False,indent=2),encoding='utf-8')
    # Caminhos relativos ao relatório no host: ambos estão sob a raiz do projeto.
    caminho_rel='../resultados_transicoes_col9/'+raiz.name+'/analise_exploratoria/figuras/'
    with relatorio.open('a',encoding='utf-8') as f:
        f.write('\n## Figuras exploratórias\n\n')
        for nome,info in manifesto.items():
            f.write(f"![{info['titulo'].replace('<br>',' — ')}]({caminho_rel}{nome})\n\n")
    print(f'Seis figuras novas exportadas em {figuras}; sem banco ou modelo.')


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--analise',type=Path,required=True); p.add_argument('--relatorio',type=Path,required=True)
    a=p.parse_args(); gerar(a.analise,a.relatorio)
